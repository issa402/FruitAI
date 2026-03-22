"""
================================================================================
FILE: src/core/database.py
================================================================================

╔══════════════════════════════════════════════════════════════════════════════╗
║            🎓 FAANG-LEVEL LESSON: DATABASES, SQL, AND SQLITE                ║
╚══════════════════════════════════════════════════════════════════════════════╝

WHAT IS THIS FILE?
──────────────────
Your local database. Instead of loading 100 JSON files to search for
something, a database answers queries in milliseconds.

Why you need this eventually:
  "Show me all scenes where Mango Man was the speaker"
  "How many scenes has Chocolate Cherry appeared in?"
  "Find every prompt that used 'flirty tone' and was marked approved"

With JSON files: You'd load EVERY file and filter in Python (slow, messy)
With SQLite: One line query returns exactly what you need (fast, clean)


WHAT IS A DATABASE?
────────────────────
A database is organized storage for structured data.
Think of it like a SPREADSHEET, but:
  - Can handle millions of rows efficiently
  - Can link tables together (like Excel VLOOKUP, but way better)
  - Can be queried with a powerful language (SQL)
  - Prevents data corruption (transactions, ACID properties)

Your tables:
  characters  → One row per character
  scenes      → One row per scene clip
  prompts     → One row per saved prompt
  projects    → One row per project


WHAT IS SQL? (Structured Query Language)
──────────────────────────────────────────
SQL is the language for talking to databases. It's the #1 most-used
data language in the world. Every FAANG engineer knows SQL.

Basic SQL vocabulary:
  CREATE TABLE → Create a new table (like creating a spreadsheet)
  INSERT INTO  → Add a new row
  SELECT       → Get rows you want
  UPDATE       → Change a row
  DELETE       → Remove a row (soft-delete is better!)
  WHERE        → Filter rows by condition
  JOIN         → Combine two tables

Examples:
  SELECT * FROM scenes WHERE project_slug = 'fruit_ep1';
  SELECT COUNT(*) FROM scenes WHERE status = 'completed';
  INSERT INTO characters (name, slug, role) VALUES ('Mango Man', 'mango_man', 'contestant');
  UPDATE scenes SET status = 'approved' WHERE scene_id = 'S001';


WHAT IS SQLite?
────────────────
SQLite = A full SQL database stored in a SINGLE FILE (e.g., pipeline.db).

Why SQLite (not MySQL, PostgreSQL)?
  → No server to set up or run
  → One file, portable, works everywhere
  → Built into Python (no pip install needed!)
  → Perfect for local tools, apps under 1M rows

Used in:
  - Android and iOS apps (every app has SQLite)
  - Firefox stores bookmarks in SQLite
  - Python itself uses SQLite internally

For your project: SQLite is PERFECT. No complexity, just a .db file.

If you outgrow it later → upgrade to PostgreSQL (same SQL, different server).


WHAT IS "import sqlite3"?
──────────────────────────
sqlite3 is INCLUDED with Python. No pip install needed.

Basic workflow:
  import sqlite3

  # Connect (creates the file if it doesn't exist)
  conn = sqlite3.connect("pipeline.db")

  # Create a cursor (executes SQL commands)
  cursor = conn.cursor()

  # Execute SQL
  cursor.execute("CREATE TABLE IF NOT EXISTS characters (id INTEGER PRIMARY KEY, name TEXT)")

  # Insert data
  cursor.execute("INSERT INTO characters (name) VALUES (?)", ("Mango Man",))

  # ALWAYS commit changes (saves to disk)
  conn.commit()

  # Query data
  cursor.execute("SELECT * FROM characters")
  rows = cursor.fetchall()  # [ (1, "Mango Man"), (2, "Chocolate Cherry") ]

  # ALWAYS close when done
  conn.close()


WHAT IS A CONTEXT MANAGER (with statement)?
────────────────────────────────────────────
The "with" statement automatically closes the connection when done:

  with sqlite3.connect("pipeline.db") as conn:
      cursor = conn.cursor()
      cursor.execute("SELECT * FROM characters")
  # conn is automatically closed here, even if an error occurred!

This is the CORRECT way to use files and databases.
Without "with": if your code crashes, the file/db stays open (LEAK).


WHAT IS A TRANSACTION?
────────────────────────
A transaction is a group of SQL operations that either ALL succeed
or ALL fail — never partially.

Example: "Create a scene AND update the project's scene count"
  Without transaction: Scene created, but crash → project count not updated → INCONSISTENT data
  With transaction: Either BOTH happen, or NEITHER does → always consistent

  cursor.execute("BEGIN")
  try:
      cursor.execute("INSERT INTO scenes ...")
      cursor.execute("UPDATE projects SET scene_count = scene_count + 1 ...")
      conn.commit()  # Both succeed!
  except:
      conn.rollback()  # Both fail → database stays clean

ACID Properties (what makes a database reliable):
  Atomicity  → All or nothing (transactions)
  Consistency → Data is always valid
  Isolation  → Concurrent operations don't interfere
  Durability → Committed data survives crashes

This is what separates a real database from JSON files.


WHAT IS AN ORM? (Object-Relational Mapper)
────────────────────────────────────────────
An ORM lets you use Python objects instead of raw SQL.

Raw SQL:
  cursor.execute("INSERT INTO characters (name, slug) VALUES (?, ?)", (name, slug))

With an ORM (SQLAlchemy or Django ORM):
  db.add(Character(name=name, slug=slug))
  db.commit()

For your learning: START with raw SQL (understand what's happening).
Later: Move to SQLAlchemy (what FAANG companies use for complex apps).

===========================================================================================
"""

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# TODO 1: Connect to the database and inspect it with DB Browser for SQLite
#   Download: https://sqlitebrowser.org/
#   Open pipeline.db and see your tables visually
#
# TODO 2: Write a query that returns all scenes for a specific project:
#   SELECT * FROM scenes WHERE project_slug = 'fruit_ep1'
#
# TODO 3: Add a new table "exports" that tracks every time you export prompts:
#   (id, project_slug, export_path, exported_at)
#
# TODO 4: Learn about JOIN. Write a query that shows scenes WITH character names:
#   SELECT s.scene_id, c.name FROM scenes s
#   JOIN scene_characters sc ON s.id = sc.scene_id
#   JOIN characters c ON sc.character_slug = c.slug
#
# TODO 5: Add a method "get_production_stats()" that returns:
#   total characters, total scenes, total prompts, total projects
# ─────────────────────────────────────────────────────────────────────────────


# ═══════════════════════════════════════════════════════════════════════════
# FULL CODE (try it yourself first!)
# ═══════════════════════════════════════════════════════════════════════════

# # SQL CREATE TABLE statements (the schema)
# # TEXT = string, INTEGER = number, REAL = float, PRIMARY KEY = unique identifier
# # UNIQUE = no duplicates. NOT NULL = required. DEFAULT = if not provided.
# # This is DDL (Data Definition Language) — how you define the shape of your data.
# SCHEMA: str = """
# CREATE TABLE IF NOT EXISTS characters (
#     id              INTEGER PRIMARY KEY AUTOINCREMENT,
#     name            TEXT    NOT NULL,
#     slug            TEXT    NOT NULL UNIQUE,
#     role            TEXT    DEFAULT 'contestant',
#     description     TEXT    DEFAULT '',
#     style_notes     TEXT    DEFAULT '',
#     personality     TEXT    DEFAULT '',
#     reference_image TEXT,
#     created_at      TEXT    NOT NULL,
#     updated_at      TEXT    NOT NULL
# );
#
# CREATE TABLE IF NOT EXISTS projects (
#     id              INTEGER PRIMARY KEY AUTOINCREMENT,
#     name            TEXT    NOT NULL,
#     slug            TEXT    NOT NULL UNIQUE,
#     description     TEXT    DEFAULT '',
#     series          TEXT    DEFAULT '',
#     status          TEXT    DEFAULT 'active',
#     created_at      TEXT    NOT NULL,
#     updated_at      TEXT    NOT NULL
# );
#
# CREATE TABLE IF NOT EXISTS scenes (
#     id              INTEGER PRIMARY KEY AUTOINCREMENT,
#     scene_id        TEXT    NOT NULL,
#     scene_number    INTEGER NOT NULL,
#     project_slug    TEXT    NOT NULL REFERENCES projects(slug),
#     scene_type      TEXT    DEFAULT 'flirt',
#     environment     TEXT    DEFAULT 'beach at sunset',
#     duration_secs   INTEGER DEFAULT 6,
#     status          TEXT    DEFAULT 'draft',
#     is_continuation INTEGER DEFAULT 0,
#     continuation_frame_path TEXT,
#     video_output_path TEXT,
#     director_notes  TEXT    DEFAULT '',
#     created_at      TEXT    NOT NULL,
#     updated_at      TEXT    NOT NULL,
#     UNIQUE(scene_id, project_slug)
# );
#
# CREATE TABLE IF NOT EXISTS scene_characters (
#     id              INTEGER PRIMARY KEY AUTOINCREMENT,
#     scene_id        TEXT    NOT NULL,
#     project_slug    TEXT    NOT NULL,
#     character_slug  TEXT    NOT NULL REFERENCES characters(slug),
#     role            TEXT    DEFAULT 'listener',
#     dialogue        TEXT    DEFAULT '',
#     tone_override   TEXT    DEFAULT ''
# );
#
# CREATE TABLE IF NOT EXISTS prompts (
#     id              INTEGER PRIMARY KEY AUTOINCREMENT,
#     scene_id        TEXT,
#     project_slug    TEXT,
#     prompt_type     TEXT    DEFAULT 'video',
#     prompt_text     TEXT    NOT NULL,
#     tags            TEXT    DEFAULT '[]',
#     notes           TEXT    DEFAULT '',
#     favorite        INTEGER DEFAULT 0,
#     is_deleted      INTEGER DEFAULT 0,
#     created_at      TEXT    NOT NULL
# );
# """
#
#
# class Database:
#     """
#     SQLite database interface for the Fruit Love Island pipeline.
#
#     Provides a clean Python API over raw SQL operations.
#     Every operation is wrapped in proper error handling and logging.
#
#     Usage:
#         db = Database()
#         db.save_character(character_dict)
#         db.save_scene(scene_dict)
#         scenes = db.get_scenes_for_project("fruit_ep1")
#     """
#
#     def __init__(self, db_path: str = "pipeline.db"):
#         self.db_path = Path(db_path)
#         self._initialize()
#
#     def _get_connection(self) -> sqlite3.Connection:
#         """
#         Create a database connection.
#         row_factory = sqlite3.Row makes rows act like dicts:
#           row["name"] instead of row[0]
#         """
#         conn = sqlite3.connect(str(self.db_path))
#         conn.row_factory = sqlite3.Row
#         return conn
#
#     def _initialize(self) -> None:
#         """Run the schema SQL to create tables if they don't exist."""
#         with self._get_connection() as conn:
#             # executescript runs multiple SQL statements at once
#             conn.executescript(SCHEMA)
#         logger.info(f"Database initialized: {self.db_path}")
#
#     # ─────────────────────────────────────────────────────────────────────────
#     # CHARACTER OPERATIONS
#     # ─────────────────────────────────────────────────────────────────────────
#
#     def save_character(self, character_data: Dict[str, Any]) -> bool:
#         """
#         Insert or update a character record.
#         Uses "INSERT OR REPLACE" = upsert (insert if not exists, replace if does).
#         """
#         try:
#             with self._get_connection() as conn:
#                 conn.execute("""
#                     INSERT OR REPLACE INTO characters
#                     (name, slug, role, description, style_notes, personality,
#                      reference_image, created_at, updated_at)
#                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
#                 """, (
#                     character_data.get("name"),
#                     character_data.get("slug"),
#                     character_data.get("role", "contestant"),
#                     character_data.get("description", ""),
#                     character_data.get("style_notes", ""),
#                     character_data.get("personality", ""),
#                     character_data.get("reference_image_path"),
#                     character_data.get("created_at", datetime.now().isoformat()),
#                     datetime.now().isoformat(),
#                 ))
#             logger.info(f"Saved character: {character_data.get('slug')}")
#             return True
#         except sqlite3.Error as e:
#             logger.error(f"Failed to save character: {e}")
#             return False
#
#     def get_character(self, slug: str) -> Optional[Dict[str, Any]]:
#         """Get a character by slug. Returns dict or None."""
#         with self._get_connection() as conn:
#             row = conn.execute(
#                 "SELECT * FROM characters WHERE slug = ?", (slug,)
#             ).fetchone()
#         return dict(row) if row else None
#
#     def get_all_characters(self) -> List[Dict[str, Any]]:
#         """Get all characters, sorted by name."""
#         with self._get_connection() as conn:
#             rows = conn.execute(
#                 "SELECT * FROM characters ORDER BY name ASC"
#             ).fetchall()
#         return [dict(row) for row in rows]
#
#     # ─────────────────────────────────────────────────────────────────────────
#     # SCENE OPERATIONS
#     # ─────────────────────────────────────────────────────────────────────────
#
#     def save_scene(self, scene_data: Dict[str, Any]) -> bool:
#         """Insert or update a scene record."""
#         try:
#             with self._get_connection() as conn:
#                 conn.execute("""
#                     INSERT OR REPLACE INTO scenes
#                     (scene_id, scene_number, project_slug, scene_type, environment,
#                      duration_secs, status, is_continuation, continuation_frame_path,
#                      video_output_path, director_notes, created_at, updated_at)
#                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#                 """, (
#                     scene_data.get("scene_id"),
#                     scene_data.get("scene_number"),
#                     scene_data.get("project_slug"),
#                     scene_data.get("scene_type", "flirt"),
#                     scene_data.get("environment", "beach at sunset"),
#                     scene_data.get("duration_seconds", 6),
#                     scene_data.get("status", "draft"),
#                     int(scene_data.get("is_continuation", False)),
#                     scene_data.get("continuation_frame_path"),
#                     scene_data.get("video_output_path"),
#                     scene_data.get("director_notes", ""),
#                     scene_data.get("created_at", datetime.now().isoformat()),
#                     datetime.now().isoformat(),
#                 ))
#             logger.info(f"Saved scene: {scene_data.get('scene_id')}")
#             return True
#         except sqlite3.Error as e:
#             logger.error(f"Failed to save scene: {e}")
#             return False
#
#     def get_scenes_for_project(self, project_slug: str) -> List[Dict[str, Any]]:
#         """Get all scenes for a project, ordered by scene number."""
#         with self._get_connection() as conn:
#             rows = conn.execute(
#                 "SELECT * FROM scenes WHERE project_slug = ? ORDER BY scene_number ASC",
#                 (project_slug,)
#             ).fetchall()
#         return [dict(row) for row in rows]
#
#     def get_scenes_for_character(self, character_slug: str) -> List[Dict[str, Any]]:
#         """Find all scenes involving a character (via scene_characters join table)."""
#         with self._get_connection() as conn:
#             rows = conn.execute("""
#                 SELECT s.*
#                 FROM scenes s
#                 JOIN scene_characters sc ON s.scene_id = sc.scene_id
#                     AND s.project_slug = sc.project_slug
#                 WHERE sc.character_slug = ?
#                 ORDER BY s.project_slug, s.scene_number
#             """, (character_slug,)).fetchall()
#         return [dict(row) for row in rows]
#
#     # ─────────────────────────────────────────────────────────────────────────
#     # PROMPT OPERATIONS
#     # ─────────────────────────────────────────────────────────────────────────
#
#     def save_prompt(self, prompt_data: Dict[str, Any]) -> bool:
#         """Insert a new prompt record."""
#         try:
#             with self._get_connection() as conn:
#                 conn.execute("""
#                     INSERT INTO prompts
#                     (scene_id, project_slug, prompt_type, prompt_text,
#                      tags, notes, favorite, created_at)
#                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)
#                 """, (
#                     prompt_data.get("scene_id"),
#                     prompt_data.get("project_slug"),
#                     prompt_data.get("prompt_type", "video"),
#                     prompt_data.get("prompt", ""),
#                     json.dumps(prompt_data.get("tags", [])),
#                     prompt_data.get("notes", ""),
#                     int(prompt_data.get("favorite", False)),
#                     datetime.now().isoformat(),
#                 ))
#             return True
#         except sqlite3.Error as e:
#             logger.error(f"Failed to save prompt: {e}")
#             return False
#
#     def search_prompts(self, keyword: str) -> List[Dict[str, Any]]:
#         """Search prompts by keyword in text, notes, or tags."""
#         with self._get_connection() as conn:
#             rows = conn.execute("""
#                 SELECT * FROM prompts
#                 WHERE is_deleted = 0
#                 AND (
#                     prompt_text LIKE ?
#                     OR notes LIKE ?
#                     OR tags LIKE ?
#                 )
#                 ORDER BY created_at DESC
#             """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")).fetchall()
#         return [dict(row) for row in rows]
#
#     def get_favorites(self) -> List[Dict[str, Any]]:
#         """Get all favorite prompts."""
#         with self._get_connection() as conn:
#             rows = conn.execute(
#                 "SELECT * FROM prompts WHERE favorite = 1 AND is_deleted = 0"
#             ).fetchall()
#         return [dict(row) for row in rows]
#
#     def get_production_stats(self) -> Dict[str, int]:
#         """Return a dict of counts across all tables."""
#         with self._get_connection() as conn:
#             return {
#                 "characters": conn.execute("SELECT COUNT(*) FROM characters").fetchone()[0],
#                 "projects":   conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0],
#                 "scenes":     conn.execute("SELECT COUNT(*) FROM scenes").fetchone()[0],
#                 "prompts":    conn.execute("SELECT COUNT(*) FROM prompts WHERE is_deleted=0").fetchone()[0],
#                 "favorites":  conn.execute("SELECT COUNT(*) FROM prompts WHERE favorite=1").fetchone()[0],
#                 "completed_scenes": conn.execute(
#                     "SELECT COUNT(*) FROM scenes WHERE status='completed'"
#                 ).fetchone()[0],
#             }
#
#
# # ─────────────────────────────────────────────────────────────────────────────
# # EXAMPLE: python src/core/database.py
# # ─────────────────────────────────────────────────────────────────────────────
# if __name__ == "__main__":
#     db = Database()
#
#     # Insert a character
#     db.save_character({
#         "name": "Mango Man",
#         "slug": "mango_man",
#         "role": "contestant",
#         "description": "A tall tropical mango fruit character.",
#         "created_at": datetime.now().isoformat(),
#     })
#
#     # Query it back
#     result = db.get_character("mango_man")
#     print("From DB:", result)
#
#     # Print production stats
#     stats = db.get_production_stats()
#     print("\n📊 Production Stats:")
#     for key, val in stats.items():
#         print(f"  {key:<25} {val}")
