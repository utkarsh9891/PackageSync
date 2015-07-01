# PackageSync

Store off-line backup of your packages & restore them on the same or any other machine.

> Online syncing of packages coming in soon. :thumbsup:

## Table of Contents
  + [Features](#features)
  + [Usage](#usage)
  + [Settings](#settings)
  + [Installation](#installation)
  + [Note to Users](#note-to-users)
  + [License](#license)

## Features

This package currently supports the following functionalities:

#### Backup/Restore via a Zip file (Recommended)
  + __Backup__ - This backs up your package list & the custom settings you have made for each of the packages into a zipped file.
  + __Restore__ - This restores packages list & their user settings from the zipped file backup created using PackageSync.

#### Backup/Restore via folder
  + __Backup__ - Works the same way as the zip file, with the only difference that the contents are placed in a folder instead of a zip file.
  + __Restore__ - Works the same way as a zip file, with the only difference that the contents are fetched from a folder instead of a zip file.

#### Backup/Restore only Package List
  + __Backup__ - Backs up only the installed packages list to a file. All user settings are ignored in this option.
  + __Restore__ - Restores only the installed packages list from a file. User settings are ignored in this option.

> *The user-setting file for PackageSync (PackageSync.sublime-settings) is never synced.*

## Usage

The commands are available under the menu `Tools -> PackageSync`.

Alternatively, from inside Sublime Text, open Package Control's Command Pallet: <kbd>CTRL</kbd> <kbd>SHIFT</kbd> <kbd>P</kbd> (Windows, Linux) or <kbd>CMD</kbd> <kbd>SHIFT</kbd> <kbd>P</kbd> (Mac) & search for `PackageSync:` to get the list of available commands.

## Settings

PackageSync provides the following user configurable settings:

#### prompt_for_location *[boolean, true by default]*
Decides if the user is asked for providing location to back up to or restore from.  
If set as true, user is prompted every time for a path upon back up or restore operation.  
If set as false, the location specified in settings is used. If no location has been specified in settings, by default user's desktop is used for backup.

#### zip_backup_path *[string]*
The zip file path to use for backing up or restoring package list & user settings.  
> *`"prompt_for_location" = false`* & `"zip_backup_path" = ""`  
> This combination backs up & restores using the zip file `SublimePackagesBackup.zip` on the current user's Desktop. It also overrides any existing backup at this location without confirmation.

#### folder_backup_path *[string]*
The folder path to use for backing up or restoring package list & user settings.  
> *`"prompt_for_location" = false`* & `"folder_backup_path" = ""`  
> This combination backs up & restores using the folder `SublimePackagesBackup` on the current user's Desktop. It also overrides any existing backup at this location without confirmation.

#### list_backup_path *[string]*
The file path to use for backing up or restoring only the package list.  
> *`"prompt_for_location" = false`* & `"list_backup_path" = ""`  
> This combination backs up & restores using the file `SublimePackagesList.txt` on the current user's Desktop. It also overrides any existing backup at this location without confirmation.

#### ignore_files *[array]*
The list of files to ignore when backing up.  
It supports wildcarded file names as well. Supported wildcard entries are '*', '?', '[seq]' & '[!seq]'. For further details, please see the [fnmatch documentation](https://docs.python.org/2/library/fnmatch.html).

#### include_files *[array]*
The list of files to include when backing up.  
Do note that __*ignore_files holds higher priority as compared to include_files*__. So a file matching both the settings would essentially be ignored, as governed by ignore_files. Also, the user settings for PackageSync (PackageSync.sublime-settings) would __never__ be synced.  
It supports wildcarded file names as well. Supported wildcard entries are '*', '?', '[seq]' & '[!seq]'. For further details, please see the [fnmatch documentation](https://docs.python.org/2/library/fnmatch.html).

#### ignore_dirs *[array]*
Directories to ignore when backing up.  
By default, all directories created by other packages are included. Only the directories specified in this list are ignored while syncing.  
> Do note that an "include_dirs" option has not been provided on purpose.  
> This has been done in order to avoid confusion for the user when syncing across OSX, WIN & LINUX mahcines as path would be different across all machines of the same user.

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


## Note to Users

Please use the form [PackageSync Feedback](http://goo.gl/forms/hM2eaHb0Ne) for providing any Feedback or Suggestions or for reporting Issues that you face while using or installing PackageSync.

> Do note that PackageSync only syncs your __*packages list*__ and your __*user settings*__ offline. But the actual __*installation of missing/new packages requires a working internet connection*__.

> Additionally, this package is currently in development phase & still requires additional features. The online syncing support is soon to be added.

## License

All files in this package is licensed under the MIT license.

Copyright (c) 2015 Utkarsh (<utkarsh9891@gmail.com>)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
