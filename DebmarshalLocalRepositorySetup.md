# Introduction #

This is a setup for a local repository for your own packages on top of a DebmarshalRepositoryMirrorSetup.


# Details #

## Upstream mirror repository ##

Set up a mirror as in DebmarshalRepositoryMirrorSetup.  make sure there is sufficient space for your own local packages (usually very small compared to an upstream repository).

## Your gnupg key ##

If you don't already have a gnupg key, create one (and a revocation certificate.

```
gpg --gen-key
[ some interactive questions and passphrase ]
gpg --gen-revoke --armor >mykey.revoke.asc
gpg --armor --export {keyid} >uploader.asc
```



## Import uploader's gpg keys ##

```
su - debmarshal
gpg --no-default-keyring --keyring ~/.gnupg/trustedkeys.gpg --import uploader.asc
```

## Create repository ##

This sets up a repository named local (as opposed to debian or ubuntu), and a distribution track local0 inside that repository (as opposed to lenny for instance).  Using your own descriptive name(s) is advised.

```
cd /var/lib/debmarshal
mkdir local local/incoming local/dists local/pool local/dbs local/config
chown -R debmarshal:debmarshal local
chmod 2777 local/incoming
```

local/config/repository

---

```
Mode: supervised
Component: local
Architectures: i386, amd64

[local0]
Origin: Local
Description: Local packages
Underlying:
 http://localhost/debian lenny/latest
```


local/config/local0.spec

---

```
# specify policies for which packages go in this distribution track
# List packages by name without revision to track latest versions
# of those.  Before a package is specified, an optional version
# restriction may also be specified.  eg.
#    local-package (= 1)
#    local-package
# + means all packages. 
+
```

## Uploading your packages ##

Sign your packages if debuild didn't already do this.
```
for f in *.changes ; do debsign $f ; done
```

Copy the signed packages to the incoming directory on the debmarshal host machine.
```
cp *.deb *.changes *.diff.gz *.tar.gz *.dsc *.changes \
  /var/lib/debmarshal/local/incoming/
```

As the debmarshal user, run enter\_incoming.py from the root of the repository.
```
su - debmarshal
cd /var/lib/debmarshal/local
/usr/lib/debmarshal/enter_incoming.py
```

Verify that the snapshot dist looks correct for the newly uploaded packages.  Normally you wouldn't use the snapshot track (which always has the latest packages just uploaded), but the more carefully maintained local0 track.
```
ls -lR dists/snapshot
dists/snapshot:
  ... 0
  ... latest -> 0
dists/snapshot/0:
  ... local
  ... Release
  ... Release.gpg
dists/snapshot/0/local:
  ... binary-amd64
  ... binary-i386
  ... source
dists/snapshot/0/local/binary-amd64:
  ... Packages
  ... Packages.gz
  ... Release
dists/snapshot/0/local/binary-i386:
  ... Packages
  ... Packages.gz
  ... Release
dists/snapshot/0/local/source:
total 12
  ... Release
  ... Sources
  ... Sources.gz
```

The packages themselves should be moved to subdirectories of pool/, and no files should remain in incoming after a successful upload.

.build files are not normally part of an upload, and would be left behind.  .changes files will be deleted on unsuccessful uploads, to prevent the uploader from trying and failing to verify them repeatedly.

## Make a first release ##

```
cd /var/lib/debmarshal/local
/usr/lib/debmarshal/make_release.py --release snapshot/latest --track local0 commit
```

dists/local0 should have a similar layout to dists/snapshot, until you start putting restrictions into your local0.spec file.

## Check new changes ##

After modifying the pool (through enter\_incoming.py) or the package specification (.spec file), there may or may not be changes to the Packages files for a release track.  To preview them:

```
/usr/lib/debmarshal/make_release.py --release snapshot/latest --track local0 diff local0/latest
```

This pulls in packages from snapshot/latest acording to the local0 spec file, then diffs the result against the current contents of local0/latest.  No change to the repository is made.  The output from this command may be used to determine when a new release should be made again using the same command as the initial track creation above (with commit).

### Further verification ###

Undeclared package conflicts such as file overlaps, and unresolvable dependencies may be detected with a verify run.

```
/usr/lib/debmarshal/make_release.py --release local0/latest --track local0 verify
```

The output from this command may be used to determine when to bump a label (eg. "testable") to the latest release with all dependencies met and conflicts declared.

Sample output:
```
INFO     Importing dependency data from http://localhost/debian
INFO     Checking dependency for architecture i386
INFO     Validating local-package_1_i386 ...
WARNING  Cannot fulfill dependency locales (>= 2.3.11)
ERROR    local-package_1_i386 is uninstallable
```


This functionality is very similar to the recently uploaded edos-distcheck, which may be used as a replacement in the future.  See http://www.edos-project.org/xwiki/bin/view/Main/WebHome .


## Staging and export ##

These are carried out using the same commands, but in the local rather than debian (or ubuntu) repository.  The same labels as in the upstream mirror are usually updated at the same time, as they are tested together.  See [DebmarshalRepositoryMirrorSetup#Staging](DebmarshalRepositoryMirrorSetup#Staging.md) .