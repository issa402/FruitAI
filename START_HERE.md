# 🍑 FRUIT LOVE ISLAND — START HERE
## Your Complete Learning Roadmap + Project Guide

> This is the ONLY file you need to read first. It tells you exactly what to do, in what order, and why. No guessing.

---

## ⚡ THE GOLDEN RULE

Every single file in this project follows the SAME structure:

```
📚  BIG LESSON AT TOP     ← Read it once, slowly. Real knowledge here.
✅  TODO EXERCISES         ← Try to build it yourself first.
💻  FULL CODE AT BOTTOM    ← Commented out. Uncomment when stuck.
▶️  EXAMPLE BLOCK          ← Un-comment the if __name__ == "__main__" block to test.
```

**Your job:** Try the TODOs → Get stuck → Uncomment the solution → Compare → Understand.

---

## 📁 FULL PROJECT MAP

```
Fruit-Love_ID/
│
│   START_HERE.md              ← YOU ARE HERE
│   main.py                    ← Week 4: The full interactive menu app
│   requirements.txt           ← Week 1: Install dependencies
│   .env.example               ← Week 3: Copy to .env, add your API keys
│   .gitignore                 ← Already set up. Never commit .env!
│
├── src/
│   │
│   ├── models/                ← WEEK 1–2: Start here. Core data structures.
│   │   ├── character.py       ← FILE 1: Build your Character class
│   │   ├── scene.py           ← FILE 2: Build your Scene class (6-sec clip)
│   │   ├── project.py         ← FILE 3: Build your Project class (episode)
│   │   └── __init__.py
│   │
│   ├── prompts/               ← WEEK 2: Prompt generation system
│   │   ├── manager.py         ← FILE 4: The "Prompt Factory"
│   │   ├── library.py         ← FILE 5: Search/save/export prompts
│   │   └── __init__.py
│   │
│   ├── utils/                 ← WEEK 3: Automation tools
│   │   ├── image_processor.py ← FILE 6: Combine images, check quality
│   │   ├── video_processor.py ← FILE 7: Extract last frame from videos
│   │   ├── file_manager.py    ← FILE 8: Organize all your files
│   │   └── __init__.py
│   │
│   └── core/                  ← WEEK 3: Foundation systems
│       ├── database.py        ← FILE 9: SQLite database (track everything)
│       ├── config.py          ← FILE 10: Settings, API keys, logging
│       └── __init__.py
│
├── templates/
│   └── prompt_templates.yaml  ← All your prompt templates. Edit freely.
│
├── tests/
│   └── test_character.py      ← Week 4: Verify your code works correctly
│
└── assets/                    ← Your content lives here (git-ignored large files)
    ├── characters/            ← character.save() puts files here
    ├── scenes/                ← scene.save() puts files here
    ├── frames/                ← Extracted last-frames go here
    ├── prompts/library/       ← Saved prompts searchable library
    └── projects/              ← project.save() puts files here
```

---

## 🗺️ YOUR LEARNING ROADMAP

### WEEK 1 — Master File 1: `character.py`
**This is the most important file. Master it and you know 60% of Python OOP.**

**What you'll learn:**
- `@dataclass` — Python's way to auto-generate class boilerplate
- `__post_init__` — runs after `__init__` for validation/auto-generation
- `__repr__` — makes your objects print nicely in the terminal
- `@classmethod` — methods you call on the CLASS (not an instance)
- `json.dump / json.load` — save Python objects to disk and load them back
- `pathlib.Path` — modern cross-platform file paths

**Step-by-step for this file:**

1. Open `src/models/character.py`
2. Read the entire lesson at the top (lines 1–172)
3. Try to write `Character` class yourself using only the TODO hints
4. Scroll to the bottom — uncomment the `if __name__ == "__main__"` block
5. Run it: `python src/models/character.py`
6. You should see:
```
=== CHARACTER INFO ===
Character(name='Mango Man', role='contestant', scenes=0)

=== IMAGE PROMPT ===
Use ONLY the character shown in image 1. Do NOT redesign...

=== VIDEO PROMPT ===
Use ONLY the provided image exactly as it is...
...Camera stays 100% locked. No zooming, no panning...

✅ Character saved: assets/characters/mango_man/character.json

=== LOADED FROM DISK ===
Character(name='Mango Man', role='contestant', scenes=0)
```
7. Now open `assets/characters/mango_man/character.json` and read the saved data.

---

### WEEK 2 — Files 2, 3, 4: Scene + Project + Prompts

#### File 2: `src/models/scene.py`
**What you'll learn:**
- `Enum` — fixed sets of valid values (prevents typo bugs)
- Composition — scene CONTAINS characters (HAS-A relationship)
- `SceneCharacter` — the "association class" linking character to scene roles
- `create_continuation()` — automates your screenshot workflow

**Step-by-step:**
1. Read the lesson at top (pay close attention to the Continuity section)
2. Try the TODOs, especially `get_speaker()` and `create_continuation()`
3. Uncomment the `if __name__ == "__main__"` block at the bottom
4. Run it: `python src/models/scene.py`
5. You should see Scene 1 and Scene 2 prompts printed — ready to paste into AI

#### File 3: `src/models/project.py`
**What you'll learn:**
- Aggregate Root pattern — Project is the entry point to all scenes
- `@property` — computed attributes (no parentheses)
- `__len__`, `__contains__`, `__repr__` — dunder/magic methods
- `export_prompts()` — generate a single text file with ALL prompts

#### File 4: `src/prompts/manager.py`
**What you'll learn:**
- Manager Pattern — one class responsible for one type of operation
- `string.Template` — safe placeholder substitution (`$variable`)
- YAML templates — human-editable config for prompts
- `pyperclip` — auto-copy the generated prompt to clipboard

**This is your #1 time-saver.** After this file is working:
```python
manager = PromptManager()
prompt = manager.generate_flirt_scene_prompt(
    speaker_name="Mango Man",
    dialogue="You know… being here with you? Yeah… it hits different.",
    listener_name="Chocolate Cherry",
)
manager.copy_to_clipboard(prompt)  # Auto-copied! Just paste into AI.
```

---

### WEEK 3 — Files 5–10: Automation Tools + Core Systems

#### File 5: `src/prompts/library.py`
**What you'll learn:**
- Repository Pattern — one place to access all saved prompts
- List comprehensions — `[p for p in all if "mango" in p["tags"]]`
- Sorting with lambda — `sorted(prompts, key=lambda p: p["created_at"])`
- Soft delete — never permanently delete data (FAANG rule)

#### File 6: `src/utils/image_processor.py`
**Install first:** `pip install Pillow`

**What you'll learn:**
- Pillow (PIL) — Python's image library
- Image composition — pasting two images onto a canvas
- EXIF metadata — embedding prompts inside image files

**This automates your Google Docs combine workflow:**
```python
processor = ImageProcessor()
processor.combine_side_by_side("char1.png", "char2.png")
# → saves combined.png in assets/processed/
```

#### File 7: `src/utils/video_processor.py`
**Install first:** `pip install opencv-python`

**What you'll learn:**
- OpenCV (cv2) — video/image processing library
- `subprocess` — call external programs (ffmpeg) from Python
- Frame extraction — get the last frame of a video automatically

**This automates your screenshot workflow:**
```python
processor = VideoProcessor()
processor.extract_continuation_frame("scene1_output.mp4")
# → saves scene1_output_continuation_frame.png automatically
```

#### File 8: `src/utils/file_manager.py`
**What you'll learn:**
- `pathlib.Path` advanced usage — `glob()`, `rglob()`, `stat()`
- `shutil` — copy/move/backup entire folders
- Timestamped auto-naming — `fruit_ep1_S001_video_20240315_143022.txt`
- Directory trees — `find_all_videos()`, print folder structure

#### File 9: `src/core/database.py`
**Install:** No install needed — SQLite is built into Python

**What you'll learn:**
- SQL (Structured Query Language) — SELECT, INSERT, UPDATE, DELETE
- SQLite — a full database stored in ONE file (`pipeline.db`)
- Transactions — all-or-nothing operations (ACID properties)
- The Repository pattern applied to a database

**Tool to visualize your database:** Download [DB Browser for SQLite](https://sqlitebrowser.org/) (free). Open `pipeline.db` and see your data visually.

#### File 10: `src/core/config.py`
**Install first:** `pip install python-dotenv`

**What you'll learn:**
- `.env` files — where API keys live (NEVER in code)
- `os.getenv()` — read environment variables safely
- Singleton pattern — one config object shared by everything
- `logging.basicConfig()` — set up the logging system ONCE

**Setup:**
```bash
copy .env.example .env
# Edit .env and add your real API keys when you get them
```

---

### WEEK 4 — `main.py` + Tests

#### `main.py` — The Full App
**What you'll learn:**
- `if __name__ == "__main__"` — why this matters
- `argparse` — command-line arguments
- REPL loop — `while True: input() → process → print → repeat`
- Dependency injection — passing services into functions

**To run the full interactive app:**
```bash
python main.py
```
You'll see a menu like:
```
  1. Generate Flirt Scene Prompt
  2. Generate Zipline Host Prompt
  3. Combine Two Character Images
  4. Extract Last Frame from Video
  ...
```

#### `tests/test_character.py` — Verify Your Code
**Install first:** `pip install pytest`

**What you'll learn:**
- `pytest` — Python's test runner
- AAA pattern — Arrange, Act, Assert
- Fixtures — reusable test setup
- Mocking — test without real API calls

**Run tests:**
```bash
pytest tests/ -v
```

---

## ⚙️ SETUP (Do This First, Right Now)

```bash
# Step 1: Create a virtual environment
python -m venv venv

# Step 2: Activate it
venv\Scripts\activate      # Windows

# Step 3: Install core dependencies
pip install Pillow PyYAML pyperclip python-dotenv

# Step 4: Install video and testing tools
pip install opencv-python pytest

# Step 5: Copy the .env example
copy .env.example .env
# (edit .env later when you have API keys)

# Step 6: Run your first file!
python src/models/character.py
```

---

## 🔁 HOW THE WHOLE SYSTEM CONNECTS

Here's the data flow when you create a complete scene:

```
1. Create character objects
   character.py → Character("Mango Man") → save to assets/characters/mango_man/

2. Create a scene
   scene.py → Scene(scene_number=1, characters=[mango, cherry])
             → add dialogue to speakers
             → generate_video_prompt() → copy-paste into AI video tool

3. AI generates your video → you save the .mp4

4. Extract last frame for continuity
   video_processor.py → extract_continuation_frame("scene1.mp4")
                      → saves "scene1_continuation_frame.png"

5. Register the frame + create next scene
   scene1.set_continuation_frame("scene1_continuation_frame.png")
   scene2 = scene1.create_continuation()
   scene2.characters[0].dialogue = "Relax Mango... I'm still deciding."

6. Generate scene 2 prompt
   scene2.generate_video_prompt() → copy-paste into AI

7. Save everything to database
   database.py → save_scene(scene1), save_scene(scene2), save_character(mango)

8. Export all prompts for the day
   project.export_prompts() → fruit_ep1_prompts.txt (all in one file!)
```

---

## 📋 PAIN POINT → SOLUTION TABLE

| Your Current Workflow | File That Fixes It | Method |
|---|---|---|
| Re-typing 400-word prompts | `src/prompts/manager.py` | `generate_flirt_scene_prompt()` |
| AI redesigning characters | `src/models/character.py` | `generate_image_prompt()` stores spec |
| Screenshot → Google Docs → combine | `src/utils/image_processor.py` | `combine_side_by_side()` |
| Manually screenshot last video frame | `src/utils/video_processor.py` | `extract_continuation_frame()` |
| Forgetting which prompt worked | `src/prompts/library.py` | `search("mango")` |
| Files named "output_final_2.png" | `src/utils/file_manager.py` | Auto-timestamped naming |
| Losing track of scene order | `src/models/project.py` | `add_scene_id()` + `export_prompts()` |
| Characters disappear between sessions | `src/core/database.py` | Persistent SQLite storage |
| API key in code → security risk | `src/core/config.py` | `.env` file loading |

---

## 🔑 QUICK REFERENCE: KEY PYTHON CONCEPTS BY FILE

| Concept | File | Line Range |
|---|---|---|
| `@dataclass` | `character.py` | Lesson: top 172 lines |
| `__post_init__` | `character.py` | ~line 287 in commented code |
| `@classmethod` | `character.py` | `Character.load()` |
| `json.dump/load` | `character.py` | `save()` and `load()` methods |
| `Enum` | `scene.py` | `SceneStatus`, `SceneType` |
| Composition (HAS-A) | `scene.py` | `Scene` contains `SceneCharacter` |
| `@property` | `project.py` | `total_scenes`, `completion_percentage` |
| `__len__`, `__contains__` | `project.py` | Magic methods |
| `string.Template` | `manager.py` | `fill_template()` |
| Repository Pattern | `library.py` | `get_all()`, `search()` |
| Pillow image ops | `image_processor.py` | `combine_side_by_side()` |
| OpenCV video | `video_processor.py` | `extract_continuation_frame()` |
| `pathlib` advanced | `file_manager.py` | `rglob()`, `stat()` |
| SQL + SQLite | `database.py` | Full CRUD + schema |
| `.env` + Singleton | `config.py` | `Config` class |
| HTTP APIs | `services/llm.py` | `LLMService` |
| `pytest` | `tests/test_character.py` | Full test suite |
| CLI (`argparse`, REPL) | `main.py` | `run_interactive_cli()` |

---

> [!IMPORTANT]
> **START WITH:** `python src/models/character.py`
> That's it. That's your first task. Everything else flows from there.

> [!TIP]
> **When you get stuck:** Scroll to the bottom of the file you're in. The full working code is there, commented out. Uncomment it, run it, then write it yourself to understand it.

> [!NOTE]
> **How long does this take?**
> - Week 1 (character.py) → 2–4 hours over a few days
> - Week 2 (scene, project, prompts) → 3–5 hours
> - Week 3 (utils, database, config) → 4–6 hours
> - Week 4 (main.py, tests) → 2–3 hours
> Total: 11–18 focused hours to go from zero to a working automated pipeline.
> But honestly? After just Week 1–2, your workflow is already 10x faster.
