import sublime
import sublime_plugin

import os
import sys
import tempfile
import time
import json
import fnmatch
import threading

local_watcher = None
remote_watcher = None


def get_psync_settings():
    s = sublime.load_settings("PackageSync.sublime-settings")
    return {
        "prompt_for_location": s.get("prompt_for_location", False),
        "list_backup_path": s.get("list_backup_path", ""),
        "zip_backup_path": s.get("zip_backup_path", ""),
        "folder_backup_path": s.get("folder_backup_path", ""),
        "ignore_files": s.get("ignore_files", []),
        "include_files": s.get("include_files", []),
        "ignore_dirs": s.get("ignore_dirs", []),
        "preserve_packages": s.get("preserve_packages", True),
        "online_sync_enabled": s.get("online_sync_enabled", False),
        "online_sync_folder": s.get("online_sync_folder", ""),
        "online_sync_interval": s.get("online_sync_interval", 10),
    }


def set_psync_settings(**kwargs):
    s = sublime.load_settings("PackageSync.sublime-settings")
    for setting, value in kwargs.items():
        s.set(setting, value)
    sublime.save_settings("PackageSync.sublime-settings")


def init_paths():
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

    #: Path of file to be used when backing up to or restoring from the sublime-settings file for Package Control
    global default_list_backup_path
    default_list_backup_path = os.path.join(
        desktop_path, "SublimePackagesList.txt")

    #: Path of the installed "/packages/user/" folder to backup or restore
    global user_settings_folder
    user_settings_folder = os.path.join(sublime.packages_path(), "User")

    #: Path to be used when backing up to or restoring from the "/packages/user" folder as a folder
    global default_folder_backup_path
    default_folder_backup_path = os.path.join(
        desktop_path, "SublimePackagesBackup")

    #: Path to be used when backing up to or restoring from the "/packages/user" folder as a zip file
    global default_zip_backup_path
    default_zip_backup_path = os.path.join(
        desktop_path, "SublimePackagesBackup.zip")

    #: Path to be used as temporary location to store files during backup operation
    global temp_backup_folder
    temp_backup_folder = os.path.join(
        tempfile.gettempdir(), "backup_" + str(time.time()))

    #: Path to be used as temporary location to store files during restore operation
    global temp_restore_folder
    temp_restore_folder = os.path.join(
        tempfile.gettempdir(), "restore_" + str(time.time()))


def add_packagesync_to_installed_packages():
    package_control_settings = sublime.load_settings(
        "Package Control.sublime-settings")
    installed_packages = package_control_settings.get("installed_packages", [])

    if "PackageSync" not in installed_packages:
        print("PackageSync: Adding self to installed packages list")
        installed_packages.append("PackageSync")

    package_control_settings.set("installed_packages", installed_packages)
    sublime.save_settings("Package Control.sublime-settings")


def install_new_packages():
    try:
        def run_package_control_cleanup():
            # Remove the last-run file in order to trigger the package
            # installation
            pkg_control_last_run = os.path.join(
                sublime.packages_path(), "User", "Package Control.last-run")
            if os.path.isfile(pkg_control_last_run):
                os.remove(pkg_control_last_run)

            # Import package control cleanup
            pkg_control_cleanup = sys.modules["Package Control.package_control.package_cleanup"] if sublime.version(
            )[0] == "3" else sys.modules["package_control.package_cleanup"]
            pkg_control_cleanup.PackageCleanup().start()

        # TODO: Verify whether this function call is actually needed. Added as
        # a hack only to cater to a user issue
        # Add PackageSync to the installed packages list if it has been removed
        add_packagesync_to_installed_packages()

        sublime.set_timeout(run_package_control_cleanup, 1000)

    except Exception as e:
        print(
            "PackageSync: Error while installing packages via Package Control.")
        print("PackageSync: Error message: %s" % str(e))


def remove_packages(packages_to_remove):
    print("PackageSync: remove packages %s" % packages)

    # Reset wait_flag
    wait_flag = [True]

    # At first ignore packages on main thread
    def ignore_packages():
        settings = sublime.load_settings("Preferences.sublime-settings")
        ignored_packages = settings.get('ignored_packages')
        settings.set("ignored_packages", [item for item in packages_to_remove])
        sublime.save_settings("Preferences.sublime-settings")
        #
        wait_flag[0] = False

    sublime.set_timeout(ignore_packages, 0)

    # Wait to complete writing ignored_packages
    while wait_flag[0]:
        time.sleep(0.25)

    # wait for sublime text to ignore packages
    time.sleep(1)

    removed_packages = []
    for package in packages_to_remove[:]:
        status = remove_package(package)
        if status:
            removed_packages += [package]

    # Reset wait flag
    wait_flag[0] = True

    # Update ignore packages on main thread
    def unignore_packages():
        settings = sublime.load_settings("Preferences.sublime-settings")
        settings.set("ignored_packages", [])
        sublime.save_settings("Preferences.sublime-settings")
        #
        wait_flag[0] = False

    sublime.set_timeout(unignore_packages, 1000)

    # Wait to complete writing ignored_packages
    while wait_flag[0]:
        time.sleep(0.25)

    return removed_packages


def remove_package(package):
    # Check for installed_package path
    try:
        installed_package_path = os.path.join(
            sublime.installed_packages_path(), package + ".sublime-package")
        if os.path.exists(installed_package_path):
            os.remove(installed_package_path)
    except:
        return False

    # Check for pristine_package_path path
    try:
        pristine_package_path = os.path.join(os.path.dirname(
            sublime.packages_path()), "Pristine Packages", package + ".sublime-package")
        if os.path.exists(pristine_package_path):
            os.remove(pristine_package_path)
    except:
        return False

    # Check for package dir
    try:
        os.chdir(sublime.packages_path())
        package_dir = os.path.join(sublime.packages_path(), package)
        if os.path.exists(package_dir):
            if shutil.rmtree(package_dir):
                open(
                    os.path.join(package_dir, 'package-control.cleanup'), 'w').close()
    except:
        return False

    return True


def load_last_run_data():
    try:
        with open(os.path.join(sublime.packages_path(), "User", "PackageSync.last-run"), "r", encoding="utf8") as f:
            last_run_data = json.load(f)
    except:
        last_run_data = {}

    return last_run_data


def save_last_run_data(**kwargs):
    # Load current last run data
    last_run_data = load_last_run_data()

    # Update with new values
    for key, value in kwargs.items():
        last_run_data[key] = value

    try:
        with open(os.path.join(sublime.packages_path(), "User", "PackageSync.last-run"), "w", encoding="utf8") as f:
            json.dump(last_run_data, f, sort_keys=True, indent=4)
    except Exception as e:
        print("PackageSync: Error while updating PackageSync.last-run")
        print("PackageSync: Error message %s" % str(e))


def get_installed_packages_list(settings_path):
    try:
        with open(settings_path, "r", encoding="utf8") as f:
            package_control_settings = json.load(f)
    except:
        package_control_settings = {}

    return package_control_settings.get("installed_packages", [])


def packagesync_cancelled():
    print("PackageSync: Backup/Restore/Sync operation cancelled")


def start_watcher(psync_settings, local=True, remote=True):
    global local_watcher
    global remote_watcher

    if not psync_settings.get("online_sync_enabled", False):
        return

    # Build required options for the watcher
    local_dir = os.path.join(sublime.packages_path(), "User")
    remote_dir = psync_settings.get("online_sync_folder")
    sync_interval = psync_settings.get("online_sync_interval")
    include_files = psync_settings.get("include_files", [])
    ignore_files = psync_settings.get("ignore_files", [])
    ignore_dirs = psync_settings.get("ignore_dirs", [])

    # Create local watcher
    if local:
        local_watcher = WatcherThread(
            local_dir, "psync_online_push_item", sync_interval, include_files, ignore_files, ignore_dirs)
        local_watcher.start()

    # Create remote watcher
    if remote:
        remote_watcher = WatcherThread(
            remote_dir, "psync_online_pull_item", sync_interval, include_files, ignore_files, ignore_dirs)
        remote_watcher.start()


def pause_watcher(status=True, local=True, remote=True):
    global local_watcher
    global remote_watcher

    # Pause local watcher
    if local_watcher and local:
        local_watcher.pause(status)

    # Pause remote watcher
    if remote_watcher and remote:
        remote_watcher.pause(status)


def restart_watcher():
    psync_settings = get_psync_settings()

    pause_watcher(local=False)
    stop_watcher(local=False)
    start_watcher(psync_settings, local=False)

    # Run sync operation
    sublime.set_timeout(
        lambda: sublime.run_command("psync_online_sync", {"mode": ["pull", "push"]}), 3000)


def stop_watcher(local=True, remote=True):
    global local_watcher
    global remote_watcher

    # Stop local watcher
    if local_watcher and local:
        local_watcher.stop = True

    # Stop remote watcher
    if remote_watcher and remote:
        remote_watcher.stop = True


class WatcherThread(threading.Thread):

    stop = False

    def __init__(self, dir_to_watch, callback, sync_interval, include_files=[], ignore_files=[], ignore_dirs=[]):
        self.dir_to_watch = dir_to_watch
        self.callback = callback

        self.sync_interval = sync_interval

        self.include_files = include_files
        self.ignore_files = ignore_files
        self.ignore_dirs = ignore_dirs

        self.watcher = Watcher(
            self.dir_to_watch, self.callback, self.include_files, self.ignore_files, self.ignore_dirs)

        threading.Thread.__init__(self)

    def run(self):
        while not self.stop:
            self.watcher.loop()
            time.sleep(self.sync_interval)

    def pause(self, status=True):
        # Update file list before unpause watcher
        if not status:
            self.watcher.loop()
        self.watcher.pause = status


class Watcher(object):

    pause = True

    def __init__(self, dir_to_watch, callback, include_files=[], ignore_files=[], ignore_dirs=[]):

        self.dir_to_watch = dir_to_watch
        self.callback = callback

        self.include_files = include_files
        self.ignore_files = ignore_files
        self.ignore_dirs = ignore_dirs

        self.files_map = {}

        self.update_files()
        self.pause = False

    def __del__(self):
        print("Watcher stopped")
        for key, value in self.files_map.items():
            pass
            # print("PackageSync: Stopped watching %s" % value["path"])

    def get_sync_items(self, walk=False):
        sync_items = []
        for root, dirs, files in os.walk(self.dir_to_watch):
            [dirs.remove(dir)
             for dir in dirs if dir in self.ignore_dirs]

            for file in files:
                absolute_path = os.path.join(root, file)
                relative_path = os.path.relpath(
                    absolute_path, self.dir_to_watch)

                include_matches = [
                    fnmatch.fnmatch(relative_path, p) for p in self.include_files]
                ignore_matches = [
                    fnmatch.fnmatch(relative_path, p) for p in self.ignore_files]

                if any(ignore_matches) or not any(include_matches):
                    continue

                sync_items += [{"key": relative_path, "path": absolute_path, "dir":
                                os.path.dirname(relative_path), "version": os.path.getmtime(absolute_path)}]

        return sync_items

    def loop(self):
        self.update_files()
        for key, value in self.files_map.items():
            self.check_file(key, value)

    def check_file(self, key, value):
        file_mod_time = os.path.getmtime(value["path"])
        if file_mod_time != value["version"]:
            self.files_map[key]["version"] = file_mod_time
            item = dict({"type": "m"}, **value)

            # Run callback if file changed
            if not self.pause:
                sublime.set_timeout(
                    lambda: sublime.run_command(self.callback, {"item": item}), 0)
            else:
                pass
                # print(
                #     "PackageSync: Inside check_file - Callback skipped for %s" % item)

    def update_files(self):
        sync_items = []

        for item in self.get_sync_items():
            if item["key"] not in self.files_map:
                sync_items += [item]

        # check non-existent files
        for key, value in self.files_map.copy().items():
            if not os.path.exists(value["path"]):
                self.unwatch(value)

        for item in sync_items:
            if item["key"] not in self.files_map:
                self.watch(item)

    def watch(self, item):
        # print("PackageSync: Started watching %s" % item["path"])
        self.files_map[item["key"]] = item
        item = dict({"type": "c"}, **item)

        # Run callback if file created
        if not self.pause:
            sublime.set_timeout(
                lambda: sublime.run_command(self.callback, {"item": item}), 0)
        else:
            pass
            # print("PackageSync: Inside watch - Callback skipped for %s" % item)

    def unwatch(self, item):
        # print("PackageSync: Stopped watching %s" % item["path"])
        del self.files_map[item["key"]]
        item = dict({"type": "d"}, **item)

        # Run callback if file deleted
        if not self.pause:
            sublime.set_timeout(
                lambda: sublime.run_command(self.callback, {"item": item}), 0)
        else:
            pass
            # print(
            #     "PackageSync: Inside unwatch - Callback skipped for %s" % item)
