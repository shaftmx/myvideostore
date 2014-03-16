myvideostore
============

Small cli script with this features :
  * Sync only new video in your server. Allow include et exclude rules.
  * Browse your video directory, tag viewed video and launch vlc


Installation
============

**Requirements :**

For myvideostore-launch.py

    apt-get install vlc

**Setup :**

Just clone the repo :

    git clone https://github.com/shaftmx/myvideostore

And launch setup.py and it's done.

    cd myvideostore && python setyp.py install

For update version you can do a git pull and apply the setup commands

Usage
======


myvideostore-sync-new-files.py
------------------------------

**How it's work :** This script create target dir and put db.json file inside the target dir. When you launch a sync, each file copied are added in the db.json. File already in db.json will not be copied.
You also can add exclude and include filter.

  * Browse your video directory, tag viewed video and launch vlc


**Help :**

    usage: myvideostore-sync-new-files.py [-h] [-d] [-l]
                                        [-a exclude [exclude ...]]
                                        [-x exclude_id [exclude_id ...]] [-L]
                                        [-A include [include ...]]
                                        [-X include_id [include_id ...]] -s
                                        SOURCE -t TARGET
    
    optional arguments:
    -h, --help            show this help message and exit
    -d, --dry-run         Launch script in dry run mode
    -l, --list-exclude    List all excludes with ID. (Don't copy any file)
    -a exclude [exclude ...], --add-exclude exclude [exclude ...]
                          Add exclude in exclude list (Don't copy any file)
    -x exclude_id [exclude_id ...], --del-exclude exclude_id [exclude_id ...]
                          Delete all exclude specified (Don't copy any file)
    -L, --list-include    List all includes with ID. (Don't copy any file)
    -A include [include ...], --add-include include [include ...]
                          Add include in include list. Is take before an exclude
                          (Don't copy any file)
    -X include_id [include_id ...], --del-include include_id [include_id ...]
                          Delete all include specified (Don't copy any file)
    -s SOURCE, --source SOURCE
                          Source directory to get videos
    -t TARGET, --target TARGET
                          Target directory where you want copy your videos
    --pre pre_cmd         Launch a command before sync directory
    --post post_cmd       Launch a command after sync directory
    --db-list             List all file already copied in db
    --db-purge regex      Specify a regex and purge matching entry in db


**Example :**

Launch sync dir in dry run mode (do nothings) :

    myvideostore-sync-new-files.py --source Videos --target myVideos --dry-run

Sync a directory :

    myvideostore-sync-new-files.py --source Videos --target myVideos

Launch pre and post command :

    myvideostore-sync-new-files.py --source Videos --target myVideos --pre "mount Videos" --post "sync ; umount Videos"

List all file referenced in db (file in db are file copied) :

    myvideostore-sync-new-files.py --source Videos --target myVideos --db-list

Remove file entry in db matching ^foo :

    myvideostore-sync-new-files.py --source Videos --target myVideos --db-purge '^foo'

**Use case** : I have an existing dir with subdir foo and bar. I only want things in bar. The easy way is exclude all and implicy include bar.

Add global exclude on all :

    myvideostore-sync-new-files.py --source Videos --target myVideos --add-exclude '.*'

Add Specific include for bar directory :

    myvideostore-sync-new-files.py --source Videos --target myVideos --add-include '^bar/'

Finally launch the sync :

    myvideostore-sync-new-files.py --source Videos --target myVideos


myvideostore-launch.py
----------------------
**How it's work :** This script put db.json file inside the directory.

**Features :**
  * Browse directory
  * Remove video file and empty dirs
  * Mark file as viewed
  * Launch vlc



**Example :**

Launch sync dir in dry run mode (do nothings) :

    myvideostore-launch.py --directory Videos

**Screenshots**

Menu :

![ScreenShot](https://raw.github.com/shaftmx/myvideostore/master/docs/img/menu.png)

Help :

![ScreenShot](https://raw.github.com/shaftmx/myvideostore/master/docs/img/help.png)
