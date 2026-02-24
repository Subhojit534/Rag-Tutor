"""
LLM Module - Phi-3 Mini via Ollama (Local, Offline)
Uses LangChain for better abstraction and stability.
"""
from typing import AsyncGenerator
from langchain_community.chat_models import ChatOllama
from langchain.schema import HumanMessage, SystemMessage
from app.config import settings
import logging

logger = logging.getLogger(__name__)

def get_llm(temperature: float = 0.7, max_tokens: int = 1024):
    """
    Get configured ChatOllama instance.
    """
    return ChatOllama(
        base_url=settings.OLLAMA_BASE_URL,
        model=settings.OLLAMA_MODEL,
        temperature=temperature,
        num_predict=max_tokens,
        timeout=120.0
    )

async def generate_response(
    prompt: str,
    system_prompt: str = "",
    temperature: float = 0.7,
    max_tokens: int = 1024
) -> str:
    """
    Generate response using Phi-3 Mini via Ollama (LangChain).
    
    Args:
        prompt: User prompt
        system_prompt: System instructions
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        
    Returns:
        Generated response text
    """
    try:
        llm = get_llm(temperature, max_tokens)
        
        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        
        messages.append(HumanMessage(content=prompt))
        
        response = await llm.ainvoke(messages)
        return response.content
        
    except Exception as e:
        logger.error(f"Ollama generation failed: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        # Check if it's a connection error
        if "connection" in str(e).lower() or "timeout" in str(e).lower():
            return "I apologize, but I cannot connect to my AI engine right now. Please ensure Ollama is running."
        # Otherwise generic error
        return f"I encountered an error while processing your request: {str(e)[:100]}"

async def generate_stream(
    prompt: str,
    system_prompt: str = "",
    temperature: float = 0.7
) -> AsyncGenerator[str, None]:
    """
    Stream response from Phi-3 Mini via Ollama.
    """
    try:
        llm = get_llm(temperature)
        
        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        
        messages.append(HumanMessage(content=prompt))
        
        async for chunk in llm.astream(messages):
            yield chunk.content
            
    except Exception as e:
        yield f"Error: {str(e)}"

async def check_ollama_health() -> bool:
    """Check if Ollama is running and model is available."""
    # Simple check by trying to invoke with a tiny prompt
    try:
        llm = get_llm(max_tokens=1)
        await llm.ainvoke("hi")
        return True
    except:
        return False
