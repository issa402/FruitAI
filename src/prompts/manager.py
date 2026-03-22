"""
================================================================================
FILE: src/prompts/manager.py
================================================================================

╔══════════════════════════════════════════════════════════════════════════════╗
║          🎓 FAANG-LEVEL LESSON: THE MANAGER PATTERN & PROMPT SYSTEMS        ║
╚══════════════════════════════════════════════════════════════════════════════╝

WHAT IS THIS FILE?
──────────────────
The PromptManager is the HEART of your automation system. It:
  1. Stores all your prompt templates (scene types, image types, video types)
  2. Generates complete prompts by filling in templates with character/scene data
  3. Saves successful prompts to your library so you never lose them
  4. Loads saved prompts for reuse

Think of it like a "Prompt Factory" — raw ingredients go in (character, scene),
finished prompt comes out (ready to copy-paste into your AI tool).


WHAT IS THE "MANAGER PATTERN"?
───────────────────────────────
The Manager pattern is a classic software pattern where one class is
responsible for a specific TYPE of operation across your system.

Examples in FAANG systems:
  ConnectionManager  → Manages database connections
  CacheManager       → Manages caching
  TaskManager        → Manages async jobs

YOUR PromptManager → Manages all prompt generation

It's NOT the same as a God Class (anti-pattern where one class does EVERYTHING).
The PromptManager does ONE thing: work with prompts.


WHAT IS STRING FORMATTING IN PYTHON?
──────────────────────────────────────
There are 4 ways to format strings in Python. Here's what FAANG engineers use:

1. f-strings (MODERN, preferred at all FAANG companies):
   name = "Mango"
   result = f"Hello {name}!"   # "Hello Mango!"

2. .format() (older, sometimes used for templates):
   template = "Hello {name}!"
   result = template.format(name="Mango")  # "Hello Mango!"

3. Template strings (great for user-provided templates — SAFE):
   from string import Template
   t = Template("Hello $name!")
   result = t.safe_substitute(name="Mango")  # "Hello Mango!" (won't crash if key missing)

4. % formatting (OLD, avoid this):
   result = "Hello %s!" % "Mango"  # Don't do this

For YAML-based templates (user-editable config files), .format() or
Template strings are preferred because they're safer.


WHAT IS YAML AND WHY IS IT BETTER THAN JSON FOR TEMPLATES?
────────────────────────────────────────────────────────────
JSON is great for machine-to-machine data.
YAML is better for human-editable configuration files.

JSON (hard to read/edit):
  {
    "template": "Use ONLY the character in image {num}. Do NOT redesign..."
  }

YAML (easy to read/edit):
  template: |
    Use ONLY the character in image {num}.
    Do NOT redesign...

The | character in YAML means "literal block" — preserves newlines.

Used by: Kubernetes configs, GitHub Actions, Docker Compose.


WHAT IS A "PROMPT TEMPLATE"? (How Netflix/OpenAI builds prompts)
────────────────────────────────────────────────────────────────
Instead of hard-coding prompts, you store TEMPLATES with PLACEHOLDERS:

Template:
  "Animate {character_name} for {duration}s with {tone} delivery.
   Mouth syncs to: '{dialogue}'"

At runtime you fill in the placeholders:
  template.format(
      character_name="Mango Man",
      duration=6,
      tone="warm and teasing",
      dialogue="It hits different.",
  )

Output:
  "Animate Mango Man for 6s with warm and teasing delivery.
   Mouth syncs to: 'It hits different.'"

This is EXACTLY how OpenAI's system prompts work internally.


THE SINGLETON PATTERN (How your PromptManager should be used):
───────────────────────────────────────────────────────────────
A Singleton is a class that can only have ONE instance.
Good for: anything that should be shared (database, config, prompt library).

Basic Python Singleton:
  class PromptManager:
      _instance = None

      @classmethod
      def get_instance(cls):
          if cls._instance is None:
              cls._instance = cls()
          return cls._instance

Usage:
  manager = PromptManager.get_instance()  # Always same instance
  manager2 = PromptManager.get_instance() # Same object as manager

For your project: one PromptManager loads templates once, used everywhere.


WHAT IS LOGGING? (How FAANG engineers debug)
──────────────────────────────────────────────
NEVER use print() in production code. Use Python's logging module.

Why?
  - print() goes to stdout, lost forever
  - logging writes to files, can be replayed when debugging
  - logging has LEVELS (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  - You can turn off DEBUG logs in production without code changes

import logging
logger = logging.getLogger(__name__)  # Creates logger named after this file
logger.info("Prompt generated for scene S001")
logger.warning("Character image not found, using default")
logger.error("Failed to save prompt: {e}")

In production: log file saves everything. Errors get alerts.
At Google: logs go to Stackdriver. At AWS: CloudWatch.

================================================================================
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from string import Template
from typing import Optional, Dict, List, Any

# Create a logger named after this file (src.prompts.manager)
# This is the standard FAANG pattern — never use print() in real code.
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# TODO 1: Open templates/prompt_templates.yaml and understand the structure
#   - Each template has a name, type, and template string with {placeholders}
#   - Load one template and fill a placeholder manually with .format()
#
# TODO 2: Add a method "search_library(keyword)" that searches all saved
#   prompts for ones containing a keyword (e.g., search_library("mango"))
#
# TODO 3: Add a method "get_favorite_prompts()" that loads prompts that
#   have been marked as favorites (add a "favorite: bool" field in saved JSON)
#
# TODO 4: Add a method that takes a SCENE TYPE (flirt, zipline, host_intro)
#   and returns that specific template from the YAML file
#
# TODO 5: Add clipboard copy functionality using the pyperclip library:
#   import pyperclip
#   pyperclip.copy(prompt_text)
#   print("✅ Copied to clipboard!")
# ─────────────────────────────────────────────────────────────────────────────


# ═══════════════════════════════════════════════════════════════════════════
# FULL CODE (try it yourself first!)
# ═══════════════════════════════════════════════════════════════════════════

# class PromptManager:
#     """
#     Manages prompt templates and the saved prompt library.
#
#     Responsibilities:
#     - Load prompt templates from YAML config
#     - Fill templates with scene/character data
#     - Save successful prompts to library
#     - Search and retrieve saved prompts
#     - Export prompts for copy-pasting
#
#     Usage:
#         manager = PromptManager()
#         prompt = manager.generate_flirt_scene_prompt(
#             speaker_name="Mango Man",
#             dialogue="It hits different.",
#             tone="confident and warm",
#         )
#         manager.save_prompt(prompt, scene_id="S001", project="fruit_ep1")
#         manager.copy_to_clipboard(prompt)
#     """
#
#     def __init__(
#         self,
#         templates_dir: str = "templates",
#         library_dir: str = "assets/prompts/library",
#     ):
#         """
#         Initialize the PromptManager.
#
#         Args:
#             templates_dir: Folder containing YAML template files
#             library_dir: Folder where saved prompts are stored
#         """
#         self.templates_dir = Path(templates_dir)
#         self.library_dir = Path(library_dir)
#         self.library_dir.mkdir(parents=True, exist_ok=True)
#
#         # Cache for loaded templates (so we don't re-read the file every call)
#         # This is a standard performance optimization
#         self._template_cache: Dict[str, Any] = {}
#
#         # Load templates on startup
#         self._load_templates()
#         logger.info("PromptManager initialized.")
#
#     def _load_templates(self) -> None:
#         """
#         Load all YAML template files into memory.
#
#         The underscore prefix (_load_templates) means this is a PRIVATE method.
#         Private methods are internal implementation details — not part of the
#         public API. Other code should NOT call this directly.
#
#         This loads templates/prompt_templates.yaml into self._template_cache.
#         """
#         try:
#             import yaml
#             templates_file = self.templates_dir / "prompt_templates.yaml"
#             if templates_file.exists():
#                 with open(templates_file, "r", encoding="utf-8") as f:
#                     self._template_cache = yaml.safe_load(f) or {}
#                 logger.info(
#                     f"Loaded {len(self._template_cache)} templates from {templates_file}"
#                 )
#             else:
#                 logger.warning(f"Templates file not found: {templates_file}")
#                 self._template_cache = {}
#         except ImportError:
#             logger.warning("PyYAML not installed. Templates will be empty. Run: pip install pyyaml")
#             self._template_cache = {}
#         except Exception as e:
#             logger.error(f"Failed to load templates: {e}")
#             self._template_cache = {}
#
#     def get_template(self, template_name: str) -> Optional[str]:
#         """
#         Retrieve a raw template string by name.
#
#         Args:
#             template_name: Key name in the YAML file (e.g., "flirt_scene")
#
#         Returns:
#             str: The raw template string with placeholders, or None if not found.
#         """
#         template = self._template_cache.get(template_name)
#         if template is None:
#             logger.warning(f"Template not found: '{template_name}'")
#             return None
#         # Templates can be stored as dicts with a "template" key, or plain strings
#         if isinstance(template, dict):
#             return template.get("template", "")
#         return str(template)
#
#     def fill_template(self, template_name: str, **kwargs) -> Optional[str]:
#         """
#         Fill a template with values and return the complete prompt.
#
#         Uses Python's string.Template for SAFE substitution.
#         If a placeholder is missing, safe_substitute leaves it unreplaced
#         (instead of crashing), so partially filled prompts are still usable.
#
#         Args:
#             template_name: The template to use
#             **kwargs: Key-value pairs for placeholder substitution
#                       Example: fill_template("flirt_scene", speaker="Mango")
#
#         Returns:
#             str: Filled prompt ready to copy-paste, or None if template missing.
#
#         Example:
#             prompt = manager.fill_template(
#                 "flirt_scene",
#                 speaker_name="Mango Man",
#                 dialogue="It hits different.",
#                 tone="confident, warm",
#                 duration=6,
#             )
#         """
#         raw_template = self.get_template(template_name)
#         if raw_template is None:
#             return None
#
#         # string.Template uses $variable or ${variable} syntax
#         # .safe_substitute won't crash if a variable is missing
#         t = Template(raw_template)
#         filled = t.safe_substitute(**kwargs)
#
#         logger.debug(f"Filled template '{template_name}' with keys: {list(kwargs.keys())}")
#         return filled
#
#     # ─────────────────────────────────────────────────────────────────────────
#     # SPECIFIC PROMPT GENERATORS (covering your exact use cases)
#     # ─────────────────────────────────────────────────────────────────────────
#
#     def generate_flirt_scene_prompt(
#         self,
#         speaker_name: str,
#         dialogue: str,
#         tone: str = "playful, flirty, and confident",
#         listener_name: str = "the other character",
#         environment: str = "beach blanket at sunset",
#         duration: int = 6,
#     ) -> str:
#         """
#         Generate a complete flirt scene video prompt.
#         This is your most common use case — covers 90% of your scenes.
#         """
#         return (
#             f"Use ONLY the provided image exactly as it is. "
#             f"Do NOT add new characters, props, fruit, or background elements. "
#             f"Do NOT duplicate anything. "
#             f"Keep the same art style, colors, lighting, and composition. "
#             f"Animate the scene for {duration} seconds in a Love-Island-Fruit-AI style.\n\n"
#             f"Environment: {environment}\n"
#             f"Both characters remain in their exact positions. "
#             f"Their bodies must NOT shift, slide, stand, or change pose. "
#             f"Only natural micro-movements are allowed.\n\n"
#             f"They look directly at each other the entire time — never at the camera.\n\n"
#             f"Add subtle, realistic idle animation:\n"
#             f"- gentle breathing in chest and shoulders\n"
#             f"- soft blinking for both characters\n"
#             f"- tiny facial micro-expressions that match the mood\n"
#             f"- slight head tilts toward each other within original pose\n\n"
#             f"Add soft environment animation:\n"
#             f"- palm trees sway slightly\n"
#             f"- ocean waves move gently\n"
#             f"- warm lighting flickers subtly\n\n"
#             f"Dialogue + Delivery Style:\n"
#             f"For the full {duration} seconds, ONLY {speaker_name} speaks.\n"
#             f"Deliver with {tone} tone — not exaggerated.\n"
#             f"Mouth syncs naturally to the words:\n"
#             f"'{dialogue}'\n\n"
#             f"{listener_name} reacts only with subtle micro-expressions: "
#             f"a small smile, a slow blink — nothing more.\n\n"
#             f"Camera stays 100% locked.\n"
#             f"No zooming, no panning, no drifting, no rotation."
#         )
#
#     def generate_zipline_prompt(
#         self,
#         dialogue: str = "",
#         exits_frame: bool = False,
#         exit_after_seconds: int = 3,
#         duration: int = 6,
#     ) -> str:
#         """
#         Generate a host zipline scene prompt.
#         Covers your zipline intro use case.
#
#         Args:
#             dialogue: What the host says (empty = silent zipline shot)
#             exits_frame: True = host zips out of camera view
#             exit_after_seconds: How many seconds before host exits (if exits_frame)
#             duration: Total clip duration
#         """
#         base = (
#             "Use ONLY the character shown in the provided image. "
#             "Do NOT add new characters, props, or background elements. "
#             "Do NOT duplicate anything. "
#             "Keep the same art style, colors, lighting, and composition.\n\n"
#             "Place the character on a zipline harness, holding the handle naturally. "
#             "Her body stays stable and centered — no unnatural bending or pose changes.\n\n"
#             "Animate a smooth forward zipline motion across the tropical island:\n"
#             "- island background moves behind her with controlled motion blur\n"
#             "- palm trees, cliffs, and ocean pass by softly\n"
#             "- lighting stays consistent\n"
#             "- wind affects her hair, clothing, and accessories naturally\n"
#             "- she blinks softly and shows natural micro-expressions\n"
#             "- subtle breathing in chest and shoulders\n\n"
#             "Camera stays locked on her upper body and face — no zooming, no panning, no rotation.\n\n"
#         )
#
#         if exits_frame:
#             base += (
#                 f"At the very start of the clip, she is already moving toward the right side of the frame.\n"
#                 f"She does NOT look at the camera — she looks forward in the direction she is traveling.\n"
#                 f"By the {exit_after_seconds}-second mark, she should be completely out of camera view.\n"
#                 f"For the remaining seconds: camera stays locked, island view remains visible, "
#                 f"palm trees sway, ocean moves gently.\n\n"
#                 f"No dialogue. No subtitles. No voiceover.\n"
#                 f"Only the zipline motion, wind, and the environment."
#             )
#         elif dialogue:
#             base += (
#                 f"Dialogue + Delivery Style ({duration} seconds):\n"
#                 f"ONLY this character speaks.\n"
#                 f"She delivers her line with energetic, charismatic Love-Island-host confidence — "
#                 f"bright smile, expressive eyes, playful tone.\n"
#                 f"Her mouth moves naturally and precisely to the words:\n"
#                 f"'{dialogue}'\n"
#                 f"Her delivery should feel bold, fun, and inviting — not exaggerated.\n"
#                 f"No other characters appear. No new props appear."
#             )
#         else:
#             base += "No dialogue. No subtitles. No voiceover."
#
#         return base
#
#     def generate_character_into_background_prompt(
#         self,
#         character_image_num: int = 1,
#         background_image_num: int = 2,
#         position: str = "center",
#         additional: str = "",
#     ) -> str:
#         """
#         YOUR USE CASE: "Use character from Image 1 into the background of Image 2"
#         This is the prompt for combining images.
#         """
#         prompt = (
#             f"Use ONLY the character from image {character_image_num}. "
#             f"Do NOT redesign, redraw, or alter the character in any way. "
#             f"Place this character exactly as they appear into the scene from image {background_image_num}. "
#             f"Do NOT add new characters, props, or elements. "
#             f"Do NOT duplicate anything from either image. "
#             f"Match the art style, lighting, and color palette of image {background_image_num}. "
#             f"Keep the character's proportions, features, and details identical to image {character_image_num}. "
#             f"Position: {position} of frame.\n"
#         )
#         if additional:
#             prompt += f"\nAdditional instructions: {additional}"
#         return prompt
#
#     def generate_combine_two_characters_prompt(
#         self,
#         char1_image_num: int = 1,
#         char2_image_num: int = 2,
#         scene_description: str = "standing together, looking at each other",
#         art_style_reference: int = 1,
#     ) -> str:
#         """
#         YOUR USE CASE: "Combine two characters from two different images"
#         This replaces your manual: screenshot → Google Docs → paste workflow.
#         """
#         return (
#             f"Combine the characters from BOTH images into a single scene. "
#             f"Use the character from image {char1_image_num} exactly as they appear — "
#             f"do NOT redesign them. "
#             f"Use the character from image {char2_image_num} exactly as they appear — "
#             f"do NOT redesign them. "
#             f"Scene: {scene_description}. "
#             f"Art style, lighting, and color palette must match image {art_style_reference}. "
#             f"Do NOT add new characters, props, or background elements. "
#             f"Do NOT duplicate, morph, or blend character features. "
#             f"Both characters must be clearly distinguishable and faithful to their source images."
#         )
#
#     def generate_video_recreation_prompt(
#         self,
#         reference_events: str,
#         art_style_image_num: int = 1,
#         duration: int = 6,
#     ) -> str:
#         """
#         YOUR USE CASE: "Recreate a video in my art style"
#         When you screenshot a video and want to recreate it as Fruit Love Island.
#         """
#         return (
#             f"Use ONLY the character(s) shown in image {art_style_image_num}. "
#             f"Do NOT add new characters, props, or elements. "
#             f"Keep the same art style, colors, lighting, and composition from image {art_style_image_num}. "
#             f"Animate for {duration} seconds. "
#             f"Recreate the following events exactly: {reference_events}. "
#             f"Do NOT improvise or add movements not described. "
#             f"Camera movement should match the original where specified. "
#             f"Every action listed must occur within the {duration}-second window."
#         )
#
#     # ─────────────────────────────────────────────────────────────────────────
#     # LIBRARY METHODS (saving and loading prompts)
#     # ─────────────────────────────────────────────────────────────────────────
#
#     def save_prompt(
#         self,
#         prompt_text: str,
#         scene_id: str,
#         project_slug: str = "default",
#         prompt_type: str = "video",
#         tags: List[str] = None,
#         notes: str = "",
#     ) -> Path:
#         """
#         Save a generated prompt to the library.
#         Prompts are saved as JSON with metadata for searching later.
#         """
#         tags = tags or []
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         filename = f"{project_slug}_{scene_id}_{prompt_type}_{timestamp}.json"
#
#         data = {
#             "prompt": prompt_text,
#             "scene_id": scene_id,
#             "project_slug": project_slug,
#             "prompt_type": prompt_type,
#             "tags": tags,
#             "notes": notes,
#             "created_at": datetime.now().isoformat(),
#             "character_count": len(prompt_text),
#             "favorite": False,
#         }
#
#         save_path = self.library_dir / filename
#         with open(save_path, "w", encoding="utf-8") as f:
#             json.dump(data, f, indent=2, ensure_ascii=False)
#
#         logger.info(f"Prompt saved to library: {save_path}")
#         return save_path
#
#     def search_library(self, keyword: str) -> List[Dict]:
#         """
#         Search saved prompts by keyword.
#         Returns list of matching prompt dicts.
#         """
#         results = []
#         for json_file in self.library_dir.glob("*.json"):
#             try:
#                 with open(json_file, "r", encoding="utf-8") as f:
#                     data = json.load(f)
#                 # Search in prompt text, notes, and tags
#                 searchable = (
#                     data.get("prompt", "")
#                     + data.get("notes", "")
#                     + " ".join(data.get("tags", []))
#                 ).lower()
#                 if keyword.lower() in searchable:
#                     results.append(data)
#             except (json.JSONDecodeError, KeyError) as e:
#                 logger.warning(f"Could not read prompt file {json_file}: {e}")
#         logger.info(f"Search for '{keyword}' found {len(results)} results")
#         return results
#
#     def copy_to_clipboard(self, text: str) -> bool:
#         """
#         Copy text to system clipboard.
#         Requires: pip install pyperclip
#         """
#         try:
#             import pyperclip
#             pyperclip.copy(text)
#             print("✅ Copied to clipboard! Paste into your AI tool.")
#             return True
#         except ImportError:
#             print("⚠️  Install pyperclip for clipboard support: pip install pyperclip")
#             print("=" * 60)
#             print(text)  # Fallback: print it so user can copy manually
#             print("=" * 60)
#             return False
#
#
# # ─────────────────────────────────────────────────────────────────────────────
# # EXAMPLE: Run this file directly
# # python src/prompts/manager.py
# # ─────────────────────────────────────────────────────────────────────────────
# if __name__ == "__main__":
#     manager = PromptManager()
#
#     # Generate a flirt scene prompt
#     prompt = manager.generate_flirt_scene_prompt(
#         speaker_name="Mango Man",
#         dialogue="You know… being here with you? Yeah… it hits different.",
#         tone="confident, warm, slightly teasing",
#         listener_name="the chocolate cherry woman",
#     )
#
#     print("=== GENERATED PROMPT ===")
#     print(prompt)
#
#     # Save it to library
#     manager.save_prompt(
#         prompt_text=prompt,
#         scene_id="S001",
#         project_slug="fruit_ep1",
#         tags=["mango", "cherry", "flirt"],
#     )
#
#     # Try to copy to clipboard
#     manager.copy_to_clipboard(prompt)
