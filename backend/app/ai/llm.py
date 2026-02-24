"""
LLM Module - Google Gemini API
Uses google-generativeai for fast, free cloud inference.
"""
from typing import AsyncGenerator
import google.generativeai as genai
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Configure API key on module load
genai.configure(api_key=settings.GEMINI_API_KEY)


def get_llm(temperature: float = 0.7):
    """
    Get configured Gemini GenerativeModel instance.
    """
    generation_config = genai.GenerationConfig(
        temperature=temperature,
        max_output_tokens=1024,
    )
    return genai.GenerativeModel(
        model_name=settings.GEMINI_MODEL,
        generation_config=generation_config,
    )


async def generate_response(
    prompt: str,
    system_prompt: str = "",
    temperature: float = 0.7,
    max_tokens: int = 1024
) -> str:
    """
    Generate response using Google Gemini API.

    Args:
        prompt: User prompt
        system_prompt: System instructions (prepended to prompt)
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate

    Returns:
        Generated response text
    """
    try:
        generation_config = genai.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        model = genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL,
            generation_config=generation_config,
            system_instruction=system_prompt if system_prompt else None,
        )

        # Use async generation
        response = await model.generate_content_async(prompt)
        return response.text

    except Exception as e:
        logger.error(f"Gemini generation failed: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        if "quota" in str(e).lower() or "429" in str(e):
            return "I'm currently rate-limited. Please try again in a moment."
        if "api_key" in str(e).lower() or "api key" in str(e).lower():
            return "Gemini API key is missing or invalid. Please set GEMINI_API_KEY in your .env file."
        return f"I encountered an error while processing your request: {str(e)[:100]}"


async def generate_stream(
    prompt: str,
    system_prompt: str = "",
    temperature: float = 0.7
) -> AsyncGenerator[str, None]:
    """
    Stream response from Google Gemini API.
    """
    try:
        generation_config = genai.GenerationConfig(
            temperature=temperature,
            max_output_tokens=1024,
        )
        model = genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL,
            generation_config=generation_config,
            system_instruction=system_prompt if system_prompt else None,
        )

        response = await model.generate_content_async(prompt, stream=True)
        async for chunk in response:
            if chunk.text:
                yield chunk.text

    except Exception as e:
        yield f"Error: {str(e)}"


async def check_llm_health() -> bool:
    """Check if Gemini API is reachable and key is valid."""
    try:
        generation_config = genai.GenerationConfig(max_output_tokens=5)
        model = genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL,
            generation_config=generation_config,
        )
        await model.generate_content_async("hi")
        return True
    except Exception as e:
        logger.warning(f"Gemini health check failed: {e}")
        return False


# Keep backward-compatible alias
check_ollama_health = check_llm_health
