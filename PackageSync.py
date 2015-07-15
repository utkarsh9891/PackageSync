import sublime
import sublime_plugin
import os
import tempfile
import fnmatch
import time
import shutil
import zipfile
import json
import sys

try:
    from .package_sync_helpers import tools
    from .package_sync_helpers import offline
except ValueError:
    from package_sync_helpers import tools
    from package_sync_helpers import offline


class BackupInstalledPackagesListCommand(sublime_plugin.WindowCommand):

    def run(self):
        """ Backup the sublime-settings file for Package Control.
        This file contains the list of installed packages.
        The backup is stored on the backup location with the name specified in the
        config file. """

        tools.load_settings()

        if tools.sync_settings["prompt_for_location"] is False:
            list_backup_path = tools.sync_settings["list_backup_path"]

            try:
                if list_backup_path is "":
                    backup_path = tools.default_list_backup_path
                elif os.path.exists(list_backup_path):
                    if sublime.ok_cancel_dialog("Backup already exists @ %s \nOverride it?" % list_backup_path) is True:
                        os.remove(list_backup_path)
                        backup_path = list_backup_path
                    else:
                        backup_path = None
                elif os.path.isabs(os.path.dirname(list_backup_path)):
                    backup_path = list_backup_path
                else:
                    sublime.error_message(
                        "Invalid path provided in user-settings. Please correct & then retry.")
                    backup_path = None
            except Exception as e:
                print("PackageSync: Error while fetching backup path.")
                print("PackageSync: Error message: %s" % str(e))

            self.backup_pkg_list(backup_path)
        else:
            offline.prompt_parameters = {
                "mode": "backup",
                "type": "file",
                "window_context": self.window,
                "initial_text": tools.default_list_backup_path,
                "operation_to_perform": self.backup_pkg_list,
                "on_change": None,
                "on_cancel": offline.packagesync_cancelled
            }
            offline.prompt_for_location()

    def backup_pkg_list(self, backup_path):
        if backup_path is not None:
            try:
                package_control_settings = sublime.load_settings(
                    "Package Control.sublime-settings")
                installed_packages = package_control_settings.get(
                    "installed_packages") or []

                if os.path.isfile(backup_path):
                    os.remove(backup_path)
                elif not os.path.exists(os.path.dirname(backup_path)):
                    os.makedirs(os.path.dirname(backup_path))

                with open(backup_path, "w") as _backupFile:
                    json.dump(
                        {"installed_packages": installed_packages}, _backupFile)

                print("PackageSync: Backup of installed packages list created at %s" %
                      backup_path)
            except Exception as e:
                print(
                    "PackageSync: Error while backing up installed packages list")
                print("PackageSync: Error message: %s" % str(e))
        else:
            offline.packagesync_cancelled()


class RestoreInstalledPackagesListCommand(sublime_plugin.WindowCommand):

    def run(self):
        """ Restore the sublime-settings file for Package Control.
        This file contains the list of installed packages.
        The backup file should be stored on the backup location with the name
        specified in the config file. """

        tools.load_settings()

        if tools.sync_settings["prompt_for_location"] is False:
            list_backup_path = tools.sync_settings["list_backup_path"]

            try:
                if list_backup_path is "":
                    backup_path = tools.default_list_backup_path
                elif os.path.isfile(list_backup_path):
                    backup_path = list_backup_path
                else:
                    sublime.error_message(
                        "Invalid path provided in user-settings. Please correct & then retry.")
                    backup_path = None
            except Exception as e:
                print("PackageSync: Error while fetching backup path.")
                print("PackageSync: Error message: %s" % str(e))

            self.restore_pkg_list(backup_path)
        else:
            offline.prompt_parameters = {
                "mode": "restore",
                "type": "file",
                "window_context": self.window,
                "initial_text": tools.default_list_backup_path,
                "operation_to_perform": self.restore_pkg_list,
                "on_change": None,
                "on_cancel": offline.packagesync_cancelled
            }
            offline.prompt_for_location()

    def restore_pkg_list(self, backup_path):
        if backup_path is not None:
            try:
                print("PackageSync: Restoring package list from %s" %
                      backup_path)
                with open(backup_path, "r") as f:
                    _installed_packages = json.load(f)["installed_packages"]

                    _package_control_settings = sublime.load_settings(
                        "Package Control.sublime-settings")
                    _package_control_settings.set(
                        "installed_packages", _installed_packages)
                    sublime.save_settings("Package Control.sublime-settings")

                tools.install_new_packages()

            except Exception as e:
                print(
                    "PackageSync: Error while restoring packages from package list")
                print("PackageSync: Error message: %s" % str(e))
        else:
            offline.packagesync_cancelled()


class BackupPackagesToFolderCommand(sublime_plugin.WindowCommand):

    def run(self):
        """ Backup the "/Packages/User" folder to the backup location.
        This backs up the sublime-settings file created by user settings.
        Package Control settings file is also inherently backed up. """

        tools.load_settings()

        if tools.sync_settings["prompt_for_location"] is False:
            folder_backup_path = tools.sync_settings["folder_backup_path"]

            try:
                if folder_backup_path is "":
                    backup_path = tools.default_folder_backup_path
                elif os.path.exists(folder_backup_path) and len(os.listdir(folder_backup_path)) > 0:
                    if sublime.ok_cancel_dialog("Backup already exists @ %s \nOverride it?" % folder_backup_path) is True:
                        backup_path = folder_backup_path
                    else:
                        backup_path = None
                elif os.path.isabs(os.path.dirname(folder_backup_path)):
                    backup_path = folder_backup_path
                else:
                    sublime.error_message(
                        "Invalid path provided in user-settings. Please correct & then retry.")
                    backup_path = None
            except Exception as e:
                print("PackageSync: Error while fetching backup path.")
                print("PackageSync: Error message: %s" % str(e))

            self.backup_folder(backup_path)
        else:
            offline.prompt_parameters = {
                "mode": "backup",
                "type": "folder",
                "window_context": self.window,
                "initial_text": tools.default_folder_backup_path,
                "operation_to_perform": self.backup_folder,
                "on_change": None,
                "on_cancel": offline.packagesync_cancelled
            }
            offline.prompt_for_location()

    def backup_folder(self, backup_path):
        if backup_path is not None:
            try:
                offline.create_temp_backup()

                if os.path.isdir(backup_path):
                    shutil.rmtree(backup_path, True)
                shutil.copytree(tools.temp_backup_folder, backup_path)

                print("PackageSync: Backup of packages & settings created at %s" %
                      backup_path)
            except Exception as e:
                print("PackageSync: Error while backing up packages to folder")
                print("PackageSync: Error message: %s" % str(e))
        else:
            offline.packagesync_cancelled()


class RestorePackagesFromFolderCommand(sublime_plugin.WindowCommand):

    def run(self):
        """ Restore the "/Packages/User" folder from the backup location.
        This restores the sublime-settings file created by user settings.
        Package Control settings file is also inherently restored. """

        tools.load_settings()

        if tools.sync_settings["prompt_for_location"] is False:
            folder_backup_path = tools.sync_settings["folder_backup_path"]

            try:
                if folder_backup_path is "":
                    backup_path = tools.default_folder_backup_path
                elif os.path.isdir(folder_backup_path):
                    backup_path = folder_backup_path
                else:
                    sublime.error_message(
                        "Invalid path provided in user-settings. Please correct & then retry.")
                    backup_path = None
            except Exception as e:
                print("PackageSync: Error while fetching backup path.")
                print("PackageSync: Error message: %s" % str(e))

            self.restore_folder(backup_path)
        else:
            offline.prompt_parameters = {
                "mode": "restore",
                "type": "folder",
                "window_context": self.window,
                "initial_text": tools.default_folder_backup_path,
                "operation_to_perform": self.restore_folder,
                "on_change": None,
                "on_cancel": offline.packagesync_cancelled
            }
            offline.prompt_for_location()

    def restore_folder(self, backup_path):
        if backup_path is not None:
            try:
                print(
                    "PackageSync: Restoring package list & user settings from %s" % backup_path)
                # Backup PackageSync user settings before restore operation
                packagesync_settings_backup = os.path.join(
                    tempfile.gettempdir(), str(time.time()))
                packagesync_settings_original = os.path.join(
                    tools.user_settings_folder, "PackageSync.sublime-settings")
                # Verify that user setting are present before backing up
                if os.path.exists(packagesync_settings_original):
                    shutil.copy2(
                        packagesync_settings_original, packagesync_settings_backup)
                    print("PackageSync: PackageSync.sublime-settings backed up to %s" %
                          packagesync_settings_backup)

                if os.path.exists(tools.temp_restore_folder):
                    shutil.rmtree(tools.temp_restore_folder, True)
                # Copy to temp restore folder & restore as per the preserve
                # setting
                shutil.copytree(backup_path, tools.temp_restore_folder)
                offline.restore_from_temp()

                # Restore PackageSync user settings if they were backed up
                if os.path.exists(packagesync_settings_backup) and not os.path.exists(packagesync_settings_original):
                    shutil.copy2(
                        packagesync_settings_backup, packagesync_settings_original)
                    print("PackageSync: PackageSync.sublime-settings restored from %s" %
                          packagesync_settings_backup)

                tools.install_new_packages()

            except Exception as e:
                print(
                    "PackageSync: Error while restoring packages from folder")
                print("PackageSync: Error message: %s" % str(e))
        else:
            offline.packagesync_cancelled()


class BackupPackagesToZipCommand(sublime_plugin.WindowCommand):

    def run(self):
        """ Backup the "/Packages/User" folder to the backup location.
        This backs up the sublime-settings file created by user settings.
        Package Control settings file is also inherently backed up. """

        tools.load_settings()

        if tools.sync_settings["prompt_for_location"] is False:
            zip_backup_path = tools.sync_settings["zip_backup_path"]

            try:
                if zip_backup_path is "":
                    backup_path = tools.default_zip_backup_path
                elif os.path.exists(zip_backup_path):
                    if sublime.ok_cancel_dialog("Backup already exists @ %s \nOverride it?" % zip_backup_path) is True:
                        os.remove(zip_backup_path)
                        backup_path = zip_backup_path
                    else:
                        backup_path = None
                elif os.path.isabs(os.path.dirname(zip_backup_path)):
                    backup_path = zip_backup_path
                else:
                    sublime.error_message(
                        "Invalid path provided in user-settings. Please correct & then retry.")
                    backup_path = None
            except Exception as e:
                print("PackageSync: Error while fetching backup path.")
                print("PackageSync: Error message: %s" % str(e))

            self.backup_zip(backup_path)
        else:
            offline.prompt_parameters = {
                "mode": "backup",
                "type": "file",
                "window_context": self.window,
                "initial_text": tools.default_zip_backup_path,
                "operation_to_perform": self.backup_zip,
                "on_change": None,
                "on_cancel": offline.packagesync_cancelled
            }
            offline.prompt_for_location()

    def backup_zip(self, backup_path):
        if backup_path is not None:
            try:
                offline.create_temp_backup()

                temp_zip_file_path = os.path.join(
                    tempfile.gettempdir(), str(time.time()))
                shutil.make_archive(
                    temp_zip_file_path, "zip", tools.temp_backup_folder)

                if os.path.isfile(backup_path):
                    os.remove(backup_path)
                elif not os.path.exists(os.path.dirname(backup_path)):
                    os.makedirs(os.path.dirname(backup_path))
                shutil.move(temp_zip_file_path + ".zip", backup_path)

                print("PackageSync: Zip backup of packages & settings created at %s" %
                      backup_path)
            except Exception as e:
                print(
                    "PackageSync: Error while backing up packages to zip file")
                print("PackageSync: Error message: %s" % str(e))
        else:
            offline.packagesync_cancelled()


class RestorePackagesFromZipCommand(sublime_plugin.WindowCommand):

    def run(self):
        """ Restore the "/Packages/User" folder from the backup location.
        This restores the sublime-settings file created by user settings.
        Package Control settings file is also inherently restored. """

        tools.load_settings()

        if tools.sync_settings["prompt_for_location"] is False:
            zip_backup_path = tools.sync_settings["zip_backup_path"]

            try:
                if zip_backup_path is "":
                    backup_path = tools.default_zip_backup_path
                elif os.path.isfile(zip_backup_path):
                    backup_path = zip_backup_path
                else:
                    sublime.error_message(
                        "Invalid path provided in user-settings. Please correct & then retry.")
                    backup_path = None
            except Exception as e:
                print("PackageSync: Error while fetching backup path.")
                print("PackageSync: Error message: %s" % str(e))

            self.restore_zip(backup_path)
        else:
            offline.prompt_parameters = {
                "mode": "restore",
                "type": "file",
                "window_context": self.window,
                "initial_text": tools.default_zip_backup_path,
                "operation_to_perform": self.restore_zip,
                "on_change": None,
                "on_cancel": offline.packagesync_cancelled
            }
            offline.prompt_for_location()

    def restore_zip(self, backup_path):
        if backup_path is not None:
            try:
                print(
                    "PackageSync: Restoring package list & user settings from %s" % backup_path)
                # Backup PackageSync user settings before restore operation
                packagesync_settings_backup = os.path.join(
                    tempfile.gettempdir(), str(time.time()))
                packagesync_settings_original = os.path.join(
                    tools.user_settings_folder, "PackageSync.sublime-settings")
                # Verify that user setting are present before backing up
                if os.path.exists(packagesync_settings_original):
                    shutil.copy2(
                        packagesync_settings_original, packagesync_settings_backup)
                    print("PackageSync: PackageSync.sublime-settings backed up to %s" %
                          packagesync_settings_backup)

                if os.path.exists(tools.temp_restore_folder):
                    shutil.rmtree(tools.temp_restore_folder, True)
                # Extract to temp restore folder & then perform restore operation
                # as per the preserve setting
                with zipfile.ZipFile(backup_path, "r") as z:
                    z.extractall(tools.temp_restore_folder)
                offline.restore_from_temp()

                # Restore PackageSync user settings if they were backed up
                if os.path.exists(packagesync_settings_backup) and not os.path.exists(packagesync_settings_original):
                    shutil.copy2(
                        packagesync_settings_backup, packagesync_settings_original)
                    print("PackageSync: PackageSync.sublime-settings restored from %s" %
                          packagesync_settings_backup)

                tools.install_new_packages()

            except Exception as e:
                print(
                    "PackageSync: Error while restoring packages from zip file")
                print("PackageSync: Error message: %s" % str(e))
        else:
            offline.packagesync_cancelled()
