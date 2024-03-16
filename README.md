# Git Line Stats Widget

A small GUI widget for displaying how many lines have changed in one or more git repositories. Used for programming streams.

![Screenshot of widget in horizontal layout](https://i.imgur.com/W8tUybp.png)
![Screenshot of widget in stacked layout](https://i.imgur.com/bavyUnQ.png)

Fonts and colors can be configured via `settings.json`. Most HTML-safe fonts and color codes will work.

You may also export stats to files that can be read by OBS, which allows for nearly unlimited customization.
![Screenshot of customization using OBS](https://i.imgur.com/RZyRMws.png)

# Prerequisites

You need Python3 installed (and on the PATH, if launching via batch file).

On Windows, tkinter should come with Python. On other platforms you may need to do `pip install tk`.

You'll also need git installed and on the PATH, which you presumably should already if you have a git repository.

# Usage

Download and extract the repository (click the green "Code" button -> "Download as zip").

Launch the widget using `python git_linestats_widget.py` or by double clicking `launch.bat` on Windows. It will ask you for a path to a repository on the first run.

![Repository prompt](https://i.imgur.com/hlNmFhn.png)

In OBS, add a window capture for the Git Line Stats Widget. Then, apply a chroma key filter, and use the eye dropper on the background color of the window. You may need to play with the "similarity" slider to make it look right.

![Chroma Key Settings](https://i.imgur.com/mCgZWf7.png)

You may also need to add a crop filter to remove the window border depending on platform.

# Advanced Usage

## Reading from file
If want to customize things more than Tkinter's limited selection of fonts, you can export diff stats to text files and read them in OBS.

### In settings.json
Change the "enabled" property of `"changed_files_file"`, `"plus_lines_file"`, and `"minus_lines_file"` to `true`. Run the app to generate the files.
```json
  "changed_files_file": {
    "enabled": true,
    ...
  },
  "plus_lines_file": {
    "enabled": true,
    ...
  },
  "minus_lines_file": {
    "enabled": true,
    ...
  }
```
In OBS, add a Text source.

![Adding a text source in OBS](https://i.imgur.com/GcMgIr6.png)

In the properties of the text source, check "Read from file" and Browse and select the .txt file generated by the app.

![Text source settings](https://i.imgur.com/Btv0M73.png)

Repeat for the other two text files, and customize as desired.

You'll likely also want to disable the GUI window if you're using text files instead:
```json
  "window": {
    "enabled": false,
    ...                     
  },
```


## Multiple repositories
Edit `settings.json` and add additional repositories to the "repo" property.
```json
"repo": [
    "C:/Projects/mycoolrepository",
    "C:/Projects/mycoolrepository/mycoolsubmodule",
    "C:/Projects/myotherrepository"
]
```
You **must** use forward slashes `/` or double backslashes `\\` for the path separators.

## Count lines in untracked files
Git won't report insertions from untracked files (i.e. files that haven't been committed yet). If you wish to include these, you can enable it here:

```json
"include_untracked_files": true
```

Note that this feature requires reading the untracked files when they are added or changed, so it may be intensive on CPU and disk resources at those times. If you have issues, turn this feature off.

## All settings
```json
{
  "repo": [                           # List of repositories to track
    "C:/Path/To/Repository1",         # Example repository path
    "C:/Path/To/Repository2"          # Example repository path
  ],
  "refresh_rate": 5,                  # Update the diff stats once every "refresh_rate" seconds
  "include_untracked_files": false,   # Count insertions from files untracked by git (i.e. new files that haven't been committed yet)
  "window": {                         # GUI window settings
    "enabled": true,                  # Show window
    "title": "Git Line Stats Widget", # Set window title (appears in OBS)
    "background": "#00FFFF",          # Background color of window. Most HTML color codes are valid.
    "geometry": "500x100",            # Inner geometry of window in pixels. Make this large enough to contain the text.
    "layout": "horizontal",           # The layout of the elements on screen. Valid options: "horizontal", "vertical", "stacked"
    "pad": 10                         # Padding between GUI elements
  },
  "separator": {     # Label inserted between elements of the stats
    "text": " | ",   # Text of the label; can be an empty string "" or a space " " or any other text
    "font": "Arial", # Font. Most HTML-safe fonts will work
    "size": 25,      # Font size
    "color": "black" # Color of the text. Most HTML color codes are valid
  },
  "changed_files": {     # GUI element representing the files changed stat
    "enabled": true,     # Show this stat
    "font": "Arial",     # Font. Most HTML-safe fonts will work
    "size": 25,          # Font size
    "color": "black",    # Color of the text. Most HTML color codes are valid
    "number_only": false # Only print the number of changes without extra text
  },
  "plus_lines": {        # GUI element representing the insertions stat
    "enabled": true,     # Show this stat
    "font": "Arial",     # Font. Most HTML-safe fonts will work
    "size": 25,          # Font size
    "color": "green",    # Color of the text. Most HTML color codes are valid
    "number_only": false # Only print the number of changes without extra text
  },
  "minus_lines": {       # GUI element representing the deletions stat
    "enabled": true,     # Show this stat
    "font": "Arial",     # Font. Most HTML-safe fonts will work
    "size": 25,          # Font size
    "color": "red",      # Color of the text. Most HTML color codes are valid
    "number_only": false # Only print the number of changes without extra text
  },
  "changed_files_file": {        # Text file representing the files changed stat
    "enabled": false,            # Write this stat to a file
    "path": "changed_files.txt", # Path to the file that this stat will be written to
    "number_only": false         # Only print the number of changes without extra text
  },
  "plus_lines_file": {        # Text file representing the insertions stat
    "enabled": false,         # Write this stat to a file
    "path": "plus_lines.txt", # Path to the file that this stat will be written to
    "number_only": false      # Only print the number of changes without extra text
  },
  "minus_lines_file": {        # Text file representing the deletions stat
    "enabled": false,          # Write this stat to a file
    "path": "minus_files.txt", # Path to the file that this stat will be written to
    "number_only": false       # Only print the number of changes without extra text
  }
}
```