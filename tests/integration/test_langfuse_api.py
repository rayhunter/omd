"""
Test to understand Langfuse v3.6 API usage.
"""
import os
from dotenv import load_dotenv
load_dotenv()

from langfuse import Langfuse

# Initialize client
client = Langfuse(
    public_key=os.getenv('LANGFUSE_PUBLIC_KEY'),
    secret_key=os.getenv('LANGFUSE_SECRET_KEY'),
    host=os.getenv('LANGFUSE_HOST'),
    debug=True
)

print("Testing Langfuse v3.6 API...")

# Test 1: Create a trace with metadata
print("\n1. Creating trace with metadata...")
with client.start_as_current_span(name="test_trace") as span:
    client.update_current_trace(
        user_id="test_user_123",
        session_id="test_session_456",
        tags=["test", "api_check"],
        metadata={"environment": "test"}
    )
    print("   ✅ Trace created with metadata")

# Test 2: Create a generation (LLM call)
print("\n2. Creating generation (LLM call)...")
with client.start_as_current_generation(
    name="llm_call_test",
    model="gpt-3.5-turbo"
) as generation:
    generation.update(
        input="What is the capital of France?",
        output="The capital of France is Paris.",
        usage={
            "input": 10,
            "output": 8,
            "total": 18
        },
        metadata={"provider": "openai"}
    )
    print("   ✅ Generation created")

# Test 3: Nested spans
print("\n3. Creating nested spans...")
with client.start_as_current_span(name="parent_operation") as parent:
    parent.update(metadata={"level": "parent"})

    with client.start_as_current_span(name="child_operation") as child:
        child.update(
            input="child input",
            output="child output",
            metadata={"level": "child"}
        )

    print("   ✅ Nested spans created")

# Test 4: Score a trace
print("\n4. Scoring trace...")
with client.start_as_current_span(name="scored_operation") as span:
    span.update(output="test output")

client.score_current_trace(
    name="quality",
    value=0.95,
    comment="Test score"
)
print("   ✅ Trace scored")

# Flush and shutdown
print("\n5. Flushing to Langfuse...")
client.flush()
client.shutdown()
print("   ✅ Flushed and shutdown")

print("\n✅ All API tests complete!")
print("Check your dashboard at: https://us.cloud.langfuse.com")
