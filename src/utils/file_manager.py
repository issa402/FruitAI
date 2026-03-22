"""
================================================================================
FILE: src/utils/file_manager.py
================================================================================

╔══════════════════════════════════════════════════════════════════════════════╗
║          🎓 FAANG-LEVEL LESSON: FILE SYSTEMS, PATHLIB, AND ORGANIZATION     ║
╚══════════════════════════════════════════════════════════════════════════════╝

WHAT IS THIS FILE?
──────────────────
Your file organization system. Every time you generate content, it goes
somewhere on disk. This file manages WHERE and HOW files are stored.

Problems it solves:
  - "I have a million images and can't find any of them"
  - "Which PNG goes with which scene?"
  - "I accidentally overwrote a good prompt file"
  - "I need to move all Scene 1 files to a project folder"


WHAT IS pathlib.Path? (THE MODERN WAY TO HANDLE FILES)
───────────────────────────────────────────────────────
pathlib was added in Python 3.4. FAANG companies use it exclusively.
The old way (os.path) is considered deprecated for new code.

OLD WAY (don't do this):
  import os
  path = os.path.join("assets", "scenes", "S001", "prompt.txt")
  if os.path.exists(path):
      with open(path, "r") as f:
          content = f.read()

NEW WAY (pathlib):
  from pathlib import Path
  path = Path("assets") / "scenes" / "S001" / "prompt.txt"
  if path.exists():
      content = path.read_text()  # One-liner!

Key pathlib methods:
  path.exists()          → True if exists on disk
  path.is_file()         → True if it's a file (not folder)
  path.is_dir()          → True if it's a directory
  path.mkdir(parents=True, exist_ok=True)  → Create folder (and parents)
  path.read_text()       → Read file content as string
  path.write_text(data)  → Write string to file
  path.stem              → Filename without extension ("scene1" from "scene1.mp4")
  path.suffix            → Extension (".mp4" from "scene1.mp4")
  path.name              → Filename with extension ("scene1.mp4")
  path.parent            → Parent folder path
  path.glob("*.json")    → Find all JSON files in folder (returns generator)
  path.rglob("*.json")   → Find all JSONs recursively in all subfolders
  path.stat().st_size    → File size in bytes
  path.rename(new_path)  → Move/rename a file
  path.unlink()          → Delete a file (CAREFUL!)
  shutil.copy2(src, dst) → Copy a file (use shutil, NOT path.copy — deprecated)


WHAT IS shutil?
───────────────
shutil (Shell Utilities) = Python's module for file OPERATIONS.
  shutil.copy2(src, dst)         → Copy file (preserves metadata)
  shutil.copytree(src, dst)      → Copy entire folder recursively
  shutil.move(src, dst)          → Move file or folder
  shutil.rmtree(path)            → Delete folder and all contents (DANGEROUS!)
  shutil.make_archive(...)       → Create zip/tar archives

Rule: For file PATHS → pathlib. For file OPERATIONS → shutil.


AUTO-NAMING FILES: THE FAANG WAY
──────────────────────────────────
Files like "output.png", "image1.png", "final.png" are terrible names.
You'll never know what they are in 3 months.

GOOD naming convention:
  {project}_{scene_id}_{type}_{timestamp}.{ext}
  "fruit_ep1_S001_video_20240315_143022.mp4"

Even better:
  {project}/{scene_id}/{type}_{timestamp}.{ext}
  "fruit_ep1/S001/video_20240315_143022.mp4"

This is called "namespacing by hierarchy" — used in:
  AWS S3: bucket/year/month/day/filename
  Google Cloud Storage: bucket/project/entity/id/file
  Netflix: show/season/episode/asset/version


WHAT IS datetime.strftime()?
─────────────────────────────
strftime = "string format time" — converts datetime to a formatted string.

  from datetime import datetime
  now = datetime.now()
  now.strftime("%Y%m%d_%H%M%S")  # → "20240315_143022"
  now.strftime("%Y-%m-%d")        # → "2024-03-15"
  now.strftime("%B %d, %Y")       # → "March 15, 2024"

Used for:
  - Timestamped filenames (prevent overwriting)
  - Log entries
  - Report headers


WHAT IS VERSIONING?
────────────────────
At FAANG, EVERY asset is versioned — you never overwrite the original.

Simple version example:
  prompt_v1.txt  → Your first attempt
  prompt_v2.txt  → After refinement
  prompt_v3.txt  → Final version used

Or timestamp-based (no conflicts even in parallel):
  prompt_20240315_143022.txt
  prompt_20240315_144500.txt

Git uses SHA hashes:
  8f14e45f → Version 1 of the code
  b14a7b8f → Version 2 of the code

For your project: timestamp-based versioning is simplest and best.


DIRECTORY TRAVERSAL (Finding files automatically)
──────────────────────────────────────────────────
  # Find all video files in the scenes folder:
  videos = list(Path("assets/scenes").rglob("*.mp4"))

  # Find all JSON files named "scene.json":
  scene_files = list(Path("assets").rglob("scene.json"))

  # Filter: find all files modified in the last day:
  import time
  cutoff = time.time() - 86400  # 86400 seconds = 1 day
  recent = [p for p in Path("assets").rglob("*") if p.stat().st_mtime > cutoff]

This is how file managers work. You will use this to build:
  "Show me everything generated today"
  "Find all images for this character"
  "Clean up old files I haven't used"

================================================================================
"""

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# TODO 1: Implement "create_project_structure(project_slug)" as a standalone function
#   It should create ALL the folders for a new project in one call:
#   assets/projects/{slug}/, assets/scenes/{slug}/, assets/characters/, etc.
#
# TODO 2: Add "find_all_videos()" that finds every .mp4 and .mov in assets/
#   Return them as a list of Path objects sorted by modification time
#
# TODO 3: Add "find_orphaned_frames()" — frames that exist but whose
#   scene ID can't be found in any project.json (cleanup tool)
#
# TODO 4: Add "backup_project(project_slug)" that copies the entire project
#   to a backup folder with a timestamp:
#   backup/fruit_ep1_backup_20240315_143022/
#
# TODO 5: Add "get_disk_usage()" that shows how much disk space each
#   project folder is using (in MB). Use path.stat().st_size
# ─────────────────────────────────────────────────────────────────────────────


# ═══════════════════════════════════════════════════════════════════════════
# FULL CODE (try it yourself first!)
# ═══════════════════════════════════════════════════════════════════════════

# class FileManager:
#     """
#     File system organization and management for the Fruit Love Island pipeline.
#
#     Handles:
#     - Creating standardized folder structures for new projects
#     - Auto-naming files with timestamps (no more "final_final2.png")
#     - Finding and organizing existing assets
#     - Backing up projects before making changes
#     - Disk usage tracking
#
#     Usage:
#         fm = FileManager()
#         fm.setup_project("fruit_ep1")          # Create all folders
#         path = fm.get_scene_path("fruit_ep1", "S001", "video")  # Get file path
#         fm.backup_project("fruit_ep1")          # Backup before changes
#     """
#
#     # The root directory for all project assets
#     # Everything lives under this path for clean organization
#     ROOT = Path("assets")
#
#     STRUCTURE = {
#         "projects":    ROOT / "projects",
#         "scenes":      ROOT / "scenes",
#         "characters":  ROOT / "characters",
#         "prompts":     ROOT / "prompts" / "library",
#         "frames":      ROOT / "frames",
#         "processed":   ROOT / "processed",
#         "exports":     Path("exports"),
#         "backups":     Path("backups"),
#     }
#
#     def __init__(self):
#         # Ensure base directories exist on initialization
#         for name, path in self.STRUCTURE.items():
#             path.mkdir(parents=True, exist_ok=True)
#         logger.info("FileManager initialized. Base directories ready.")
#
#     def setup_project(self, project_slug: str) -> Dict[str, Path]:
#         """
#         Create the complete folder structure for a new project.
#
#         One call creates:
#           assets/projects/{slug}/
#           assets/scenes/{slug}/
#           exports/{slug}/
#
#         Args:
#             project_slug: Unique project identifier ("fruit_ep1")
#
#         Returns:
#             Dict mapping folder names to their created Paths.
#         """
#         project_dirs = {
#             "project":  self.STRUCTURE["projects"] / project_slug,
#             "scenes":   self.STRUCTURE["scenes"] / project_slug,
#             "exports":  self.STRUCTURE["exports"] / project_slug,
#         }
#
#         for dir_name, dir_path in project_dirs.items():
#             dir_path.mkdir(parents=True, exist_ok=True)
#
#         logger.info(f"Project structure created for: {project_slug}")
#         print(f"✅ Project '{project_slug}' folder structure ready.")
#         return project_dirs
#
#     def setup_scene(self, project_slug: str, scene_id: str) -> Path:
#         """
#         Create the folder for a specific scene.
#
#         Creates: assets/scenes/{project_slug}/{scene_id}/
#
#         Returns the scene folder path.
#         """
#         scene_dir = self.STRUCTURE["scenes"] / project_slug / scene_id
#         scene_dir.mkdir(parents=True, exist_ok=True)
#         return scene_dir
#
#     def generate_filename(
#         self,
#         project_slug: str,
#         scene_id: str,
#         file_type: str,
#         extension: str = "txt",
#     ) -> str:
#         """
#         Generate a standardized, timestamped filename.
#
#         Format: {project}_{scene_id}_{type}_{timestamp}.{ext}
#         Example: "fruit_ep1_S001_video_prompt_20240315_143022.txt"
#
#         This prevents overwriting files and makes sorting by date easy.
#         """
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         return f"{project_slug}_{scene_id}_{file_type}_{timestamp}.{extension}"
#
#     def get_scene_path(
#         self,
#         project_slug: str,
#         scene_id: str,
#         file_type: str = "scene",
#         extension: str = "json",
#     ) -> Path:
#         """
#         Get the standardized path for a scene file.
#
#         Args:
#             project_slug: Project identifier
#             scene_id: Scene identifier ("S001")
#             file_type: What the file contains ("scene", "prompt", "frame")
#             extension: File extension without dot
#
#         Returns:
#             Path object for the file.
#         """
#         scene_dir = self.STRUCTURE["scenes"] / project_slug / scene_id
#         scene_dir.mkdir(parents=True, exist_ok=True)
#         return scene_dir / f"{file_type}.{extension}"
#
#     def find_all_videos(self, search_path: Optional[str] = None) -> List[Path]:
#         """
#         Find all video files in the assets directory.
#
#         Returns paths sorted by modification time (newest first).
#         """
#         search_root = Path(search_path) if search_path else self.ROOT
#
#         # rglob = recursive glob (searches all subdirectories)
#         video_extensions = ["*.mp4", "*.mov", "*.webm", "*.avi", "*.mkv"]
#         videos = []
#         for pattern in video_extensions:
#             videos.extend(search_root.rglob(pattern))
#
#         # Sort by modification time, newest first
#         return sorted(videos, key=lambda p: p.stat().st_mtime, reverse=True)
#
#     def find_assets_for_scene(
#         self,
#         project_slug: str,
#         scene_id: str,
#     ) -> Dict[str, List[Path]]:
#         """
#         Find all files associated with a specific scene.
#
#         Returns a dict categorizing files by type:
#         {"images": [...], "videos": [...], "prompts": [...]}
#         """
#         scene_dir = self.STRUCTURE["scenes"] / project_slug / scene_id
#
#         if not scene_dir.exists():
#             return {"images": [], "videos": [], "prompts": []}
#
#         all_files = list(scene_dir.rglob("*"))
#         return {
#             "images": [f for f in all_files if f.suffix in (".png", ".jpg", ".webp")],
#             "videos": [f for f in all_files if f.suffix in (".mp4", ".mov", ".webm")],
#             "prompts": [f for f in all_files if f.suffix in (".txt", ".json")],
#         }
#
#     def backup_project(self, project_slug: str) -> Path:
#         """
#         Create a timestamped backup of an entire project.
#
#         FAANG rule: BEFORE making any significant change, BACKUP FIRST.
#         This is also the "version control" substitute if not using Git.
#
#         Returns:
#             Path to the backup folder.
#         """
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         backup_name = f"{project_slug}_backup_{timestamp}"
#         backup_path = self.STRUCTURE["backups"] / backup_name
#
#         project_dir = self.STRUCTURE["projects"] / project_slug
#         scenes_dir = self.STRUCTURE["scenes"] / project_slug
#
#         backup_path.mkdir(parents=True, exist_ok=True)
#
#         # Copy project metadata
#         if project_dir.exists():
#             shutil.copytree(project_dir, backup_path / "project", dirs_exist_ok=True)
#
#         # Copy scene data
#         if scenes_dir.exists():
#             shutil.copytree(scenes_dir, backup_path / "scenes", dirs_exist_ok=True)
#
#         logger.info(f"✅ Project backed up to: {backup_path}")
#         print(f"✅ Backup created: {backup_path}")
#         return backup_path
#
#     def get_disk_usage(self) -> Dict[str, str]:
#         """
#         Get disk usage for each project folder in MB.
#
#         Returns:
#             Dict mapping folder names to their size (e.g., {"fruit_ep1": "24.3 MB"})
#         """
#         usage = {}
#         for section, base_path in self.STRUCTURE.items():
#             if not base_path.exists():
#                 continue
#             total_bytes = sum(
#                 f.stat().st_size
#                 for f in base_path.rglob("*")
#                 if f.is_file()
#             )
#             usage[section] = f"{total_bytes / (1024 * 1024):.1f} MB"
#         return usage
#
#     def print_directory_tree(self, max_depth: int = 3) -> None:
#         """Print a visual tree of the assets directory structure."""
#         def _print_tree(path: Path, prefix: str = "", depth: int = 0):
#             if depth > max_depth:
#                 return
#             items = sorted(path.iterdir()) if path.is_dir() else []
#             for i, item in enumerate(items):
#                 connector = "└── " if i == len(items) - 1 else "├── "
#                 size = f" ({item.stat().st_size} bytes)" if item.is_file() else ""
#                 print(f"{prefix}{connector}{item.name}{size}")
#                 if item.is_dir():
#                     extension = "    " if i == len(items) - 1 else "│   "
#                     _print_tree(item, prefix + extension, depth + 1)
#
#         print(f"\n📁 {self.ROOT.absolute()}")
#         _print_tree(self.ROOT)
#
#
# # ─────────────────────────────────────────────────────────────────────────────
# # EXAMPLE: python src/utils/file_manager.py
# # ─────────────────────────────────────────────────────────────────────────────
# if __name__ == "__main__":
#     fm = FileManager()
#
#     # Create a project structure
#     fm.setup_project("fruit_ep1")
#     fm.setup_scene("fruit_ep1", "S001")
#     fm.setup_scene("fruit_ep1", "S002")
#
#     # Print the directory tree
#     fm.print_directory_tree()
#
#     # Check disk usage
#     usage = fm.get_disk_usage()
#     print("\n📊 Disk Usage:")
#     for folder, size in usage.items():
#         print(f"  {folder:<20} {size}")
