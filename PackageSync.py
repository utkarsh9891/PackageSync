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
    from .package_sync_helpers import online
    from .package_sync_helpers import offline
except ValueError:
    from package_sync_helpers import tools
    from package_sync_helpers import online
    from package_sync_helpers import offline

sync_queue = online.Queue()

class PsyncLocalBackupListCommand(sublime_plugin.WindowCommand):

    # def is_enabled(self):
    #     return True

    def run(self):
        psync_settings = tools.get_psync_settings()

        if psync_settings["prompt_for_location"] == False:
            list_backup_path = psync_settings["list_backup_path"]

            backup_path = None
            try:
                if list_backup_path == "":
                    backup_path = tools.default_list_backup_path
                elif os.path.exists(list_backup_path):
                    if sublime.ok_cancel_dialog(
                            "Backup already exists @ %s \nReplace it?" % list_backup_path) == True:
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
                "on_cancel": tools.packagesync_cancelled
            }
            offline.prompt_for_location()

    def backup_pkg_list(self, backup_path):
        if backup_path != None:
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
                        {"installed_packages": installed_packages}, _backupFile, indent=4)

                print("PackageSync: Backup of installed packages list created at %s" %
                      backup_path)
            except Exception as e:
                print(
                    "PackageSync: Error while backing up installed packages list")
                print("PackageSync: Error message: %s" % str(e))
        else:
            tools.packagesync_cancelled()


class PsyncLocalRestoreListCommand(sublime_plugin.WindowCommand):

    # def is_enabled(self):
    #     return True

    def run(self):
        psync_settings = tools.get_psync_settings()

        if psync_settings["prompt_for_location"] == False:
            list_backup_path = psync_settings["list_backup_path"]

            backup_path = None
            try:
                if list_backup_path == "":
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
                "on_cancel": tools.packagesync_cancelled
            }
            offline.prompt_for_location()

    def restore_pkg_list(self, backup_path):
        if backup_path != None:
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
            tools.packagesync_cancelled()


class PsyncLocalBackupFolderCommand(sublime_plugin.WindowCommand):

    # def is_enabled(self):
    #     return True

    def run(self):
        psync_settings = tools.get_psync_settings()

        if psync_settings["prompt_for_location"] == False:
            folder_backup_path = psync_settings["folder_backup_path"]

            backup_path = None
            try:
                if folder_backup_path == "":
                    backup_path = tools.default_folder_backup_path
                elif os.path.exists(folder_backup_path) and len(os.listdir(folder_backup_path)) > 0:
                    if sublime.ok_cancel_dialog(
                            "Backup already exists @ %s \nReplace it?" % folder_backup_path) == True:
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
                "on_cancel": tools.packagesync_cancelled
            }
            offline.prompt_for_location()

    def backup_folder(self, backup_path):
        if backup_path != None:
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
            tools.packagesync_cancelled()


class PsyncLocalRestoreFolderCommand(sublime_plugin.WindowCommand):

    # def is_enabled(self):
    #     return True

    def run(self):
        psync_settings = tools.get_psync_settings()

        if psync_settings["prompt_for_location"] == False:
            folder_backup_path = psync_settings["folder_backup_path"]

            backup_path = None
            try:
                if folder_backup_path == "":
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
                "on_cancel": tools.packagesync_cancelled
            }
            offline.prompt_for_location()

    def restore_folder(self, backup_path):
        if backup_path != None:
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
            tools.packagesync_cancelled()


class PsyncLocalBackupZipCommand(sublime_plugin.WindowCommand):

    # def is_enabled(self):
    #     return True

    def run(self):
        psync_settings = tools.get_psync_settings()

        if psync_settings["prompt_for_location"] == False:
            zip_backup_path = psync_settings["zip_backup_path"]

            backup_path = None
            try:
                if zip_backup_path == "":
                    backup_path = tools.default_zip_backup_path
                elif os.path.exists(zip_backup_path):
                    if sublime.ok_cancel_dialog(
                            "Backup already exists @ %s \nReplace it?" % zip_backup_path) == True:
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
                "on_cancel": tools.packagesync_cancelled
            }
            offline.prompt_for_location()

    def backup_zip(self, backup_path):
        if backup_path != None:
            try:
                offline.create_temp_backup()

                temp_zip_file_path = os.path.join(
                    tempfile.gettempdir(), str(time.time())) + ".zip"

                # create temp backup zip from the temp backup
                z = zipfile.ZipFile(temp_zip_file_path, 'w')
                basePath = tools.temp_backup_folder.rstrip("\\/") + ""
                basePath = basePath.rstrip("\\/")

                for root, dirs, files in os.walk(tools.temp_backup_folder):
                    for item in (files + dirs):
                        itemPath = os.path.join(root, item)
                        inZipPath = itemPath.replace(
                            basePath, "", 1).lstrip("\\/")
                        z.write(itemPath, inZipPath)

                # close the temp backup file
                z.close()

                if os.path.isfile(backup_path):
                    os.remove(backup_path)
                elif not os.path.exists(os.path.dirname(backup_path)):
                    os.makedirs(os.path.dirname(backup_path))
                shutil.move(temp_zip_file_path, backup_path)

                print("PackageSync: Zip backup of packages & settings created at %s" %
                      backup_path)
            except Exception as e:
                print(
                    "PackageSync: Error while backing up packages to zip file")
                print("PackageSync: Error message: %s" % str(e))
        else:
            tools.packagesync_cancelled()


class PsyncLocalRestoreZipCommand(sublime_plugin.WindowCommand):

    # def is_enabled(self):
    #     return True

    def run(self):
        psync_settings = tools.get_psync_settings()

        if psync_settings["prompt_for_location"] == False:
            zip_backup_path = psync_settings["zip_backup_path"]

            backup_path = None
            try:
                if zip_backup_path == "":
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
                "on_cancel": tools.packagesync_cancelled
            }
            offline.prompt_for_location()

    def restore_zip(self, backup_path):
        if backup_path != None:
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
                #
                # Sublime 2 has Python 2.6.9 as interpreter. So using with zipfile.ZipFile would not work
                # Therefore explicitly open & close the zip file for operation
                z = zipfile.ZipFile(backup_path, "r")
                z.extractall(tools.temp_restore_folder)
                z.close()

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
            tools.packagesync_cancelled()


class PsyncOnlineSyncEnableCommand(sublime_plugin.WindowCommand):

    def is_enabled(self):
        s = tools.get_psync_settings()
        return not s.get("online_sync_enabled", False)

    def run(self):
        s = sublime.load_settings("PackageSync.sublime-settings")
        s.set("online_sync_enabled", True)
        sublime.save_settings("PackageSync.sublime-settings")

        # Start watcher
        tools.start_watcher(tools.get_psync_settings())

        # Run online package syncing module
        sublime.run_command("psync_online_sync", {"mode": ["pull", "push"]})


class PsyncOnlineSyncDisableCommand(sublime_plugin.WindowCommand):

    def is_enabled(self):
        s = tools.get_psync_settings()
        return s.get("online_sync_enabled", False)

    def run(self):
        s = sublime.load_settings("PackageSync.sublime-settings")
        s.set("online_sync_enabled", False)
        sublime.save_settings("PackageSync.sublime-settings")

        # Stop watcher
        tools.stop_watcher()


class PsyncOnlineSyncCommand(sublime_plugin.ApplicationCommand):

    def is_enabled(self):
        s = tools.get_psync_settings()
        return s.get("online_sync_enabled", False) and s.get("online_sync_folder", False) != False

    def run(self, mode=["pull", "push"], override=False):
        # Load settings
        settings = sublime.load_settings("PackageSync.sublime-settings")

        # Check for valid online_sync_folder
        if not os.path.isdir(settings.get("online_sync_folder")):
            sublime.error_message(
                "Invalid path provided for online_sync_folder in PackageSync settings. Online syncing has been turned off. Please correct and retry.\n %s" % settings.get(
                    "online_sync_folder"))
            settings.set("online_sync_enabled", False)
            sublime.save_settings("PackageSync.sublime-settings")
            return

        # Check if sync is already running
        if not sync_queue.has("sync_online"):
            t = online.Sync(mode, override)
            sync_queue.add(t, "sync_online")
        else:
            print("PackageSync: Sync operation already running.")


class PsyncOnlinePullItemCommand(sublime_plugin.ApplicationCommand):

    def is_enabled(self):
        s = tools.get_psync_settings()
        return s.get("online_sync_enabled", False) and s.get("online_sync_folder", False) and os.path.isdir(s.get("online_sync_folder"))

    def run(self, item):
        print("PsyncOnlinePullItemCommand %s", item)

        # Start a thread to pull the current item
        t = online.Sync(mode=["pull"], item=item)
        sync_queue.add(t)


class PsyncOnlinePushItemCommand(sublime_plugin.ApplicationCommand):

    def is_enabled(self):
        s = tools.get_psync_settings()
        return s.get("online_sync_enabled", False) and s.get("online_sync_folder", False) and os.path.isdir(s.get("online_sync_folder"))

    def run(self, item):
        print("PsyncOnlinePushItemCommand %s", item)

        # Start a thread to push the current item
        t = online.Sync(mode=["push"], item=item)
        sync_queue.add(t)


class PsyncOnlineSyncFolderCommand(sublime_plugin.WindowCommand):

    def is_enabled(self):
        return not sync_queue.has("sync_online")

    def run(self):
        # Load settings to provide an initial value for the input panel
        settings = sublime.load_settings("PackageSync.sublime-settings")
        settings.clear_on_change("package_sync")
        sublime.save_settings("PackageSync.sublime-settings")

        sync_folder = settings.get("online_sync_folder")

        # Suggest user dir if nothing set or folder do not exists
        if not sync_folder:
            sync_folder = os.path.expanduser("~")

        def get_sync_folder_on_done(path):
            if not os.path.isdir(path):
                os.makedirs(path)

            if os.path.isdir(path):
                if os.listdir(path):
                    if sublime.ok_cancel_dialog("Backup already exists @ %s \nReplace it?" % path, "Continue"):
                        override = True
                    else:
                        self.window.show_input_panel(
                            "Online Sync Folder", path, get_sync_folder_on_done, None, tools.packagesync_cancelled)
                        return
                else:
                    override = False

                # Adjust settings
                settings.set("online_sync_enabled", True)
                settings.set("online_sync_folder", path)

                # Reset last-run file for Package Control
                last_run_file = os.path.join(
                    sublime.packages_path(), "User", "Package Control.last-run")
                if os.path.isfile(last_run_file):
                    os.remove(last_run_file)

                # Reset last-run file for PackageSync
                last_run_file = os.path.join(
                    sublime.packages_path(), "User", "PackageSync.last-run")
                if os.path.isfile(last_run_file):
                    os.remove(last_run_file)

                sublime.save_settings("PackageSync.sublime-settings")
                sublime.status_message(
                    "online_sync_folder has been set to \n %s" % path)

                # Restart watcher
                tools.pause_watcher(local=False)
                tools.stop_watcher(local=False)
                tools.start_watcher(tools.get_psync_settings(), local=False)

                # Run pkg_sync
                sublime.set_timeout(lambda: sublime.run_command(
                    "psync_online_sync", {"mode": ["pull", "push"], "override": override}), 1000)

            else:
                sublime.error_message("Invalid Path \n %s" % path)

            # Add an on_change listener
            sublime.set_timeout(
                lambda: settings.add_on_change("package_sync", tools.restart_watcher), 500)

        self.window.show_input_panel(
            "Online Sync Folder", sync_folder, get_sync_folder_on_done, None, tools.packagesync_cancelled)

def plugin_loaded():
    tools.init_paths()

    s = sublime.load_settings("PackageSync.sublime-settings")
    s.clear_on_change("package_sync")
    s.add_on_change("package_sync", tools.restart_watcher)
    sublime.save_settings("PackageSync.sublime-settings")

    # Start watcher
    sublime.set_timeout(lambda: tools.start_watcher(tools.get_psync_settings()), 100)

    # Run online package syncing
    sublime.set_timeout(lambda: sublime.run_command(
        "psync_online_sync", {"mode": ["pull", "push"]}), 1000)


def plugin_unloaded():
    s = sublime.load_settings("PackageSync.sublime-settings")
    s.clear_on_change("package_sync")
    sublime.save_settings("PackageSync.sublime-settings")

    # Stop folder watcher
    tools.stop_watcher()


if sublime.version()[0] == "2":
    plugin_loaded()
