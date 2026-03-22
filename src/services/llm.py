"""
================================================================================
FILE: src/services/llm.py
================================================================================

╔══════════════════════════════════════════════════════════════════════════════╗
║          🎓 FAANG-LEVEL LESSON: API CLIENTS, HTTP, AND SERVICE LAYER        ║
╚══════════════════════════════════════════════════════════════════════════════╝

WHAT IS THIS FILE?
──────────────────
The "Service Layer" — where your Python code talks to EXTERNAL SERVICES.

For you right now: You manually paste prompts into ChatGPT, Copilot, Gemini.
When you get API keys, THIS FILE will do that AUTOMATICALLY.

Service layer principle:
  The rest of your code doesn't care HOW an LLM is called.
  It just calls: llm.ask("Describe this image")
  And gets back a string response.

This is called "abstraction" or "encapsulation" of external dependencies.


WHAT IS AN API? (Application Programming Interface)
─────────────────────────────────────────────────────
An API is a contract for how to communicate with a service.

OpenAI's API contract:
  REQUEST: POST to https://api.openai.com/v1/chat/completions
           with headers:  {"Authorization": "Bearer API_KEY"}
           with body:     {"model": "gpt-4", "messages": [...]}

  RESPONSE: {"choices": [{"message": {"content": "The response text..."}}]}

Instead of writing raw HTTP, use the official SDK:
  from openai import OpenAI
  client = OpenAI(api_key="your_key")
  response = client.chat.completions.create(
      model="gpt-4",
      messages=[{"role": "user", "content": "Your prompt here"}]
  )
  text = response.choices[0].message.content


WHAT IS HTTP? (The protocol of the internet)
──────────────────────────────────────────────
HTTP = HyperText Transfer Protocol.
Every API call is an HTTP request.

4 main HTTP methods (CRUD):
  GET    → Read data              (like loading a webpage)
  POST   → Create / submit data  (like submitting a form)
  PUT    → Replace data          (update everything)
  DELETE → Delete data

For API calls, you usually use POST (sending data to get a response).

HTTP Status Codes (you'll see these everywhere):
  200 OK           → Success
  201 Created      → Created successfully
  400 Bad Request  → Your request is wrong (check your code)
  401 Unauthorized → Bad/missing API key
  403 Forbidden    → You don't have permission
  404 Not Found    → The endpoint doesn't exist
  429 Too Many Requests → Rate limited (slow down!)
  500 Server Error → Their problem, not yours

MEMORIZE these. You'll debug with them constantly.


WHAT ARE API RATE LIMITS?
──────────────────────────
Every API has limits on how many requests you can make.

OpenAI: 3 requests/minute (free tier), 3,500/minute (paid tier)
Gemini: 15 requests/minute (free tier)

When you hit rate limits: the API returns 429 Too Many Requests.
Your code must handle this with RETRY LOGIC.

Exponential Backoff (the FAANG approach):
  Try 1: Wait 1 second
  Try 2: Wait 2 seconds
  Try 3: Wait 4 seconds
  Try 4: Wait 8 seconds
  Give up after N retries.

Library: tenacity
  from tenacity import retry, wait_exponential, stop_after_attempt
  @retry(wait=wait_exponential(min=1, max=60), stop=stop_after_attempt(5))
  def call_api():
      ...


WHAT IS A "SERVICE" IN SOFTWARE ARCHITECTURE?
─────────────────────────────────────────────────
A Service encapsulates calls to a specific external system.
  LLMService     → Talks to OpenAI/Gemini/Anthropic
  ImageService   → Talks to image generation APIs
  VideoService   → Talks to video generation APIs
  StorageService → Talks to AWS S3 or local file system

Your code says: "I want to call an AI" → calls LLMService
It does NOT hardcode "openai.chat.completions.create".
This means: if OpenAI raises prices, you switch to Gemini by changing
only the Service file. The rest of your code changes NOTHING.

This pattern is called "Dependency Inversion" (the D in SOLID).


HOW THE SERVICE LAYER EVOLVES:
─────────────────────────────────────────────────────────────────────────
TODAY (No API key):
  llm = LLMService()
  prompt = llm.get_refined_prompt("My rough idea...")
  # Returns: "Here's the prompt, paste it into ChatGPT manually: [prompt]"

TOMORROW (Got an API key):
  llm = LLMService(api_key="sk-proj-...")
  prompt = llm.get_refined_prompt("My rough idea...")
  # Returns: The actual AI response!

SAME CODE. Different result based on config. This is proper architecture.

================================================================================
"""

import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# TODO 1: Get a free OpenAI API key at platform.openai.com
#   (Free tier = $5 credit, enough for hundreds of test calls)
#   Then: pip install openai
#   And: test your first API call manually in a scratch script
#
# TODO 2: Implement retry logic with manual sleep:
#   for attempt in range(3):
#       try:
#           response = call_api()
#           break
#       except Exception:
#           time.sleep(2 ** attempt)  # 1, 2, 4 seconds
#
# TODO 3: Add a "manual_mode_helper(prompt)" method that:
#   Prints the prompt with clear formatting and
#   Asks you which AI you pasted it into and what the response was
#   (For when you don't have API keys yet)
#
# TODO 4: Implement call_gemini() using google.generativeai:
#   pip install google-generativeai
#
# TODO 5: Add token counting: count the words in a prompt and
#   warn if it's longer than 2,000 words (expensive for API calls)
# ─────────────────────────────────────────────────────────────────────────────


# ═══════════════════════════════════════════════════════════════════════════
# FULL CODE (try it yourself first!)
# ═══════════════════════════════════════════════════════════════════════════

# class LLMService:
#     """
#     Service layer for Large Language Model API calls.
#
#     Supports:
#       - OpenAI (ChatGPT, GPT-4)
#       - Google Gemini
#       - Manual mode (for when you don't have API keys)
#
#     Automatically falls back to "manual mode" if no API key is configured.
#     In manual mode, it prints the prompt to the terminal so you can
#     copy-paste it into the AI tool of your choice.
#
#     Usage (no API key):
#         llm = LLMService()
#         response = llm.ask("What dialogue should Mango say next?")
#         # Prints: "COPY THIS INTO YOUR AI TOOL: ..."
#         # You paste response back when prompted
#
#     Usage (with API key):
#         llm = LLMService(openai_api_key="sk-proj-...")
#         response = llm.ask("What dialogue should Mango say next?")
#         # Returns AI response automatically!
#     """
#
#     def __init__(
#         self,
#         openai_api_key: Optional[str] = None,
#         gemini_api_key: Optional[str] = None,
#         default_model: str = "gpt-4o-mini",
#         max_retries: int = 3,
#     ):
#         self.openai_api_key = openai_api_key
#         self.gemini_api_key = gemini_api_key
#         self.default_model = default_model
#         self.max_retries = max_retries
#
#         # Detect which services are available
#         self.has_openai = bool(openai_api_key)
#         self.has_gemini = bool(gemini_api_key)
#         self.manual_mode = not (self.has_openai or self.has_gemini)
#
#         if self.manual_mode:
#             logger.info("LLMService: Manual mode (no API keys configured).")
#         if self.has_openai:
#             logger.info("LLMService: OpenAI available.")
#         if self.has_gemini:
#             logger.info("LLMService: Gemini available.")
#
#     def ask(
#         self,
#         prompt: str,
#         system_message: str = "You are a helpful creative AI assistant.",
#         temperature: float = 0.7,
#     ) -> Optional[str]:
#         """
#         Send a prompt to an LLM and get a response.
#
#         Priority: OpenAI → Gemini → Manual Mode
#
#         Args:
#             prompt: The user's message/question
#             system_message: Instructions that define the AI's behavior
#             temperature: Creativity level 0.0 (deterministic) to 2.0 (very creative)
#                          For prompts: 0.7 is a good balance
#
#         Returns:
#             str: The AI's response, or None if all methods fail.
#         """
#         if self.has_openai:
#             return self._call_openai(prompt, system_message, temperature)
#         elif self.has_gemini:
#             return self._call_gemini(prompt)
#         else:
#             return self._manual_mode(prompt)
#
#     def _call_openai(
#         self,
#         prompt: str,
#         system_message: str,
#         temperature: float,
#     ) -> Optional[str]:
#         """Call OpenAI's Chat Completions API with retry logic."""
#         try:
#             from openai import OpenAI, RateLimitError, APIError
#         except ImportError:
#             logger.error("OpenAI SDK not installed. Run: pip install openai")
#             return None
#
#         client = OpenAI(api_key=self.openai_api_key)
#
#         for attempt in range(self.max_retries):
#             try:
#                 response = client.chat.completions.create(
#                     model=self.default_model,
#                     messages=[
#                         {"role": "system", "content": system_message},
#                         {"role": "user", "content": prompt},
#                     ],
#                     temperature=temperature,
#                     max_tokens=2000,
#                 )
#                 return response.choices[0].message.content
#
#             except RateLimitError:
#                 # Exponential backoff: wait 2^attempt seconds
#                 wait = 2 ** attempt
#                 logger.warning(f"Rate limited. Waiting {wait}s... (attempt {attempt+1})")
#                 time.sleep(wait)
#
#             except APIError as e:
#                 logger.error(f"OpenAI API error: {e}")
#                 return None
#
#         logger.error(f"All {self.max_retries} OpenAI retries failed.")
#         return None
#
#     def _call_gemini(self, prompt: str) -> Optional[str]:
#         """Call Google Gemini API."""
#         try:
#             import google.generativeai as genai
#         except ImportError:
#             logger.error("Gemini SDK not installed. Run: pip install google-generativeai")
#             return None
#
#         genai.configure(api_key=self.gemini_api_key)
#         model = genai.GenerativeModel("gemini-pro")
#
#         try:
#             response = model.generate_content(prompt)
#             return response.text
#         except Exception as e:
#             logger.error(f"Gemini API error: {e}")
#             return None
#
#     def _manual_mode(self, prompt: str) -> Optional[str]:
#         """
#         Manual mode: print the prompt so you can copy-paste it into your AI tool.
#         Then ask you to paste the response back.
#
#         This bridges the gap until you have API keys.
#         Your workflow is STILL faster than before because the prompt
#         is already perfectly formatted and ready to go.
#         """
#         print("\n" + "=" * 70)
#         print("🤖 MANUAL MODE — Copy this prompt into ChatGPT/Copilot/Gemini:")
#         print("=" * 70)
#         print(prompt)
#         print("=" * 70)
#
#         try:
#             print("\n📋 Paste the AI's response here (press Enter twice when done):")
#             lines = []
#             while True:
#                 line = input()
#                 if line == "" and lines and lines[-1] == "":
#                     break
#                 lines.append(line)
#             return "\n".join(lines[:-1])  # Remove the trailing empty line
#         except KeyboardInterrupt:
#             print("\n[Input cancelled]")
#             return None
#
#     # ─────────────────────────────────────────────────────────────────────────
#     # SPECIALIZED PROMPTS (Your specific use cases)
#     # ─────────────────────────────────────────────────────────────────────────
#
#     def refine_video_prompt(self, rough_idea: str) -> Optional[str]:
#         """
#         YOUR USE CASE: Give a rough idea, get a perfectly formatted 6-second video prompt.
#
#         This replaces: you → ChatGPT → many back-and-forths → final prompt.
#         With this: rough idea → perfect formatted prompt in one call.
#         """
#         system = (
#             "You are an expert AI video prompt writer for a show called 'Fruit Love Island'. "
#             "The show features anthropomorphic fruit characters in a Love Island format. "
#             "Videos are exactly 6 seconds. "
#             "Always include: character position, idle animations, dialogue delivery style, "
#             "environment details, and camera instructions (always locked, no movement). "
#             "Format prompts professionally, with clear sections."
#         )
#
#         prompt = f"""
# Write a complete, professional 6-second video animation prompt based on this rough idea:

# "{rough_idea}"

# Requirements:
# - Start with: "Use ONLY the provided image exactly as it is..."
# - Specify that characters stay in their exact positions
# - Include idle animation details (blinking, breathing, micro-expressions)
# - Include environment animation (wind, ocean, lighting)
# - Include dialogue delivery style if there's dialogue
# - End with: "Camera stays 100% locked. No zooming, no panning, no drifting, no rotation."
# - Maximum 6 seconds worth of content
# """
#         return self.ask(prompt, system)
#
#     def describe_image_for_recreation(self, image_description: str) -> Optional[str]:
#         """
#         YOUR USE CASE: "I have a video/image and want to recreate it in my art style."
#         Takes your description of what's in the image and generates a recreation prompt.
#         """
#         system = (
#             "You are an expert at writing detailed scene recreation prompts for AI video generators. "
#             "Your prompts are precise, sequential, and well-structured."
#         )
#
#         prompt = f"""
# Based on this description of a reference video/image:

# "{image_description}"

# Write a detailed 6-second animation prompt that recreates these exact events
# but adapted for the Fruit Love Island art style (animated, tropical, vibrant fruit characters).

# Include:
# 1. Every movement/action described, in the order they happen
# 2. Camera movement (or explicit note to keep camera locked)
# 3. Duration timing (e.g., "In the first 2 seconds...", "From second 3-6...")
# 4. Art style: animated fruit characters, tropical island setting
# """
#         return self.ask(prompt, system)
#
#
# # ─────────────────────────────────────────────────────────────────────────────
# # EXAMPLE: python src/services/llm.py
# # ─────────────────────────────────────────────────────────────────────────────
# if __name__ == "__main__":
#     # Test in manual mode (no API key needed)
#     llm = LLMService()
#
#     # This will print the prompt and ask you to paste the response
#     print("Testing LLMService in manual mode...")
#     response = llm.refine_video_prompt(
#         "Mango Man waves to Cherry from across the beach, she notices and smiles"
#     )
#     if response:
#         print("\n=== YOUR AI RESPONSE ===")
#         print(response)
