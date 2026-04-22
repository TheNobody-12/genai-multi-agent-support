"""
test_lmstudio.py — Quick smoke test to verify the system works with LM Studio local models.

Tests:
  1. LM Studio server connectivity
  2. Chat completion via llm_factory
  3. Embeddings via llm_factory
  4. Full router pipeline (classify → agent → response)
"""

import os
import sys
import json

# ── Setup env for LM Studio ──
os.environ["LLM_PROVIDER"] = "lmstudio"
os.environ["LM_STUDIO_BASE_URL"] = "http://localhost:1234/v1"
os.environ["LM_STUDIO_API_KEY"] = "lm-studio"
os.environ["LM_STUDIO_MODEL"] = "google/gemma-4-e4b"
os.environ["LM_STUDIO_EMBED_MODEL"] = "text-embedding-nomic-embed-text-v1.5"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests

PASS = "✅"
FAIL = "❌"
WARN = "⚠️"

def divider(title):
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print(f"{'─' * 60}")


# ──────────────── Test 1: Server Connectivity ─────────────────

divider("Test 1: LM Studio Server Connectivity")

try:
    resp = requests.get("http://localhost:1234/v1/models", timeout=5)
    resp.raise_for_status()
    models = resp.json()
    print(f"{PASS} LM Studio server is running")
    print(f"   Available models:")
    for m in models.get("data", []):
        print(f"     • {m['id']}")
except Exception as e:
    print(f"{FAIL} LM Studio server is NOT reachable: {e}")
    print("   Please start LM Studio and load a model before running this test.")
    sys.exit(1)


# ──────────────── Test 2: Chat Completion ─────────────────────

divider("Test 2: Chat Completion (llm_factory.get_llm)")

try:
    from llm_factory import get_llm
    llm = get_llm(temperature=0.1)
    print(f"   Provider: lmstudio")
    print(f"   Model:    {llm.model_name}")
    print(f"   Base URL: {llm.openai_api_base}")
    
    response = llm.invoke("Say hello in exactly 5 words.")
    content = response.content
    if isinstance(content, list):
        content = " ".join([str(block) for block in content])
    print(f"{PASS} Chat completion succeeded")
    print(f"   Response: {content}")
except Exception as e:
    print(f"{FAIL} Chat completion failed: {e}")
    import traceback
    traceback.print_exc()


# ──────────────── Test 3: Embeddings ──────────────────────────

divider("Test 3: Embeddings (llm_factory.get_embeddings)")

try:
    from llm_factory import get_embeddings
    embeddings = get_embeddings()
    print(f"   Model: {embeddings.model}")
    
    test_texts = ["Customer refund policy", "Support ticket escalation"]
    vectors = embeddings.embed_documents(test_texts)
    
    print(f"{PASS} Embedding generation succeeded")
    print(f"   Input texts: {len(test_texts)}")
    print(f"   Vector dims: {len(vectors[0])}")
    print(f"   First 5 values: {vectors[0][:5]}")
except Exception as e:
    print(f"{FAIL} Embedding generation failed: {e}")
    import traceback
    traceback.print_exc()


# ──────────────── Test 4: Query Classification ────────────────

divider("Test 4: Query Classification (Router)")

try:
    from agents.router import classify_query
    
    test_cases = [
        ("Show me all premium customers", "sql"),
        ("What is the refund policy?", "rag"),
        ("Does customer Ema qualify for a refund based on our policy?", "both"),
    ]
    
    all_passed = True
    for query, expected in test_cases:
        state = {
            "query": query,
            "classification": "",
            "sql_response": "",
            "rag_response": "",
            "final_response": "",
        }
        result = classify_query(state)
        actual = result["classification"]
        status = PASS if actual == expected else WARN
        if actual != expected:
            all_passed = False
        print(f"   {status} \"{query}\"")
        print(f"      Expected: {expected} | Got: {actual}")
    
    if all_passed:
        print(f"\n{PASS} All classifications correct")
    else:
        print(f"\n{WARN} Some classifications differ (local model may classify differently — this is acceptable)")
except Exception as e:
    print(f"{FAIL} Classification test failed: {e}")
    import traceback
    traceback.print_exc()


# ──────────────── Test 5: Full Router Pipeline ────────────────

divider("Test 5: Full Router Pipeline (end-to-end)")

try:
    from agents.router import query_router
    
    test_query = "Show me all open support tickets"
    print(f"   Query: \"{test_query}\"")
    print(f"   Processing...")
    
    response = query_router(test_query, thread_id="lmstudio-test")
    
    print(f"{PASS} Full pipeline completed successfully")
    print(f"   Response (first 500 chars):")
    print(f"   {response[:500]}")
except Exception as e:
    print(f"{FAIL} Full pipeline failed: {e}")
    import traceback
    traceback.print_exc()


# ──────────────── Summary ─────────────────────────────────────

divider("Summary")
print("  LM Studio integration test complete.")
print("  If all tests show ✅, the system is working correctly with local models.")
print("  ⚠️ warnings on classification are acceptable — local models may classify differently than Gemini.")
print()
