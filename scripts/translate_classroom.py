#!/usr/bin/env python3
"""
Translate an existing OpenMAIC classroom to Portuguese.

Fetches classroom content, translates all text fields using Kimi API,
and saves the translated classroom back to OpenMAIC.

Usage:
    uv run python scripts/translate_classroom.py <classroom_id>
    Example: uv run python scripts/translate_classroom.py FMvaZTyXRu
"""

import asyncio
import json
import logging
import sys
from typing import Any

import httpx

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

OPENMAIC_URL = "http://localhost:3000"
KIMI_API_KEY = ""  # Will be read from env or .env.local
KIMI_BASE_URL = "https://api.moonshot.ai/v1"


def load_kimi_config():
    """Load Kimi config from OpenMAIC .env.local."""
    import re

    env_path = "/Dados/OpenMAIC/.env.local"
    try:
        with open(env_path) as f:
            content = f.read()
        key_match = re.search(r"^KIMI_API_KEY=(.+)", content, re.MULTILINE)
        url_match = re.search(r"^KIMI_BASE_URL=(.+)", content, re.MULTILINE)
        if key_match:
            globals()["KIMI_API_KEY"] = key_match.group(1).strip()
        if url_match and url_match.group(1).strip():
            globals()["KIMI_BASE_URL"] = url_match.group(1).strip()
    except FileNotFoundError:
        logger.warning(f"Could not find {env_path}, using defaults")


async def translate_text(text: str, client: httpx.AsyncClient) -> str:
    """Translate a single text string to Portuguese using Kimi API."""
    if not text or len(text.strip()) < 2:
        return text

    prompt = f"""Translate the following text from Chinese (or any language) to Brazilian Portuguese (pt-BR).
Keep all markdown formatting, HTML tags, code, numbers, and special characters exactly as they are.
Only translate the natural language content. Return ONLY the translated text.

Text to translate:
{text}

Portuguese translation:"""

    try:
        response = await client.post(
            f"{KIMI_BASE_URL}/chat/completions",
            json={
                "model": "kimi-k2.5",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 4000,
            },
            headers={
                "Authorization": f"Bearer {KIMI_API_KEY}",
                "Content-Type": "application/json",
            },
            timeout=60.0,
        )
        response.raise_for_status()
        result = response.json()
        translated = result["choices"][0]["message"]["content"].strip()
        return translated
    except Exception as e:
        logger.warning(f"Translation failed for text: {text[:50]}... Error: {e}")
        return text  # Return original on failure


async def translate_scene(
    scene: dict, client: httpx.AsyncClient, scene_idx: int
) -> dict:
    """Translate all text content in a scene."""
    translated_scene = json.loads(json.dumps(scene))  # Deep copy

    # Translate title
    if "title" in translated_scene:
        logger.info(f"  Scene {scene_idx}: Translating title: {translated_scene['title'][:50]}")
        translated_scene["title"] = await translate_text(translated_scene["title"], client)

    # Translate content based on scene type
    content = translated_scene.get("content", {})
    if not content:
        return translated_scene

    content_type = content.get("type", "")

    if content_type == "slide":
        canvas = content.get("canvas", {})
        # Translate slide elements
        for key in ["title", "subtitle", "description", "notes"]:
            if key in canvas and isinstance(canvas[key], str):
                logger.info(f"    Translating slide {key}")
                canvas[key] = await translate_text(canvas[key], client)

        # Translate text elements in shapes/texts
        for shapes_key in ["shapes", "texts", "elements"]:
            if shapes_key in canvas and isinstance(canvas[shapes_key], list):
                for shape in canvas[shapes_key]:
                    if "text" in shape and isinstance(shape["text"], str):
                        shape["text"] = await translate_text(shape["text"], client)

    elif content_type == "quiz":
        # Translate quiz questions and options
        if "question" in content:
            logger.info(f"    Translating quiz question")
            content["question"] = await translate_text(content["question"], client)
        for key in ["explanation", "hint"]:
            if key in content:
                content[key] = await translate_text(content[key], client)

        # Translate options
        if "options" in content and isinstance(content["options"], list):
            for opt in content["options"]:
                if "text" in opt:
                    opt["text"] = await translate_text(opt["text"], client)

    elif content_type == "simulation":
        # Translate simulation content
        for key in ["title", "description", "instructions", "scenario"]:
            if key in content:
                content[key] = await translate_text(content[key], client)

    elif content_type == "pbl":
        # Translate project-based learning content
        for key in ["title", "description", "challenge", "context"]:
            if key in content:
                content[key] = await translate_text(content[key], client)

    return translated_scene


async def translate_classroom(classroom_id: str):
    """Main function to translate an entire classroom."""
    load_kimi_config()

    if not KIMI_API_KEY:
        logger.error("KIMI_API_KEY not found. Set it in /Dados/OpenMAIC/.env.local")
        sys.exit(1)

    logger.info(f"Fetching classroom {classroom_id} from OpenMAIC")

    async with httpx.AsyncClient() as client:
        # Fetch classroom
        resp = await client.get(f"{OPENMAIC_URL}/api/classroom", params={"id": classroom_id})
        resp.raise_for_status()
        data = resp.json()

        classroom = data.get("data", {}).get("classroom", data.get("classroom", data))
        stage = classroom.get("stage", {})
        scenes = classroom.get("scenes", [])

        if not scenes:
            logger.error("No scenes found in classroom")
            sys.exit(1)

        logger.info(
            f"Classroom: {stage.get('name', 'N/A')} | "
            f"Language: {stage.get('language', '?')} | "
            f"Scenes: {len(scenes)}"
        )

        # Translate stage metadata
        if "name" in stage:
            logger.info("Translating stage name...")
            stage["name"] = await translate_text(stage["name"], client)
        stage["language"] = "pt-BR"

        # Translate each scene
        translated_scenes = []
        for i, scene in enumerate(scenes):
            logger.info(f"Translating scene {i+1}/{len(scenes)} (type: {scene.get('type')})")
            translated_scene = await translate_scene(scene, client, i + 1)
            translated_scenes.append(translated_scene)

        # Save translated classroom
        logger.info("Saving translated classroom...")
        save_resp = await client.post(
            f"{OPENMAIC_URL}/api/classroom",
            json={
                "stage": {
                    **stage,
                    "id": classroom_id,  # Keep same ID
                },
                "scenes": translated_scenes,
            },
        )
        save_resp.raise_for_status()
        save_data = save_resp.json()

        result = save_data.get("data", save_data)
        new_url = result.get("url", f"{OPENMAIC_URL}/classroom/{classroom_id}")

        logger.info(f"✅ Classroom translated successfully!")
        logger.info(f"URL: {new_url}")

        return {
            "classroom_id": classroom_id,
            "url": new_url,
            "scenes_translated": len(translated_scenes),
            "language": "pt-BR",
        }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run python scripts/translate_classroom.py <classroom_id>")
        sys.exit(1)

    classroom_id = sys.argv[1]
    result = asyncio.run(translate_classroom(classroom_id))
    print(json.dumps(result, indent=2, ensure_ascii=False))
