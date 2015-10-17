import sublime

import os
import fnmatch
import shutil
import json

try:
    from . import tools
except ValueError:
    from package_sync_helpers import tools

prompt_parameters = {}


def create_temp_backup():
    psync_settings = tools.get_psync_settings()

    try:
        if os.path.exists(tools.temp_backup_folder):
            shutil.rmtree(tools.temp_backup_folder, True)

        shutil.copytree(tools.user_settings_folder, tools.temp_backup_folder)

        for root, dirs, files in os.walk(tools.temp_backup_folder):
            for dir in dirs:
                if dir in psync_settings["ignore_dirs"]:
                    shutil.rmtree(os.path.join(root, dir), True)

            for file in files:
                absolute_path = os.path.join(root, file)
                relative_path = os.path.relpath(
                    absolute_path, tools.temp_backup_folder)

                include_matches = [
                    fnmatch.fnmatch(relative_path, p) for p in psync_settings["include_files"]]
                ignore_matches = [
                    fnmatch.fnmatch(relative_path, p) for p in psync_settings["ignore_files"]]

                if any(ignore_matches) or not any(include_matches):
                    os.remove(absolute_path)

    except Exception as e:
        print("PackageSync: Error while creating temp backup.")
        print("PackageSync: Error message: %s" % str(e))


def restore_from_temp():
    try:
        if tools.get_psync_settings()["preserve_packages"] == False:
            # Delete all existing user settings & restore from temp backup
            shutil.rmtree(tools.user_settings_folder, True)
            shutil.copytree(
                tools.temp_restore_folder, tools.user_settings_folder)

        else:
            for src_root, dirs, files in os.walk(tools.temp_restore_folder):
                dst_root = src_root.replace(
                    tools.temp_restore_folder, tools.user_settings_folder)

                if not os.path.exists(dst_root):
                    os.mkdir(dst_root)

                for file in files:
                    src_file = os.path.join(src_root, file)
                    dst_file = os.path.join(dst_root, file)

                    if file == "Package Control.sublime-settings":
                        new_installed_packages = []

                        with open(src_file, "r") as f:
                            new_installed_packages = json.load(
                                f)["installed_packages"]

                        package_control_settings = sublime.load_settings(
                            "Package Control.sublime-settings")
                        current_installed_packages = package_control_settings.get(
                            "installed_packages")
                        for package_name in new_installed_packages:
                            if package_name not in current_installed_packages:
                                current_installed_packages.append(package_name)
                        package_control_settings.set(
                            "installed_packages", current_installed_packages)
                        sublime.save_settings(
                            "Package Control.sublime-settings")

                    else:
                        if os.path.exists(dst_file):
                            os.remove(dst_file)
                        shutil.move(src_file, dst_root)

    except Exception as e:
        print("PackageSync: Error while restoring from backup.")
        print("PackageSync: Error message: %s" % str(e))


def backup_with_prompt_on_done(path):
    global prompt_parameters

    if os.path.exists(path) == True:

        if sublime.version()[0] == "2":
            if sublime.ok_cancel_dialog(
                    "Backup already exists @ %s \nReplace it?" % path, "Continue") == True:
                prompt_parameters["operation_to_perform"](path)

            else:
                tools.packagesync_cancelled()
        else:
            confirm_override = sublime.yes_no_cancel_dialog(
                "Backup already exists @ %s \nReplace it?" % path, "Continue")

            if confirm_override == sublime.DIALOG_YES:
                prompt_parameters["operation_to_perform"](path)
            elif sublime.version()[0] == "3" and confirm_override == sublime.DIALOG_NO:
                prompt_parameters["initial_text"] = path
                prompt_for_location()
            else:
                tools.packagesync_cancelled()

    elif os.path.isabs(os.path.dirname(path)) == True:
        prompt_parameters["operation_to_perform"](path)

    else:
        sublime.error_message("Please provide a valid path for backup.")
        prompt_parameters["initial_text"] = path
        prompt_for_location()


def restore_with_prompt_on_done(path):
    global prompt_parameters

    if os.path.exists(path) == True:
        if prompt_parameters["type"] == "file" and os.path.isfile(path) == True:
            prompt_parameters["operation_to_perform"](path)

        elif prompt_parameters["type"] == "folder" and os.path.isdir(path) == True:
            prompt_parameters["operation_to_perform"](path)

        else:
            sublime.error_message("Please provide a valid path for backup.")
            prompt_parameters["initial_text"] = path
            prompt_for_location()

    else:
        sublime.error_message("Please provide a valid path for backup.")
        prompt_parameters["initial_text"] = path
        prompt_for_location()


def prompt_for_location():
    if prompt_parameters["mode"] == "backup":
        prompt_parameters["window_context"].show_input_panel("Backup Path", prompt_parameters[
                                                             "initial_text"], backup_with_prompt_on_done, None, tools.packagesync_cancelled)
    elif prompt_parameters["mode"] == "restore":
        prompt_parameters["window_context"].show_input_panel("Backup Path", prompt_parameters[
                                                             "initial_text"], restore_with_prompt_on_done, None, tools.packagesync_cancelled)
