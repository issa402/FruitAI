# 🍑 Fruit Love Island — AI Content Automation System

> **Your personal AI content pipeline. No more copy-paste hell.**

## What This Does
- Generates perfect video animation prompts every time
- Tracks every scene, character, and asset
- Manages your prompt library so you never lose a good one
- Chains your workflow: Image → Video → Extension → Continuity

## Project Structure
```
Fruit-Love_ID/
├── src/                    # All source code
│   ├── models/             # OOP Classes (Character, Scene, Prompt)
│   ├── prompts/            # Prompt templates and manager
│   ├── services/           # External API calls
│   ├── utils/              # Helper tools (image, video, file)
│   └── core/               # Database + Config
├── assets/                 # Your images, videos, prompts
│   ├── characters/         # Character reference images
│   ├── scenes/             # Scene outputs
│   ├── prompts/            # Saved prompt files
│   └── projects/           # Full project folders
├── templates/              # Reusable YAML prompt templates
├── tests/                  # Unit tests
├── scripts/                # One-click automation scripts
└── main.py                 # Entry point
```

## Quick Start
```bash
pip install -r requirements.txt
python main.py
```
