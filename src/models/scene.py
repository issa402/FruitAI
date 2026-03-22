"""
================================================================================
FILE: src/models/scene.py
================================================================================

╔══════════════════════════════════════════════════════════════════════════════╗
║           🎓 FAANG-LEVEL LESSON: RELATIONSHIPS BETWEEN OBJECTS              ║
╚══════════════════════════════════════════════════════════════════════════════╝

WHAT IS THIS FILE?
──────────────────
A Scene is the "unit of work" in your AI content pipeline. Every 6-second
clip you create IS a Scene. This file models that.

Think of it like a movie production system:
  - Character = Actor (defined in character.py)
  - Scene = A shot in the film (defined HERE)
  - Project = The full episode (ties scenes together)

A Scene REFERENCES Characters — it doesn't own them. This is a fundamental
concept in software engineering called:

  "HAS-A vs IS-A Relationship"

  Scene HAS-A Character (composition — contained reference)
  HostCharacter IS-A Character (inheritance — extended type)

A scene has multiple characters, each with a role in that specific shot.


WHAT IS COMPOSITION? (The most important OOP pattern at FAANG)
──────────────────────────────────────────────────────────────
Composition = "Build complex things from simpler parts"

  Scene → contains → List[SceneCharacter]
  SceneCharacter → references → Character
  Scene → produces → List[str] (prompts)

This is better than inheritance in most cases. Google's engineering guide
literally says "Favor composition over inheritance." Why?
  - Inheritance creates tight coupling (change parent = breaks child)
  - Composition is flexible (swap out parts without breaking anything)

In your project:
  - A Scene can contain 0, 1, or 2 characters
  - Each character in a scene has a ROLE (speaking, listening, absent)
  - This is the SAME structure Netflix uses for "who appears in episode X"


HOW SCENE CONTINUITY WORKS (Your Biggest Pain Point):
───────────────────────────────────────────────────────
You manually screenshot the last frame of a video to continue it.
This Scene class TRACKS that automatically:

  scene.set_continuation_frame(path_to_screenshot)
  next_scene = scene.create_continuation()
  print(next_scene.generate_continuation_prompt())
  # → Outputs a prompt that starts right where Scene 1 ended

The system remembers:
  - What the last frame looked like (path to screenshot)
  - Who was speaking and what they said
  - What environment they were in
  - What camera position was locked

This eliminates your manual "screenshot → upscale → paste" workflow.


WHAT IS AN ENUM?
────────────────
Enum (Enumeration) = A fixed set of named constants.

Instead of strings like:
  scene.status = "draft"     # Could typo as "DRAFT", "Draft", "draf"

Use an Enum:
  scene.status = SceneStatus.DRAFT   # Only valid values possible
  # Python will throw an error if you try an invalid value

This is how FAANG companies prevent hard-to-debug typo bugs.
Django (Python web framework used by Instagram) uses enums everywhere.


WHAT IS Optional vs List TYPE HINTS?
──────────────────────────────────────
Optional[X] = "This value is either X or None"
  - Optional[str] = it's either a string, or it hasn't been set yet

List[X] = "This is a list containing items of type X"
  - List[Character] = a list of Character objects

These hints don't ENFORCE types at runtime (Python is dynamic), but:
  1. Your IDE shows errors before you run the code
  2. Other developers instantly understand what a function expects
  3. Tools like mypy can verify types across the whole codebase

Google's Python Style Guide REQUIRES type hints for all public functions.


WHAT IS A DATACLASS WITH __post_init__?
────────────────────────────────────────
When you use @dataclass, Python auto-generates __init__ for you.
But sometimes you need to run code AFTER the initial assignment.

  @dataclass
  class Scene:
      characters: list = field(default_factory=list)
      scene_id: str = None

      def __post_init__(self):
          # This runs AFTER __init__
          if self.scene_id is None:
              self.scene_id = generate_unique_id()  # Auto-assign ID

This is the standard pattern. __post_init__ is for:
  - Validation (raise error if invalid data)
  - Auto-computation (calculate derived fields)
  - Default generation (assign IDs, timestamps)


THE PATTERN OF "scene_id":
────────────────────────────
Every entity in a FAANG system has a globally unique ID. This allows:
  - Database lookups: "Find scene with id='S001'"
  - Cross-references: "Character X appeared in scenes ['S001', 'S003']"
  - Naming files automatically: "assets/scenes/S001/prompt.txt"

For now you use simple incremental IDs ("S001", "S002").
In production, systems use UUID4 (universally unique random IDs).

================================================================================
"""

import json
import dataclasses
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, List


# ─────────────────────────────────────────────────────────────────────────────
# TODO 1: Understand the Enum class
#   - Create a new Enum called "CameraPosition" with values:
#     LOCKED, SLOW_ZOOM_IN, PAN_RIGHT
#   - Add a camera_position field to the Scene class that uses this Enum
#
# TODO 2: Add a field "environment" to Scene (str, default "beach at sunset")
#   - This should be included in generated prompts
#
# TODO 3: Add a method "add_character(character)" that appends a Character
#   to the scene's character list
#
# TODO 4: Write a method "generate_scene_folder_name()" that returns:
#   "scene_001_flirt" for scene_number=1, scene_type="flirt"
#
# TODO 5: Write a method "get_speaker()" that returns the Character who
#   is currently set as the speaker (hint: iterate self.characters and
#   find the one with role="speaker")
# ─────────────────────────────────────────────────────────────────────────────


# ═══════════════════════════════════════════════════════════════════════════
# FULL CODE (try it yourself first!)
# ═══════════════════════════════════════════════════════════════════════════

# class SceneStatus(Enum):
#     """
#     Enum for tracking where a scene is in the production pipeline.
#
#     Using an Enum prevents typo bugs ("draff" vs "draft").
#     Each value in the Enum has a .value (the string) and .name (the key).
#
#     Usage:
#         scene.status = SceneStatus.DRAFT
#         if scene.status == SceneStatus.COMPLETED:
#             print("Done!")
#     """
#     DRAFT = "draft"                 # Prompt written, not generated yet
#     GENERATING = "generating"       # Currently being generated by AI
#     REVIEW = "review"               # Generated, needs human review
#     APPROVED = "approved"           # Approved, ready to use
#     COMPLETED = "completed"         # Used in final video
#     NEEDS_REDO = "needs_redo"       # Failed quality check, redo


# class SceneType(Enum):
#     """Categorizes what kind of scene this is for template selection."""
#     FLIRT = "flirt"                 # Two characters flirting (your main scene)
#     DIALOGUE = "dialogue"           # Characters talking (non-flirt)
#     HOST_INTRO = "host_intro"       # Host introducing show/segment
#     ZIPLINE = "zipline"             # Host on zipline (your specific use case)
#     REACTION = "reaction"           # One character reacting to something
#     CONTINUATION = "continuation"  # Extending a previous scene
#     ESTABLISHING = "establishing"   # Wide shot of environment, no dialogue
#     RECREATION = "recreation"       # Recreating a video from a reference


# @dataclass
# class SceneCharacter:
#     """
#     Represents a Character's role IN a specific Scene.
#
#     WHY A SEPARATE CLASS? Why not just List[Character]?
#     Because a character's role changes per scene. Mango Man might be
#     "speaking" in Scene 1 but "listening" in Scene 2. The Character
#     object itself doesn't know its role — that's Scene-specific.
#
#     This pattern is called an "Association Class" or "Junction Object"
#     in database design. It's the same as a user_roles table in SQL.
#     """
#     # Reference to the character's slug (not the full object — just the ID)
#     # We keep it as a string to avoid circular imports and keep JSON simple.
#     character_slug: str
#
#     # Role in this specific scene
#     # "speaker" = this character delivers dialogue
#     # "listener" = reacts only with micro-expressions
#     # "absent" = referenced but not in frame
#     role: str = "listener"  # "speaker", "listener", "absent"
#
#     # The exact dialogue lines this character speaks in THIS scene
#     # Empty string = no dialogue (idle animation only)
#     dialogue: str = ""

#     # Delivery tone override for this specific scene
#     # If empty, will use the Character's voice_assignments dict
#     tone_override: str = ""


# @dataclass
# class Scene:
#     """
#     Represents one 6-second AI-generated video clip.
#
#     This is the central workflow unit. Every prompt you generate,
#     every video you create, every screenshot you take — all tracked here.
#
#     Example usage:
#         scene = Scene(
#             scene_number=1,
#             scene_type=SceneType.FLIRT,
#             environment="beach blanket at sunset, tropical island",
#         )
#         scene.characters = [
#             SceneCharacter("mango_man", role="speaker", dialogue="It hits different."),
#             SceneCharacter("chocolate_cherry", role="listener"),
#         ]
#         print(scene.generate_video_prompt())
#         scene.save()
#     """
#
#     # ── IDENTITY ─────────────────────────────────────────────────────────────
#     # Unique scene identifier. Auto-generated as "S001", "S002", etc.
#     scene_id: Optional[str] = None
#
#     # Human-readable scene number (1, 2, 3...)
#     scene_number: int = 1
#
#     # What kind of scene is this? (flirt, host_intro, zipline, etc.)
#     scene_type: str = SceneType.FLIRT.value
#
#     # Project this scene belongs to
#     # Example: "fruit_love_island_ep1" or "mango_cherry_beach"
#     project_slug: str = "default"
#
#     # ── SCENE CONTENT ────────────────────────────────────────────────────────
#     # Duration is ALWAYS 6 seconds for your AI video generator
#     duration_seconds: int = 6
#
#     # Where the scene takes place
#     environment: str = "beach blanket at sunset, tropical island"
#
#     # Characters in this scene (list of SceneCharacter objects)
#     characters: List[SceneCharacter] = field(default_factory=list)
#
#     # ── PROMPT DATA ───────────────────────────────────────────────────────────
#     # The generated video prompt (None until generate_video_prompt() is called)
#     generated_video_prompt: Optional[str] = None
#
#     # The generated image prompt if this scene needed a new image
#     generated_image_prompt: Optional[str] = None
#
#     # Notes about what needs to happen in this scene
#     director_notes: str = ""
#
#     # ── CONTINUITY ───────────────────────────────────────────────────────────
#     # This is YOUR exact workflow automated:
#     # "I screenshot the last frame to continue the next scene"
#     # Path to the screenshot of the last frame from the PREVIOUS scene
#     continuation_frame_path: Optional[str] = None
#
#     # Was this scene extended from a previous scene?
#     is_continuation: bool = False
#
#     # The scene_id this scene continues from (if is_continuation=True)
#     continues_from_scene_id: Optional[str] = None
#
#     # ── FILE PATHS ───────────────────────────────────────────────────────────
#     # Path to the reference image used for this scene
#     reference_image_path: Optional[str] = None
#
#     # Path to the generated video output
#     video_output_path: Optional[str] = None
#
#     # ── STATUS & TIMESTAMPS ───────────────────────────────────────────────────
#     status: str = SceneStatus.DRAFT.value
#     created_at: str = field(default_factory=lambda: datetime.now().isoformat())
#     updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
#
#     def __post_init__(self):
#         """Auto-generate scene_id if not provided."""
#         if self.scene_id is None:
#             self.scene_id = f"S{self.scene_number:03d}"  # "S001", "S042", etc.
#
#     def get_speaker(self) -> Optional[SceneCharacter]:
#         """Return the character who is speaking in this scene (or None)."""
#         for sc in self.characters:
#             if sc.role == "speaker":
#                 return sc
#         return None
#
#     def get_listeners(self) -> List[SceneCharacter]:
#         """Return all characters who are listening (not speaking)."""
#         return [sc for sc in self.characters if sc.role == "listener"]
#
#     def set_continuation_frame(self, screenshot_path: str) -> None:
#         """
#         Register the screenshot of the last frame from this scene.
#         The next scene will use this to start right where you ended.
#         This automates your manual screenshot workflow.
#         """
#         self.continuation_frame_path = screenshot_path
#         self.updated_at = datetime.now().isoformat()
#         print(f"✅ Continuation frame set: {screenshot_path}")
#
#     def create_continuation(self, new_scene_number: Optional[int] = None) -> "Scene":
#         """
#         Create a new Scene that continues from where this one ended.
#
#         This generates the next scene pre-filled with:
#         - The continuation frame path (your screenshot)
#         - The same environment
#         - The same characters (but listener becomes speaker, speaker becomes listener)
#         - Marked as is_continuation = True
#
#         Returns:
#             Scene: A new Scene ready to fill in the dialogue and generate a prompt.
#         """
#         next_num = new_scene_number or (self.scene_number + 1)
#
#         # Swap speaking roles: if Mango spoke in scene 1, Cherry speaks in scene 2
#         new_characters = []
#         for sc in self.characters:
#             new_role = "listener" if sc.role == "speaker" else "speaker"
#             new_characters.append(SceneCharacter(
#                 character_slug=sc.character_slug,
#                 role=new_role,
#                 dialogue="",  # Director fills this in
#                 tone_override=sc.tone_override,
#             ))
#
#         return Scene(
#             scene_number=next_num,
#             scene_type=self.scene_type,
#             project_slug=self.project_slug,
#             environment=self.environment,
#             characters=new_characters,
#             continuation_frame_path=self.continuation_frame_path,
#             is_continuation=True,
#             continues_from_scene_id=self.scene_id,
#             reference_image_path=self.continuation_frame_path,  # Use the frame!
#         )
#
#     def generate_video_prompt(self, character_descriptions: dict = None) -> str:
#         """
#         Generate the complete 6-second video animation prompt.
#
#         This is the 400-word prompt you manually write every time.
#         Now it's one function call.
#
#         Args:
#             character_descriptions: Optional dict of {slug: description}
#                 for characters you want explicitly described in the prompt.
#                 Leave empty to use "Use ONLY the character in the image."
#
#         Returns:
#             str: Complete, copy-paste-ready video prompt.
#         """
#         character_descriptions = character_descriptions or {}
#         speaker = self.get_speaker()
#
#         # ── HEADER BLOCK (always the same) ──────────────────────────────────
#         lines = [
#             "Use ONLY the provided image exactly as it is. "
#             "Do NOT add new characters, props, fruit, or background elements. "
#             "Do NOT duplicate anything. "
#             "Keep the same art style, colors, lighting, and composition. "
#             f"Animate the scene for {self.duration_seconds} seconds "
#             "in a Love-Island-Fruit-AI style.",
#             "",
#             "Both characters remain in their exact positions.",
#             "Their bodies must NOT shift, slide, stand, or change pose.",
#             "Only natural micro-movements are allowed.",
#             "",
#             "They look directly at each other the entire time — never at the camera.",
#             "",
#             "Add subtle, realistic idle animation:",
#             "- gentle breathing in chest and shoulders",
#             "- soft blinking for both characters",
#             "- tiny facial micro-expressions that match the mood",
#             "- slight head tilts toward each other within original pose",
#             "",
#             "Add soft environment animation:",
#             "- palm trees sway slightly",
#             "- ocean waves move gently",
#             "- warm lighting flickers subtly",
#             "",
#         ]
#
#         # ── DIALOGUE / DELIVERY BLOCK ────────────────────────────────────────
#         if speaker and speaker.dialogue:
#             # Build speaker description
#             if speaker.character_slug in character_descriptions:
#                 speaker_desc = character_descriptions[speaker.character_slug]
#             else:
#                 speaker_desc = "the character"
#
#             lines += [
#                 f"Dialogue + Delivery Style:",
#                 f"For the full {self.duration_seconds} seconds, "
#                 f"ONLY {speaker_desc} speaks.",
#                 f"Tone: {speaker.tone_override or 'natural and controlled'}.",
#                 f"Mouth syncs naturally to the words:",
#                 f"'{speaker.dialogue}'",
#                 "",
#             ]
#
#             # Describe listener reactions
#             listeners = self.get_listeners()
#             if listeners:
#                 listener_names = ", ".join(
#                     character_descriptions.get(l.character_slug, "the other character")
#                     for l in listeners
#                 )
#                 lines.append(
#                     f"{listener_names} reacts only with subtle micro-expressions: "
#                     "a small smile, a slow blink — nothing more."
#                 )
#         else:
#             lines += [
#                 "No dialogue. No subtitles. No voiceover.",
#                 "Only natural idle animation.",
#             ]
#
#         # ── FOOTER BLOCK (always the same) ───────────────────────────────────
#         lines += [
#             "",
#             "Camera stays 100% locked.",
#             "No zooming, no panning, no drifting, no rotation.",
#         ]
#
#         # ── CONTINUATION NOTE ─────────────────────────────────────────────────
#         if self.is_continuation:
#             lines.insert(1,
#                 "This scene continues directly from the previous clip. "
#                 "Match the exact final frame composition, lighting, and character positions."
#             )
#
#         self.generated_video_prompt = "\n".join(lines)
#         self.updated_at = datetime.now().isoformat()
#         return self.generated_video_prompt
#
#     def save(self, base_dir: str = "assets/scenes") -> Path:
#         """Save scene data to its own folder."""
#         self.updated_at = datetime.now().isoformat()
#         scene_dir = Path(base_dir) / self.project_slug / self.scene_id
#         scene_dir.mkdir(parents=True, exist_ok=True)
#
#         # Save scene metadata
#         json_path = scene_dir / "scene.json"
#         with open(json_path, "w", encoding="utf-8") as f:
#             json.dump(dataclasses.asdict(self), f, indent=2, ensure_ascii=False)
#
#         # Save the generated prompt to a text file for easy copy-paste
#         if self.generated_video_prompt:
#             prompt_path = scene_dir / "video_prompt.txt"
#             with open(prompt_path, "w", encoding="utf-8") as f:
#                 f.write(self.generated_video_prompt)
#
#         print(f"✅ Scene saved: {json_path}")
#         return scene_dir
#
#     @classmethod
#     def load(cls, scene_id: str, project_slug: str, base_dir: str = "assets/scenes") -> "Scene":
#         """Load a scene from disk by its ID and project."""
#         json_path = Path(base_dir) / project_slug / scene_id / "scene.json"
#
#         if not json_path.exists():
#             raise FileNotFoundError(f"Scene '{scene_id}' not found at {json_path}")
#
#         with open(json_path, "r", encoding="utf-8") as f:
#             data = json.load(f)
#
#         # Re-hydrate SceneCharacter objects from dicts
#         if "characters" in data:
#             data["characters"] = [SceneCharacter(**c) for c in data["characters"]]
#
#         return cls(**data)
#
#     def __repr__(self) -> str:
#         speaker = self.get_speaker()
#         speaker_info = f", speaker={speaker.character_slug!r}" if speaker else ""
#         return (
#             f"Scene(id={self.scene_id!r}, type={self.scene_type!r}, "
#             f"chars={len(self.characters)}{speaker_info}, status={self.status!r})"
#         )
#
#
# # ─────────────────────────────────────────────────────────────────────────────
# # EXAMPLE: Run this file directly to test it
# # python src/models/scene.py
# # ─────────────────────────────────────────────────────────────────────────────
# if __name__ == "__main__":
#     # Create Scene 1: Mango speaks
#     scene1 = Scene(
#         scene_number=1,
#         scene_type=SceneType.FLIRT.value,
#         environment="beach blanket at sunset",
#         characters=[
#             SceneCharacter(
#                 character_slug="mango_man",
#                 role="speaker",
#                 dialogue="You know… being here with you? Yeah… it hits different.",
#                 tone_override="confident, warm, slightly teasing",
#             ),
#             SceneCharacter(
#                 character_slug="chocolate_cherry",
#                 role="listener",
#             ),
#         ]
#     )
#
#     prompt = scene1.generate_video_prompt()
#     print("=== SCENE 1 VIDEO PROMPT ===")
#     print(prompt)
#
#     # Scene 1 ended, screenshot taken → Create Scene 2
#     scene1.set_continuation_frame("assets/screenshots/scene1_last_frame.png")
#     scene2 = scene1.create_continuation()
#     scene2.characters[0].dialogue = "Relax, Mango… you're cute, but I'm still deciding."
#     scene2.characters[0].tone_override = "playful, teasing, slightly seductive"
#
#     print("\n=== SCENE 2 VIDEO PROMPT ===")
#     print(scene2.generate_video_prompt())
#
#     # Save both scenes
#     scene1.save()
#     scene2.save()
