# Stomp
A game where you can experience what it's like to be that bug you crushed!

Use A/D to move left and right, and avoid the people trying to crush you. It's quite simple, really.

# Running on MacOS
There seems to be an issue with the MacOS releases, which cause the operating system to refuse to open the .app file.
Luckily you can use a single command in the terminal to fix this!

Simply run:
```
xattr -d com.apple.quarantine <path_to_app_file>
```
Make sure to replace "<path_to_app_file>" with a valid path which points to the .app file you were given after you unzipped the zip file.
You might need to surround your path with quotation marks, like this:
"<path_to_app_file>"

# Running from source
To run the source code, you'll need to have python installed, as well as the pygame-ce module.
After installing python, pygame-ce can be installed by running the following command in a terminal:
```
pip3 install pygame-ce
```
If that doesn't work, try just "pip" rather than "pip3"

After installed everything, just run the main.py script from a terminal by doing the following command:
```
python3 <path_to_main.py_script>
```
You might need to replace "python3" with just "python".
