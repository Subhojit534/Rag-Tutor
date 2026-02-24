import sys
import os
import asyncio
from unittest.mock import MagicMock, patch

# Mock dependencies that might be missing in validaton env
sys.modules["faiss"] = MagicMock()
sys.modules["sentence_transformers"] = MagicMock()
sys.modules["langchain_community"] = MagicMock()
sys.modules["langchain"] = MagicMock()
sys.modules["langchain.schema"] = MagicMock()

# Add app to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ai.prompts import SOCRATIC_TUTOR_SYSTEM_PROMPT
# We need to be careful with imports that might fail
with patch.dict('sys.modules', {'langchain_community.chat_models': MagicMock(), 'langchain.schema': MagicMock()}):
    from app.ai.rag_chain import rag_query
    from app.routers.ai_tutor import extract_pdf_chunks

def test_prompt_format():
    print("Testing Prompt Format...", end=" ")
    try:
        formatted = SOCRATIC_TUTOR_SYSTEM_PROMPT.format(
            subject_name="Math",
            retrieved_chunks="Content",
            question="What is X?"
        )
        assert "Subject: Math" in formatted or "subject: Math" in formatted
        assert "Content" in formatted
        assert "What is X?" in formatted
        print("PASSED")
    except Exception as e:
        print(f"FAILED: {e}")

async def test_rag_flow():
    print("Testing RAG Flow (Mocked)...", end=" ")
    
    # Mock vector store
    mock_store = MagicMock()
    mock_store.search.return_value = [{"text": "Content", "score": 0.5, "source": "Book", "page": 1}]
    
    # Mock LLM
    with patch("app.ai.rag_chain.get_vector_store", return_value=mock_store):
        with patch("app.ai.rag_chain.generate_response", return_value="AI Answer") as mock_gen:
            answer, citations, scope = await rag_query(1, "Math", "Question")
            
            assert answer == "AI Answer"
            assert len(citations) == 1
            assert scope is True
            
            # Verify prompt passed to generate_response
            call_args = mock_gen.call_args
            prompt_arg = call_args.kwargs.get('prompt')
            assert "Question" in prompt_arg
            assert "Content" in prompt_arg
            
            print("PASSED")

def main():
    test_prompt_format()
    asyncio.run(test_rag_flow())
    print("\nVerification Complete.")

if __name__ == "__main__":
    main()
