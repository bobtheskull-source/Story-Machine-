from __future__ import annotations

from pathlib import Path

from .core import StoryMachine


def _prompt(label: str) -> str:
    return input(label).strip()


def _print_scene(game: StoryMachine, scene_id: str) -> None:
    scene = game.scenes[scene_id]
    print(f"\n[{scene_id}] {scene.text}")
    if scene.choices:
        for i, choice in enumerate(scene.choices, start=1):
            suffix = f" ({choice.trigger})" if choice.trigger else ""
            print(f"  {i}. {choice.text} -> {choice.target_scene}{suffix}")


def _menu_story(game: StoryMachine) -> None:
    scene_id = _prompt("Scene ID: ").upper()
    text = _prompt("Scene text: ")
    game.add_scene(scene_id, text)
    print(f"Saved scene {scene_id}")


def _menu_dictionary(game: StoryMachine) -> None:
    category = _prompt("Category (verbs/nouns/articles): ").lower()
    word = _prompt("Word to add: ")
    game.add_word(category, word)
    print(f"Added {word.upper()} to {category}")


def _menu_story_disk(game: StoryMachine) -> StoryMachine:
    print("1) Save story disk")
    print("2) Load story disk")
    choice = _prompt("> ")
    if choice == "1":
        path = Path(_prompt("Save path (e.g. story_disk.json): ") or "story_disk.json")
        game.save(path)
        print(f"Saved to {path}")
        return game
    if choice == "2":
        path = Path(_prompt("Load path: ") or "story_disk.json")
        loaded = StoryMachine.load(path)
        print(f"Loaded {loaded.title} from {path}")
        return loaded
    return game


def _menu_game_choices(game: StoryMachine) -> None:
    from_scene = _prompt("From scene ID: ").upper()
    text = _prompt("Choice text: ")
    to_scene = _prompt("Target scene ID: ").upper()
    trigger = _prompt("Trigger command (optional, e.g. GO FOREST): ")
    game.add_choice(from_scene, text, to_scene, trigger=trigger or None)
    print("Choice added")


def _menu_play(game: StoryMachine) -> None:
    print("Play mode. Type HELP, LOOK, CHOOSE <n>, or VERB NOUN. Type EXIT to return.")
    current = "START"
    while True:
        _print_scene(game, current)
        cmd = _prompt("\nCommand> ")
        if cmd.upper() == "EXIT":
            return
        if cmd.upper() == "LOOK":
            continue
        if cmd.upper() == "HELP":
            print("Use CHOOSE <number> or a dictionary command like GO FOREST")
            continue
        current = game.resolve_command(current, cmd)


def main() -> None:
    print("Story Machine Modern (Python Edition)")
    title = _prompt("Project title: ") or "Story Machine Modern"
    game = StoryMachine.new_project(title)

    while True:
        print("\n1) Write Story")
        print("2) Dictionary")
        print("3) Story Disk")
        print("4) Game Choices")
        print("5) Play")
        print("0) Exit")

        selection = _prompt("> ")
        if selection == "1":
            _menu_story(game)
        elif selection == "2":
            _menu_dictionary(game)
        elif selection == "3":
            game = _menu_story_disk(game)
        elif selection == "4":
            _menu_game_choices(game)
        elif selection == "5":
            _menu_play(game)
        elif selection == "0":
            print("Goodbye.")
            return
        else:
            print("Unknown option")


if __name__ == "__main__":
    main()
