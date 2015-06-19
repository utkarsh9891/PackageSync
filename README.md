# PackageSync

Store off-line backup of your packages & restore them on the same or any other machine.

> Online syncing of packages coming in soon. :thumbsup:

## Features

This package currently supports the following functionalities:

#### Backup/Restore via a Zip file (Recommended)
  * __Backup__ - This backs up your package list & the custom settings you have made for each of the packages into a zipped file.
  The zipped file is stored with the name _`SublimePackagesBackup.zip`_ on the Desktop.
  * __Restore__ - This restores packages list & their user settings from the zipped file _`SublimePackagesBackup.zip`_ on the Desktop.

#### Backup/Restore via folder
  * __Backup__ - Works the same way as the zip file, with the only difference that the contents are placed in a folder _`SublimePackagesBackup`_ on the Desktop instead of a zip file.
  * __Restore__ - Works the same way as a zip file, with the only difference that the contents are fetched from a folder _`SublimePackagesBackup`_ on the Desktop instead of a zip file.

#### Backup/Restore only Package List
  * __Backup__ - Backs up only the installed packages list to a file _`SublimePackagesList.txt`_ on the Desktop. User settings are ignored in this option.
  * __Restore__ - Restores only the installed packages list from a file _`SublimePackagesList.txt`_ on the Desktop. User settings are ignored in this option.

## Usage

The commands are available under the menu _`Tools -> PackageSync`_.

Alternatively, from inside Sublime Text, open Package Control's Command Pallet: <kbd>CTRL</kbd> <kbd>SHIFT</kbd> <kbd>P</kbd> (Windows, Linux) or <kbd>CMD</kbd> <kbd>SHIFT</kbd> <kbd>P</kbd> (Mac) & search for `PackageSync:` to get the list of available commands.

## Installation

#### Package Control

The preferred method of installation is via [Sublime Package Control](https://packagecontrol.io).

1. [Install Sublime Package Control](https://packagecontrol.io/installation)
2. From inside Sublime Text, open Package Control's Command Pallet: <kbd>CTRL</kbd> <kbd>SHIFT</kbd> <kbd>P</kbd> (Windows, Linux) or <kbd>CMD</kbd> <kbd>SHIFT</kbd> <kbd>P</kbd> (Mac).
3. Type `install package`, select command `Package Control: Install Package` and hit Return. A list of available packages will be displayed.
4. Type `PackageSync`, select the `PackageSync` package and hit Return. The package will be downloaded to the appropriate directory.

#### Manual Installation

1. Download or clone this repository to a directory `PackageSync` in the Sublime Text Packages directory for your platform:
    * Mac: `git clone https://github.com/utkarsh9891/PackageSync.git ~/Library/Application\ Support/Sublime\ Text\ 3/Packages/PackageSync`
    * Windows: `git clone https://github.com/utkarsh9891/PackageSync.git %APPDATA%\Sublime/ Text/ 3/\PackageSync`
    * Linux: `git clone https://github.com/utkarsh9891/PackageSync.git ~/.Sublime\ Text\ 3/Packages/PackageSync`
2. Restart Sublime Text to complete installation.

The features listed above should now be available.


## Note to Users

Please use the form [PackageSync Feedback](http://goo.gl/forms/hM2eaHb0Ne) for providing any Feedback, Suggestions or Issues that you face while using or installing PackageSync.

> Do note that PackageSync only syncs your __*packages list*__ and your __*user settings*__. But the actual *installation of missing/new packages* requires a working internet connection.

> Additionally, this package is currently in development phase & still requires additional features. The online syncing support is soon to be added.

## License

All files in this package is licensed under the MIT license.

Copyright (c) 2015 Utkarsh <utkarsh9891@gmail.com>

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
