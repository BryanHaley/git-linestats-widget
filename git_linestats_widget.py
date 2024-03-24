import time
import os
import os.path
import json
import re
import subprocess
import traceback
import platform
import sys
import tkinter as tk
from tkinter import *
from tkinter.simpledialog import askstring
from threading import Thread

# Default settings dict
settings = {
    "repo": ["C:/Path/To/Repository"],
    "refresh_rate": 5,
    "include_untracked_files": False,
    "window": {
        "enabled": True,
        "title": "Git Line Stats Widget",
        "background": "#00FFFF",
        "geometry": "500x100",
        "layout": "horizontal",
        "pad": 10
    },
    "separator": {
        "text": " | ",
        "font": "Arial",
        "size": 25,
        "color": "black"
    },
    "changed_files": {
        "enabled": True,
        "font": "Arial",
        "size": 25,
        "color": "black",
        "number_only": False
    },
    "plus_lines": {
        "enabled": True,
        "font": "Arial",
        "size": 25,
        "color": "green",
        "number_only": False
    },
    "minus_lines": {
        "enabled": True,
        "font": "Arial",
        "size": 25,
        "color": "red",
        "number_only": False
    },
    "changed_files_file": {
        "enabled": False,
        "path": "changed_files.txt",
        "number_only": False
    },
    "plus_lines_file": {
        "enabled": False,
        "path": "plus_lines.txt",
        "number_only": False
    },
    "minus_lines_file": {
        "enabled": False,
        "path": "minus_files.txt",
        "number_only": False
    }
}

# Memo for untracked files so we only re-read them when necessary
untracked_file_memo = { }

# Labels and files that will be updated in another thread
changed_files_label = None
plus_lines_label = None
minus_lines_label = None
changed_files_file = None
plus_lines_file = None
minus_lines_file = None

# Regular expressions for parsing git diff output
changed_regex = re.compile("[0-9]+ file[s]* changed")
plus_regex = re.compile("[0-9]+ insertion[s]*")
minus_regex = re.compile("[0-9]+ deletion[s]*")

# Signal to thread to quit
want_quit = False

# Runs in a thread to update the labels and files based on git diff output
def update_labels_and_files():
    while not want_quit:
        files_changed, insertions, deletions = get_git_info()
        print(str(files_changed) + " files changed " + str(insertions) + " insertions " + str(deletions) + " deletions")

        if settings["window"]["enabled"] and not want_quit:
            # Update changed_files_label
            if settings["changed_files"]["number_only"]:
                changed_files_label.config(text = str(files_changed))
            elif files_changed == 1:
                changed_files_label.config(text = str(files_changed) + " file changed")
            else:
                changed_files_label.config(text = str(files_changed) + " files changed")
            
            # Update plus_lines_label
            if settings["plus_lines"]["number_only"] and not want_quit:
                plus_lines_label.config(text = str(insertions))
            else:
                plus_lines_label.config(text = "+" + str(insertions))
            
            # Update minus_lines_label
            if settings["minus_lines"]["number_only"] and not want_quit:
                minus_lines_label.config(text = str(deletions))
            else:
                minus_lines_label.config(text = "-" + str(deletions))
        
        # Update changed_files file
        if settings["changed_files_file"]["enabled"]:
            changed_files_file.seek(0)
            changed_files_file.truncate()
            if settings["changed_files_file"]["number_only"]:
                changed_files_file.write(str(files_changed))
            elif files_changed == 1:
                changed_files_file.write(str(files_changed) + " file changed")
            else:
                changed_files_file.write(str(files_changed) + " files changed")
            changed_files_file.flush()
        
        # Update plus_lines file
        if settings["plus_lines_file"]["enabled"]:
            plus_lines_file.seek(0)
            plus_lines_file.truncate()
            if settings["plus_lines_file"]["number_only"]:
                plus_lines_file.write(str(insertions))
            else:
                plus_lines_file.write("+" + str(insertions))
            plus_lines_file.flush()
        
        # Update minus_lines file
        if settings["minus_lines_file"]["enabled"]:
            minus_lines_file.seek(0)
            minus_lines_file.truncate()
            if settings["minus_lines_file"]["number_only"]:
                minus_lines_file.write(str(deletions))
            else:
                minus_lines_file.write("-" + str(deletions))
            minus_lines_file.flush()
        
        time.sleep(settings["refresh_rate"])

# Runs git diff and parses output
def get_git_info():
    files_changed = 0
    insertions = 0
    deletions = 0
    
    for repo in settings["repo"]:
        try:
            if platform.system() == 'Windows':
                # Prevent a cmd prompt/terminal window from popping up
                sp_startup_info = subprocess.STARTUPINFO()
                sp_startup_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                sp_startup_info.wShowWindow = subprocess.SW_HIDE

                # Call git subprocess to get diff stats
                diff_text = subprocess.check_output(['git', '--no-pager', 'diff', '--shortstat'], cwd=repo, startupinfo=sp_startup_info).decode("utf-8").strip()
            else:
                # Call git subprocess to get diff stats without extra startup flags
                diff_text = subprocess.check_output(['git', '--no-pager', 'diff', '--shortstat'], cwd=repo).decode("utf-8").strip()
        
            # Extract stats from text
            search_result = changed_regex.search(diff_text)
            if search_result:
                files_changed += int(search_result.group(0).split()[0])
            
            search_result = plus_regex.search(diff_text)
            if search_result:
                insertions += int(search_result.group(0).split()[0])
            
            search_result = minus_regex.search(diff_text)
            if search_result:
                deletions += int(search_result.group(0).split()[0])
            
            # Handle untracked files if enabled
            if settings["include_untracked_files"]:
                if platform.system() == 'Windows':
                    # Prevent a cmd prompt/terminal window from popping up
                    sp_startup_info = subprocess.STARTUPINFO()
                    sp_startup_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    sp_startup_info.wShowWindow = subprocess.SW_HIDE

                    # Call git subprocess to get untracked files
                    diff_text = subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard'], cwd=repo, startupinfo=sp_startup_info).decode("utf-8").strip()
                else:
                    # Call git subprocess to get untracked files without extra startup flags
                    diff_text = subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard'], cwd=repo).decode("utf-8").strip()
                
                # Iterate through lines in the file to find out how many lines are in it
                for file_path in diff_text.splitlines():
                    file_path = os.path.join(repo, file_path)
                    if os.path.exists(file_path):
                        # Check memo to see if we've read this file already and don't need to re-read it
                        if file_path in untracked_file_memo:
                            # Check if the modification date has changed
                            if untracked_file_memo[file_path]["last_modified"] == os.path.getmtime(file_path):
                                # We've already read this file, just get the known stats and skip reading it
                                insertions += untracked_file_memo[file_path]["insertions"]
                                files_changed += 1
                                continue

                        # File not in memo, we gotta read it
                        lines_added_from_file = 0
                        try:
                            print ("Reading file " + file_path)
                            with open(file_path, "r") as f:
                                for l in f:
                                    lines_added_from_file += 1
                            insertions += lines_added_from_file
                            files_changed += 1
                            untracked_file_memo[file_path] = {}
                            untracked_file_memo[file_path]["last_modified"] = os.path.getmtime(file_path)
                            untracked_file_memo[file_path]["insertions"] = lines_added_from_file
                        except UnicodeDecodeError:
                            # This is a binary file, just count the file change and move on
                            files_changed += 1
                            untracked_file_memo[file_path] = {}
                            untracked_file_memo[file_path]["last_modified"] = os.path.getmtime(file_path)
                            untracked_file_memo[file_path]["insertions"] = 0

            # Try not to spam the CPU and disk
            time.sleep(0.1)
        except:
            print(traceback.format_exc())
    
    return (files_changed, insertions, deletions)

if __name__ == "__main__":
    try:
        temp_settings = settings
        try:
            # Load from JSON file
            if (os.path.exists("settings.json")):
                with open("settings.json", "r") as settings_json:
                    temp_settings = json.load(settings_json)
            
            # Test settings. This section is mostly to maintain backwards compatibility with old settings files.
            
            # Check if we have the old style repo property
            if ("repo" in temp_settings and not isinstance(temp_settings["repo"], list)):
                temp_settings["repo"] = [temp_settings["repo"]]

            # Check for a valid repository and ask for one if we don't have it
            if ("repo" not in temp_settings or
                (
                    len(temp_settings["repo"]) == 1 and # Assume if we have multiple repos they've messed with settings.json and this isn't a first run
                    temp_settings["repo"][0] == "C:/Path/To/Repository" or
                    not os.path.exists(temp_settings["repo"][0]) or
                    not os.path.exists(os.path.join(temp_settings["repo"][0], ".git"))
                )):
                # Get input from user
                temp_settings["repo"] = [tk.simpledialog.askstring("Repository", "Enter the path to a repository")]

                # If they gave us an empty string, make it the current directory
                if temp_settings["repo"][0].strip() == "":
                    temp_settings["repo"][0] = "."

                # Replace Windows-style path separators
                temp_settings["repo"][0] = temp_settings["repo"][0].replace("\\", "/")
                

            # expand ~ in all repo's specified
            for index in range(0, len(temp_settings["repo"])):
                temp_settings["repo"][index] = os.path.expanduser(temp_settings["repo"][index])

            # Verify all repositories
            for repo in temp_settings["repo"]:
                if not os.path.exists(repo):
                    raise Exception("Repository path does not exist: " + repo)
                if not os.path.exists(os.path.join(repo, ".git")):
                    raise Exception("Path is not a git repository: " + repo)
            
            # Check for top-level properties
            if "window" not in temp_settings:
                temp_settings["window"] = settings["window"]
                temp_settings["window"]["enabled"] = False # Assume if the property wasn't present the user wants it disabled
            if "separator" not in temp_settings:
                temp_settings["separator"] = settings["separator"]
                temp_settings["separator"]["text"] = ""
            if "changed_files" not in temp_settings:
                temp_settings["changed_files"] = settings["changed_files"]
                temp_settings["changed_files"]["enabled"] = False
            if "plus_lines" not in temp_settings:
                temp_settings["plus_lines"] = settings["plus_lines"]
                temp_settings["plus_lines"]["enabled"] = False
            if "minus_lines" not in temp_settings:
                temp_settings["minus_lines"] = settings["minus_lines"]
                temp_settings["minus_lines"]["enabled"] = False
            if "changed_files_file" not in temp_settings:
                temp_settings["changed_files_file"] = settings["changed_files_file"]
                temp_settings["changed_files_file"]["enabled"] = False
            if "plus_lines_file" not in temp_settings:
                temp_settings["plus_lines_file"] = settings["plus_lines_file"]
                temp_settings["plus_lines_file"]["enabled"] = False
            if "minus_lines_file" not in temp_settings:
                temp_settings["minus_lines_file"] = settings["minus_lines_file"]
                temp_settings["minus_lines_file"]["enabled"] = False
            if "include_untracked_files" not in temp_settings:
                temp_settings["include_untracked_files"] = False
            # Repo gets checked above, refresh_rate gets checked below
            
            # Check for new file settings
            if "changed_files_file" not in temp_settings:
                temp_settings["changed_files_file"] = {
                    "enabled": False,
                    "path": "changed_files.txt"
                }
            if "plus_lines_file" not in temp_settings:
                temp_settings["plus_lines_file"] = {
                    "enabled": False,
                    "path": "plus_lines.txt"
                }
            if "minus_lines_file" not in temp_settings:
                temp_settings["minus_lines_file"] = {
                    "enabled": False,
                    "path": "minus_files.txt"
                }
            
            # Add enabled property to window if not present
            if "enabled" not in temp_settings["window"]:
                temp_settings["window"]["enabled"] = True

            # Add pad value to settings if not present
            if "pad" not in temp_settings["window"]:
                temp_settings["window"]["pad"] = 0

            # Add number_only properties if not present
            if "number_only" not in temp_settings["changed_files"]:
                temp_settings["changed_files"]["number_only"] = False
            if "number_only" not in temp_settings["plus_lines"]:
                temp_settings["plus_lines"]["number_only"] = False
            if "number_only" not in temp_settings["minus_lines"]:
                temp_settings["minus_lines"]["number_only"] = False
            if "number_only" not in temp_settings["changed_files_file"]:
                temp_settings["changed_files_file"]["number_only"] = False
            if "number_only" not in temp_settings["plus_lines_file"]:
                temp_settings["plus_lines_file"]["number_only"] = False
            if "number_only" not in temp_settings["minus_lines_file"]:
                temp_settings["minus_lines_file"]["number_only"] = False
            
            # Move refresh rate if it's in the old place
            if "refresh_rate" in temp_settings["window"]:
                if "refresh_rate" not in temp_settings:
                    temp_settings["refresh_rate"] = temp_settings["window"]["refresh_rate"]
                del temp_settings["window"]["refresh_rate"]
            
            # Add refresh rate if it's not present at all
            if "refresh_rate" not in temp_settings:
                temp_settings["refresh_rate"] = settings["refresh_rate"]

            # Add untracked files property if it's not present
            if "include_untracked_files" not in temp_settings:
                temp_settings["include_untracked_files"] = False
            
            # Write updated settings to disk
            with open("settings.json", "w") as settings_json:
                settings_json.write(json.dumps(temp_settings, indent=2))
            
            # Could do more extensive testing here, but meh, it'll cause a runtime exception if something is bad
        except:
            bad_dialog = tk.Tk()
            bad_dialog.title("Error")
            error_label_1 = tk.Label(bad_dialog, text="COULD NOT LOAD SETTINGS")
            error_label_2 = tk.Label(bad_dialog, text=traceback.format_exc())
            error_label_1.pack(side='top')
            error_label_2.pack(side='top')
            bad_dialog.mainloop()
            sys.exit(1)
        settings = temp_settings

        if settings["window"]["enabled"]:
            # Create main window
            window = tk.Tk()
            window.title(settings["window"]["title"])
            window.configure(background=settings["window"]["background"])
            window.geometry(settings["window"]["geometry"])
            
            # Create labels
            changed_files_label = tk.Label(window,
                text="100 file(s) changed",
                background=settings["window"]["background"],
                foreground=settings["changed_files"]["color"],
                font=(settings["changed_files"]["font"], settings["changed_files"]["size"])
            )
            separator1 = tk.Label(window,
                text=settings["separator"]["text"],
                background=settings["window"]["background"],
                foreground=settings["separator"]["color"],
                font=(settings["separator"]["font"], settings["separator"]["size"])
            )
            plus_lines_label = tk.Label(window,
                text="+1000",
                background=settings["window"]["background"],
                foreground=settings["plus_lines"]["color"],
                font=(settings["plus_lines"]["font"], settings["plus_lines"]["size"])
            )
            separator2 = tk.Label(window,
                text=settings["separator"]["text"],
                background=settings["window"]["background"],
                foreground=settings["separator"]["color"],
                font=(settings["separator"]["font"], settings["separator"]["size"])
            )
            minus_lines_label = tk.Label(window,
                text="-1000",
                background=settings["window"]["background"],
                foreground=settings["minus_lines"]["color"],
                font=(settings["minus_lines"]["font"], settings["minus_lines"]["size"])
            )
            
            # Pack labels based on layout orientation
            if settings["window"]["layout"] == "horizontal":
                if settings["changed_files"]["enabled"]:
                    changed_files_label.pack(side='left', padx = (settings["window"]["pad"], settings["window"]["pad"]))
                    if settings["plus_lines"]["enabled"]:
                        separator1.pack(side='left')
                
                if settings["plus_lines"]["enabled"]:
                    plus_lines_label.pack(side='left', padx = (settings["window"]["pad"], settings["window"]["pad"]))
                
                if settings["minus_lines"]["enabled"]:
                    if settings["plus_lines"]["enabled"] or settings["changed_files"]["enabled"]:
                        separator2.pack(side='left')
                    minus_lines_label.pack(side='left', padx = (settings["window"]["pad"], settings["window"]["pad"]))
            elif settings["window"]["layout"] == "stacked":
                if settings["changed_files"]["enabled"]:
                    changed_files_label.pack(side='top')
                if settings["plus_lines"]["enabled"]:
                    plus_lines_label.pack(side='left', padx = (settings["window"]["pad"], 0))
                if settings["minus_lines"]["enabled"]:
                    minus_lines_label.pack(side='right', padx = (0, settings["window"]["pad"]))
            else:
                if settings["changed_files"]["enabled"]:
                    changed_files_label.pack(side='top')
                if settings["plus_lines"]["enabled"]:
                    plus_lines_label.pack(side='top')
                if settings["minus_lines"]["enabled"]:
                    minus_lines_label.pack(side='top')
        
        try:
            if settings["changed_files_file"]["enabled"]:
                changed_files_file = open(settings["changed_files_file"]["path"], "w+")
            if settings["plus_lines_file"]["enabled"]:
                plus_lines_file = open(settings["plus_lines_file"]["path"], "w+")
            if settings["minus_lines_file"]["enabled"]:
                minus_lines_file = open(settings["minus_lines_file"]["path"], "w+")
        except:
            bad_dialog = tk.Tk()
            bad_dialog.title("Error")
            error_label_1 = tk.Label(bad_dialog, text="COULD NOT OPEN FILES FOR WRITING")
            error_label_2 = tk.Label(bad_dialog, text=traceback.format_exc())
            error_label_1.pack(side='top')
            error_label_2.pack(side='top')
            bad_dialog.mainloop()
        
        if settings["include_untracked_files"]:
            print("Warning! Including untracked files can be an expensive operation when the files are added or changed. Turn this off if you have performance issues.")
        
        # Start label updater thread
        update_thread = Thread(target=update_labels_and_files)
        update_thread.start()
        
        if settings["window"]["enabled"]:
            # Start window main loop
            window.mainloop()
        else:
            print("Press Ctrl+C to exit")
            # Idle until we get an exception then quit
            try:
                while True:
                    time.sleep(0.1)
            except:
                print(traceback.format_exc())
        
        # Wait for the updater thread to finish then quit app
        want_quit = True
        update_thread.join()

        if changed_files_file:
            changed_files_file.close()
        if plus_lines_file:
            plus_lines_file.close()
        if minus_lines_file:
            minus_lines_file.close()
    except:
        bad_dialog = tk.Tk()
        bad_dialog.title("Error")
        error_label_1 = tk.Label(bad_dialog, text="EXCEPTION OCCURRED")
        error_label_2 = tk.Label(bad_dialog, text=traceback.format_exc())
        error_label_1.pack(side='top')
        error_label_2.pack(side='top')
        bad_dialog.mainloop()
