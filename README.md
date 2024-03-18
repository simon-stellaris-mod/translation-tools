# translation-tools

Translation tools for stellaris. This tool is used to help create a translation mod of another mod or mods.

![Screenshot](https://github.com/simon-stellaris-mod/translation-tools/blob/main/doc/screenshot.jpg?raw=true)

## Usage

1. Prepare your python environment
2. Start server with **CORRECT** arguments
3. Do your translation job, save and build

**Python environment**

- Tested in python 3.11.7
- Run `pip3 install -r requirements.txt`

**How to start server**

Run `python3 ./web/server.py ....` with following arguments:

- **--name**: The name of this translation, used when building stellaris localisation files. Use source mod name (or a short name) is a good practice
- **--source-path**: The path of source mod's localisation directory or file. Usually the localisation directory of a mod or a sub directory of a specific language. You can specify multiple directories or files.
- **--data-file**: The local data file which stores all translations, actually a json file.
- **--output-path**: The output directory path, usually the localisation directory of your translation mod
