"""
================================================================================
FILE: src/models/__init__.py
================================================================================

╔══════════════════════════════════════════════════════════════════════════════╗
║           🎓 FAANG-LEVEL LESSON: PYTHON PACKAGES AND __init__.py            ║
╚══════════════════════════════════════════════════════════════════════════════╝

WHAT IS __init__.py?
──────────────────────
Every folder that contains Python files needs an __init__.py to be treated
as a "package" (a Python module you can import from).

Without it:
  from src.models.character import Character   # Works
  from src.models import Character              # ❌ FAILS

With it (and the right imports inside):
  from src.models import Character              # ✅ Works!

This is the STANDARD way Python projects are organized.


WHY IMPORT EVERYTHING HERE?
─────────────────────────────
This file acts as the "public API" of the models package.

Without __init__.py:
  # Every file that uses Character must write:
  from src.models.character import Character
  from src.models.scene import Scene, SceneCharacter, SceneType, SceneStatus
  from src.models.project import Project

With __init__.py:
  # Every file just writes:
  from src.models import Character, Scene, Project

This is called "re-exporting" — you expose only what other code needs.


WHAT IS __all__?
─────────────────
__all__ is a list that tells Python WHICH names to export when someone
does "from src.models import *".

Without __all__:
  from src.models import *   # Imports EVERYTHING (messy, unpredictable)

With __all__:
  __all__ = ["Character", "Scene"]
  from src.models import *   # ONLY imports Character and Scene

At FAANG companies, __all__ is required in every __init__.py.
It explicitly documents what is public vs private.


WHAT DOES "re-exporting" LOOK LIKE IN PRODUCTION?
───────────────────────────────────────────────────
Django (Meta's framework) does this:
  # django/db/models/__init__.py
  from django.db.models.base import Model
  from django.db.models.fields import Field, CharField, IntegerField
  # etc.

  # Then you just write: from django.db import models

This is the clean, professional way.

================================================================================
"""

# ─────────────────────────────────────────────────────────────────────────────
# TODO 1: Understand why this file exists
#   - Delete this file temporarily. Try importing Character from src.models.
#   - See the error? That's what __init__.py prevents.
#   - Add it back.
#
# TODO 2: Add a new model (when you create it)
#   - Once you create src/models/prompt_template.py with class PromptTemplate
#   - Add: from src.models.prompt_template import PromptTemplate
#   - Add "PromptTemplate" to __all__
#
# TODO 3: Understand __all__ by testing it
#   - Remove a class from __all__ but keep the import
#   - Do "from src.models import *" in a test file
#   - Notice the removed class is NOT imported
# ─────────────────────────────────────────────────────────────────────────────


# ═══════════════════════════════════════════════════════════════════════════
# FULL CODE (try it yourself first!)
# ═══════════════════════════════════════════════════════════════════════════

# # Import all public classes from each model file
# # This makes them available as: from src.models import Character
# from src.models.character import Character
# from src.models.scene import Scene, SceneCharacter, SceneStatus, SceneType
# from src.models.project import Project
#
# # __all__ explicitly declares the public API of this package
# # Only these names will be exported with "from src.models import *"
# __all__ = [
#     "Character",
#     "Scene",
#     "SceneCharacter",
#     "SceneStatus",
#     "SceneType",
#     "Project",
# ]
