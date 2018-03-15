import sublime
import sublime_plugin

import fnmatch
import os
import shutil
import sys
import threading
import time

try:
    from . import tools
except ValueError:
    from package_sync_helpers import tools


class Queue(object):

    current = None
    pool = []

    def __init__(self):
        pass

    def start(self):
        # Clear old thread
        if self.current and self.current["thread"].is_alive():
            sublime.set_timeout(lambda: self.start(), 500)

        else:
            # Reset current thread, since it ended
            self.current = None

            # Check for elements in pool
            if self.pool:
                self.current = self.pool.pop(0)
                self.current["thread"].start()

                # Attemp a new start of the thread
                sublime.set_timeout(lambda: self.start(), 500)

    def has(self, key):
        pool = self.pool + [self.current] if self.current else []
        return any([item for item in pool if item["key"] == key])

    def add(self, thread, key=None):
        self.pool += [{"key": key if key else thread.name, "thread": thread}]
        self.start()


class Sync(threading.Thread):

    def __init__(self, mode=["pull", "push"], override=False, item=None):
        psync_settings = tools.get_psync_settings()

        self.psync_settings = psync_settings
        self.mode = mode
        self.item = item
        self.override = override

        threading.Thread.__init__(self)

    def run(self):
        sync_interval = self.psync_settings.get("online_sync_interval", 1)

        # Stop watcher and wait for the poll
        tools.pause_watcher(
            local="pull" in self.mode, remote="push" in self.mode)

        # If no item pull and push all
        if not self.item:
            tools.log("PackageSync: Complete sync started.", force=True)

            # Fetch all items from the remote location
            if "pull" in self.mode:
                self.pull_all()

            # Push all items to the remote location
            if "push" in self.mode:
                self.push_all()

            tools.log("PackageSync: Complete sync done.", force=True)
        else:
            # Pull the selected item
            if "pull" in self.mode:
                self.pull(self.item)

            # Push the selected item
            if "push" in self.mode:
                self.push(self.item)

        # Restart watcher again
        tools.pause_watcher(
            False, local="pull" in self.mode, remote="push" in self.mode)

    def find_files(self, path):
        tools.log("PackageSync: find_files started for %s" % path)

        include_files = self.psync_settings["include_files"]
        ignore_files = self.psync_settings["ignore_files"]
        ignore_dirs = self.psync_settings["ignore_dirs"]

        # tools.log("PackageSync: path %s" % path)
        # tools.log("PackageSync: include_files %s" % include_files)
        # tools.log("PackageSync: ignore_files %s" % ignore_files)
        # tools.log("PackageSync: ignore_dirs %s" % ignore_dirs)

        resources = {}
        for root, dirs, files in os.walk(path):
            [dirs.remove(dir)
             for dir in dirs if dir in ignore_dirs]

            for file in files:
                absolute_path = os.path.join(root, file)
                relative_path = os.path.relpath(absolute_path, path)

                include_matches = [
                    fnmatch.fnmatch(relative_path, p) for p in include_files]
                ignore_matches = [
                    fnmatch.fnmatch(relative_path, p) for p in ignore_files]
                if any(ignore_matches) or not any(include_matches):
                    continue

                resources[relative_path] = {"version": os.path.getmtime(
                    absolute_path), "path": absolute_path, "dir": os.path.dirname(relative_path)}

        return resources

    def pull_all(self):
        tools.log("PackageSync: pull_all started with override = %s" %
              self.override)

        local_dir = os.path.join(sublime.packages_path(), "User")
        remote_dir = self.psync_settings["online_sync_folder"]

        local_data = self.find_files(local_dir)
        remote_data = self.find_files(remote_dir)

        # Get data of last sync
        last_run_data = tools.load_last_run_data()
        last_run_data_local = last_run_data.get("last_run_data_local", {})
        last_run_data_remote = last_run_data.get("last_run_data_remote", {})

        deleted_local_data = [
            key for key in last_run_data_local if key not in local_data]
        deleted_remote_data = [
            key for key in last_run_data_remote if key not in remote_data]

        # tools.log("PackageSync: local_data: %s" % local_data)
        # tools.log("PackageSync: remote_data: %s" % remote_data)
        # tools.log("PackageSync: deleted_local_data: %s" % deleted_local_data)
        # tools.log("PackageSync: deleted_remote_data: %s" % deleted_remote_data)

        diff = [{"type": "d", "key": key}
                for key in last_run_data_remote if key not in remote_data]
        for key, value in remote_data.items():
            if key in deleted_local_data:
                pass
            elif key not in local_data:
                diff += [dict({"type": "c", "key": key}, **value)]
            elif int(value["version"]) > int(local_data[key]["version"]) or self.override:
                diff += [dict({"type": "m", "key": key}, **value)]

        for item in diff:
            self.pull(item)

        # Set data for next last sync
        tools.save_last_run_data(
            last_run_data_local=self.find_files(local_dir),
            last_run_data_remote=self.find_files(remote_dir))

    def pull(self, item):
        tools.log("PackageSync: pull started for %s" % item)

        local_dir = os.path.join(sublime.packages_path(), "User")
        remote_dir = self.psync_settings.get("sync_folder")

        # Get data of last sync
        last_run_data = tools.load_last_run_data()
        last_run_data_local = last_run_data.get("last_run_data_local", {})
        last_run_data_remote = last_run_data.get("last_run_data_remote", {})

        # Make target file path and directory
        target = os.path.join(local_dir, item["key"])
        target_dir = os.path.dirname(target)

        # TODO -- Added for error mitigation but theoretically this was not needed
        # Verify why the error is occuring for these variables
        try:
            previous_installed_packages
            installed_packages
        except NameError:
            previous_installed_packages = []
            installed_packages = []

        # Skip if file was just pushed
        try:
            if item["type"] == "c" or item["type"] == "m":

                # Check for an updated Package Control setting file and backup
                # old file
                if item["key"] == "Package Control.sublime-settings":
                    previous_installed_packages = tools.load_installed_packages(
                        target)
                    installed_packages = tools.load_installed_packages(
                        item["path"])

                # Check if the watcher detects a file again
                if last_run_data_local[item["key"]]["version"] == item["version"]:
                    # tools.log("PackageSync: Already pulled")
                    return
        except:
            pass

        # If a file was created
        if item["type"] == "c":

            if not os.path.isdir(target_dir):
                os.makedirs(target_dir)

            shutil.copy2(item["path"], target)
            tools.log("PackageSync: Created %s" % target)
            #
            last_run_data_local[item["key"]] = {
                "path": target, "dir": item["dir"], "version": item["version"]}
            last_run_data_remote[item["key"]] = {
                "path": item["path"], "dir": item["dir"], "version": item["version"]}

        # If a file was delated
        elif item["type"] == "d":
            if os.path.isfile(target):
                os.remove(target)
                tools.log("PackageSync: Deleted %s" % target)

            try:
                del last_run_data_local[item["key"]]
                del last_run_data_remote[item["key"]]
            except:
                pass

            # Check if directory is empty and remove it if, just cosmetic issue
            if os.path.isdir(target_dir) and not os.listdir(target_dir):
                os.rmdir(target_dir)

        # If a file was modified
        elif item["type"] == "m":

            if not os.path.isdir(target_dir):
                os.mkdir(target_dir)
            shutil.copy2(item["path"], target)
            tools.log("PackageSync: Updated %s" % target)
            #
            last_run_data_local[item["key"]] = {
                "path": target, "dir": item["dir"], "version": item["version"]}
            last_run_data_remote[item["key"]] = {
                "path": item["path"], "dir": item["dir"], "version": item["version"]}

        # Set data for next last sync
        tools.save_last_run_data(
            last_run_data_local=last_run_data_local,
            last_run_data_remote=last_run_data_remote)

        if item["type"] != "d" and item["key"] == "Package Control.sublime-settings":
            # Handle Package Control
            self.pull_package_control(
                last_run_data, previous_installed_packages, installed_packages)

    def pull_package_control(self, last_run_data, previous_installed_packages, installed_packages):
        # Save items to remove
        to_install = [
            item for item in installed_packages if item not in previous_installed_packages]
        to_remove = [
            item for item in previous_installed_packages if item not in installed_packages]

        tools.log("PackageSync: install: %s", to_install)
        tools.log("PackageSync: remove: %s", to_remove)

        # Check for old remove_packages
        packages_to_remove = last_run_data.get("packages_to_remove", [])
        packages_to_remove += [item for item in to_remove if item !=
                               "Package Control" and item not in packages_to_remove]

        tools.log("PackageSync: packages_to_remove %s", packages_to_remove)

        if packages_to_remove:
            removed_packages = tools.remove_packages(packages_to_remove)
        else:
            removed_packages = []

        # Check if new packages are available and run package cleanup to
        # install missing packages
        if to_install:
            sublime.set_timeout(tools.install_new_packages(), 1000)

        tools.save_last_run_data(
            packages_to_remove=[item for item in packages_to_remove if item not in removed_packages])

    def push_all(self):
        tools.log("PackageSync: push_all started with override = %s" %
              self.override)

        local_dir = os.path.join(sublime.packages_path(), "User")
        remote_dir = self.psync_settings.get("online_sync_folder")

        local_data = self.find_files(local_dir)
        remote_data = self.find_files(remote_dir)

        # Get data of last sync
        last_run_data = tools.load_last_run_data()
        last_run_data_local = last_run_data.get("last_run_data_local", {})
        last_run_data_remote = last_run_data.get("last_run_data_remote", {})

        deleted_local_data = [
            key for key in last_run_data_local if key not in local_data]
        deleted_remote_data = [
            key for key in last_run_data_remote if key not in remote_data]

        # tools.log("PackageSync: local_data: %s" % local_data)
        # tools.log("PackageSync: remote_data: %s" % remote_data)
        # tools.log("PackageSync: deleted_local_data: %s" % deleted_local_data)
        # tools.log("PackageSync: deleted_remote_data: %s" % deleted_remote_data)

        diff = [{"type": "d", "key": key}
                for key in last_run_data_local if key not in local_data]
        for key, value in local_data.items():
            if key in deleted_remote_data:
                pass
            elif key not in remote_data:
                diff += [dict({"type": "c", "key": key}, **value)]
            elif int(value["version"]) > int(remote_data[key]["version"]) or self.override:
                diff += [dict({"type": "m", "key": key}, **value)]

        for item in diff:
            self.push(item)

        # Set data for next last sync
        tools.save_last_run_data(
            last_run_data_local=self.find_files(local_dir),
            last_run_data_remote=self.find_files(remote_dir))

    def push(self, item):
        tools.log("PackageSync: push started for %s" % item)

        local_dir = os.path.join(sublime.packages_path(), "User")
        remote_dir = self.psync_settings.get("online_sync_folder")

        # Get data of last sync
        last_run_data = tools.load_last_run_data()
        last_run_data_local = last_run_data.get("last_run_data_local", {})
        last_run_data_remote = last_run_data.get("last_run_data_remote", {})

        # Skip if file was just copied
        try:
            if item["type"] == "c" or item["type"] == "m":
                if last_run_data_remote[item["key"]]["version"] == item["version"]:
                    tools.log("PackageSync: Already pushed")
                    return
        except:
            pass

        # Make target file path and dir
        target = os.path.join(remote_dir, item["key"])
        target_dir = os.path.dirname(target)

        if item["type"] == "c":

            if not os.path.isdir(target_dir):
                os.makedirs(target_dir)

            shutil.copy2(item["path"], target)
            tools.log("PackageSync: Created %s" % target)
            #
            last_run_data_local[item["key"]] = {
                "path": item["path"], "dir": item["dir"], "version": item["version"]}
            last_run_data_remote[item["key"]] = {
                "path": target, "dir": item["dir"], "version": item["version"]}

        elif item["type"] == "d":
            if os.path.isfile(target):
                os.remove(target)
                tools.log("PackageSync: Deleted %s" % target)

            try:
                del last_run_data_local[item["key"]]
                del last_run_data_remote[item["key"]]
            except:
                pass

            # Check if dir is empty and remove it if
            if os.path.isdir(target_dir) and not os.listdir(target_dir):
                os.rmdir(target_dir)

        elif item["type"] == "m":
            if not os.path.isdir(target_dir):
                os.mkdir(target_dir)
            shutil.copy2(item["path"], target)
            tools.log("PackageSync: Updated %s" % target)
            #
            last_run_data_local[item["key"]] = {
                "path": item["path"], "dir": item["dir"], "version": item["version"]}
            last_run_data_remote[item["key"]] = {
                "path": target, "dir": item["dir"], "version": item["version"]}

        # Set data for next last sync
        tools.save_last_run_data(
            last_run_data_local=last_run_data_local,
            last_run_data_remote=last_run_data_remote)
