# Introduction #

Often the slowest part of a test run is building the test source under a protected virtualization layer.  This benchmark configures and compiles about 3M of C source code on Debian/lenny.  This typically takes on the order of a minute and fits in a relatively small VM. Even on very underpowered host systems under heavy virtualization is likely to finish in an hour or so.  Single and multithreaded builds (make -j2) are recorded, and multiple host root filesystems and other options are compared as the particular VM allows.

# Details #

```
mkdir lenny-dir
debootstrap --arch=i386 --include=ssh,build-essential,libncurses-dev,wget --verbose lenny lenny-dir
dd if=/dev/zero bs=1M seek=1000 count=0 of=lenny.ext3
mkfs -t ext3 -F lenny.ext3
mkdir lenny-loopback
mount -o loop lenny.ext3 lenny-loopback
tar cf - -C lenny-dir . | tar xvf - -C lenny-loopback
umount lenny-loopback
```

```
aptitude install build-essential libncurses-dev wget
wget -O empire-4.3.10.tar.gz 'http://sourceforge.net/project/showfiles.php?group_id=24031&package_id=40131&release_id=537696'
tar zxvf empire-4.3.10.tar.gz
cd empire-4.3.10
./configure
time make
make clean
time make -j2
make clean
time make -j4
```

# Results #

|                      | Build | time(s) | | | | | |
|:---------------------|:------|:--------|:|:|:|:|:|
| **Containers**         |       | T60p<sup>1</sup> | Atom<sup>2</sup> | Quad<sup>3</sup> |  |  |  |
| i386 chroot<sup>a</sup>       |   -j1 |  64s<sup>*</sup> | 140s    | 39s     |
|                      |   -j2 |     37s | 106s    | 20s     |
|                      |   -j4 |         |         | 13s     |
| i386 chroot loopback<sup>b</sup> | -j1 | 54s<sup>*</sup> |         | 39s     |
|                      |   -j2 |  36s    |         | 21s     |
|                      |   -j4 |         |         | 13s     |
| x86\_64 chroot<sup>b</sup>     | -j1   | _N/A_<sup>@</sup> | 148s   | 40s     |
|                      | -j2   | _N/A_<sup>@</sup> | 112s   | 21s     |
|                      | -j4   | _N/A_<sup>@</sup> |        | 14s     |
|                      | -j8   | _N/A_<sup>@</sup> |        | 12s     |
| x86\_64 chroot loopback | -j1 | _N/A_<sup>@</sup> |        | 40s     |
|                        | -j2 | _N/A_<sup>@</sup> |        | 21s     |
|                        | -j2 | _N/A_<sup>@</sup> |        | 14s     |
| i386 openvz          |   -j1 | 53s | 149s |  |
|                      |   -j2 | 39s | 107s |  |
|                      |   -j4 |  | 105s |  |
| x86\_64 openvz        |   -j1 | _N/A_<sup>@</sup> | 148s   |  |
|                      |   -j2 | _N/A_<sup>@</sup> | 114s   |  |
| i386 vserver         |       |          |        |  |
| x86\_64 vserver       |       | _N/A_<sup>@</sup> |        |  |
|                      | Build | time(s) |  |  |  |  |  |
| **Paravirtualization** |       | T60p<sup>1</sup> | Atom<sup>2</sup> | Quad<sup>3</sup> |  |  |  |
| UML SKAS0            |   -j1 |  121s   |         |  |
|                      |   -j2 |  118s   |         |  |
| UML SKAS0 hostfs     |   -j1 |  142s   |         |  |
| UML SKAS0 hostfs     |   -j2 |  141s   |         |  |
| i386 xen<sup>b</sup>          |   -j1 | hot<sup>+</sup>  |         | 38s     |
|                      |   -j2 | hot<sup>+</sup>  |         | 39s     |
| x86\_64 xen<sup>b</sup>        |   -j1 | _N/A_<sup>@</sup> |        | 38s     |
|                      |   -j2 | _N/A_<sup>@</sup> |        | 39s     |
| 4cpu x86\_64 xen      |   -j1 | _N/A_<sup>@</sup> |        | 40s     |
|                      |   -j2 | _N/A_<sup>@</sup> |        | 21s     |
|                      |   -j4 | _N/A_<sup>@</sup> |        | 14s     |
| i386 virtualbox      |       |          |        |         |
| x86\_64 virtualbox    |       | _N/A_<sup>@</sup> |        |         |
|                      | Build | time(s) |  |  |  |  |  |
| **Full virtualiztion** |       | T60p<sup>1</sup> | Atom<sup>2</sup> | Quad<sup>3</sup> |  |  |  |
| i386 qemu<sup>c</sup>         |   -j1 | 1260s   |         |         |
|                      |   -j2 | 1479s   |         |         |
| i386 qemu<sup>c</sup> -smp 2  |   -j2 | 1450s   |         |         |
| x86\_64 qemu          |   -j1 |         |         |         |
| i386 kqemu           |   -j1 |         |         |         |
| x86\_64 kqemu         |   -j2 | _N/A_<sup>@</sup> |        |         |
| i386 kvm             |   -j1 |     72s | _N/A_<sup>&</sup> |        |
|                      |   -j2 |  75s    | _N/A_<sup>&</sup> |        |
| i386 kvm -smp 2      |   -j2 |  40s    | _N/A_<sup>&</sup> |        |
| x86\_64 kvm           |   -j1 | _N/A_<sup>@</sup> | _N/A_<sup>&</sup> |       |
| i386 xen hvm         |       |         |          |        |
| x86\_64 xen hvm       |       | _N/A_<sup>@</sup> |         |        |
| VMWare               |       |         |          |        |

<sup>1</sup> - Lenovo Thinkpad T60p, 2G RAM, 2.17GHz Core Duo, 2.6.30 Debian/sid 2009-07.  host FS is on a LUKS encrypted partition

<sup>2</sup> - Intel G945 1.6GHz, 2.6.26 Debian/lenny x86\_64 host.  1G RAM. Host FS is unencrypted 1TB 7200rpm drive

<sup>3</sup> - Dell 2950, 2x2 2.66 GHz Xeon, 4G RAM, 6x10K SCSI RAID5.

<sup>a</sup> - `mkdir lenny ; debootstrap --arch=i386 _args_ lenny ; chroot lenny /bin/bash`

<sup>b</sup> - Debian/lenny Xen 3.2 per http://www.howtoforge.com/virtualization-with-xen-on-debian-lenny-amd64

<sup>c</sup> - `dd if=/dev/zero bs=1M seek=1000 count=0 of=lenny.ext3 ; mkfs -t ext3 -F lenny.ext3 ; mkdir lenny ; mount -o loop lenny.ext3 lenny`

<sup>d</sup> - `qemu -m 256M -hda lenny.ext3 -net nic -net tap,ifname=tap0,script=no -kernel /boot/vmlinuz-2.6.30-1-686 -initrd /boot/initrd.img-2.6.30-1-686 -append root=/dev/hda`

<sup>*</sup> - very unexpected that host filesystem is typically slower than loopback

<sup>&</sup> - No harware virtualization (vmx/svm) CPU feature flag.

<sup>@</sup> - No 64bit (lm) CPU feature flag.

<sup>+</sup> - Xen runs CPUs at full clock rate, and caused multiple thermal shutdowns before file-backed VMs could be debugged on this platform. No performance numbers are available pending cooling improvements.  Running Xen on a laptop is a bad idea on power and thermal considerations.

## Warnings ##

> Verify that the local clock is accurate.  Some run slow under some virtualization engines. QEMU and UML are particularly susceptible to this.  time an ssh session into the machine that sleeps for a known amount of time.

# Preliminary results #

  1. Don't use Xen on laptops due to thermal and power considerations.

> 2 Use containers if possible (eg. OpenVZ).

> 3 Use UML if no kernel mods are possible and architecture is compatible.

> 4 Qemu always works on everything, and is a good place to start a design.

> 5 KVM is fast (90%+ bare metal) and drop-in Qemu compatible.