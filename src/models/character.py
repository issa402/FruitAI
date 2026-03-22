"""
================================================================================
FILE: src/models/character.py
================================================================================

╔══════════════════════════════════════════════════════════════════════════════╗
║              🎓 FAANG-LEVEL LESSON: OBJECT-ORIENTED PROGRAMMING             ║
╚══════════════════════════════════════════════════════════════════════════════╝

WHAT IS A "MODEL" FILE?
───────────────────────
At companies like Google, Meta, and Netflix, a "model" file defines a core
"thing" that your system understands. A model is a blueprint for an object.

Think of it like a form at a doctor's office:
  - The BLANK FORM = the Class (blueprint, reusable)
  - YOUR FILLED FORM = the Object (one specific person's data)

In YOUR project, a Character is a "thing" with:
  - DATA:    name, slug, description, reference_image_path, style_notes
  - ACTIONS: generate_image_prompt(), generate_video_prompt(), save(), load()

This file is THE single source of truth for characters. Every other file
in your project will import from here. Change it once, everything updates.


WHY OOP INSTEAD OF JUST USING DICTIONARIES OR PLAIN VARIABLES?
───────────────────────────────────────────────────────────────
BAD WAY (procedural — beginners do this):
  mango_name = "Mango Man"
  mango_desc = "A tropical mango character..."
  cherry_name = "Chocolate Cherry"
  # 10 characters later = 50+ variables. Impossible to manage.

ALSO BAD (dict-based — slightly better but still messy):
  mango = {"name": "Mango Man", "desc": "A tropical mango..."}
  # No methods. No structure. No validation. Easy to mistype keys.

PRO WAY (OOP — what FAANG engineers do):
  mango = Character(name="Mango Man", description="A tropical mango...")
  mango.save()   # Saves to disk automatically
  mango.generate_image_prompt()  # Builds a perfect prompt

  → It's ORGANIZED. It's VALIDATED. It's REUSABLE. It's TESTABLE.


THE FOUR PILLARS OF OOP (What every interview asks about):
──────────────────────────────────────────────────────────
1. ENCAPSULATION — Bundling data + methods together in one class.
   Example: Character has name (data) AND generate_prompt() (method).
   Real-world: A bank ATM encapsulates your balance (data) +
   withdraw/deposit (methods). You don't see HOW it works internally.

2. ABSTRACTION — Hiding complex logic behind a simple interface.
   Example: You call mango.generate_image_prompt(). You don't care
   HOW it builds the prompt string — you just get the result.
   Real-world: You press "Brew" on a coffee machine. You don't rewire
   the heating elements yourself.

3. INHERITANCE — A class can inherit (copy + extend) from another class.
   Example: HostCharacter(Character) — the host IS a character but also
   has extra methods like introduce_show(), introduce_contestant().
   Real-world: An ElectricCar IS a Car, but it also has charge().

4. POLYMORPHISM — Different classes respond to the same method differently.
   Example: mango.generate_prompt() vs host.generate_prompt() — same
   method name, different output based on the object type.
   Real-world: .speak() on a Dog says "Woof", on a Cat says "Meow".


WHAT IS __init__? (The Constructor)
─────────────────────────────────────
__init__ is a special method Python calls AUTOMATICALLY when you create
a new object. It's where you give the object its starting data.

  mango = Character(name="Mango Man")
  #                 ↑ This argument goes into __init__(self, name="Mango Man")

"self" is the object REFERRING TO ITSELF. Every method must have it as
the first parameter. It's how the object accesses its own data.
  self.name = name  ← "MY name is..."


WHAT IS dataclass? (FAANG loves this)
──────────────────────────────────────
@dataclass is a Python decorator that auto-generates __init__, __repr__,
and __eq__ for you. Instead of writing 20 lines of boilerplate, you write:

  @dataclass
  class Character:
      name: str
      description: str = ""
  # Python generates __init__(self, name, description="") automatically!

Type hints (name: str) tell Python AND other developers what TYPE of data
is expected. This is how Google, Meta, Netflix code looks.


WHAT IS @dataclass field(default_factory=list)?
─────────────────────────────────────────────────
For mutable defaults (like lists or dicts), you CANNOT do:
  class Character:
      scenes: list = []  # ❌ WRONG! All objects share the SAME list!

You MUST do:
  from dataclasses import field
  class Character:
      scenes: list = field(default_factory=list)  # ✅ Each object gets its OWN list


WHAT IS @property? (Computed attributes)
──────────────────────────────────────────
A @property is a method that ACTS like an attribute. No parentheses needed.
  character.slug         # Calls the slug() method but looks like an attribute
  character.slug()       # This would fail — properties don't use ()

Used when a value is DERIVED from other data rather than stored directly.
At Google, they call this a "computed property" or "getter".


PATHLIB vs os.path (Why FAANG uses pathlib):
─────────────────────────────────────────────
OLD WAY (Python 2 era — avoid this):
  import os
  path = os.path.join("assets", "characters", "mango", "ref.png")

MODERN WAY (Python 3.4+ — use this):
  from pathlib import Path
  path = Path("assets") / "characters" / "mango" / "ref.png"
  # The / operator works like folder separator! Clean, readable, cross-platform.


JSON SERIALIZATION (Saving Python objects to disk)
────────────────────────────────────────────────────
Python objects live in RAM. When your script stops, they're GONE.
To PERSIST data (save it), you serialize to JSON (a text format).

  import json
  data = {"name": "Mango", "style": "cartoon"}
  with open("character.json", "w") as f:
      json.dump(data, f, indent=2)  # Writes to disk

  # To read back:
  with open("character.json", "r") as f:
      data = json.load(f)  # Reads from disk back into Python dict

"indent=2" makes the JSON human-readable (pretty-printed).


WHAT IS dataclasses.asdict()?
──────────────────────────────
Converts a dataclass object into a regular Python dictionary, which can
then be serialized to JSON. This is the standard pattern.

  mango = Character(name="Mango Man")
  data = dataclasses.asdict(mango)  # {"name": "Mango Man", ...}
  json.dump(data, file)


HOW FAANG COMPANIES STRUCTURE THIS:
─────────────────────────────────────────────────────────────────────────
Netflix uses "domain models" — core objects that represent real-world
things (User, Movie, Episode). Meta calls them "entities". Google calls
them "protos" (protocol buffers, which is just a typed version of this).

Your Character class IS a domain model. It's the center of your system.
Everything else (prompts, scenes, videos) REFERENCES a Character.

This pattern is called "Domain-Driven Design" (DDD) — used by every
FAANG company to keep large codebases organized and maintainable.

================================================================================
"""

# These are Python's standard library imports — no installation needed.
# dataclasses: Auto-generates boilerplate (__init__, __repr__, __eq__)
# field: For safe mutable defaults (lists, dicts) inside dataclasses
# Optional: Type hint meaning "this value OR None" (from the typing module)
# List: Type hint for a list of specific types
# datetime: Getting current timestamps for created_at / updated_at fields
# json: Serializing (saving) Python objects to JSON files
# pathlib.Path: Modern, cross-platform file path handling
import dataclasses
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional, List


# ─────────────────────────────────────────────────────────────────────────────
# TODO 1: Understand the @dataclass decorator
#   - Remove @dataclass and manually write __init__. See how much more code?
#   - Then add it back. That's what @dataclass saves you.
#
# TODO 2: Understand type hints
#   - name: str means name must be a string
#   - description: str = "" means it defaults to empty string if not provided
#   - image_path: Optional[str] = None means it CAN be None (not required)
#   - scenes_involved: List[str] = field(...) means it's a list of strings
#
# TODO 3: Add a new field called "voice_style"
#   - Type: str
#   - Default: "neutral"
#   - This will be used in video prompts later
#
# TODO 4: Override __str__ to print beautiful character info
#   - def __str__(self): return f"Character: {self.name}"
#
# TODO 5: Add a method called "is_valid()" that returns True if name is not empty
# ─────────────────────────────────────────────────────────────────────────────


# ═══════════════════════════════════════════════════════════════════════════
# FULL CODE (try it yourself first! ↑ Use the TODOs above as your guide)
# ═══════════════════════════════════════════════════════════════════════════

# @dataclass
# class Character:
#     """
#     Represents one character in the Fruit Love Island universe.
#
#     This is a DOMAIN MODEL — the single source of truth for a character.
#     Every prompt, every scene, every video references this object.
#
#     Example usage:
#         mango = Character(
#             name="Mango Man",
#             slug="mango_man",
#             description="A tall, tropical mango fruit character...",
#             style_notes="Lean, animated, fruit art style. Leaf on head.",
#         )
#         print(mango.generate_image_prompt())
#         mango.save()
#     """
#
#     # ── IDENTITY ────────────────────────────────────────────────────────────
#     # name: The human-readable display name ("Mango Man", "Chocolate Cherry")
#     name: str
#
#     # slug: A URL/filename-safe identifier. "Mango Man" → "mango_man"
#     # Used for folder names, JSON keys, database lookups.
#     # Optional[str] = None means: if you don't provide it, it's None.
#     # We auto-generate it in __post_init__ if not provided.
#     slug: Optional[str] = None
#
#     # ── APPEARANCE / AI PROMPT DATA ─────────────────────────────────────────
#     # description: What the character looks like. This feeds into image prompts.
#     # CRITICAL: Keep this consistent. If AI keeps re-designing your character,
#     # it's because this description changes between prompts. Store it HERE.
#     description: str = ""
#
#     # style_notes: Extra details about art style, vibe, features
#     # Example: "Never add sunglasses unless specified. Leaf is always green."
#     style_notes: str = ""
#
#     # role: "main", "host", "contestant", "background"
#     # Determines which prompt templates get used
#     role: str = "contestant"
#
#     # ── FILE PATHS ──────────────────────────────────────────────────────────
#     # reference_image_path: Path to the character's reference image.
#     # When you tell the AI "use ONLY the character from image 1", THIS
#     # is the image path your system tracks.
#     reference_image_path: Optional[str] = None
#
#     # personality: How the character acts. This feeds into dialogue/tone.
#     # Example: "Playful, flirty, confident. Slow blinks. Teasing delivery."
#     personality: str = ""
#
#     # voice_assignments: How this character sounds when speaking in videos.
#     # Key: scene_type (e.g., "flirt", "dramatic"), Value: tone description
#     # Example: {"flirt": "warm and teasing", "dramatic": "sharp and direct"}
#     voice_assignments: dict = field(default_factory=dict)
#
#     # scenes_involved: List of scene IDs this character has appeared in.
#     # Allows you to ask: "Show me all scenes with Mango Man"
#     scenes_involved: List[str] = field(default_factory=list)
#
#     # ── TIMESTAMPS ──────────────────────────────────────────────────────────
#     # created_at: When this character was first created. Auto-set below.
#     created_at: str = field(default_factory=lambda: datetime.now().isoformat())
#
#     # updated_at: When this character was last modified. Update on save().
#     updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
#
#     def __post_init__(self):
#         """
#         __post_init__ runs AFTER __init__ (which @dataclass auto-generates).
#         Use this for: computed fields, validation, auto-generation.
#
#         This is a FAANG pattern — keep __init__ clean, do post-processing here.
#         """
#         # Auto-generate slug from name if not provided
#         # "Mango Man" → "mango_man"  |  "Chocolate Cherry" → "chocolate_cherry"
#         if self.slug is None:
#             self.slug = self.name.lower().replace(" ", "_").replace("-", "_")
#
#         # Validation: name cannot be empty
#         # In production, this would raise a custom exception.
#         if not self.name.strip():
#             raise ValueError("Character name cannot be empty.")
#
#     # ════════════════════════════════════════════════════════════════════════
#     # PROMPT GENERATION METHODS
#     # These are the CORE value of this class — they eliminate your manual work.
#     # ════════════════════════════════════════════════════════════════════════
#
#     def generate_image_prompt(
#         self,
#         scene_description: str = "",
#         reference_image_num: int = 1,
#         additional_instructions: str = "",
#     ) -> str:
#         """
#         Generate a complete image prompt for this character.
#
#         This solves YOUR problem: "AI keeps re-designing characters."
#         By storing the character spec here, every prompt is consistent.
#
#         Args:
#             scene_description: What the character is doing in this image.
#             reference_image_num: Which image number to reference (1, 2, etc.)
#             additional_instructions: Any extra one-off instructions.
#
#         Returns:
#             str: A complete, copy-paste-ready image prompt.
#         """
#         # Build the base prompt — this is the "DO NOT redesign" block
#         # that you always need at the start of every prompt.
#         base = (
#             f"Use ONLY the character shown in image {reference_image_num}. "
#             "Do NOT redesign, alter, or add details to the character. "
#             "Do NOT add new characters, props, or background elements. "
#             "Do NOT duplicate anything. "
#             "Keep the same art style, colors, lighting, and composition."
#         )
#
#         # Add the scene description if provided
#         scene_part = f"\n\nScene: {scene_description}" if scene_description else ""
#
#         # Add style notes if the character has them
#         style_part = f"\n\nStyle notes: {self.style_notes}" if self.style_notes else ""
#
#         # Add additional instructions if provided
#         extra_part = f"\n\n{additional_instructions}" if additional_instructions else ""
#
#         # Combine all parts into one complete prompt
#         return base + scene_part + style_part + extra_part
#
#     def generate_video_animation_prompt(
#         self,
#         dialogue: str = "",
#         speaker: Optional["Character"] = None,
#         duration_seconds: int = 6,
#         scene_type: str = "flirt",
#         environment: str = "beach blanket at sunset",
#         other_character: Optional["Character"] = None,
#     ) -> str:
#         """
#         Generate a 6-second video animation prompt.
#
#         This solves YOUR biggest pain: re-typing the same mega-prompt every scene.
#         The 400-word prompt you copy-paste EVERY TIME? This generates it for you.
#
#         Args:
#             dialogue: The words this character speaks (empty = no dialogue).
#             speaker: Which Character is speaking (defaults to self).
#             duration_seconds: How long the clip is (default 6).
#             scene_type: "flirt", "dramatic", "intro", "reaction"
#             environment: Where the scene takes place.
#             other_character: The other character in the scene.
#
#         Returns:
#             str: Complete, copy-paste-ready video animation prompt.
#         """
#         speaker = speaker or self
#         tone = speaker.voice_assignments.get(scene_type, "natural and controlled")
#
#         # Build the full prompt — this is your 400-word template, automated
#         prompt_parts = [
#             "Use ONLY the provided image exactly as it is. "
#             "Do NOT add new characters, props, fruit, or background elements. "
#             "Do NOT duplicate anything. "
#             "Keep the same art style, colors, lighting, and composition. "
#             f"Animate the scene for {duration_seconds} seconds in a Love-Island-Fruit-AI style.",
#             "",
#             f"Environment: {environment}",
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
#             "- slight head tilts toward each other, staying within original pose",
#         ]
#
#         # Add character-specific idle animations
#         if self.style_notes:
#             prompt_parts.append(f"- {self.style_notes}")
#
#         prompt_parts += [
#             "",
#             "Add soft environment animation:",
#             "- palm trees sway slightly",
#             "- ocean waves move gently",
#             "- warm lighting flickers subtly on bodies",
#             "",
#             "Dialogue + Delivery Style:",
#         ]
#
#         if dialogue:
#             prompt_parts += [
#                 f"For the full {duration_seconds} seconds, ONLY {speaker.name} speaks.",
#                 f"Deliver with {tone} tone — not exaggerated.",
#                 f"Mouth syncs naturally to the words:",
#                 f"'{dialogue}'",
#             ]
#             if other_character:
#                 prompt_parts.append(
#                     f"{other_character.name} reacts only with subtle micro-expressions: "
#                     "a small smile or blink — nothing more."
#                 )
#         else:
#             prompt_parts.append("No dialogue. No subtitles. No voiceover.")
#
#         prompt_parts += [
#             "",
#             "Camera stays 100% locked.",
#             "No zooming, no panning, no drifting, no rotation.",
#         ]
#
#         return "\n".join(prompt_parts)
#
#     def add_scene(self, scene_id: str) -> None:
#         """Track that this character appeared in a scene."""
#         if scene_id not in self.scenes_involved:
#             self.scenes_involved.append(scene_id)
#             self.updated_at = datetime.now().isoformat()
#
#     # ════════════════════════════════════════════════════════════════════════
#     # PERSISTENCE METHODS (Save / Load to disk)
#     # ════════════════════════════════════════════════════════════════════════
#
#     def save(self, base_dir: str = "assets/characters") -> Path:
#         """
#         Save this character to a JSON file on disk.
#
#         File structure:
#             assets/characters/{slug}/character.json
#
#         This is the FAANG pattern: each entity gets its OWN folder.
#         Later you can add: ref_image.png, approved_prompts.txt, etc.
#         """
#         self.updated_at = datetime.now().isoformat()
#
#         # Create the character's folder if it doesn't exist
#         # Path(base_dir) / self.slug = "assets/characters/mango_man"
#         char_dir = Path(base_dir) / self.slug
#         char_dir.mkdir(parents=True, exist_ok=True)
#
#         # Convert this dataclass object to a dict, then write to JSON
#         json_path = char_dir / "character.json"
#         with open(json_path, "w", encoding="utf-8") as f:
#             json.dump(dataclasses.asdict(self), f, indent=2, ensure_ascii=False)
#
#         print(f"✅ Character saved: {json_path}")
#         return json_path
#
#     @classmethod
#     def load(cls, slug: str, base_dir: str = "assets/characters") -> "Character":
#         """
#         Load a character from disk by their slug.
#
#         @classmethod means you call it on the CLASS, not an instance:
#             mango = Character.load("mango_man")    ← Right
#             mango.load("mango_man")                ← Wrong (usually)
#
#         Args:
#             slug: The character's slug identifier ("mango_man")
#             base_dir: Root folder for character data
#
#         Returns:
#             Character: A fully loaded Character object
#
#         Raises:
#             FileNotFoundError: If the character doesn't exist on disk
#         """
#         json_path = Path(base_dir) / slug / "character.json"
#
#         if not json_path.exists():
#             raise FileNotFoundError(
#                 f"Character '{slug}' not found at {json_path}. "
#                 f"Did you call .save() first?"
#             )
#
#         with open(json_path, "r", encoding="utf-8") as f:
#             data = json.load(f)
#
#         # **data "unpacks" the dict — passes all keys as keyword arguments
#         # Character(**{"name": "Mango Man"}) = Character(name="Mango Man")
#         return cls(**data)
#
#     @classmethod
#     def load_all(cls, base_dir: str = "assets/characters") -> List["Character"]:
#         """Load ALL characters from disk. Returns a list of Character objects."""
#         base = Path(base_dir)
#         characters = []
#         if base.exists():
#             for char_dir in base.iterdir():
#                 json_path = char_dir / "character.json"
#                 if json_path.exists():
#                     characters.append(cls.load(char_dir.name, base_dir))
#         return characters
#
#     def __repr__(self) -> str:
#         """
#         __repr__ is what Python prints when you do print(mango) or repr(mango).
#         Make it readable and informative.
#         """
#         return (
#             f"Character(name={self.name!r}, role={self.role!r}, "
#             f"scenes={len(self.scenes_involved)})"
#         )
#
#
# # ─────────────────────────────────────────────────────────────────────────────
# # EXAMPLE: Run this file directly to test it
# # python src/models/character.py
# # ─────────────────────────────────────────────────────────────────────────────
# if __name__ == "__main__":
#     # Create the Mango Man character
#     mango = Character(
#         name="Mango Man",
#         description="A tall tropical mango fruit character.",
#         style_notes="Leaf hair that sways in breeze. Confident posture.",
#         role="contestant",
#         personality="Smooth, confident, slightly teasing. Slow blinks.",
#         voice_assignments={
#             "flirt": "confident, warm, slightly seductive",
#             "dramatic": "sharp and intense",
#         },
#     )
#
#     print("=== CHARACTER INFO ===")
#     print(repr(mango))
#
#     print("\n=== IMAGE PROMPT ===")
#     print(mango.generate_image_prompt("sitting on beach blanket at sunset"))
#
#     print("\n=== VIDEO PROMPT ===")
#     print(mango.generate_video_animation_prompt(
#         dialogue="You know… being here with you? Yeah… it hits different.",
#         scene_type="flirt",
#     ))
#
#     # Save to disk
#     mango.save()
#
#     # Load back from disk
#     loaded = Character.load("mango_man")
#     print(f"\n=== LOADED FROM DISK ===\n{loaded}")
