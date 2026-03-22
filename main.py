"""
================================================================================
FILE: main.py
================================================================================

╔══════════════════════════════════════════════════════════════════════════════╗
║            🎓 FAANG-LEVEL LESSON: ENTRY POINTS, CLI, AND ARGPARSE           ║
╚══════════════════════════════════════════════════════════════════════════════╝

WHAT IS main.py?
─────────────────
The entry point of your application. This is the file you RUN.
Every Python application should have ONE main entry point.

    python main.py                    ← Start the full system
    python main.py --mode cli         ← Start in CLI mode
    python main.py --project fruit_ep1 ← Work on a specific project

In Python, this pattern is:
    if __name__ == "__main__":
        main()

"if __name__ == '__main__'" means: "Only run THIS code if this file
is the one being directly executed. NOT when it's imported by another file."

This is THE most important Python pattern. FAANG engineers live by this.


WHAT IS argparse? (Command-Line Interface / CLI)
──────────────────────────────────────────────────
argparse is Python's built-in library for creating command-line interfaces.

Without argparse:
    python main.py fruit_ep1 flirt    # python main.py arg1 arg2
    sys.argv = ["main.py", "fruit_ep1", "flirt"]  # How you'd read them (bad)

With argparse:
    python main.py --project fruit_ep1 --mode flirt
    # Much clearer! Named arguments, help text, validation included.

Example:
    import argparse
    parser = argparse.ArgumentParser(description="Fruit Love Island Pipeline")
    parser.add_argument("--project", help="Project slug to work on")
    parser.add_argument("--mode", choices=["cli", "gui"], default="cli")
    args = parser.parse_args()
    print(args.project)  # "fruit_ep1"


WHAT IS AN "INTERACTIVE CLI"? (Command Loop)
─────────────────────────────────────────────
A CLI where you keep typing commands until you quit.

Pattern:
    while True:
        command = input(">>> ")
        if command == "quit":
            break
        elif command == "list":
            print_all_scenes()
        else:
            print(f"Unknown command: {command}")

This is what your main.py does: shows a menu, you pick an option, it runs,
then shows the menu again. Same pattern as Django's manage.py shell.


WHAT IS THE SEPARATION OF CONCERNS PRINCIPLE?
───────────────────────────────────────────────
main.py should be THIN. It should only:
  1. Parse arguments
  2. Set up config and logging
  3. Call the right handlers

It should NOT contain business logic. Business logic lives in:
  src/models/ → Data structures
  src/prompts/ → Prompt generation
  src/services/ → API calls
  src/utils/ → Helper tools

main.py is just the "conductor" — it calls the orchestra.

At Google: they call this the "main() function pattern."
main() sets up dependencies, then calls run().
Run() orchestrates the workflow.
Individual files handle their specific responsibilities.


WHAT IS A "MENU-DRIVEN" PROGRAM?
──────────────────────────────────
A program that shows choices and waits for your input.
This is how most automation tools start (before they get a GUI).

Your menu will look like:
    ╔══════════════════════════════╗
    ║  🍑 Fruit Love Island AI     ║
    ╠══════════════════════════════╣
    ║  1. Generate Scene Prompt    ║
    ║  2. Extract Last Video Frame ║
    ║  3. Combine Characters       ║
    ║  4. Search Prompt Library    ║
    ║  5. View Project Summary     ║
    ║  0. Quit                     ║
    ╚══════════════════════════════╝

This is called a "REPL" (Read-Evaluate-Print Loop):
  Read input → Evaluate (run code) → Print result → Loop back

Python's own interactive shell IS a REPL.

================================================================================
"""

# ─────────────────────────────────────────────────────────────────────────────
# TODO 1: Run this file first WITHOUT uncomment anything.
#   Notice that nothing happens — the code is all commented out.
#   Your first task is to uncomment the __main__ block at the bottom
#   and run: python main.py
#
# TODO 2: Add a menu option for "Create New Character"
#   - Ask user for name, description, role
#   - Create Character object
#   - Save it
#
# TODO 3: Add a menu option for "Generate Flirt Scene Prompt"
#   - Ask: Who is speaking?
#   - Ask: What do they say?
#   - Ask: Who is listening?
#   - Generate prompt → Print it → Save to library
#
# TODO 4: Add a menu option for "Extract Last Frame"
#   - Ask: Path to video file?
#   - Run VideoProcessor.extract_continuation_frame()
#   - Show: "Frame saved to: {path}"
#
# TODO 5: Add a menu option for "Combine Two Characters"
#   - Ask: Path to image 1 (character 1)?
#   - Ask: Path to image 2 (character 2)?
#   - Run ImageProcessor.combine_side_by_side()
#   - Show: "Combined image saved to: {path}"
# ─────────────────────────────────────────────────────────────────────────────


# ═══════════════════════════════════════════════════════════════════════════
# FULL CODE (try it yourself first!)
# ═══════════════════════════════════════════════════════════════════════════

# import logging
# import sys
# from pathlib import Path
#
# # Add the project root to Python's import path
# # This lets you do: from src.models import Character
# # Without this, Python won't find the src folder
# sys.path.insert(0, str(Path(__file__).parent))
#
# # Import our core modules
# from src.core.config import Config, setup_logging
# from src.models.character import Character
# from src.models.scene import Scene, SceneCharacter, SceneType
# from src.models.project import Project
# from src.prompts.manager import PromptManager
# from src.prompts.library import PromptLibrary
# from src.utils.image_processor import ImageProcessor
# from src.utils.video_processor import VideoProcessor
# from src.utils.file_manager import FileManager
# from src.core.database import Database
#
# logger = logging.getLogger(__name__)
#
#
# def print_banner() -> None:
#     """Print the application banner."""
#     print("""
#  ╔════════════════════════════════════════════════════════════╗
#  ║      🍑🍒🍉 FRUIT LOVE ISLAND AI PIPELINE 🍉🍒🍑           ║
#  ║          Your Content Automation System v1.0               ║
#  ╚════════════════════════════════════════════════════════════╝
#     """)
#
#
# def print_menu() -> None:
#     """Print the main menu."""
#     print("""
#  ┌────────────────────────────────────────────┐
#  │  🎬 MAIN MENU                              │
#  ├────────────────────────────────────────────┤
#  │  1. Generate Flirt Scene Prompt            │
#  │  2. Generate Zipline Host Prompt           │
#  │  3. Combine Two Character Images           │
#  │  4. Extract Last Frame from Video          │
#  │  5. Create New Character                   │
#  │  6. List All Characters                    │
#  │  7. Search Prompt Library                  │
#  │  8. View Project Summary                   │
#  │  9. Production Stats                       │
#  │                                            │
#  │  0. Quit                                   │
#  └────────────────────────────────────────────┘
#     """)
#
#
# def handle_generate_flirt_scene(manager: PromptManager, library: PromptLibrary) -> None:
#     """Handle the 'Generate Flirt Scene Prompt' menu option."""
#     print("\n🎬 GENERATE FLIRT SCENE PROMPT")
#     print("─" * 40)
#
#     speaker = input("Who is SPEAKING? (e.g., Mango Man): ").strip()
#     dialogue = input("What do they say? (exact words): ").strip()
#     tone = input("Delivery tone? (e.g., confident, warm, teasing): ").strip() or "playful, confident"
#     listener = input("Who is LISTENING? (e.g., Chocolate Cherry): ").strip()
#
#     prompt = manager.generate_flirt_scene_prompt(
#         speaker_name=speaker,
#         dialogue=dialogue,
#         tone=tone,
#         listener_name=listener,
#     )
#
#     print("\n" + "=" * 65)
#     print("✅ GENERATED PROMPT (copy and paste into your AI video tool):")
#     print("=" * 65)
#     print(prompt)
#     print("=" * 65)
#
#     # Try to copy to clipboard
#     manager.copy_to_clipboard(prompt)
#
#     # Save to library
#     scene_id = input("\nEnter scene ID (e.g., S001) or press Enter to skip: ").strip()
#     if scene_id:
#         project = input("Project slug (e.g., fruit_ep1): ").strip() or "default"
#         library.save_prompt_to_file(prompt, scene_id, project, "flirt")
#
#
# def handle_combine_characters(processor: ImageProcessor) -> None:
#     """Handle character image combination."""
#     print("\n🖼️  COMBINE TWO CHARACTER IMAGES")
#     print("(Replaces your Google Docs workflow!)")
#     print("─" * 40)
#
#     img1 = input("Path to Image 1 (Character on LEFT): ").strip().strip('"')
#     img2 = input("Path to Image 2 (Character on RIGHT): ").strip().strip('"')
#
#     if not img1 or not img2:
#         print("❌ Both image paths are required.")
#         return
#
#     try:
#         output = processor.combine_side_by_side(img1, img2)
#         print(f"✅ Combined image: {output}")
#         quality_ok = processor.is_quality_sufficient(str(output))
#         if not quality_ok:
#             print("⚠️  Quality might be low. Consider upscaling before AI submission.")
#     except Exception as e:
#         print(f"❌ Error: {e}")
#
#
# def handle_extract_frame(processor: VideoProcessor) -> None:
#     """Handle last frame extraction from video."""
#     print("\n🎥 EXTRACT LAST FRAME FROM VIDEO")
#     print("(Automates your screenshot workflow!)")
#     print("─" * 40)
#
#     video_path = input("Path to your video file: ").strip().strip('"')
#     if not video_path:
#         print("❌ Video path is required.")
#         return
#
#     try:
#         frame_path = processor.extract_continuation_frame(video_path)
#         print(f"✅ Last frame saved: {frame_path}")
#         print("💡 Use this image as the starting frame for your next scene!")
#     except Exception as e:
#         print(f"❌ Error: {e}")
#         print("Tips: Make sure OpenCV is installed: pip install opencv-python")
#
#
# def handle_list_characters(db: Database) -> None:
#     """Display all saved characters."""
#     characters = db.get_all_characters()
#     if not characters:
#         print("\n📭 No characters saved yet.")
#         print("Create your first character by choosing option 5 from the menu.")
#         return
#
#     print(f"\n👥 ALL CHARACTERS ({len(characters)} found):")
#     print("─" * 50)
#     for c in characters:
#         print(f"  {'●'} {c['name']:<20} │ Role: {c.get('role', '?'):<15} │ Slug: {c['slug']}")
#
#
# def handle_search_library(library: PromptLibrary) -> None:
#     """Handle prompt library search."""
#     query = input("\n🔍 Search prompt library (keyword): ").strip()
#     if not query:
#         return
#
#     results = library.search(query)
#     print(f"\nFound {len(results)} prompt(s) matching '{query}':")
#     for i, r in enumerate(results[:5], 1):  # Show max 5
#         preview = r.get("prompt", "")[:100].replace("\n", " ")
#         print(f"\n  [{i}] Scene: {r.get('scene_id', '?')} | Type: {r.get('prompt_type', '?')}")
#         print(f"      Preview: {preview}...")
#
#
# def run_interactive_cli(
#     manager: PromptManager,
#     library: PromptLibrary,
#     image_proc: ImageProcessor,
#     video_proc: VideoProcessor,
#     db: Database,
# ) -> None:
#     """
#     Main interactive command loop.
#     Runs until user selects 0 (Quit).
#     """
#     print_banner()
#
#     while True:
#         print_menu()
#         choice = input("Enter your choice (0-9): ").strip()
#
#         if choice == "0":
#             print("\n👋 Goodbye! Go create some fire content! 🍑🔥\n")
#             break
#         elif choice == "1":
#             handle_generate_flirt_scene(manager, library)
#         elif choice == "2":
#             dialogue = input("Zipline dialogue (leave empty for exit shot): ").strip()
#             exits = not bool(dialogue)
#             prompt = manager.generate_zipline_prompt(dialogue=dialogue, exits_frame=exits)
#             print("\n" + "=" * 65)
#             print(prompt)
#             print("=" * 65)
#             manager.copy_to_clipboard(prompt)
#         elif choice == "3":
#             handle_combine_characters(image_proc)
#         elif choice == "4":
#             handle_extract_frame(video_proc)
#         elif choice == "5":
#             name = input("Character name: ").strip()
#             if name:
#                 role = input("Role (contestant/host): ").strip() or "contestant"
#                 desc = input("Description (appearance): ").strip()
#                 char = Character(name=name, role=role, description=desc)
#                 char.save()
#                 db.save_character({"name": char.name, "slug": char.slug,
#                                    "role": char.role, "description": char.description,
#                                    "created_at": char.created_at})
#                 print(f"✅ Character '{name}' saved!")
#         elif choice == "6":
#             handle_list_characters(db)
#         elif choice == "7":
#             handle_search_library(library)
#         elif choice == "8":
#             projects = Project.list_all()
#             if projects:
#                 for slug in projects:
#                     try:
#                         p = Project.load(slug)
#                         print(f"\n  {p}")
#                     except Exception:
#                         pass
#             else:
#                 print("No projects found. Start by creating scenes!")
#         elif choice == "9":
#             stats = db.get_production_stats()
#             print("\n📊 PRODUCTION STATS:")
#             for k, v in stats.items():
#                 print(f"  {k:<25} {v}")
#         else:
#             print("❌ Invalid choice. Enter a number 0-9.")
#
#         input("\n[Press ENTER to continue...]")
#
#
# def main() -> None:
#     """
#     Application entry point.
#
#     Sets up: Config → Logging → Database → Services → CLI
#     Then runs the interactive menu.
#     """
#     # 1. Load configuration
#     cfg = Config()
#     cfg.setup()
#     cfg.print_config()
#
#     # 2. Initialize services
#     db = Database(db_path=cfg.database_path)
#     manager = PromptManager()
#     library = PromptLibrary()
#     image_proc = ImageProcessor()
#     video_proc = VideoProcessor()
#     fm = FileManager()
#
#     logger.info("All services initialized. Starting CLI...")
#
#     # 3. Run interactive CLI
#     run_interactive_cli(manager, library, image_proc, video_proc, db)
#
#
# if __name__ == "__main__":
#     main()
