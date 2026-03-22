"""
================================================================================
FILE: src/models/project.py
================================================================================

╔══════════════════════════════════════════════════════════════════════════════╗
║         🎓 FAANG-LEVEL LESSON: AGGREGATE ROOT & PROJECT MANAGEMENT          ║
╚══════════════════════════════════════════════════════════════════════════════╝

WHAT IS THIS FILE?
──────────────────
A Project is the top-level container for your content. Every episode,
every series, every batch of content is a PROJECT.

In Domain-Driven Design (DDD) — used at Amazon, Google, Netflix — a
Project is called an "Aggregate Root." It's the ENTRY POINT to a cluster
of related objects.

Your hierarchy:
    Project (root)
    └── Episode
        └── Scene (5-10 scenes per episode)
            └── SceneCharacter (1-2 per scene)
                └── Character (defined in character.py)

WHY DO YOU NEED THIS?
──────────────────────
Right now your workflow is:
  - "Mango and Cherry beach scene" (some files somewhere?)
  - "Zipline host intro" (in another folder?)
  - Forget which prompt belongs to which scene

With a Project:
  project = Project.load("fruit_love_island_ep1")
  print(project.get_all_scenes())          # Every scene in order
  print(project.get_character_scenes("mango_man"))  # All Mango scenes
  project.export_all_prompts()             # Dump every prompt to a folder


WHAT IS AN "AGGREGATE ROOT" IN FAANG ENGINEERING?
────────────────────────────────────────────────────
An Aggregate is a cluster of objects treated as a single unit.
The "root" is the main object you interact with.

  → You don't directly create/delete Scenes without going through Project
  → Project.add_scene(scene) is the correct API
  → This keeps data consistent

Netflix's content system organizes: Show → Season → Episode → Scene
Your system organizes: Project → Episode → Scene → Character

Same pattern. Different domain.


WHAT IS A PROPERTY DECORATOR?
──────────────────────────────
@property makes a method callable WITHOUT parentheses:

  class Project:
      @property
      def total_scenes(self):
          return len(self.scenes)

  proj.total_scenes    # ✅ No parentheses needed
  proj.total_scenes()  # ❌ This will fail

Use @property when:
  - The value is computed from other data
  - You want it to look like an attribute but BE a method
  - The value might change (it recalculates each time)


WHAT IS A SETTER?
──────────────────
A @property.setter allows you to control what happens when you SET a value:

  @property
  def status(self):
      return self._status

  @status.setter
  def status(self, value):
      valid = ["active", "completed", "archived"]
      if value not in valid:
          raise ValueError(f"Status must be one of {valid}")
      self._status = value

Now: project.status = "active"   → Works fine
    project.status = "DONE"      → Raises ValueError ← Catches bugs early


WHAT IS __len__ AND __iter__? (Magic Methods / Dunder Methods)
────────────────────────────────────────────────────────────────
Python has special "dunder" (double-underscore) methods that make
your objects work with built-in functions.

  __len__:  Called when you do len(project)
  __iter__: Called when you do for scene in project:
  __str__:  Called when you do print(project)
  __repr__: Called in the REPL/debugger

This is how Python's built-in types (list, dict, str) work internally.
By implementing these, your objects behave "naturally" in Python code.

  project = Project(...)
  len(project)           # How many scenes?
  for scene in project:  # Iterate over scenes
      print(scene)

FAANG engineers implement these for any "container" class.


THE DIFFERENCE BETWEEN save() AND export():
────────────────────────────────────────────
save():   Persist internal state to disk (for loading later)
          → assets/projects/fruit_ep1/project.json
          → Used for your own system's state management

export(): Produce human-readable output files
          → exports/fruit_ep1_all_prompts.txt
          → Used for YOUR actual copy-paste workflow

Keep these separate. save() = system state. export() = user output.

================================================================================
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional, List


# ─────────────────────────────────────────────────────────────────────────────
# TODO 1: Understand how Project contains Scenes
#   - A Project is a list of scene IDs, NOT the full Scene objects
#   - Why? To avoid storing duplicate data
#   - Real scenes are stored in assets/scenes/{project}/{scene_id}/
#
# TODO 2: Add a method called "get_scene_count_by_type()"
#   - Returns a dict like {"flirt": 4, "host_intro": 2}
#   - Hint: Loop through scene metadata and count by type
#
# TODO 3: Add a method called "generate_script()"
#   - Returns a formatted string of all dialogue in scene order
#   - Format: "Scene 1 [Mango]: 'It hits different.'\nScene 2 [Cherry]: '...'"
#
# TODO 4: Add a class method called "list_all()" that finds all project
#   JSON files in "assets/projects/" and returns their slugs
#
# TODO 5: Add a "__contains__" method so you can do: "S001" in project
# ─────────────────────────────────────────────────────────────────────────────


# ═══════════════════════════════════════════════════════════════════════════
# FULL CODE (try it yourself first!)
# ═══════════════════════════════════════════════════════════════════════════

# @dataclass
# class Project:
#     """
#     Top-level container for a content project.
#
#     Think of it as a "production folder" — it tracks:
#     - All scenes in this project (in order)
#     - All characters involved
#     - The series/show this belongs to
#     - Export history
#
#     Example usage:
#         project = Project(
#             name="Fruit Love Island Episode 1",
#             slug="fruit_ep1",
#             description="Beach flirt scene between Mango and Chocolate Cherry"
#         )
#         project.add_scene_id("S001")
#         project.add_scene_id("S002")
#         project.save()
#     """
#
#     # ── IDENTITY ─────────────────────────────────────────────────────────────
#     name: str                          # "Fruit Love Island Episode 1"
#     slug: str                          # "fruit_ep1" (no spaces, URL-safe)
#
#     # ── CONTENT TRACKING ──────────────────────────────────────────────────────
#     # List of scene IDs in order ["S001", "S002", "S003"]
#     # Not full Scene objects — just the IDs (foreign key pattern from databases)
#     scene_ids: List[str] = field(default_factory=list)
#
#     # List of character slugs in this project
#     character_slugs: List[str] = field(default_factory=list)
#
#     # ── PROJECT INFO ─────────────────────────────────────────────────────────
#     description: str = ""
#     series: str = ""                   # "Fruit Love Island" (the show name)
#     episode_number: Optional[int] = None
#
#     # ── WORKFLOW STATUS ───────────────────────────────────────────────────────
#     # "active", "completed", "archived"
#     status: str = "active"
#
#     # Total number of scenes planned for this project
#     planned_scene_count: int = 0
#
#     # ── TIMESTAMPS ───────────────────────────────────────────────────────────
#     created_at: str = field(default_factory=lambda: datetime.now().isoformat())
#     updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
#
#     # ─────────────────────────────────────────────────────────────────────────
#     # PROPERTIES (computed attributes)
#     # ─────────────────────────────────────────────────────────────────────────
#
#     @property
#     def total_scenes(self) -> int:
#         """How many scenes have been added to this project."""
#         return len(self.scene_ids)
#
#     @property
#     def completion_percentage(self) -> float:
#         """What % of planned scenes are done. Returns 0.0 if nothing planned."""
#         if self.planned_scene_count == 0:
#             return 0.0
#         return round((self.total_scenes / self.planned_scene_count) * 100, 1)
#
#     @property
#     def base_dir(self) -> Path:
#         """The project's folder on disk."""
#         return Path("assets/projects") / self.slug
#
#     # ─────────────────────────────────────────────────────────────────────────
#     # MANAGEMENT METHODS
#     # ─────────────────────────────────────────────────────────────────────────
#
#     def add_scene_id(self, scene_id: str) -> None:
#         """Add a scene ID to this project (if not already in it)."""
#         if scene_id not in self.scene_ids:
#             self.scene_ids.append(scene_id)
#             self.updated_at = datetime.now().isoformat()
#
#     def remove_scene_id(self, scene_id: str) -> bool:
#         """Remove a scene from this project. Returns True if removed."""
#         if scene_id in self.scene_ids:
#             self.scene_ids.remove(scene_id)
#             self.updated_at = datetime.now().isoformat()
#             return True
#         return False
#
#     def add_character_slug(self, slug: str) -> None:
#         """Register a character as part of this project."""
#         if slug not in self.character_slugs:
#             self.character_slugs.append(slug)
#
#     def reorder_scenes(self, new_order: List[str]) -> None:
#         """
#         Reorder scenes to match new_order list.
#         Raises ValueError if new_order doesn't contain the same scene IDs.
#         """
#         if set(new_order) != set(self.scene_ids):
#             raise ValueError("new_order must contain the exact same scene IDs")
#         self.scene_ids = new_order
#         self.updated_at = datetime.now().isoformat()
#
#     def export_prompts(self, output_dir: str = "exports") -> Path:
#         """
#         Export all scene prompts to a single text file for easy copy-paste.
#
#         This is your "production day" tool. Run this before a work session
#         and you have every prompt ready in one file.
#
#         Each prompt is labeled with its scene number and type.
#         """
#         output_path = Path(output_dir) / f"{self.slug}_prompts.txt"
#         output_path.parent.mkdir(parents=True, exist_ok=True)
#
#         lines = [
#             f"{'='*70}",
#             f"PROJECT: {self.name}",
#             f"SCENES: {self.total_scenes} / {self.planned_scene_count or '?'}",
#             f"EXPORTED: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
#             f"{'='*70}",
#             "",
#         ]
#
#         for i, scene_id in enumerate(self.scene_ids, 1):
#             prompt_path = (
#                 Path("assets/scenes") / self.slug / scene_id / "video_prompt.txt"
#             )
#             if prompt_path.exists():
#                 lines.append(f"{'─'*70}")
#                 lines.append(f"SCENE {i} | ID: {scene_id}")
#                 lines.append(f"{'─'*70}")
#                 lines.append(prompt_path.read_text(encoding="utf-8"))
#                 lines.append("")
#             else:
#                 lines.append(f"[SCENE {scene_id}: No prompt generated yet]")
#                 lines.append("")
#
#         output_path.write_text("\n".join(lines), encoding="utf-8")
#         print(f"✅ Prompts exported: {output_path}")
#         return output_path
#
#     # ─────────────────────────────────────────────────────────────────────────
#     # MAGIC METHODS
#     # ─────────────────────────────────────────────────────────────────────────
#
#     def __len__(self) -> int:
#         """len(project) returns scenes count."""
#         return self.total_scenes
#
#     def __contains__(self, scene_id: str) -> bool:
#         """'S001' in project → True/False"""
#         return scene_id in self.scene_ids
#
#     def __repr__(self) -> str:
#         return (
#             f"Project(name={self.name!r}, scenes={self.total_scenes}, "
#             f"status={self.status!r}, completion={self.completion_percentage}%)"
#         )
#
#     # ─────────────────────────────────────────────────────────────────────────
#     # PERSISTENCE
#     # ─────────────────────────────────────────────────────────────────────────
#
#     def save(self) -> Path:
#         """Save project metadata to disk."""
#         import dataclasses
#         self.updated_at = datetime.now().isoformat()
#         self.base_dir.mkdir(parents=True, exist_ok=True)
#         json_path = self.base_dir / "project.json"
#         with open(json_path, "w", encoding="utf-8") as f:
#             json.dump(dataclasses.asdict(self), f, indent=2, ensure_ascii=False)
#         print(f"✅ Project saved: {json_path}")
#         return json_path
#
#     @classmethod
#     def load(cls, slug: str, base_dir: str = "assets/projects") -> "Project":
#         """Load a project from disk by slug."""
#         json_path = Path(base_dir) / slug / "project.json"
#         if not json_path.exists():
#             raise FileNotFoundError(f"Project '{slug}' not found at {json_path}")
#         with open(json_path, "r", encoding="utf-8") as f:
#             data = json.load(f)
#         return cls(**data)
#
#     @classmethod
#     def list_all(cls, base_dir: str = "assets/projects") -> List[str]:
#         """Return slugs of all saved projects."""
#         base = Path(base_dir)
#         if not base.exists():
#             return []
#         return [
#             d.name for d in base.iterdir()
#             if d.is_dir() and (d / "project.json").exists()
#         ]
