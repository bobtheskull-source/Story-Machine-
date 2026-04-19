Story Machine Modern (Python)

A modern rewrite of the original DOS Story Machine image found in `Story-Machine_DOS_EN.zip`.

This remake preserves the original workflow concept:
- Write Story
- Dictionary
- Story Disk (save/load)
- Game Choices
- Play

Implemented as a Python 3 CLI with JSON persistence.

Web test build (GitHub Pages):

https://bobtheskull-source.github.io/Story-Machine-/

Local CLI run:

python3 -m story_machine_modern.cli

CLI tests:

python3 -m unittest tests/test_story_machine.py -v
