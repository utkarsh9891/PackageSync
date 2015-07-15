import sublime
import sublime_plugin

import os
import sys
import tempfile
import time

from threading import Timer


def load_settings():
    s = sublime.load_settings("PackageSync.sublime-settings")

    global sync_settings
    sync_settings = {
        "prompt_for_location": s.get("prompt_for_location", False),
        "list_backup_path": s.get("list_backup_path", ""),
        "zip_backup_path": s.get("zip_backup_path", ""),
        "folder_backup_path": s.get("folder_backup_path", ""),
        "ignore_files": s.get("ignore_files", []) + ["PackageSync.sublime-settings"],
        "include_files": s.get("include_files", []),
        "ignore_dirs": s.get("ignore_dirs", []),
        "preserve_packages": s.get("preserve_packages", True)
    }


def plugin_loaded():
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
            pkg_control_cleanup = sys.modules[
                "Package Control.package_control.package_cleanup"]
            pkg_control_cleanup.PackageCleanup().start()

        # TODO: Verify whether this function call is actually needed. Added as
        # a hack only to cater to a user issue
        # Add PackageSync to the installed packages list if it has been removed
        add_packagesync_to_installed_packages()

        t = Timer(3, run_package_control_cleanup)
        t.start()

    except Exception as e:
        print(
            "PackageSync: Error while installing packages via Package Control.")
        print("PackageSync: Error message: %s" % str(e))


if sublime.version()[0] == "3":
    plugin_loaded()
