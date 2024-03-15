# Git Line Stats Widget

A small GUI widget for displaying how many lines have changed in a git repo. Used for programming streams.

![Screenshot of widget in horizontal layout](https://i.imgur.com/W8tUybp.png)
![Screenshot of widget in stacked layout](https://i.imgur.com/bavyUnQ.png)

Fonts and colors can be configured via `settings.json`. Most HTML fonts and color codes will work.

# Prerequisites

You need Python3 installed (and on the PATH, if launching via batch file).

On Windows, tkinter should come with Python. On other platforms you may need to do `pip install tk`.

You'll also need git installed and on the PATH, which you presumably should already if you have a git repository.

# Usage

Download and extract the repository (click the green "Code" button -> "Download as zip").

Edit `settings.json` and at minimum change the `"repo"` property to the path to the repository you want to track. E.g.:
```
"repo": "C:/Projects/mycoolrepository"
```
You **must** use forward slashes `/` or double backslashes `\\` for the path separators.

Launch the widget using `python git_linestats_widget.py` or by double clicking `launch.bat` on Windows.

In OBS, add a window capture for the Git Line Stats Widget. Then, apply a chroma key filter, and set the color to the color you chose for `background` in the settings.
