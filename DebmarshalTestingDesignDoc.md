# Objective #

Provide an easy to use, freely available framework for testing whole systems and multi-package interactions at a system level. Using virtualization to build entire platforms for running automated tests in an environment isolated from the outside world to minimize risk.

It is not a goal of this project to create or provision virtual machines that are intended to persist for long periods of time, or even necessarily virtual machines that the user can interact with.

# Background #

Most testing happens at a very fine level through unit tests, while there are relatively few methods for total system testing, and even fewer for testing system interaction. As a simple example, what happens to a phpMyAdmin server if the MySQL server goes away, or delivers bogus data?

## Related Projects ##

[Ganeti](http://code.google.com/p/ganeti/) is used for virtual machine hosting in server farms, but VMs are typically allocated one at a time for long-term usage. This project is different in that it is designed for creating and running multiple, very temporary virtual machines in network isolation.

The [Zumastor](http://zumastor.org/) project previously used virtual machines in qemu for testing functionality; this project is the spiritual descendant of that project.

The Debmarshal testing framework hopes to integrate multiple virtualization technologies to allow developers to balance performance against the extent to which the guest environment will be virtualized. [libvirt](http://libvirt.org/) is designed to provide a single API to multiple virtualization platforms. It also seems to be acquiring Linux distribution buy-in (e.g. [Ubuntu](https://help.ubuntu.com/8.04/serverguide/C/virtualization.html), [Red Hat](http://www.redhat.com/rhel/server/details/)), especially through the [virt-manager](http://virt-manager.et.redhat.com/) software package.

# Overview #

The Debmarshal suite of software is designed for simplifying management and rollout of Debian packages. The Debmarshal testing framework is specifically targeted at the testing stage of development, but is also designed with a wide enough view to expand to other forms of software delivery.

Since it is currently difficult to do total systems and systems integration testing, the Debmarshal testing framework intends to provide a framework for easily specifying virtual machine-based tests. A test "minisuite" is broken into two pieces: the test parameters and the test script.

The test parameters cover information about the VMs to create: how much memory and disk space to allocate, and what distribution and software to install. The parameters can also indicate a timeout for the test, and whather a or not a test is expected to fail. Finally, the test parameters can also include a collection of files to install in the various VMs.

The actual test script is simply any executable. Many system-level tests are more easily conducted from bash than from other scripting languages, so we didn't want to limit developers by restricting tests to Python. However, we will provide convenience libraries for Python to make common operations for these tests (e.g. remotely accessing and running a command on a particular VM) easy. A test will pass if the test script returns 0, otherwise it will be considered a failure.

The separation between test parameters and test scripts is deliberate for security reasons. In order to isolate any potential side-effects of executing the test, the test script itself will only be executed from one of the VMs created for the purpose of running the test. The test parameters, on the other hand, are purely declarative and non-executable.

The Debmarshal testing framework will initially be used to build a test suite for internal Google services, including testing interactions between multiple dependent systems.