# PackageSync

__*Synchronize*__ your Sublime Text packages and your user-settings across different devices effortlessly. For this, PackageSync requires an online syncing application like Google Drive, Dropbox or SkyDrive installed on your devices.  
Alternatively, PackageSync also allows you to __*take portable backups*__ of your packages & __*restore*__ them on the same or any other machine without any need for third party applications mentioned above.


## Table of Contents
  + [Features](#features)
  + [Usage](#usage)
  + [Settings](#settings)
  + [Installation](#installation)
  + [Feedback](#feedback)
  + [License](#license)


## Features

#### Backup/Restore
This allows you to backup the installed packages list & the user settings for each package. This backup can then be restored to any other device using PackageSync.  

+ __Backup/Restore via a Zip file (Recommended)__ - Backs up the installed packages list & their settings into a zip file. The zip file is the best portable format for offline syncing.
+ __Backup/Restore via folder__ - Works the same way as the zip file, with the only difference that the contents are placed in a folder instead of an archived zip file.
+ __Backup/Restore only Package List__ - Backs up only the installed packages list to a file. User settings for packages are ignored in this option.

> *The user-setting file for PackageSync (PackageSync.sublime-settings) is never synced.*  

Do note that this Backup/Restore operation only syncs your __*packages list*__ and your __*user settings*__ offline. But the actual __*installation of missing/new packages requires a working Internet connection*__.

Also, while restoring from PackageSync backup, __please ensure that all `*.sublime-settings` files are closed__. Files in open state would interrupt the restore operation, resulting in unforeseen errors.

#### Sync Online
This allows you to sync the packages & user settings in real time across different devices. For this, the installed packages list & user settings are be saved to & synced via a folder monitored by Dropbox, Google Drive or SkyDrive etc.  

+ __First Machine__  
Turn on PackageSync's online syncing module by setting the sync folder via "PackageSync: Sync Online - Define Online Sync Folder" from the command palette or Tools menu. In the ensuing input panel, give the complete path to any directory on your computer inside your Dropbox or Google Drive sync folder.  

+ __Second Machine (or after a fresh installation of Sublime Text)__  
On your second machine please wait until all the backup files are available and then simply set the sync folder and PackageSync will automatically pull all available files from that folder. The following message dialog should appear which you just have to confirm.  

![OnlineSyncFolder](https://cloud.githubusercontent.com/assets/9902630/8914964/b20c58ae-34bf-11e5-86d3-b478afb161d3.png)

__Restart__ Sublime Text & Package Control will check for missing packages and install them automatically. From now on everything should work very smoothly.

> *Note*: __For PackageSync to automatically manage installation & removal of packages (without requiring any restart)__ as per sync or restore operation [Package Control](https://sublime.wbond.net) needs to be installed as well. Otherwise, installation or removal would require restart of Sublime Text.

## Usage

The commands are available under the menu `Tools -> PackageSync`.

Alternatively, from inside Sublime Text, open Package Control's Command Pallet: <kbd>CTRL</kbd>+<kbd>SHIFT</kbd>+<kbd>P</kbd> (Windows, Linux) or <kbd>CMD</kbd>+<kbd>SHIFT</kbd>+<kbd>P</kbd> (Mac) & search for `PackageSync:` to get the list of available commands.

## Settings

PackageSync provides the following user configurable settings:

+ __prompt_for_location *[boolean, true by default]*__  
Decides if the user is asked for providing location to back up to or restore from.  
If set as true, user is prompted every time for a path upon back up or restore operation.  
If set as false, the location specified in settings is used. If no location has been specified in settings, by default user's desktop is used for backup.

+ __zip_backup_path *[string]*__  
The zip file path to use for backing up or restoring package list & user settings.  
> `"prompt_for_location" = false` & `"zip_backup_path" = ""`  
> This combination backs up & restores using the zip file `SublimePackagesBackup.zip` on the current user's Desktop. During backup operation, it also overrides any existing backup at this location without confirmation.

+ __folder_backup_path *[string]*__  
The folder path to use for backing up or restoring package list & user settings.  
> `"prompt_for_location" = false` & `"folder_backup_path" = ""`  
> This combination backs up & restores using the folder `SublimePackagesBackup` on the current user's Desktop. During backup operation, it also overrides any existing backup at this location without confirmation.

+ __list_backup_path *[string]*__  
The file path to use for backing up or restoring only the package list.  
> `"prompt_for_location" = false` & `"list_backup_path" = ""`  
> This combination backs up & restores using the file `SublimePackagesList.txt` on the current user's Desktop. During backup operation, it also overrides any existing backup at this location without confirmation.

+ __ignore_files *[array]*__  
The list of files to ignore when backing up.  
It supports wildcarded file names as well. Supported wildcard entries are '*', '?', '[seq]' & '[!seq]'. For further details, please see the [fnmatch documentation](https://docs.python.org/2/library/fnmatch.html).  
> Files ignored by default are \*.DS_Store, \*.last-run, Package Control.ca-list, Package Control.ca-bundle, Package Control.system-ca-bundle & \*.sublime-package.

+ __sync_package_sync_settings *[boolean, false by default]*__  
Toggle to determine whether to synchronize user setting for this package (`PackageSync.sublime-settings`).
> Caution: Use this feature very cautiously. This overrides your PackageSync settings across the synced devices. If you wish to keep different sync folder paths across the devices, DO NOT set this as True

+ __include_files *[array]*__  
The list of files to include when backing up.  
Note: __*ignore_files holds higher priority as compared to include_files*__. So a file matching both the settings would essentially be ignored, as governed by ignore_files.  
It supports wildcarded file names as well. Supported wildcard entries are '*', '?', '[seq]' & '[!seq]'. For further details, please see the [fnmatch documentation](https://docs.python.org/2/library/fnmatch.html).  
> The user settings for PackageSync (PackageSync.sublime-settings) would __never__ be synced, even if added to this list.  
> Files included by default are \*.sublime-\*, \*.tmLanguage, \*.tmTheme, \*.tmPreferences, \*.json, \*.png, \*.txt, \*.py, \*.md.

+ __ignore_dirs *[array]*__  
Directories to ignore when backing up.  
By default, all directories created by other packages are included. Only the directories specified in this list are ignored while syncing.  
> Do note that an "include_dirs" option has not been provided on purpose.  
> This has been done in order to avoid confusion for the user when syncing across OSX, WIN & LINUX mahcines as path would be different across all machines of the same user.

+ __preserve_packages *[boolean, true by default]*__  
Decides if the existing packages are to be preserved while restoring from a backup.  
If set as false, existing packages & their settings are removed during restore operation. Only the packages included in the backup are restored.  
If set as true, PackageSync keeps the existing packages intact. Packages not included in the backup therefore remain unharmed even after restore operation. However, user-settings are overwritten if the backup contains user-settings for the same package.

+ __online_sync_enabled *[boolean, false by default]*__  
Toggle to determine if online syncing is enabled or not.  
Turning this toggle ON/OFF requires Online Sync Folder to be setup first.

+ __online_sync_folder *[string]*__  
Folder to use for syncing the backup with online syncing services.  
This should be the path to a folder inside the Google Drive, Dropbox or SkyDrive sync folder. Any other online syncing application can be used as well.

+ __online_sync_interval *[integer, default 1]*__  
The frequency (in seconds) at which PackageSync should poll to see if there are any changes in the local folder or in the online sync folder.  
PackageSync will keep your settings up to date across machines by checking regularly at this interval. If you face any performance issues you can increase this time via the settings and a restart of Sublime Text.

+ __debug *[boolean, false by default]*__
Whether or not PackageSync should log to the console. Enable this if you're having issues and want to see PackageSync's activity.

## Installation

#### Package Control

The preferred method of installation is via [Sublime Package Control](https://packagecontrol.io).

1. [Install Sublime Package Control](https://packagecontrol.io/installation)
2. From inside Sublime Text, open Package Control's Command Pallet: <kbd>CTRL</kbd> <kbd>SHIFT</kbd> <kbd>P</kbd> (Windows, Linux) or <kbd>CMD</kbd> <kbd>SHIFT</kbd> <kbd>P</kbd> (Mac).
3. Type `install package`, select command `Package Control: Install Package` and hit Return. A list of available packages will be displayed.
4. Type `PackageSync`, select the `PackageSync` package and hit Return. The package will be downloaded to the appropriate directory.

#### Manual Installation

1. Download or clone this repository to a directory `PackageSync` in the Sublime Text Packages directory for your platform:
    + Mac: `git clone https://github.com/utkarsh9891/PackageSync.git ~/Library/Application\ Support/Sublime\ Text\ 3/Packages/PackageSync`
    + Windows: `git clone https://github.com/utkarsh9891/PackageSync.git %APPDATA%\Sublime/ Text/ 3/\PackageSync`
    + Linux: `git clone https://github.com/utkarsh9891/PackageSync.git ~/.Sublime\ Text\ 3/Packages/PackageSync`
2. Restart Sublime Text to complete installation.

The features listed above should now be available.


## Feedback

Please use the form [PackageSync Feedback](http://goo.gl/forms/hM2eaHb0Ne) for providing any Feedback or Suggestions or for reporting Issues that you face while using or installing PackageSync.


## License

All files in this package are licensed under the MIT license. See the [LICENSE](LICENSE.md) file for license rights and limitations.
