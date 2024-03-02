import time
import os
import os.path
import json
import re
import subprocess
import traceback
import tkinter as tk
from tkinter import *
from threading import Thread

settings = {
    "repo": "C:/Path/To/Repository",
    "window": {
        "title": "Git Line Stats Widget",
        "background": "#00FFFF",
        "geometry": "600x100",
        "layout": "horizontal",
        "refresh_rate": 5
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
        "color": "black"
    },
    "plus_lines": {
        "enabled": True,
        "font": "Arial",
        "size": 25,
        "color": "green"
    },
    "minus_lines": {
        "enabled": True,
        "font": "Arial",
        "size": 25,
        "color": "red"
    }
}

# Labels that will be updated in another thread
changed_files = None
plus_lines = None
minus_lines = None

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
        if files_changed == 1:
            changed_files.config(text = str(files_changed) + " file changed")
        else:
            changed_files.config(text = str(files_changed) + " files changed")
        plus_lines.config(text = "+" + str(insertions))
        minus_lines.config(text = "-" + str(deletions))
        time.sleep(settings["window"]["refresh_rate"])

# Runs git diff and parses output
def get_git_info():
    files_changed = 0
    insertions = 0
    deletions = 0
    
    try:
        diff_text = subprocess.check_output(['git', '--no-pager', 'diff', '--shortstat'], cwd=settings["repo"]).decode("ansi").strip()
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
            if (os.path.isfile("settings.json")):
                with open("settings.json", "r") as settings_json:
                    temp_settings = json.load(settings_json)
            # No settings JSON found, generate one
            else:
                with open("settings.json", "w") as settings_json:
                    settings_json.write(json.dumps(settings, indent=2))
            # Test settings
            test = temp_settings["repo"]
            if not os.path.exists(test):
                raise Exception("Repository path does not exist: " + test)
            if not os.path.exists(os.path.join(test, ".git")):
                raise Exception("Path is not a git repository: " + test)
            
            # Could do more extensive testing here, but meh, it'll cause a runtime exception if something is bad
        except:
            bad_dialog = tk.Tk()
            bad_dialog.title("Error")
            error_label_1 = tk.Label(text="COULD NOT LOAD SETTINGS")
            error_label_2 = tk.Label(text=traceback.format_exc())
            error_label_1.pack(side='top')
            error_label_2.pack(side='top')
            bad_dialog.mainloop()
            temp_settings = settings
        settings = temp_settings
        # Create main window
        window = tk.Tk()
        window.title(settings["window"]["title"])
        window.configure(background=settings["window"]["background"])
        window.geometry(settings["window"]["geometry"])
        
        # Create labels
        changed_files = tk.Label(window,
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
        plus_lines = tk.Label(window,
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
        minus_lines = tk.Label(window,
            text="-1000",
            background=settings["window"]["background"],
            foreground=settings["minus_lines"]["color"],
            font=(settings["minus_lines"]["font"], settings["minus_lines"]["size"])
        )
        
        # Pack labels based on layout orientation
        if settings["window"]["layout"] == "horizontal":
            if settings["changed_files"]["enabled"]:
                changed_files.pack(side='left')
                if settings["plus_lines"]["enabled"]:
                    separator1.pack(side='left')
            
            if settings["plus_lines"]["enabled"]:
                plus_lines.pack(side='left')
            
            if settings["minus_lines"]["enabled"]:
                if settings["plus_lines"]["enabled"] or settings["changed_files"]["enabled"]:
                    separator2.pack(side='left')
                minus_lines.pack(side='left')
        else:
            changed_files.pack(side='top')
            plus_lines.pack(side='top')
            minus_lines.pack(side='top')
        
        
        # Start label updater thread
        update_thread = Thread(target=update_labels)
        update_thread.start()
        
        # Start window main loop
        window.mainloop()
        
        # Wait for the updater thread to quit then quit app
        want_quit = True
        update_thread.join()
    except:
        bad_dialog = tk.Tk()
        bad_dialog.title("Error")
        error_label_1 = tk.Label(bad_dialog, text="EXCEPTION OCCURRED")
        error_label_2 = tk.Label(bad_dialog, text=traceback.format_exc())
        error_label_1.pack(side='top')
        error_label_2.pack(side='top')
        bad_dialog.mainloop()