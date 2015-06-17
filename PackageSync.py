import sublime
import sublime_plugin
import os
import shutil
import zipfile
import json
import sys


def _initPaths():
    #: Path to folder where backups are stored
    global _backupLocation
    _backupLocation = os.path.join(os.path.expanduser('~'), 'Desktop')

    #: Path of file to be used when backing up to or restoring from the sublime-settings file for Package Control
    global _packageControlSettingsBackup
    _packageControlSettingsBackup = os.path.join(
        _backupLocation, 'SublimePackagesList.txt')

    #: Path of the installed '/packages/user/' folder to backup or restore
    global _userSettingsFolder
    _userSettingsFolder = os.path.join(sublime.packages_path(), 'User')

    #: Path to be used when backing up to or restoring from the '/packages/user' folder as a folder
    global _userSettingsBackupFolder
    _userSettingsBackupFolder = os.path.join(
        _backupLocation, 'SublimePackagesBackup')

    #: Path to be used when backing up to or restoring from the '/packages/user' folder as a zip file
    global _userSettingsBackupZip
    _userSettingsBackupZip = os.path.join(
        _backupLocation, 'SublimePackagesBackup.zip')


def _removeExistingBackup(backupPath):
    if os.path.isdir(backupPath):
        shutil.rmtree(backupPath, True)
    elif os.path.isfile(backupPath):
        os.remove(backupPath)

    lastRunFile = os.path.join(
        sublime.packages_path(), "User", "Package Control.last-run")
    if os.path.isfile(lastRunFile):
        os.remove(lastRunFile)


def _installNewPackages():
    try:
        # Remove the last-run file in order to trigger the package installation
        lastRunFile = os.path.join(
            sublime.packages_path(), "User", "Package Control.last-run")
        if os.path.isfile(lastRunFile):
            os.remove(lastRunFile)

        # Import packageControlCleaner
        cleanupModule = sys.modules[
            "Package Control.package_control.package_cleanup"]
        packageControlCleaner = cleanupModule.PackageCleanup()
        packageControlCleaner.start()
    except Exception as e:
        print(
            "PackageSync: Error while installing packages via Package Control.")
        raise e


class BackupInstalledPackagesListCommand(sublime_plugin.WindowCommand):

    def __init__(self, pluginClass):
        _initPaths()

    def run(self):
        """ Backup the sublime-settings file for Package Control.
        This file contains the list of installed packages.
        The backup is stored on the backup location with the name specified in the
        config file. """

        try:
            _packageControlSettings = sublime.load_settings(
                'Package Control.sublime-settings')
            _installed_packages = _packageControlSettings.get(
                'installed_packages') or []

            with open(_packageControlSettingsBackup, 'w') as _backupFile:
                json.dump(
                    {'installed_packages': _installed_packages}, _backupFile)

            print("PackageSync: Installed packages List backed up to %s" %
                  _packageControlSettingsBackup)
        except Exception as e:
            print(
                "PackageSync: Error while backing up installed packages list")
            raise e


class RestoreInstalledPackagesListCommand(sublime_plugin.WindowCommand):

    def __init__(self, pluginClass):
        _initPaths()

    def run(self):
        """ Restore the sublime-settings file for Package Control.
        This file contains the list of installed packages.
        The backup file should be stored on the backup location with the name
        specified in the config file. """

        if os.path.isfile(_packageControlSettingsBackup):
            try:
                with open(_packageControlSettingsBackup, 'r') as _backupFile:
                    _installed_packages = json.load(
                        _backupFile)['installed_packages']

                    _packageControlSettings = sublime.load_settings(
                        'Package Control.sublime-settings')
                    _packageControlSettings.set(
                        'installed_packages', _installed_packages)
                    sublime.save_settings('Package Control.sublime-settings')

                # sublime.message_dialog(
                    # 'Packages list has been updated. Please restart Sublime Text to download the missing packages.')
                _installNewPackages()

            except Exception as e:
                print(
                    "PackageSync: Error while restoring packages from package list")
                raise e
        else:
            sublime.error_message(
                'Could not find packages list backup file at location %s' % _packageControlSettingsBackup)


class BackupPackagesToFolderCommand(sublime_plugin.WindowCommand):

    def __init__(self, pluginClass):
        _initPaths()

    def run(self):
        """ Backup the "/Packages/User" folder to the backup location.
        This backs up the sublime-settings file created by user settings.
        Package Control settings file is also inherently backed up. """

        _removeExistingBackup(_userSettingsBackupFolder)
        try:
            shutil.copytree(_userSettingsFolder, _userSettingsBackupFolder)
        except Exception as e:
            print("PackageSync: Error while backing up packages to folder")
            raise e


class RestorePackagesFromFolderCommand(sublime_plugin.WindowCommand):

    def __init__(self, pluginClass):
        _initPaths()

    def run(self):
        """ Restore the "/Packages/User" folder from the backup location.
        This restores the sublime-settings file created by user settings.
        Package Control settings file is also inherently restored. """

        if os.path.isdir(_userSettingsBackupFolder):
            try:
                shutil.rmtree(_userSettingsFolder)
                shutil.copytree(_userSettingsBackupFolder, _userSettingsFolder)
                # sublime.message_dialog(
                # 'Packages list & settings have been updated. Please restart Sublime Text to download the missing packages.')
                _installNewPackages()
            except Exception as e:
                print(
                    "PackageSync: Error while restoring packages from folder")
                raise e
        else:
            sublime.error_message(
                'Could not find packages backup folder at location %s' % _userSettingsBackupFolder)


class BackupPackagesToZipCommand(sublime_plugin.WindowCommand):

    def __init__(self, pluginClass):
        _initPaths()

    def run(self):
        """ Backup the "/Packages/User" folder to the backup location.
        This backs up the sublime-settings file created by user settings.
        Package Control settings file is also inherently backed up. """

        _removeExistingBackup(_userSettingsBackupZip)
        try:
            shutil.make_archive(
                _userSettingsBackupFolder, 'zip', _userSettingsFolder)
        except Exception as e:
            print("PackageSync: Error while backing up packages to zip file")
            raise e


class RestorePackagesFromZipCommand(sublime_plugin.WindowCommand):

    def __init__(self, pluginClass):
        _initPaths()

    def run(self):
        """ Restore the "/Packages/User" folder from the backup location.
        This restores the sublime-settings file created by user settings.
        Package Control settings file is also inherently restored. """

        if os.path.isfile(_userSettingsBackupZip):
            try:
                shutil.rmtree(_userSettingsFolder)
                with zipfile.ZipFile(_userSettingsBackupZip, 'r') as z:
                    z.extractall(_userSettingsFolder)
                # sublime.message_dialog(
                    # 'Packages list & settings have been updated. Please restart Sublime Text to download the missing packages.')
                _installNewPackages()
            except Exception as e:
                print(
                    "PackageSync: Error while restoring packages from zip file")
                raise e
        else:
            sublime.error_message(
                'Could not find packages backup zip at location %s' % _userSettingsBackupZip)
