import tempfile
import unittest
from pathlib import Path

from story_machine_modern.core import StoryMachine


class StoryMachineTests(unittest.TestCase):
    def test_new_project_has_default_dictionary_and_start_scene(self):
        game = StoryMachine.new_project("Demo")

        self.assertEqual(game.title, "Demo")
        self.assertIn("LOOK", game.dictionary["verbs"])
        self.assertIn("HELP", game.dictionary["verbs"])
        self.assertIn("START", game.scenes)

    def test_can_add_scene_choice_and_traverse_by_choose_command(self):
        game = StoryMachine.new_project("Demo")
        game.add_scene("FOREST", "You stand at the forest edge.")
        game.add_choice("START", "Walk into the forest", "FOREST", trigger="GO FOREST")

        next_scene = game.resolve_command("START", "CHOOSE 1")

        self.assertEqual(next_scene, "FOREST")

    def test_can_traverse_by_verb_noun_command_when_dictionary_allows_it(self):
        game = StoryMachine.new_project("Demo")
        game.add_scene("FOREST", "You stand at the forest edge.")
        game.add_word("verbs", "GO")
        game.add_word("nouns", "FOREST")
        game.add_choice("START", "Walk into the forest", "FOREST", trigger="GO FOREST")

        next_scene = game.resolve_command("START", "go forest")

        self.assertEqual(next_scene, "FOREST")

    def test_save_and_load_roundtrip_preserves_story_content(self):
        game = StoryMachine.new_project("Demo")
        game.add_word("verbs", "TAKE")
        game.add_word("nouns", "LANTERN")
        game.add_scene("CAVE", "It is dark and quiet.")
        game.add_choice("START", "Enter cave", "CAVE", trigger="GO CAVE")

        with tempfile.TemporaryDirectory() as td:
            save_path = Path(td) / "story_disk.json"
            game.save(save_path)

            loaded = StoryMachine.load(save_path)

            self.assertEqual(loaded.title, "Demo")
            self.assertIn("TAKE", loaded.dictionary["verbs"])
            self.assertIn("LANTERN", loaded.dictionary["nouns"])
            self.assertEqual(loaded.scenes["CAVE"].text, "It is dark and quiet.")
            self.assertEqual(loaded.scenes["START"].choices[0].target_scene, "CAVE")


if __name__ == "__main__":
    unittest.main()
