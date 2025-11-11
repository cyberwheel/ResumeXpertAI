# backend/app/llm.py
import httpx
import asyncio
import logging
from .config import settings
from backend.app.config import settings  
logger = logging.getLogger("resume_ai")

async def call_openai(prompt: str):
    """Call OpenAI GPT-4o-mini with robust retry & logging."""
    api_key = settings.OPENAI_API_KEY
    if not api_key:
        logger.error("❌ No OpenAI API key found in environment.")
        return {"text": "AI key missing on server. Please contact admin."}

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 180,
        "temperature": 0.7,
    }

    async with httpx.AsyncClient(timeout=40) as client:
        for attempt in range(3):
            try:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=data
                )
                if response.status_code == 429:
                    await asyncio.sleep(2 * (attempt + 1))
                    continue

                response.raise_for_status()
                result = response.json()
                text = (
                    result.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "")
                    .strip()
                )
                logger.info("✅ AI response received successfully.")
                return {"text": text or "No response from model."}

            except httpx.HTTPStatusError as e:
                logger.error(f"⚠️ OpenAI HTTP error {e.response.status_code}: {e.response.text}")
                if e.response.status_code == 429:
                    await asyncio.sleep(3)
                    continue
                return {"text": f"AI HTTP error {e.response.status_code}."}

            except Exception as e:
                logger.exception(f"💥 Unexpected AI call error: {e}")
                return {"text": "AI service error occurred. Check logs."}

    return {"text": "AI quota limit reached or API temporarily unavailable."}
