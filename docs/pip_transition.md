## Transition from using pip packages

This documents the proposed transition to no longer using pip packages (fully debianised system)

### Rationale
Currently we use PIP as well as debian packages to install some python modules. There are a few problems with this:
  * We can't automate dependency tracking between pip and deb packages
  * Not all pip packages are pinned, so upstream can push an update and break our customers updates without us knowing
  * pip is a less robust package installer. In particular, it doesn't track what files it installed.
  * We have some evidence that there may be a race condition which is causing python packages to be corrupted on install.
  
  
Steps

### 1.  Build python packages and add them to dr
* Building:
   * py2deb seems to work reasonably well. The only caveat is that it needs `pip-accel` to be manually installed first `pip install pip-accel` as otherwise you get a version of pip which pip-accel is not compatible with. Then do `pip install py2deb`.
* Choice of packages and versions:
  * It is not necessary to install pip once we transition.
  * Some packages also already have raspbian versions. I propose to build new ones where the pip ones we currently install are newer, but not where they are older. There are only two where the raspbian version is newer (pam and futures). If this proves to be a problem, we can build the exact version and pin in the debian control file.
  
  
  * Although some people may have updated and got requests 2.18.4, the last release had 2.6.0 so I still propose to use that.
    The reason is that 2.18.4 installs a bunch of other stuff.




### 2. Transition from pip to deb packages.

This must:

  * Install the new deb packages
  * Ensure the old pip packages don't override them.
  
It turns out by deafult pip packages do override deb packages. Python load modules from `sys.path`

* deb installs to `/usr/lib/python2.7/dist-packages`
* pip installs to `/usr/local/lib/python2.7/dist-packages`

`sys.path` is set up so that pip has priority. Therefore we need to make sure that the deb files
get priority. My suggested fix is to add a new path `/usr/local/lib/python2.7/dist-packages.pip-fallback` later in the sys.path list, and then move
the current pip files there. In the event of a failure of some kind, python will still work.


#### Transition update process
##### 1 `python-docopt` installed as a (new) dependency of kano-updater

##### 2 Install fallback path
 `kano-updater.install` , adds a file
   `/usr/lib/python2.7/dist-packages/kano-pip-compat.pth`
 containing `/usr/local/lib/python2.7/dist-packages.pip-fallback`
This adds that path to sys.path after `/usr/lib/python2.7/dist-packages`.

##### 3 Pre-update scenario Move old pip packages to fallback path 
```
mkdir -p /usr/local/lib/python2.7/dist-packages.pip-fallback
mv /usr/local/lib/python2.7/dist-packages{,.pip-fallback}
```
##### 5 deb packages installed as part of main install step
A new package `kano-os-pip-transition-depends` which depends on the new deb packages will be added.

The code in the updater which downloads/installs pip packages needs to be removed before this update.

### 3. Pay down tech debt:
 * Add correct dependencies to other packages.
 * Stop shipping our built python deb files once newer ones become available in raspbian\
 
 
### 4 Things that need to be checked:

  * No other calls to pip in the system outside the updater
  * No other useful files in `/usr/local/lib/python2.7/dist-packages`
  * newer versions of pam and futures don't cause problems
  * All versions correct on installed system
  
