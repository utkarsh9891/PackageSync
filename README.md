# PackageSync
Store off-line backup of your packages & restore them on the same or any other machine.

This package currently supports the following functionalities:

1. ###Backup/Restore via a Zip file###
  * #####Backup Packages To Zip (Recommended)#####
  
    This backs up your package list & the custom settings you have made for each of the packages into a zipped file.
    The zipped file is stored with the name _`SublimePackagesBackup.zip`_ on the Desktop.
  * #####Restore Packages From Zip (Recommended)#####
  
    This restores packages list & their user settings from the zipped file _`SublimePackagesBackup.zip`_ on the Desktop.

2. ###Backup/Restore via folder###
  * #####Backup Packages To Folder#####
  
    Works the same way as the zip file, with the only difference that the contents are placed in a folder _`SublimePackagesBackup`_ on the Desktop instead of a zip file.
  * #####Restore Packages From Folder#####
  
    Works the same way as a zip file, with the only difference that the contents are fetched from a folder _`SublimePackagesBackup`_ on the Desktop instead of a zip file.

3. ###Backup/Restore only Package List###
  * #####Backup Installed Packages List Only#####
  
    Backs up only the installed packages list to a file _`SublimePackagesList.txt`_ on the Desktop. User settings are ignored in this option.
  * #####Restore Installed Packages List Only#####
  
    Restores only the installed packages list from a file _`SublimePackagesList.txt`_ on the Desktop. User settings are ignored in this option.

> **_Do note that in order to restore your plugins, you require a working internet connection. PackageSync only syncs your packages list as well as your user settings. But the packages are actually downloaded upon re-launch for installation._**

> This package is currently in development phase & still requires additional features. Any feedback/suggestion is welcome.

_-- Utkarsh_
