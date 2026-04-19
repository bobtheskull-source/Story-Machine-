Story Machine Modern (Python)

A modern rewrite of the original DOS Story Machine image found in `Story-Machine_DOS_EN.zip`.

This remake preserves the original workflow concept:
- Write Story
- Dictionary
- Story Disk (save/load)
- Game Choices
- Play

Implemented as a Python 3 CLI with JSON persistence.

Run:

python3 -m story_machine_modern.cli

Test:

python3 -m unittest tests/test_story_machine.py -v
