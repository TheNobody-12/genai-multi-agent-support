import os
from unittest import mock
import pytest
from llm_factory import get_provider, get_llm, get_embeddings

def test_get_provider_default():
    with mock.patch.dict(os.environ, {}, clear=True):
        assert get_provider() == "gemini"

def test_get_provider_lmstudio():
    with mock.patch.dict(os.environ, {"LLM_PROVIDER": "lmstudio"}):
        assert get_provider() == "lmstudio"

def test_get_llm_gemini():
    with mock.patch.dict(os.environ, {"LLM_PROVIDER": "gemini", "GEMINI_API_KEY": "test"}):
        llm = get_llm()
        assert llm.__class__.__name__ == "ChatGoogleGenerativeAI"

def test_get_llm_lmstudio():
    with mock.patch.dict(os.environ, {"LLM_PROVIDER": "lmstudio", "LM_STUDIO_API_KEY": "test"}):
        llm = get_llm()
        assert llm.__class__.__name__ == "ChatOpenAI"
        assert llm.temperature == 0.0

def test_get_embeddings_gemini():
    with mock.patch.dict(os.environ, {"LLM_PROVIDER": "gemini", "GEMINI_API_KEY": "test"}):
        embed = get_embeddings()
        assert embed.__class__.__name__ == "GoogleGenerativeAIEmbeddings"

def test_get_embeddings_lmstudio():
    with mock.patch.dict(os.environ, {"LLM_PROVIDER": "lmstudio", "LM_STUDIO_API_KEY": "test"}):
        embed = get_embeddings()
        assert embed.__class__.__name__ == "OpenAIEmbeddings"

def test_get_llm_openai():
    with mock.patch.dict(os.environ, {"LLM_PROVIDER": "openai", "OPENAI_API_KEY": "test"}):
        llm = get_llm()
        assert llm.__class__.__name__ == "ChatOpenAI"
        assert llm.temperature == 0.0

def test_get_embeddings_openai():
    with mock.patch.dict(os.environ, {"LLM_PROVIDER": "openai", "OPENAI_API_KEY": "test"}):
        embed = get_embeddings()
        assert embed.__class__.__name__ == "OpenAIEmbeddings"

def test_get_llm_anthropic():
    with mock.patch.dict(os.environ, {"LLM_PROVIDER": "anthropic", "ANTHROPIC_API_KEY": "test"}):
        llm = get_llm()
        assert llm.__class__.__name__ == "ChatAnthropic"
        assert llm.temperature == 0.0

def test_get_embeddings_anthropic():
    with mock.patch.dict(os.environ, {"LLM_PROVIDER": "anthropic", "ANTHROPIC_API_KEY": "test"}):
        with pytest.raises(NotImplementedError):
            get_embeddings()
