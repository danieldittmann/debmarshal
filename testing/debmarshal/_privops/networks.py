#!/usr/bin/python
# -*- python-indent: 2; py-indent-offset: 2 -*-
# Copyright 2009 Google Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
"""debmarshal privileged networking operations.

This module handles creating and destroying virtual networks that are
used for debmarshal test suites.
"""


__authors__ = [
    'Evan Broder <ebroder@google.com>',
]


import itertools
import re

import libvirt
from lxml import etree

from debmarshal import errors
from debmarshal import ip
from debmarshal._privops import utils
import debmarshal.utils as u


def _listBridges():
  """Return a generator containing all network bridges.

  Yields:
    A list of network bridges that exist on the host system.
  """
  out = u.captureCall(['brctl', 'show'])
  lines = out.strip().split('\n')
  for line in lines[1:]:
    net = line.split()[0]
    if net.startswith('debmarshal-'):
      yield net


_hostname_re = re.compile(
  r"([a-z0-9][a-z0-9-]{0,62}\.)*[a-z0-9][a-z0-9-]{0,62}$", re.I)


def _validateHostname(name):
  """Check that the input is a valid hostname.

  Args:
    name: The hostname to validate

  Returns:
    None

  Raises:
    debmarshal.errors.InvalidInput if the hostname is not valid
  """
  if not _hostname_re.match(name):
    raise errors.InvalidInput('Invalid hostname: %s' % name)


def loadNetworkState():
  """Load state for any networks previously created by debmarshal.

  State is written to /var/run/debmarshal-networks as a pickle. Ubuntu
  makes /var/run a tmpfs, so state vanishes after reboots - which is
  good, because the networks debmarshal has created do as well.

  Not all distributions do this, though, so we loop over the networks
  in the pickle and see which ones still exist. If a network no longer
  exists, we assume that it was deleted outside of debmarshal, and we
  erase our record of it.

  Returns:
    A list of networks. Each network is a tuple of (network_name,
      owner_uid, gateway_ip_address)
  """
  networks = utils.loadState('debmarshal-networks')
  if not networks:
    networks = {}

  bridges = set(_listBridges())

  for n in networks.keys():
    if n not in bridges:
      del networks[n]

  return networks


def _networkBounds(gateway, netmask):
  """Find the start and end of available IP addresses in a network.

  Args:
    gateway: The gateway addresses of the network
    netmask: The netmask of the network

  Returns:
    Tuple of the form (low_ip, high_ip)
  """
  net = ip.IP('%s/%s' % (gateway, netmask))
  low = ip.IP(ip.IP(gateway).ip + 1)
  high = ip.IP(net.broadcast - 1)
  return (low.ip_ext, high.ip_ext)


def _genNetworkXML(name, gateway, netmask, hosts):
  """Generate the libvirt XML specification for a debmarshal network.

  Args:
    name: Name of the network, usually debmarshal-##
    gateway: The "gateway" for the network. Although debmarshal
      networks are isolated, you still need a gateway for things like
      the DHCP server to live at
    netmask: Network mask for the gateway.
    hosts: The hosts that will be attached to this network. It is a
      dict from hostnames to a 2-tuple of (IP address, MAC address),
      similar to the one that's returned from createNetwork

  Returns:
    The string representation of the libvirt XML network matching the
      parameters passed in
  """
  xml = etree.Element('network')
  etree.SubElement(xml, 'name').text = name
  xml_ip = etree.SubElement(xml, 'ip',
                            address=gateway,
                            netmask=netmask)

  low, high = _networkBounds(gateway, netmask)

  xml_dhcp = etree.SubElement(xml_ip, 'dhcp')
  etree.SubElement(xml_dhcp, 'range',
                   start=low,
                   end=high)

  for hostname, hostinfo in hosts.iteritems():
    etree.SubElement(xml_dhcp, 'host',
                     name=hostname,
                     ip=hostinfo[0],
                     mac=hostinfo[1])

  return etree.tostring(xml)


def _findUnusedName():
  """Find a name for a new debmarshal network.

  This picks a name for a new debmarshal network by simply
  incrementing the name until a name is found that is not currently
  being used.

  To prevent races, this function should be called by a function that
  has taken out the debmarshal-netlist lock exclusively.

  Returns:
    An unused name to use for creating a new network.
  """
  bridges = _listBridges()

  for n in itertools.count(0):
    name = 'debmarshal-%s' % n

    if name not in bridges:
      return name


def _findUnusedNetwork(host_count):
  """Find an IP address network for a new debmarshal network.

  This picks a gateway IP address by simply incrementing the subnet
  until one is found that is not currently being used.

  To prevent races, this function should be called by a function that
  has taken out the debmarshal-netlist lock exclusively.

  Currently IP addresses are allocated in /24 blocks from
  169.254.0.0/16. Although this is sort of a violation of RFC 3927,
  these addresses are still link-local, so it's not a misuse of the
  block.

  This does mean that debmarshal currently has an effective limit of
  256 test suites running simultaneously. But that also means that
  you'd be running at least 256 VMs simultaneously, which would
  require some pretty impressive hardware.

  Args:
    host_count: How many hosts will be attached to this network.

  Returns:
    A network to use of the form (gateway, netmask)

  Raises:
    debmarshal.errors.NoAvailableIPs: Raised if no suitable subnet
      could be found.
  """
  # TODO(ebroder): Include the netmask of the existing networks when
  #   calculating available IP address space
  net_gateways = set()
  for net in _listBridges():
    # ifdata is part of moreutils (http://kitenet.net/~joey/code/moreutils/)
    net_gateways.add(u.captureCall(['ifdata', '-pa', net]).strip())

  for i in xrange(256):
    # TODO(ebroder): Allow for configuring which subnet to allocate IP
    #   addresses out of
    net = '169.254.%d.1' % i
    if net not in net_gateways:
      # TODO(ebroder): Adjust the size of the network based on the
      #   number of hosts that need to fit in it
      return (net, '255.255.255.0')

  raise errors.NoAvailableIPs('No unused subnet could be found.')


def _setupBridge(iface, ip, mask):
  """Create and up an ethernet bridge.

  Args:
    iface: The name of the bridge.
    gateway: The IP address to listen on.
    mask: The subnet mask of the gateway.
  """
  u.captureCall(['brctl', 'addbr', iface])
  u.captureCall(['ifconfig', iface,
                 ip,
                 'netmask', mask,
                 'up'])


def _teardownBridge(iface):
  """Down and delete an ethernet bridge.

  Args:
    iface: The name of the bridge.
  """
  u.captureCall(['ifconfig', iface, 'down'])
  u.captureCall(['brctl', 'delbr', iface])
