
# Eu4 Save Map

Converts an EU4 save game to a high quality cool looking map to share with friends. 

Python 3.12 is recommended for using this.

## Features

- Custom map mod support
- Choose a range of map effects
- Add all great powers to the map
- Include all subject nations
- Selectively pick tags to add to the map
## Usage

This will compile your provinces.bmp and definition.csv into a usable cross-platform map json file. This will also work with modded maps.
```bash
python3 main.py generate --provinces pathtoprovinces.bmp --definitions pathtodefinition.csv
```
This will paint your map using the given tag and save game file.
```bash
python3 main.py paint --tag NATIONTAG pathtosavefile.eu4
```
