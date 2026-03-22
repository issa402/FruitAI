"""
================================================================================
FILE: src/prompts/library.py
================================================================================

╔══════════════════════════════════════════════════════════════════════════════╗
║         🎓 FAANG-LEVEL LESSON: SEARCH, FILTERING & DATA ACCESS PATTERNS     ║
╚══════════════════════════════════════════════════════════════════════════════╝

WHAT IS THIS FILE?
──────────────────
The PromptLibrary is your personal "Google" for prompts. Instead of digging
through folders trying to remember which prompt worked for what — you search.

library = PromptLibrary()
library.search("zipline")          # Find all zipline prompts
library.get_by_character("mango")  # All prompts with Mango Man
library.get_favorites()            # Your saved best prompts
library.export_for_session()       # "Print me everything for today's work"


WHAT IS THE REPOSITORY PATTERN? (Used at every FAANG company)
──────────────────────────────────────────────────────────────
The Repository Pattern is a data access layer that separates:
  - HOW data is stored (files, database, cloud)
  - FROM how it's used (search, filter, display)

Without Repository pattern:
  # Every file that needs prompts writes file-reading code
  import json
  files = [f for f in Path("assets/prompts").glob("*.json")]
  results = []
  for f in files:
      data = json.load(open(f))
      if "mango" in data["prompt"]:
          results.append(data)
  # Duplicated in 5 different places!

With Repository pattern:
  library = PromptLibrary()
  results = library.get_by_character("mango")
  # One place that does this. Clean. Reusable.

This is exactly what Django's ORM (Object-Relational Mapper) does:
  Post.objects.filter(author="Isaac")  ← That's a Repository pattern call!


WHAT IS A GENERATOR IN PYTHON? (Memory-efficient iteration)
─────────────────────────────────────────────────────────────
A generator is a special function that yields values one at a time
instead of loading everything into memory at once.

NORMAL function (loads ALL files into memory):
  def get_all_prompts():
      results = []
      for f in files:
          results.append(json.load(f))
      return results  # 1000 files = all loaded at once!

GENERATOR (loads ONE file at a time):
  def get_all_prompts():
      for f in files:
          yield json.load(f)  # yields one, then pauses

Usage:
  for prompt in library.get_all_prompts():
      print(prompt)  # Processes ONE at a time — much lower memory

Netflix uses generators to process millions of rows without loading
them all into memory. For your project: maybe 100 prompts, so generators
are optional but good to learn.


LIST COMPREHENSIONS vs FILTER (FAANG interviews LOVE this)
────────────────────────────────────────────────────────────
List comprehension (Python's preferred):
  results = [p for p in all_prompts if "mango" in p["tags"]]

This is equivalent to:
  results = []
  for p in all_prompts:
      if "mango" in p["tags"]:
          results.append(p)

Both work. List comprehensions are more "Pythonic" (idiomatic).
FAANG interviews test this. Know both.

With multiple conditions:
  results = [
      p for p in all_prompts
      if "mango" in p["tags"]
      and p["prompt_type"] == "video"
      and not p["is_deleted"]
  ]


WHAT IS SORTING WITH A KEY FUNCTION?
──────────────────────────────────────
sorted() takes an optional key function that determines how to sort.

Simple sort:
  sorted(["banana", "apple", "cherry"])  # ["apple", "banana", "cherry"]

Sort by a specific field:
  prompts = [{"name": "Scene 3"}, {"name": "Scene 1"}, {"name": "Scene 2"}]
  sorted(prompts, key=lambda p: p["name"])  # Scene 1, Scene 2, Scene 3

Sort descending:
  sorted(prompts, key=lambda p: p["created_at"], reverse=True)

Lambda = tiny anonymous function. lambda p: p["name"] means:
  "Given p, return p['name'] as the sort key"

Google uses this pattern constantly for ranking search results.


WHAT IS FUZZY SEARCH?
──────────────────────
Fuzzy search = finding matches even with typos or partial words.
Your use case: "mangi" still finds "mango_man" prompts.

Libraries:
  thefuzz (formerly fuzzywuzzy) — most popular, used by many FAANG tools
  rapidfuzz — faster version of thefuzz

Example:
  from thefuzz import fuzz
  score = fuzz.ratio("mango", "mangi")  # Returns 91 (out of 100)
  if score > 70:  # 70% match threshold
      results.append(prompt)

For your project: start with simple string search first.
Add fuzzy search when you notice typos causing misses.

================================================================================
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Iterator, Optional

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# TODO 1: Add a method "delete_prompt(filename)" that marks a prompt
#   as deleted (soft delete — sets is_deleted=True instead of deleting the file)
#   NEVER permanently delete data. Only soft-delete. (FAANG rule)
#
# TODO 2: Add a method "mark_favorite(filename, is_favorite=True)"
#   Updates the JSON file to set "favorite" field to True/False
#
# TODO 3: Add "sort_by_date(prompts)" and "sort_by_type(prompts)" methods
#   Use sorted() with a lambda key function (see lesson above)
#
# TODO 4: Add "export_session_prompts(project_slug)" that creates a
#   dated text file with all prompts for that project for today's session
#
# TODO 5: Implement a basic fuzzy search using string similarity
#   (without installing thefuzz — use Python's difflib.SequenceMatcher)
# ─────────────────────────────────────────────────────────────────────────────


# ═══════════════════════════════════════════════════════════════════════════
# FULL CODE (try it yourself first!)
# ═══════════════════════════════════════════════════════════════════════════

# class PromptLibrary:
#     """
#     Repository for saved AI prompts.
#
#     Think of this as your personal "prompt Google" — search, filter,
#     export, and organize your growing library of successful prompts.
#
#     Each prompt is stored as a JSON file with metadata:
#       - The full prompt text
#       - Which character/scene it's for
#       - Tags for searching
#       - Whether it was marked as a favorite
#       - When it was created
#
#     Usage:
#         library = PromptLibrary()
#         results = library.search("mango zipline")
#         favorites = library.get_favorites()
#         library.export_session_bundle("fruit_ep1")
#     """
#
#     def __init__(self, library_dir: str = "assets/prompts/library"):
#         self.library_dir = Path(library_dir)
#         self.library_dir.mkdir(parents=True, exist_ok=True)
#
#     # ─────────────────────────────────────────────────────────────────────────
#     # DATA ACCESS METHODS (the "Repository" interface)
#     # ─────────────────────────────────────────────────────────────────────────
#
#     def get_all(self, include_deleted: bool = False) -> List[Dict[str, Any]]:
#         """
#         Load all prompts from disk.
#
#         Args:
#             include_deleted: Whether to include soft-deleted prompts.
#
#         Returns:
#             List of prompt dicts, sorted by creation date (newest first).
#         """
#         prompts = []
#         for json_file in self.library_dir.glob("*.json"):
#             try:
#                 with open(json_file, "r", encoding="utf-8") as f:
#                     data = json.load(f)
#                 data["_filename"] = json_file.name  # Track filename for updates
#                 if not include_deleted and data.get("is_deleted", False):
#                     continue
#                 prompts.append(data)
#             except (json.JSONDecodeError, OSError) as e:
#                 logger.warning(f"Could not read {json_file.name}: {e}")
#
#         # Sort by created_at descending (newest first)
#         return sorted(
#             prompts,
#             key=lambda p: p.get("created_at", ""),
#             reverse=True,
#         )
#
#     def search(self, query: str) -> List[Dict[str, Any]]:
#         """
#         Search prompts by keyword (checks prompt text, notes, and tags).
#
#         Args:
#             query: Search term (case-insensitive). Multiple words search all.
#
#         Returns:
#             List of matching prompt dicts.
#         """
#         query_lower = query.lower()
#         query_words = query_lower.split()
#
#         results = []
#         for prompt in self.get_all():
#             # Build searchable text combining all text fields
#             searchable = " ".join([
#                 prompt.get("prompt", ""),
#                 prompt.get("notes", ""),
#                 " ".join(prompt.get("tags", [])),
#                 prompt.get("scene_id", ""),
#                 prompt.get("project_slug", ""),
#             ]).lower()
#
#             # ALL words must appear (AND search, not OR)
#             if all(word in searchable for word in query_words):
#                 results.append(prompt)
#
#         logger.info(f"Search '{query}' → {len(results)} results")
#         return results
#
#     def get_by_character(self, character_slug: str) -> List[Dict[str, Any]]:
#         """Get all prompts related to a specific character."""
#         return self.search(character_slug)
#
#     def get_by_project(self, project_slug: str) -> List[Dict[str, Any]]:
#         """Get all prompts for a specific project."""
#         all_prompts = self.get_all()
#         return [p for p in all_prompts if p.get("project_slug") == project_slug]
#
#     def get_by_type(self, prompt_type: str) -> List[Dict[str, Any]]:
#         """Get prompts by type: 'video', 'image', 'zipline', etc."""
#         all_prompts = self.get_all()
#         return [p for p in all_prompts if p.get("prompt_type") == prompt_type]
#
#     def get_favorites(self) -> List[Dict[str, Any]]:
#         """Get all prompts marked as favorites."""
#         return [p for p in self.get_all() if p.get("favorite", False)]
#
#     # ─────────────────────────────────────────────────────────────────────────
#     # MUTATION METHODS (updating prompt records)
#     # ─────────────────────────────────────────────────────────────────────────
#
#     def _update_field(self, filename: str, field: str, value: Any) -> bool:
#         """
#         Internal helper to update a single field in a prompt JSON file.
#         This is a private method — prefixed with underscore.
#
#         Args:
#             filename: The JSON filename (e.g., "fruit_ep1_S001_video_20240101.json")
#             field: The field to update
#             value: The new value
#
#         Returns:
#             bool: True if updated successfully, False otherwise.
#         """
#         file_path = self.library_dir / filename
#         if not file_path.exists():
#             logger.error(f"Cannot update — file not found: {filename}")
#             return False
#
#         try:
#             with open(file_path, "r", encoding="utf-8") as f:
#                 data = json.load(f)
#
#             data[field] = value
#             data["updated_at"] = datetime.now().isoformat()
#
#             with open(file_path, "w", encoding="utf-8") as f:
#                 json.dump(data, f, indent=2, ensure_ascii=False)
#
#             logger.info(f"Updated {field} in {filename}")
#             return True
#         except (json.JSONDecodeError, OSError) as e:
#             logger.error(f"Failed to update {filename}: {e}")
#             return False
#
#     def mark_favorite(self, filename: str, is_favorite: bool = True) -> bool:
#         """Mark or unmark a prompt as a favorite."""
#         return self._update_field(filename, "favorite", is_favorite)
#
#     def soft_delete(self, filename: str) -> bool:
#         """
#         Soft-delete a prompt (marks it as deleted, does NOT remove the file).
#         FAANG rule: NEVER permanently delete. Always soft-delete.
#         This way mistakes can be reversed.
#         """
#         return self._update_field(filename, "is_deleted", True)
#
#     def restore(self, filename: str) -> bool:
#         """Restore a soft-deleted prompt."""
#         return self._update_field(filename, "is_deleted", False)
#
#     # ─────────────────────────────────────────────────────────────────────────
#     # EXPORT METHODS
#     # ─────────────────────────────────────────────────────────────────────────
#
#     def export_session_bundle(
#         self,
#         project_slug: str,
#         output_dir: str = "exports",
#     ) -> Path:
#         """
#         Export all prompts for a project into one text file for today's session.
#         This is your "morning prep" tool — run it before you start work.
#         """
#         output_dir_path = Path(output_dir)
#         output_dir_path.mkdir(parents=True, exist_ok=True)
#
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M")
#         output_path = output_dir_path / f"{project_slug}_session_{timestamp}.txt"
#
#         prompts = self.get_by_project(project_slug)
#
#         lines = [
#             f"{'='*70}",
#             f"SESSION BUNDLE: {project_slug}",
#             f"EXPORTED: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
#             f"TOTAL PROMPTS: {len(prompts)}",
#             f"{'='*70}",
#             "",
#         ]
#
#         for i, prompt_data in enumerate(prompts, 1):
#             lines += [
#                 f"{'─'*70}",
#                 f"  [{i}] Scene: {prompt_data.get('scene_id', 'Unknown')}",
#                 f"  Type: {prompt_data.get('prompt_type', '?').upper()}",
#                 f"  Tags: {', '.join(prompt_data.get('tags', []))}",
#                 f"  Notes: {prompt_data.get('notes', 'None')}",
#                 f"{'─'*70}",
#                 prompt_data.get("prompt", "[No prompt text]"),
#                 "",
#             ]
#
#         output_path.write_text("\n".join(lines), encoding="utf-8")
#         print(f"✅ Session bundle exported: {output_path}")
#         return output_path
#
#     def print_summary(self) -> None:
#         """Print a human-readable summary of the library to console."""
#         all_prompts = self.get_all()
#         favorites = self.get_favorites()
#         by_type: Dict[str, int] = {}
#         for p in all_prompts:
#             t = p.get("prompt_type", "unknown")
#             by_type[t] = by_type.get(t, 0) + 1
#
#         print(f"\n{'='*50}")
#         print(f"📚 PROMPT LIBRARY SUMMARY")
#         print(f"{'='*50}")
#         print(f"Total prompts:    {len(all_prompts)}")
#         print(f"Favorites:        {len(favorites)}")
#         print(f"\nBy type:")
#         for ptype, count in by_type.items():
#             print(f"  {ptype:<20} {count}")
#         print(f"{'='*50}\n")
#
#
# # ─────────────────────────────────────────────────────────────────────────────
# # EXAMPLE: python src/prompts/library.py
# # ─────────────────────────────────────────────────────────────────────────────
# if __name__ == "__main__":
#     library = PromptLibrary()
#     library.print_summary()
#
#     results = library.search("mango")
#     print(f"Found {len(results)} prompts mentioning 'mango'")
