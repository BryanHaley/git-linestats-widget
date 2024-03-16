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

settings = {
    "repo": "C:/Path/To/Repository",
    "window": {
        "enabled": True,
        "title": "Git Line Stats Widget",
        "background": "#00FFFF",
        "geometry": "500x100",
        "layout": "horizontal",
        "refresh_rate": 5,
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

# Runs in a thread to update the labels based on git diff output
def update_labels():
    while not want_quit:
        files_changed, insertions, deletions = get_git_info()

        if settings["window"]["enabled"]:
            # Update changed_files_label
            if settings["changed_files"]["number_only"]:
                changed_files_label.config(text = str(files_changed))
            elif files_changed == 1:
                changed_files_label.config(text = str(files_changed) + " file changed")
            else:
                changed_files_label.config(text = str(files_changed) + " files changed")
            
            # Update plus_lines_label
            if settings["plus_lines"]["number_only"]:
                plus_lines_label.config(text = str(insertions))
            else:
                plus_lines_label.config(text = "+" + str(insertions))
            
            # Update minus_lines_label
            if settings["minus_lines"]["number_only"]:
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
        
        time.sleep(settings["window"]["refresh_rate"])

# Runs git diff and parses output
def get_git_info():
    files_changed = 0
    insertions = 0
    deletions = 0
    
    try:
        if platform.system() == 'Windows':
            # Prevent a cmd prompt/terminal window from popping up
            sp_startup_info = subprocess.STARTUPINFO()
            sp_startup_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            sp_startup_info.wShowWindow = subprocess.SW_HIDE

            # Call git subprocess
            diff_text = subprocess.check_output(['git', '--no-pager', 'diff', '--shortstat'], cwd=settings["repo"], startupinfo=sp_startup_info).decode("utf-8").strip()
        else:
            # Call git subprocess without extra startup flags
            diff_text = subprocess.check_output(['git', '--no-pager', 'diff', '--shortstat'], cwd=settings["repo"]).decode("utf-8").strip()
        print(diff_text)
    
        search_result = changed_regex.search(diff_text)
        if search_result:
            files_changed = int(search_result.group(0).split()[0])
        
        search_result = plus_regex.search(diff_text)
        if search_result:
            insertions = int(search_result.group(0).split()[0])
        
        search_result = minus_regex.search(diff_text)
        if search_result:
            deletions = int(search_result.group(0).split()[0])
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
            
            # Test settings
                    
            # Check for a valid repository and ask for one if we don't have it
            if ("repo" not in temp_settings or
                temp_settings["repo"] == "C:/Path/To/Repository" or
                not os.path.exists(temp_settings["repo"]) or
                not os.path.exists(os.path.join(temp_settings["repo"], ".git"))):
                # Get input from user
                temp_settings["repo"] = tk.simpledialog.askstring("Repository", "Enter the path to a repository")

                # If they gave us an empty string, make it the current directory
                if temp_settings["repo"].strip() == "":
                    temp_settings["repo"] = "."

                # Replace Windows-style path separators
                temp_settings["repo"] = temp_settings["repo"].replace("\\", "/")
            
            if not os.path.exists(temp_settings["repo"]):
                raise Exception("Repository path does not exist: " + temp_settings["repo"])
            if not os.path.exists(os.path.join(temp_settings["repo"], ".git")):
                raise Exception("Path is not a git repository: " + temp_settings["repo"])
            
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
        
        # Start label updater thread
        update_thread = Thread(target=update_labels)
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
        
        # Wait for the updater thread to quit then quit app
        want_quit = True
        update_thread.join()
        sys.exit(0)
    except:
        bad_dialog = tk.Tk()
        bad_dialog.title("Error")
        error_label_1 = tk.Label(bad_dialog, text="EXCEPTION OCCURRED")
        error_label_2 = tk.Label(bad_dialog, text=traceback.format_exc())
        error_label_1.pack(side='top')
        error_label_2.pack(side='top')
        bad_dialog.mainloop()
