# Git Line Stats Widget

A small GUI widget for displaying how many lines have changed in a git repo. Used for programming streams.

![Screenshot of widget](https://i.imgur.com/m2lhlCj.png)

Fonts and colors can be configured via `settings.json`.

# Prerequisites

You need Python3 installed. On Windows, tkinter should come with Python. On other platforms you may need to do `pip install tk`.

You'll also need git installed and on the PATH, which you presumably should already if you have a git repository.

# Usage

Download and extract the repository (click the green "Code" button -> "Download as zip").

Edit `settings.json` and at minimum change the `"repo"` property to the path to the repository you want to track. E.g.:
```
"repo": "C:/Projects/mycoolrepository"
```

Launch the widget using `python git_linestats_widget.py` or by double clicking `launch.bat` on Windows.

In OBS, add a window capture for the Git Line Stats Widget. Then, apply a chroma key filter, and set the color to the color you chose for `background` in the settings.
