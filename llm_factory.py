"""
llm_factory.py — Universal singleton provider for LLMs and embeddings.
Allows switching seamlessly between Google Gemini and local LM Studio.
"""

import os

# Helper to get provider preference (defaults to gemini for backward compatibility)
def get_provider():
    return os.environ.get("LLM_PROVIDER", "gemini").lower()

def get_llm(temperature=0.0):
    provider = get_provider()
    
    if provider == "lmstudio":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            base_url=os.environ.get("LM_STUDIO_BASE_URL", "http://localhost:1234/v1"),
            api_key=os.environ.get("LM_STUDIO_API_KEY", "lm-studio"),
            model=os.environ.get("LM_STUDIO_MODEL", "local-model"),
            temperature=temperature
        )
    elif provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=os.environ.get("OPENAI_MODEL", "gpt-4o"),
            api_key=os.environ.get("OPENAI_API_KEY"),
            temperature=temperature
        )
    elif provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model_name=os.environ.get("ANTHROPIC_MODEL", "claude-3-7-sonnet-20250219"),
            anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY"),
            temperature=temperature
        )
    else:
        # Default to Gemini
        gemini_key = os.environ.get("GEMINI_API_KEY")
        if not gemini_key:
            raise ValueError("GEMINI_API_KEY environment variable is missing.")
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model="gemini-3-flash-preview",
            google_api_key=gemini_key,
            temperature=temperature,
        )

def get_embeddings():
    provider = get_provider()
    
    if provider == "lmstudio":
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(
            base_url=os.environ.get("LM_STUDIO_BASE_URL", "http://localhost:1234/v1"),
            api_key=os.environ.get("LM_STUDIO_API_KEY", "lm-studio"),
            model=os.environ.get("LM_STUDIO_EMBED_MODEL", "text-embedding-nomic"),
            # LM Studio rejects tokenized (int-array) input; send raw strings instead
            check_embedding_ctx_length=False,
        )
    elif provider == "openai":
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(
            model=os.environ.get("OPENAI_EMBED_MODEL", "text-embedding-3-small"),
            api_key=os.environ.get("OPENAI_API_KEY"),
        )
    elif provider == "anthropic":
        raise NotImplementedError("Anthropic does not natively provide embeddings. Please use a different provider (e.g., set LLM_PROVIDER=openai for embeddings or use Voyage AI).")
    else:
        # Default to Gemini Embeddings
        gemini_key = os.environ.get("GEMINI_API_KEY")
        if not gemini_key:
            raise ValueError("GEMINI_API_KEY environment variable is missing.")
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        return GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=gemini_key,
        )
