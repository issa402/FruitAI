"""
================================================================================
FILE: src/core/config.py
================================================================================

╔══════════════════════════════════════════════════════════════════════════════╗
║          🎓 FAANG-LEVEL LESSON: CONFIGURATION MANAGEMENT & .env FILES       ║
╚══════════════════════════════════════════════════════════════════════════════╝

WHAT IS THIS FILE?
──────────────────
Centralized configuration. Every setting that might change (paths, API keys,
feature flags, limits) lives HERE — not scattered across 20 files.

"Never hardcode what you can configure." — Engineering principle at every FAANG


WHAT IS A .env FILE?
─────────────────────
A .env (dot-env) file stores secret configuration that should NEVER be
committed to Git or shared with anyone.

Contents of .env:
  OPENAI_API_KEY=sk-proj-abc123...
  GEMINI_API_KEY=AIzaSy...
  DATABASE_PATH=pipeline.db

In Python, you load it with python-dotenv:
  from dotenv import load_dotenv
  import os
  load_dotenv()                                 # Loads .env into environment
  api_key = os.getenv("OPENAI_API_KEY")         # Gets the value

RULE #1: NEVER put API keys in your code. Always use .env.
RULE #2: ALWAYS add .env to .gitignore (so it's never committed).
RULE #3: ALWAYS provide a .env.example file (with fake values as template).


WHY ENVIRONMENT VARIABLES?
────────────────────────────
At FAANG companies, different environments exist:
  LOCAL (your computer):     small database, debug logs, test keys
  STAGING (test server):     production-like, but test data, test keys
  PRODUCTION (real server):  real users, real keys, no debug logs

Configuration changes PER environment. Environment variables handle this:
  - In local: OPENAI_API_KEY=your_test_key
  - In production: OPENAI_API_KEY=real_production_key (set in server dashboard)

Code NEVER changes. Only environment variables change. This is The Way™.


WHAT IS A DATACLASS FOR CONFIG?
────────────────────────────────
Using a dataclass for config gives you:
  1. Type hints (you know what type each config value is)
  2. Defaults (sensible values if not set)
  3. IDE autocompletion (type config. and see all options)
  4. Validation (ensure required values are set)

Without config class:
  MINIMUM_IMAGE_WIDTH = 512      # Global variable — easy to accidentally override
  DATABASE_PATH = "pipeline.db"   # Scattered, no organization

With config class:
  cfg = Config()
  cfg.database.path              # Organized, namespaced
  cfg.quality.min_image_width    # Clear, readable, discoverable


WHAT IS logging.basicConfig?
──────────────────────────────
logging.basicConfig configures the Python logging system globally.
Call it ONCE at startup (in config or main.py).

  logging.basicConfig(
      level=logging.INFO,           # Show INFO and above. DEBUG=verbose, WARNING=quiet
      format="%(asctime)s %(name)s %(levelname)s %(message)s",  # Log format
      handlers=[
          logging.StreamHandler(),             # Print to console
          logging.FileHandler("app.log"),      # Write to file
      ]
  )

Log levels (from quietest to loudest):
  CRITICAL → Only show crashes
  ERROR    → Show errors
  WARNING  → Show warnings + errors
  INFO     → Show general info (recommended for production)
  DEBUG    → Show everything (use when debugging)

Google's logging infrastructure handles BILLIONS of log entries per second.
At your scale: don't worry about that. Just set up basic file logging.


WHAT IS A SINGLETON CLASS? (Revisited)
────────────────────────────────────────
Config should be a Singleton — loaded once, shared everywhere.

The simplest Python Singleton:
  class Config:
      _instance = None

      def __new__(cls):
          if cls._instance is None:
              cls._instance = super().__new__(cls)
          return cls._instance

  # Now:
  cfg1 = Config()
  cfg2 = Config()
  cfg1 is cfg2  # True! Same object.

This ensures config is read from disk only ONCE at startup.
Then every other file just calls Config() or Config.get_instance()
and gets the same pre-loaded object.

================================================================================
"""

import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# TODO 1: Create a .env file in your project root with:
#   OPENAI_API_KEY=your_key_here
#   GEMINI_API_KEY=your_key_here
#   Then: pip install python-dotenv
#   And: from dotenv import load_dotenv; load_dotenv()
#   Then: api_key = os.getenv("OPENAI_API_KEY")
#
# TODO 2: Add a "DEBUG_MODE" env variable that controls log verbosity:
#   if os.getenv("DEBUG_MODE", "false").lower() == "true":
#       logging.basicConfig(level=logging.DEBUG)
#
# TODO 3: Implement the Singleton pattern for Config class
#   Override __new__ to ensure only one instance exists
#
# TODO 4: Add validation: if a required setting is None, raise ValueError
#   with a helpful message like "Set OPENAI_API_KEY in your .env file"
#
# TODO 5: Add a method "print_config()" that prints all settings
#   (BUT masks API keys: show only last 4 chars: "...ab12")
# ─────────────────────────────────────────────────────────────────────────────


# ═══════════════════════════════════════════════════════════════════════════
# FULL CODE (try it yourself first!)
# ═══════════════════════════════════════════════════════════════════════════

# def setup_logging(log_level: str = "INFO", log_file: Optional[str] = "logs/pipeline.log") -> None:
#     """
#     Configure the Python logging system.
#     Call this ONCE at application startup (in main.py).
#
#     Args:
#         log_level: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
#         log_file: Path to log file. None = console only.
#     """
#     level = getattr(logging, log_level.upper(), logging.INFO)
#
#     # Create the logs folder if logging to a file
#     if log_file:
#         Path(log_file).parent.mkdir(parents=True, exist_ok=True)
#
#     handlers = [logging.StreamHandler()]  # Always log to console
#     if log_file:
#         handlers.append(logging.FileHandler(log_file, encoding="utf-8"))
#
#     logging.basicConfig(
#         level=level,
#         format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
#         datefmt="%Y-%m-%d %H:%M:%S",
#         handlers=handlers,
#         force=True,  # Override any previous basicConfig calls
#     )
#     logger.info(f"Logging configured: level={log_level}, file={log_file}")
#
#
# class Config:
#     """
#     Centralized configuration for the Fruit Love Island pipeline.
#
#     All settings live here. Change here = changes everywhere.
#
#     Usage:
#         cfg = Config()
#         cfg.setup()              # Load .env and configure logging
#         key = cfg.openai_key     # Get API key
#         if cfg.has_openai:       # Check if API is available
#             # use it
#     """
#
#     _instance: Optional["Config"] = None
#
#     def __new__(cls) -> "Config":
#         """Singleton: only one Config instance ever exists."""
#         if cls._instance is None:
#             cls._instance = super().__new__(cls)
#         return cls._instance
#
#     def setup(self, env_file: str = ".env") -> None:
#         """
#         Load environment variables and configure logging.
#         Call once at the start of main.py.
#         """
#         # Load .env file if it exists (suppresses errors if missing)
#         try:
#             from dotenv import load_dotenv
#             loaded = load_dotenv(env_file, override=False)
#             if loaded:
#                 logger.info(f"Loaded environment from: {env_file}")
#             else:
#                 logger.info("No .env file found. Using system environment variables.")
#         except ImportError:
#             logger.warning("python-dotenv not installed. Run: pip install python-dotenv")
#
#         # Configure logging based on environment
#         log_level = os.getenv("LOG_LEVEL", "INFO")
#         setup_logging(log_level=log_level)
#
#     # ─────────────────────────────────────────────────────────────────────────
#     # API KEYS (from .env file)
#     # ─────────────────────────────────────────────────────────────────────────
#
#     @property
#     def openai_key(self) -> Optional[str]:
#         """OpenAI API key. Set as OPENAI_API_KEY in .env"""
#         return os.getenv("OPENAI_API_KEY")
#
#     @property
#     def gemini_key(self) -> Optional[str]:
#         """Google Gemini API key. Set as GEMINI_API_KEY in .env"""
#         return os.getenv("GEMINI_API_KEY")
#
#     @property
#     def has_openai(self) -> bool:
#         """True if OpenAI API key is configured."""
#         return bool(self.openai_key)
#
#     @property
#     def has_gemini(self) -> bool:
#         """True if Gemini API key is configured."""
#         return bool(self.gemini_key)
#
#     # ─────────────────────────────────────────────────────────────────────────
#     # PATHS (configurable, with defaults)
#     # ─────────────────────────────────────────────────────────────────────────
#
#     @property
#     def database_path(self) -> str:
#         return os.getenv("DATABASE_PATH", "pipeline.db")
#
#     @property
#     def assets_dir(self) -> Path:
#         return Path(os.getenv("ASSETS_DIR", "assets"))
#
#     @property
#     def exports_dir(self) -> Path:
#         return Path(os.getenv("EXPORTS_DIR", "exports"))
#
#     @property
#     def templates_dir(self) -> Path:
#         return Path(os.getenv("TEMPLATES_DIR", "templates"))
#
#     # ─────────────────────────────────────────────────────────────────────────
#     # QUALITY SETTINGS
#     # ─────────────────────────────────────────────────────────────────────────
#
#     @property
#     def min_image_width(self) -> int:
#         return int(os.getenv("MIN_IMAGE_WIDTH", "512"))
#
#     @property
#     def min_image_height(self) -> int:
#         return int(os.getenv("MIN_IMAGE_HEIGHT", "512"))
#
#     @property
#     def default_scene_duration(self) -> int:
#         """Default scene duration in seconds (your AI generator = 6 seconds)."""
#         return int(os.getenv("DEFAULT_SCENE_DURATION", "6"))
#
#     # ─────────────────────────────────────────────────────────────────────────
#     # UTILITY METHODS
#     # ─────────────────────────────────────────────────────────────────────────
#
#     def _mask_key(self, key: Optional[str]) -> str:
#         """Mask an API key for safe display. Shows last 4 chars only."""
#         if not key:
#             return "NOT SET"
#         return f"...{key[-4:]}"
#
#     def print_config(self) -> None:
#         """Print current configuration (masks sensitive keys)."""
#         print(f"\n{'='*55}")
#         print(f"⚙️  FRUIT LOVE ISLAND PIPELINE CONFIG")
#         print(f"{'='*55}")
#         print(f"  Database:       {self.database_path}")
#         print(f"  Assets:         {self.assets_dir}")
#         print(f"  Exports:        {self.exports_dir}")
#         print(f"  OpenAI Key:     {self._mask_key(self.openai_key)}")
#         print(f"  Gemini Key:     {self._mask_key(self.gemini_key)}")
#         print(f"  Min Image:      {self.min_image_width}x{self.min_image_height}px")
#         print(f"  Scene Duration: {self.default_scene_duration}s")
#         print(f"{'='*55}\n")
#
#
# # ─────────────────────────────────────────────────────────────────────────────
# # EXAMPLE: python src/core/config.py
# # ─────────────────────────────────────────────────────────────────────────────
# if __name__ == "__main__":
#     cfg = Config()
#     cfg.setup()
#     cfg.print_config()
