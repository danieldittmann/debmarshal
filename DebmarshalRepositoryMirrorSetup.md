# Introduction #

The best way to do a verbatim mirror into a debmarshal repository is using a patch and flag (--debmarshal) to debmirror to build the repository directly.  See http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=550007 for the patch and status of merging that into upstream.

Eventually Mode: tracking in debmarshal will go away.

# Debmarshal tracking mode #

This is a simple setup to mirror and upstream Debian or Ubuntu repository, keeping snapshots and allowing aliases to be kept.

This is a prerequisite to having a repository of your own directly supervised packages, which will have dependencies on the mirrored archive.


# Details #

## debmirror ##

### Allocate archive space ###

Make sure /var/lib/debmarshal has sufficient space.  Allocate at least 40G per distribution and architecture, and probably its own filesystem so it can't fill /var.
If one of your mirrors is rapidly changing, you'll need lots of diskspace.

### Create debmarshal user ###

A separate user will download and verify packages, and later maintain the upload queue and
distribution tracks.

```
adduser --disabled-login debmarshal
```

### Install debmirror and gnupg ###

```
aptitude install debmirror gnupg
```

### Add repository keys ###

```
su - debmarshal
gpg --no-default-keyring --keyring ~/.gnupg/trustedkeys.gpg --keyserver hkp://subkeys.pgp.net --recv-key 55BE302B F42584E6
gpg --no-default-keyring --keyring ~/.gnupg/trustedkeys.gpg --list-key
```

Verify and modify trust using =gpg= with your web of trust as well you can.

### Archive pull ###

Make sure archive pulls are working first, before setting up the debmarshal portion of the archive.

/usr/local/bin/mirror-debian
```
/usr/bin/debmirror --debug -v --progress \
        --method=http \
        -h ftp.us.debian.org --root=/debian \
        --dist=lenny \
        --section=main,contrib,non-free,main/debian-installer \
        --arch=i386,amd64 \
        --nocleanup --source \
        --debmarshal \
        /var/lib/debmarshal/debian
```

/etc/cron.d/debian-mirror
```
MAILTO="debmarshal@localhost"
PATH=/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin:/bin:/sbin
10 15     * * *   debmarshal   /usr/local/bin/mirror-debian
```

# Debmarshal configuration #

## generate a gpg signing key ##

Its easiest if the debmarshal signing key has no passphrase, but you can also put it unencrypted on ramdisk, set up a signing agent, or type in the passphrase each time debmarshal requires.

```
aptitude install gnupg
su - debmarshal
gpg --gen-key
```

## pool injection ##

The new packages in debian/pool need to be indexed first and added to the Debmarshal database.  The configuration of the releases to track is

/var/lib/debmarshal/debian/config/repository
```
Mode: tracking
Architectures: i386, amd64

[[lenny]
Origin: Debian
Description: Debian/lenny
```

Multiple [.md](.md) stanzas may be used to track multiple releases in the same repository.

The cwd is used to determine where the configuration, database, pool, and dist directories are for the pool indexer.  pool\_indexer assumes all package's signatures are already verified, so it is important that debmirror be configured to verify release signatures.

```
su - debmarshal
cd /var/lib/debmarshal/debian
mkdir dbs
/usr/lib/debmarshal/index_pool.py
```

Append the cd and index\_pool.py invocations to your mirror script to automatically index on each download.

## Snapshot a release ##

First, check to see whether anything would change between the latest snapshot and a new one.

```
cd /var/lib/debmarshal/debian
/usr/lib/debmarshal/make_release.py --dist dists/lenny --track lenny diff lenny/latest
```

Lines that start with + or - are changes.  If there are changes in packages or versions, make a new snapshot:

```
/usr/lib/debmarshal/make_release.py --dist dists/lenny --track lenny commit
```

This will create numbered subdirectories starting with dists/lenny/0 with the distribution as it exists in dists/lenny/Release at the time this is run, embedding
snapshots within the existing release structure.  dists/lenny/latest will be a symlink to the most recent snapshot.

Leave out `commit`, or replace it with `diff dists/lenny/latest` to see what make\_release.py would do on a commit.

Append the make\_release command(s) after index\_pool in your cron job.

# Staging #

The main reason to use debmarshal for even simple mirrors is to control when a particular release goes to a set of machines.  With this, you can have all of your machines pulling named aliases, and then update those aliases as you want machines to upgrade themselves.
Each numbered release in a track can be pointed to by any number of aliases. Any number of aliases may be created to meet your staging requirements, for instance: latest, bleeding, tested, canary, golden, ...
> latest always availble, and created and updated automatically by `make_release.py`.  The others are created by you or your own scripts and processes as follows:

```
cd /var/lib/debmarshal/debian
/usr/lib/debmarshal/handle_alias.py update lenny/golden 0
```

These are little more than symlinks in the dists/lenny directory, but register in the central database for auditing and cleanup purposes.  To see the history of an alias:

```
/usr/lib/debmarshal/handle_alias.py log lenny/latest
```

# Export #

Use any web server you like to export your `debian` or `ubuntu` tree.  Symlinks in /var/www are simplest, or create real VirtualHost entries in /etc/apache2/sites-available and a2ensite, ...

```
aptitude install apache2
cd /var/www
ln -s /var/lib/debmarshal/debian debian
```