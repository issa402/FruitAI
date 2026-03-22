"""
================================================================================
FILE: tests/test_character.py
================================================================================

╔══════════════════════════════════════════════════════════════════════════════╗
║              🎓 FAANG-LEVEL LESSON: UNIT TESTING WITH pytest                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

WHAT IS TESTING?
─────────────────
Tests are code that verify your code WORKS correctly.
They catch bugs BEFORE they reach production.

At Google: 80%+ code coverage is required before merging.
At Meta: No PR (pull request) is approved without tests.
At Amazon: Tests run on every commit. No tests = no deployment.

For your project: Tests verify that:
  - Character.generate_image_prompt() always includes "Do NOT redesign"
  - Scene.create_continuation() correctly swaps speaker/listener roles
  - PromptManager always generates 6-second compatible prompts
  - Database.save_character() actually saves and loads correctly


WHAT IS pytest?
────────────────
pytest is THE industry-standard Python testing library.

Install: pip install pytest

Run all tests: pytest
Run specific test: pytest tests/test_character.py
Run with output: pytest -v (verbose)

A test function:
  def test_something():
      # Arrange: set up the data
      char = Character(name="Mango Man")

      # Act: call the code being tested
      result = char.generate_image_prompt("sitting on beach")

      # Assert: verify the result is correct
      assert "Do NOT redesign" in result
      assert "mango" in result.lower()
      # If the assertion fails → test FAILS → you know something broke


THE "AAA" PATTERN (Every test at FAANG follows this):
──────────────────────────────────────────────────────
Arrange → Act → Assert

  def test_character_saves_correctly():
      # ARRANGE: set up test data
      character = Character(name="Test Mango", slug="test_mango")

      # ACT: do the thing being tested
      saved_path = character.save("tests/temp")

      # ASSERT: verify the outcome
      assert saved_path.exists()
      loaded = Character.load("test_mango", "tests/temp")
      assert loaded.name == "Test Mango"

      # CLEANUP (optional): remove test files
      shutil.rmtree("tests/temp", ignore_errors=True)


WHAT IS A FIXTURE? (@pytest.fixture)
──────────────────────────────────────
A fixture is reusable test setup. Instead of creating the same objects
in every test, define it once as a fixture.

  @pytest.fixture
  def sample_character():
      return Character(name="Mango Man", slug="mango_test")

  def test_something(sample_character):  # ← pytest injects the fixture!
      assert sample_character.name == "Mango Man"

  def test_something_else(sample_character):  # Same fixture, reused!
      prompt = sample_character.generate_image_prompt()
      assert len(prompt) > 100


WHAT IS setUp/tearDown? (Test lifecycle)
──────────────────────────────────────────
Some tests need setup/cleanup:
  - Create temp files before test
  - Delete temp files after test

pytest's way: use tmp_path fixture (automatically gives you a temp folder)

  def test_saves_to_disk(tmp_path):
      char = Character(name="Test")
      char.save(str(tmp_path))  # Save to temp folder
      # pytest automatically deletes tmp_path after the test!
      assert (tmp_path / "test" / "character.json").exists()


WHAT IS MOCKING? (Testing WITHOUT calling real APIs)
──────────────────────────────────────────────────────
When your code calls an API, you don't want tests to make real API calls.
Why? Slow, costs money, requires internet, might fail for unrelated reasons.

Instead: MOCK the API (replace it with a fake that returns pre-set data).

  from unittest.mock import patch, MagicMock

  def test_llm_service(mock_openai):
      with patch("openai.OpenAI") as MockClient:
          MockClient.return_value.chat.completions.create.return_value.choices[0].message.content = "Mocked response"
          llm = LLMService(openai_api_key="fake-key")
          result = llm.ask("Test prompt")
          assert result == "Mocked response"  # Got the mocked value, not real API!

For your project: start without mocks (manual mode tests are fine).
Add mocks when you add API keys.

================================================================================
"""

# ─────────────────────────────────────────────────────────────────────────────
# TODO 1: Install pytest and run: pytest tests/ -v
#   pip install pytest
#   Make sure all tests PASS (they should, they're testing correct behavior)
#
# TODO 2: Write a test for Scene.create_continuation()
#   - Create a Scene with Mango as speaker, Cherry as listener
#   - Call create_continuation()
#   - Assert that in the new scene, Cherry is the speaker and Mango is the listener
#
# TODO 3: Write a test for PromptManager.generate_flirt_scene_prompt()
#   - Verify "Camera stays 100% locked" is in every flirt scene prompt
#   - Verify the dialogue text appears in the prompt
#   - Verify the speaker name appears in the prompt
#
# TODO 4: Write a test that verifies Character.save() + Character.load() round-trip
#   - Save a character
#   - Load it back
#   - Assert all fields match (name, slug, role, description)
#
# TODO 5: Write a FAILING test first (TDD — Test Driven Development)
#   - Write: assert character.is_valid() == True  (method doesn't exist yet!)
#   - See it FAIL
#   - Then add is_valid() to Character class
#   - See it PASS
#   - This is "Red-Green-Refactor" — the FAANG testing methodology
# ─────────────────────────────────────────────────────────────────────────────


# ═══════════════════════════════════════════════════════════════════════════
# FULL CODE (try it yourself first!)
# ═══════════════════════════════════════════════════════════════════════════

# import sys
# import shutil
# from pathlib import Path
# import pytest
#
# # Add project root to Python path so we can import our modules
# sys.path.insert(0, str(Path(__file__).parent.parent))
#
# from src.models.character import Character
# from src.models.scene import Scene, SceneCharacter, SceneType
# from src.prompts.manager import PromptManager
#
#
# # ─────────────────────────────────────────────────────────────────────────────
# # FIXTURES (Shared test setup)
# # ─────────────────────────────────────────────────────────────────────────────
#
# @pytest.fixture
# def mango_character():
#     """A pre-built Mango Man character for testing."""
#     return Character(
#         name="Mango Man",
#         description="A tropical mango fruit character.",
#         style_notes="Leaf hair that sways in breeze.",
#         role="contestant",
#         personality="Confident, warm.",
#         voice_assignments={"flirt": "confident, warm, slightly teasing"},
#     )
#
#
# @pytest.fixture
# def cherry_character():
#     """A pre-built Chocolate Cherry character for testing."""
#     return Character(
#         name="Chocolate Cherry",
#         description="A chocolate-covered cherry character with glasses.",
#         style_notes="Cherry stem sways gently. Glasses catch reflections.",
#         role="contestant",
#         personality="Playful, teasing.",
#         voice_assignments={"flirt": "playful, teasing, slightly seductive"},
#     )
#
#
# @pytest.fixture
# def prompt_manager():
#     """A PromptManager instance for testing."""
#     return PromptManager()
#
#
# # ─────────────────────────────────────────────────────────────────────────────
# # CHARACTER TESTS
# # ─────────────────────────────────────────────────────────────────────────────
#
# class TestCharacter:
#     """Tests for the Character model."""
#
#     def test_character_creation_with_name(self, mango_character):
#         """Test that a Character is created correctly."""
#         assert mango_character.name == "Mango Man"
#         assert mango_character.slug == "mango_man"  # Auto-generated
#         assert mango_character.role == "contestant"
#
#     def test_slug_auto_generation(self):
#         """Test that slug is generated from name automatically."""
#         char = Character(name="Chocolate Cherry Woman")
#         assert char.slug == "chocolate_cherry_woman"
#
#     def test_slug_with_hyphens(self):
#         """Test that hyphens in names are converted to underscores."""
#         char = Character(name="Mango-Tango")
#         assert char.slug == "mango_tango"
#
#     def test_empty_name_raises_error(self):
#         """Test that creating a Character with no name raises ValueError."""
#         with pytest.raises(ValueError, match="cannot be empty"):
#             Character(name="")
#
#     def test_generate_image_prompt_contains_no_redesign(self, mango_character):
#         """Critical: Image prompts MUST contain the 'do not redesign' instruction."""
#         prompt = mango_character.generate_image_prompt("sitting at beach")
#         assert "Do NOT redesign" in prompt
#         assert "Do NOT add new characters" in prompt
#
#     def test_generate_image_prompt_includes_scene(self, mango_character):
#         """Test that scene description appears in the image prompt."""
#         scene_desc = "dancing on the beach at sunset"
#         prompt = mango_character.generate_image_prompt(scene_desc)
#         assert scene_desc in prompt
#
#     def test_generate_video_prompt_includes_locked_camera(self, mango_character):
#         """Video prompts MUST have locked camera instruction."""
#         prompt = mango_character.generate_video_animation_prompt(
#             dialogue="It hits different."
#         )
#         assert "100% locked" in prompt
#         assert "No zooming" in prompt
#
#     def test_generate_video_prompt_includes_dialogue(self, mango_character):
#         """Dialogue must appear exactly in the video prompt."""
#         dialogue = "You know… being here with you? Yeah… it hits different."
#         prompt = mango_character.generate_video_animation_prompt(dialogue=dialogue)
#         assert dialogue in prompt
#
#     def test_add_scene_tracks_scenes(self, mango_character):
#         """Test that add_scene() tracks scene involvement."""
#         mango_character.add_scene("S001")
#         mango_character.add_scene("S002")
#         mango_character.add_scene("S001")  # Duplicate — should not be added twice
#         assert "S001" in mango_character.scenes_involved
#         assert "S002" in mango_character.scenes_involved
#         assert len(mango_character.scenes_involved) == 2  # Not 3 (no duplicates)
#
#     def test_save_and_load_roundtrip(self, mango_character, tmp_path):
#         """Test that saving and loading a character preserves all data."""
#         mango_character.save(str(tmp_path))
#         loaded = Character.load("mango_man", str(tmp_path))
#
#         assert loaded.name == mango_character.name
#         assert loaded.slug == mango_character.slug
#         assert loaded.description == mango_character.description
#         assert loaded.role == mango_character.role
#
#
# # ─────────────────────────────────────────────────────────────────────────────
# # SCENE TESTS
# # ─────────────────────────────────────────────────────────────────────────────
#
# class TestScene:
#     """Tests for the Scene model."""
#
#     def test_scene_id_auto_generation(self):
#         """Test that scene_id is auto-generated from scene_number."""
#         scene = Scene(scene_number=1)
#         assert scene.scene_id == "S001"
#
#         scene2 = Scene(scene_number=42)
#         assert scene2.scene_id == "S042"
#
#     def test_get_speaker_returns_speaking_character(self):
#         """Test that get_speaker() returns the character with role='speaker'."""
#         scene = Scene(characters=[
#             SceneCharacter("mango_man", role="speaker", dialogue="It hits different."),
#             SceneCharacter("chocolate_cherry", role="listener"),
#         ])
#         speaker = scene.get_speaker()
#         assert speaker is not None
#         assert speaker.character_slug == "mango_man"
#
#     def test_get_speaker_returns_none_when_no_speaker(self):
#         """Test that get_speaker() returns None when no speaker is set."""
#         scene = Scene(characters=[
#             SceneCharacter("mango_man", role="listener"),
#         ])
#         assert scene.get_speaker() is None
#
#     def test_create_continuation_swaps_roles(self):
#         """
#         CRITICAL: When creating a continuation, speaking roles should swap.
#         If Mango spoke in Scene 1, Cherry speaks in Scene 2.
#         """
#         scene1 = Scene(
#             scene_number=1,
#             characters=[
#                 SceneCharacter("mango_man", role="speaker", dialogue="It hits different."),
#                 SceneCharacter("chocolate_cherry", role="listener"),
#             ]
#         )
#         scene1.set_continuation_frame("fake_frame.png")
#         scene2 = scene1.create_continuation()
#
#         assert scene2.is_continuation is True
#         assert scene2.continues_from_scene_id == "S001"
#         assert scene2.scene_number == 2
#
#         # Cherry should now be the speaker
#         new_speaker = scene2.get_speaker()
#         assert new_speaker is not None
#         assert new_speaker.character_slug == "chocolate_cherry"
#
#     def test_video_prompt_contains_no_camera_movement(self):
#         """Video prompts must ALWAYS include the locked camera instruction."""
#         scene = Scene(characters=[
#             SceneCharacter("mango_man", role="speaker", dialogue="Test dialogue."),
#             SceneCharacter("cherry", role="listener"),
#         ])
#         prompt = scene.generate_video_prompt()
#         assert "Camera stays 100% locked" in prompt
#         assert "No zooming" in prompt
#
#
# # ─────────────────────────────────────────────────────────────────────────────
# # PROMPT MANAGER TESTS
# # ─────────────────────────────────────────────────────────────────────────────
#
# class TestPromptManager:
#     """Tests for the PromptManager."""
#
#     def test_flirt_scene_includes_speaker_name(self, prompt_manager):
#         """The speaker's name must appear in a flirt scene prompt."""
#         prompt = prompt_manager.generate_flirt_scene_prompt(
#             speaker_name="Mango Man",
#             dialogue="It hits different.",
#             listener_name="Chocolate Cherry",
#         )
#         assert "Mango Man" in prompt
#
#     def test_flirt_scene_includes_dialogue(self, prompt_manager):
#         """The exact dialogue must appear in the prompt."""
#         dialogue = "You know what? You're something else."
#         prompt = prompt_manager.generate_flirt_scene_prompt(
#             speaker_name="Mango",
#             dialogue=dialogue,
#             listener_name="Cherry",
#         )
#         assert dialogue in prompt
#
#     def test_flirt_scene_has_locked_camera(self, prompt_manager):
#         """Flirt scenes must always have locked camera."""
#         prompt = prompt_manager.generate_flirt_scene_prompt(
#             speaker_name="X",
#             dialogue="Test.",
#             listener_name="Y",
#         )
#         assert "100% locked" in prompt
#
#     def test_zipline_exit_has_no_dialogue(self, prompt_manager):
#         """When exits_frame=True, no dialogue should appear."""
#         prompt = prompt_manager.generate_zipline_prompt(
#             dialogue="",
#             exits_frame=True,
#         )
#         assert "No dialogue" in prompt
#         assert "No subtitles" in prompt
#
#     def test_character_into_background_uses_both_images(self, prompt_manager):
#         """Character swap prompts must reference both images by number."""
#         prompt = prompt_manager.generate_character_into_background_prompt(
#             character_image_num=1,
#             background_image_num=2,
#         )
#         assert "image 1" in prompt.lower()
#         assert "image 2" in prompt.lower()
