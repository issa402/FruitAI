"""
================================================================================
FILE: src/utils/image_processor.py
================================================================================

╔══════════════════════════════════════════════════════════════════════════════╗
║       🎓 FAANG-LEVEL LESSON: IMAGE PROCESSING, PILLOW, AND FILE I/O         ║
╚══════════════════════════════════════════════════════════════════════════════╝

WHAT IS THIS FILE?
──────────────────
This is your image manipulation toolbox. All the manual image work you do
(cropping, combining, upscaling, quality checking) gets automated here.

Your manual workflow currently:
  Screenshot → Google Docs → Paste two images → Send to AI → Prompt

With this file:
  processor = ImageProcessor()
  processor.combine_side_by_side("char1.png", "char2.png", output="combined.png")
  # Done. One line. No Google Docs.


WHAT IS PILLOW? (The Python Image Library)
────────────────────────────────────────────
Pillow (PIL) is THE standard Python image processing library.
Used by: Instagram, Pinterest, virtually every Python app that touches images.

Install: pip install Pillow

Core concepts:
  Image.open(path)         → Load an image from disk
  Image.new(mode, size)   → Create a blank image
  image.resize(size)       → Resize to (width, height)
  image.crop(box)          → Crop to (left, top, right, bottom) box
  image.paste(other, pos)  → Paste one image ON TOP of another (compositing)
  image.save(path)         → Save to disk
  image.show()             → Open in default viewer (for testing)


WHAT IS AN IMAGE "MODE"?
─────────────────────────
An image mode defines the color/channel format.

  "RGB"  → Red, Green, Blue. Standard photo mode. 3 channels.
  "RGBA" → RGB + Alpha (transparency). 4 channels. For PNG with transparency.
  "L"    → Grayscale (luminance). 1 channel.
  "1"    → Black and white. 1 bit per pixel.

Always check the mode when combining:
  image.mode  # → "RGBA" or "RGB"

If you paste an RGBA image onto RGB, you need to handle the alpha channel.
If you ignore this, you get weird color artifacts.


WHAT IS A BOUNDING BOX?
────────────────────────
In Pillow, a "box" is a 4-tuple: (left, top, right, bottom)
  - (0, 0, 100, 100) = top-left 100x100 pixels
  - (0, 0) is ALWAYS top-left corner
  - Values are in pixels

Crop example:
  image.crop((50, 50, 200, 200))  # Cut a 150x150 region starting at (50, 50)

Paste example:
  base.paste(overlay, (x, y))     # Paste overlay at position (x, y) on base


WHAT IS IMAGE COMPOSITION?
────────────────────────────
Composition = layering images on top of each other.

YOUR USE CASE: "I have character A and character B in separate images.
I want them in ONE image."

Step 1: Create a new blank canvas (wide enough for both)
Step 2: Paste character A on the left half
Step 3: Paste character B on the right half
Step 4: Save the combined image


WHAT IS IMAGE QUALITY?
────────────────────────
JPEGs are compressed — the "quality" setting (1-95) controls the trade-off:
  High quality (95+): Large file, looks great
  Low quality (50):   Small file, looks blurry/artifact-y

When you screenshot a video and get a low-quality image, the system can:
  1. Detect it's low quality (check file size, pixel density, or use blur detection)
  2. Auto-flag it: "This image might be too low quality for the AI"
  3. Suggest: "Do you want to upscale this before using it?"

Simple quality check: image size in pixels. Under 512x512 = warn the user.


WHAT IS EXIF DATA?
────────────────────
EXIF (Exchangeable Image File Format) is metadata embedded in image files.
It stores: camera settings, GPS coordinates, timestamps, etc.

YOUR USE CASE: You can EMBED your prompt into the image as EXIF data!
So your image.png actually CONTAINS the prompt that generated it.

  from PIL import Image
  import piexif

  img = Image.open("output.png")
  exif_bytes = piexif.dump({
      "0th": {piexif.ImageIFD.ImageDescription: prompt.encode()}
  })
  img.save("output.png", exif=exif_bytes)

Later:
  exif_data = piexif.load("output.png")
  embedded_prompt = exif_data["0th"][piexif.ImageIFD.ImageDescription].decode()


WHAT IS OpenCV (cv2)?
──────────────────────
OpenCV is a computer vision library, more powerful than Pillow.
Used by: Google Photos, Instagram for face detection, self-driving cars.

For you:
  import cv2
  cap = cv2.VideoCapture("scene1.mp4")  # Open a video
  cap.set(cv2.CAP_PROP_POS_AVI_RATIO, 1)  # Seek to end
  ret, frame = cap.read()  # Read the last frame
  cv2.imwrite("last_frame.png", frame)  # Save as image!

This AUTOMATES your "screenshot the last frame" workflow completely.
One function call instead of: pause video → Print Screen → crop → save.

================================================================================
"""

import logging
import shutil
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# TODO 1: Install Pillow and test Image.open() on one of your images
#   pip install Pillow
#   from PIL import Image
#   img = Image.open("your_character.png")
#   print(img.size, img.mode)
#
# TODO 2: Implement combine_side_by_side() step by step:
#   a) Open both images
#   b) Find the MAX height of the two
#   c) Create a new blank canvas: width = img1.width + img2.width, height = max_height
#   d) Paste img1 at (0, 0)
#   e) Paste img2 at (img1.width, 0)
#   f) Save the result
#
# TODO 3: Implement extract_last_frame() using OpenCV (cv2):
#   pip install opencv-python
#   cap = cv2.VideoCapture(video_path)
#   and loop to the last frame
#
# TODO 4: Implement is_low_quality(image_path) that returns True if:
#   - Image dimensions are less than 512x512
#   - OR file size is less than 50KB
#
# TODO 5: Research piexif and implement embed_prompt_in_image()
#   pip install piexif
# ─────────────────────────────────────────────────────────────────────────────


# ═══════════════════════════════════════════════════════════════════════════
# FULL CODE (try it yourself first!)
# ═══════════════════════════════════════════════════════════════════════════

# class ImageProcessor:
#     """
#     Image manipulation toolbox for the Fruit Love Island pipeline.
#
#     Automates your current manual tasks:
#       - Combining two character images (replaces Google Docs workflow)
#       - Extracting the last frame from a video (replaces manual screenshot)
#       - Checking image quality before submitting to AI
#       - Embedding prompts into image metadata
#
#     Usage:
#         processor = ImageProcessor()
#         combined = processor.combine_side_by_side("char1.png", "char2.png")
#         quality_ok = processor.is_quality_sufficient(combined)
#         if not quality_ok:
#             print("⚠️ Low quality! Consider upscaling first.")
#     """
#
#     def __init__(self, output_dir: str = "assets/processed"):
#         self.output_dir = Path(output_dir)
#         self.output_dir.mkdir(parents=True, exist_ok=True)
#         self._check_dependencies()
#
#     def _check_dependencies(self) -> None:
#         """Check if required libraries are installed and warn if not."""
#         try:
#             from PIL import Image
#             logger.info("Pillow: ✅ Available")
#         except ImportError:
#             logger.warning("Pillow not installed. Run: pip install Pillow")
#
#         try:
#             import cv2
#             logger.info("OpenCV: ✅ Available")
#         except ImportError:
#             logger.warning("OpenCV not installed. Run: pip install opencv-python")
#
#     def combine_side_by_side(
#         self,
#         image1_path: str,
#         image2_path: str,
#         output_name: Optional[str] = None,
#         gap_pixels: int = 20,
#         background_color: Tuple[int, int, int] = (255, 255, 255),
#     ) -> Path:
#         """
#         Combine two character images side by side.
#
#         THIS IS YOUR GOOGLE DOCS REPLACEMENT.
#         Instead of: screenshot → paste into Google Docs → export → upload
#         Just call: processor.combine_side_by_side("mango.png", "cherry.png")
#
#         Args:
#             image1_path: Path to first character image (will be on LEFT)
#             image2_path: Path to second character image (will be on RIGHT)
#             output_name: Output filename (auto-generated if not provided)
#             gap_pixels: Space between the two images (in pixels)
#             background_color: Background color as (R, G, B) tuple
#
#         Returns:
#             Path: Path to the combined image saved in output_dir
#         """
#         from PIL import Image
#
#         img1 = Image.open(image1_path).convert("RGBA")
#         img2 = Image.open(image2_path).convert("RGBA")
#
#         # Calculate dimensions for the canvas
#         # Match heights: scale the smaller image up to match the taller one
#         target_height = max(img1.height, img2.height)
#
#         # Resize while maintaining aspect ratio to match target height
#         def resize_to_height(img, height):
#             ratio = height / img.height
#             new_width = int(img.width * ratio)
#             return img.resize((new_width, height), Image.LANCZOS)
#
#         img1 = resize_to_height(img1, target_height)
#         img2 = resize_to_height(img2, target_height)
#
#         # Total canvas width = both images + gap between them
#         total_width = img1.width + gap_pixels + img2.width
#
#         # Create the blank white canvas
#         canvas = Image.new("RGBA", (total_width, target_height), (*background_color, 255))
#
#         # Paste images onto canvas
#         canvas.paste(img1, (0, 0), img1)  # Third arg = transparency mask
#         canvas.paste(img2, (img1.width + gap_pixels, 0), img2)
#
#         # Generate output filename if not provided
#         if output_name is None:
#             p1 = Path(image1_path).stem
#             p2 = Path(image2_path).stem
#             output_name = f"{p1}_x_{p2}_combined.png"
#
#         output_path = self.output_dir / output_name
#         canvas.convert("RGB").save(output_path, "PNG")
#
#         logger.info(f"✅ Combined image saved: {output_path}")
#         print(f"✅ Characters combined: {output_path}")
#         return output_path
#
#     def extract_last_frame(
#         self,
#         video_path: str,
#         output_name: Optional[str] = None,
#     ) -> Path:
#         """
#         Extract the very last frame from a video file.
#
#         THIS AUTOMATES YOUR MANUAL SCREENSHOT WORKFLOW.
#         Instead of: pause video at end → screenshot → crop → save
#         Just call: processor.extract_last_frame("scene1.mp4")
#
#         Args:
#             video_path: Path to the video file (mp4, mov, webm, etc.)
#             output_name: Output filename (auto-generated if not provided)
#
#         Returns:
#             Path: Path to the extracted frame image.
#         """
#         import cv2
#
#         cap = cv2.VideoCapture(str(video_path))
#
#         if not cap.isOpened():
#             raise ValueError(f"Could not open video: {video_path}")
#
#         # Get total frame count and seek to the last frame
#         total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
#         cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames - 1)
#
#         ret, frame = cap.read()
#         cap.release()
#
#         if not ret:
#             # Fallback: read frames one by one until the last one
#             cap = cv2.VideoCapture(str(video_path))
#             last_frame = None
#             while True:
#                 ret, frame = cap.read()
#                 if not ret:
#                     break
#                 last_frame = frame
#             cap.release()
#             frame = last_frame
#
#         if frame is None:
#             raise RuntimeError(f"Could not extract any frame from: {video_path}")
#
#         if output_name is None:
#             stem = Path(video_path).stem
#             output_name = f"{stem}_last_frame.png"
#
#         output_path = self.output_dir / output_name
#         cv2.imwrite(str(output_path), frame)
#
#         logger.info(f"✅ Last frame extracted: {output_path}")
#         print(f"✅ Frame extracted: {output_path}")
#         return output_path
#
#     def is_quality_sufficient(
#         self,
#         image_path: str,
#         min_width: int = 512,
#         min_height: int = 512,
#         min_file_size_kb: int = 50,
#     ) -> bool:
#         """
#         Check if an image meets minimum quality requirements.
#
#         YOUR USE CASE: "Sometimes the last frame screenshot is low quality
#         so I put it into Gemini AI to improve it first."
#
#         This function DETECTS that automatically so you know before wasting
#         a generation attempt.
#
#         Args:
#             image_path: Path to the image to check
#             min_width: Minimum acceptable width in pixels
#             min_height: Minimum acceptable height in pixels
#             min_file_size_kb: Minimum acceptable file size in kilobytes
#
#         Returns:
#             bool: True if quality looks good enough for AI input.
#         """
#         from PIL import Image
#
#         path = Path(image_path)
#         if not path.exists():
#             logger.error(f"Image not found: {image_path}")
#             return False
#
#         # Check file size
#         file_size_kb = path.stat().st_size / 1024
#         if file_size_kb < min_file_size_kb:
#             logger.warning(
#                 f"⚠️ Low file size: {file_size_kb:.1f}KB < {min_file_size_kb}KB. "
#                 f"Consider upscaling {path.name}."
#             )
#             return False
#
#         # Check pixel dimensions
#         with Image.open(path) as img:
#             width, height = img.size
#
#         if width < min_width or height < min_height:
#             logger.warning(
#                 f"⚠️ Low resolution: {width}x{height} < {min_width}x{min_height}. "
#                 f"Consider upscaling {path.name}."
#             )
#             return False
#
#         logger.info(f"✅ Quality check passed: {width}x{height}, {file_size_kb:.1f}KB")
#         return True
#
#     def crop_image(
#         self,
#         image_path: str,
#         left: int,
#         top: int,
#         right: int,
#         bottom: int,
#         output_name: Optional[str] = None,
#     ) -> Path:
#         """
#         Crop an image to specified pixel coordinates.
#
#         Box coordinates: (left, top, right, bottom)
#         (0, 0) is the TOP-LEFT corner.
#
#         Example:
#             # Crop right half of a 1920x1080 image:
#             processor.crop_image("scene.png", left=960, top=0, right=1920, bottom=1080)
#         """
#         from PIL import Image
#
#         img = Image.open(image_path)
#         cropped = img.crop((left, top, right, bottom))
#
#         if output_name is None:
#             stem = Path(image_path).stem
#             output_name = f"{stem}_cropped.png"
#
#         output_path = self.output_dir / output_name
#         cropped.save(output_path)
#
#         logger.info(f"✅ Cropped image saved: {output_path}")
#         return output_path
#
#     def embed_prompt_in_metadata(
#         self,
#         image_path: str,
#         prompt_text: str,
#     ) -> bool:
#         """
#         Embed the AI prompt used to generate this image INTO the image file.
#
#         FAANG-level trick: Store metadata WITH the asset so you always know
#         how it was generated. Instagram does this with filter data.
#
#         Requires: pip install piexif
#
#         Args:
#             image_path: Path to the image file
#             prompt_text: The prompt to embed
#
#         Returns:
#             bool: True if successfully embedded, False otherwise.
#         """
#         try:
#             import piexif
#             from PIL import Image
#
#             img = Image.open(image_path)
#
#             # Build the EXIF dict with the prompt in the ImageDescription field
#             exif_dict = {
#                 "0th": {
#                     piexif.ImageIFD.ImageDescription: prompt_text.encode("utf-8"),
#                     piexif.ImageIFD.Software: b"Fruit Love Island AI Pipeline",
#                 }
#             }
#             exif_bytes = piexif.dump(exif_dict)
#
#             # Re-save with EXIF data
#             img.save(image_path, exif=exif_bytes)
#             logger.info(f"✅ Prompt embedded in {image_path}")
#             return True
#
#         except ImportError:
#             logger.warning("piexif not installed: pip install piexif")
#             return False
#         except Exception as e:
#             logger.error(f"Failed to embed metadata: {e}")
#             return False
#
#     def read_embedded_prompt(self, image_path: str) -> Optional[str]:
#         """Read a prompt that was previously embedded in image metadata."""
#         try:
#             import piexif
#
#             exif_data = piexif.load(str(image_path))
#             description = exif_data.get("0th", {}).get(piexif.ImageIFD.ImageDescription)
#             if description:
#                 return description.decode("utf-8")
#             return None
#
#         except ImportError:
#             logger.warning("piexif not installed: pip install piexif")
#             return None
#         except Exception as e:
#             logger.error(f"Failed to read metadata: {e}")
#             return None
#
#
# # ─────────────────────────────────────────────────────────────────────────────
# # EXAMPLE: python src/utils/image_processor.py
# # ─────────────────────────────────────────────────────────────────────────────
# if __name__ == "__main__":
#     processor = ImageProcessor()
#
#     # Test quality check
#     # processor.is_quality_sufficient("path/to/screenshot.png")
#
#     # Test combine characters
#     # processor.combine_side_by_side("char1.png", "char2.png")
#
#     # Test extract last frame
#     # processor.extract_last_frame("scene1.mp4")
#
#     print("ImageProcessor ready. Uncomment above lines to test with your files.")
