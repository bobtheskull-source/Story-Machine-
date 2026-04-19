from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import json


@dataclass
class Choice:
    text: str
    target_scene: str
    trigger: str | None = None

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "target_scene": self.target_scene,
            "trigger": self.trigger,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Choice":
        return cls(
            text=data["text"],
            target_scene=data["target_scene"],
            trigger=data.get("trigger"),
        )


@dataclass
class Scene:
    text: str
    choices: list[Choice] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "choices": [c.to_dict() for c in self.choices],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Scene":
        return cls(
            text=data["text"],
            choices=[Choice.from_dict(c) for c in data.get("choices", [])],
        )


@dataclass
class StoryMachine:
    title: str
    dictionary: dict[str, set[str]]
    scenes: dict[str, Scene]

    @classmethod
    def new_project(cls, title: str) -> "StoryMachine":
        dictionary = {
            "verbs": {"LOOK", "HELP", "CHOOSE", "GO"},
            "nouns": {"START"},
            "articles": {"A", "AN", "THE"},
        }
        scenes = {
            "START": Scene(
                text="You are at the beginning of your story.",
                choices=[],
            )
        }
        return cls(title=title, dictionary=dictionary, scenes=scenes)

    def add_word(self, category: str, word: str) -> None:
        key = category.lower().strip()
        if key not in self.dictionary:
            raise ValueError(f"Unknown dictionary category: {category}")
        normalized = word.strip().upper()
        if not normalized:
            return
        self.dictionary[key].add(normalized)

    def add_scene(self, scene_id: str, text: str) -> None:
        sid = scene_id.strip().upper()
        if not sid:
            raise ValueError("scene_id cannot be empty")
        self.scenes[sid] = Scene(text=text.strip())
        self.dictionary["nouns"].add(sid)

    def add_choice(self, from_scene: str, text: str, to_scene: str, trigger: str | None = None) -> None:
        source = from_scene.strip().upper()
        target = to_scene.strip().upper()
        if source not in self.scenes:
            raise ValueError(f"Unknown source scene: {source}")
        if target not in self.scenes:
            raise ValueError(f"Unknown target scene: {target}")
        normalized_trigger = trigger.strip().upper() if trigger and trigger.strip() else None
        self.scenes[source].choices.append(
            Choice(text=text.strip(), target_scene=target, trigger=normalized_trigger)
        )

    def resolve_command(self, current_scene: str, command: str) -> str:
        scene_id = current_scene.strip().upper()
        if scene_id not in self.scenes:
            raise ValueError(f"Unknown current scene: {scene_id}")

        cmd = command.strip().upper()
        if not cmd:
            return scene_id

        if cmd.startswith("CHOOSE "):
            maybe_index = cmd.split(maxsplit=1)[1]
            if maybe_index.isdigit():
                idx = int(maybe_index) - 1
                choices = self.scenes[scene_id].choices
                if 0 <= idx < len(choices):
                    return choices[idx].target_scene
                return scene_id

        parts = [p for p in cmd.split() if p]
        if len(parts) >= 2:
            verb, noun = parts[0], parts[1]
            if verb in self.dictionary["verbs"] and noun in self.dictionary["nouns"]:
                trigger = f"{verb} {noun}"
                for choice in self.scenes[scene_id].choices:
                    if choice.trigger and choice.trigger.upper() == trigger:
                        return choice.target_scene

        return scene_id

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "dictionary": {k: sorted(v) for k, v in self.dictionary.items()},
            "scenes": {sid: scene.to_dict() for sid, scene in self.scenes.items()},
        }

    @classmethod
    def from_dict(cls, data: dict) -> "StoryMachine":
        return cls(
            title=data["title"],
            dictionary={k: set(v) for k, v in data["dictionary"].items()},
            scenes={sid: Scene.from_dict(scene_data) for sid, scene_data in data["scenes"].items()},
        )

    def save(self, path: str | Path) -> Path:
        save_path = Path(path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")
        return save_path

    @classmethod
    def load(cls, path: str | Path) -> "StoryMachine":
        load_path = Path(path)
        data = json.loads(load_path.read_text(encoding="utf-8"))
        return cls.from_dict(data)
