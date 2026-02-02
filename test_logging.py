#!/usr/bin/env python3
"""
Test script to demonstrate OpenAI API logging

Run this to see what the logs look like without making actual API calls
"""

import os
import sys
from api_logger import OpenAILogger

def test_logging():
    """Demonstrate logging with mock data"""
    
    # Create logger
    logger = OpenAILogger(log_dir="./test_logs")
    
    print("📝 Testing OpenAI API Logger...")
    print(f"📁 Logs will be written to: {logger.log_file}")
    print()
    
    # Test 1: Chat completion request
    print("1️⃣  Testing chat completion logging...")
    request_id = logger.log_request(
        operation="generate_tailored_cv",
        model="gpt-4-turbo-preview",
        messages=[
            {
                "role": "system",
                "content": "You are Edward Baitsewe's expert CV writer."
            },
            {
                "role": "user",
                "content": "Generate a CV for a Full Stack Developer position at TechCorp..."
            }
        ],
        temperature=0.2,
        response_format={"type": "json_object"}
    )
    
    # Mock response
    class MockMessage:
        content = '{"header": {"name": "Edward Baitsewe"}, "summary": "Full Stack Developer..."}'
    
    class MockChoice:
        message = MockMessage()
    
    class MockUsage:
        prompt_tokens = 2847
        completion_tokens = 1523
        total_tokens = 4370
    
    class MockResponse:
        model = "gpt-4-turbo-preview"
        choices = [MockChoice()]
        usage = MockUsage()
    
    logger.log_response(request_id, MockResponse())
    logger.log_summary("generate_tailored_cv", 3333.45)
    print(f"✅ Logged chat completion (Request ID: {request_id})")
    print()
    
    # Test 2: Embedding request
    print("2️⃣  Testing embedding logging...")
    request_id = logger.log_request(
        operation="generate_embedding",
        model="text-embedding-3-small",
        input_text="ActuallyFind – Core Platform: Production marketplace built with Laravel 11...",
        dimensions=1024
    )
    
    # Mock embedding response
    class MockEmbeddingData:
        embedding = [0.1] * 1024
    
    class MockEmbeddingUsage:
        prompt_tokens = 50
        total_tokens = 50
    
    class MockEmbeddingResponse:
        model = "text-embedding-3-small"
        data = [MockEmbeddingData()]
        usage = MockEmbeddingUsage()
    
    logger.log_response(request_id, MockEmbeddingResponse())
    logger.log_summary("generate_embedding", 145.67)
    print(f"✅ Logged embedding (Request ID: {request_id})")
    print()
    
    # Test 3: Error logging
    print("3️⃣  Testing error logging...")
    request_id = logger.log_request(
        operation="extract_skills_from_job",
        model="gpt-4-turbo-preview",
        messages=[{"role": "user", "content": "Extract skills from: ..."}],
        temperature=0.1
    )
    
    logger.log_response(
        request_id,
        None,
        error=Exception("API rate limit exceeded")
    )
    print(f"✅ Logged error (Request ID: {request_id})")
    print()
    
    print("=" * 80)
    print(f"✨ Test complete! Check the log file:")
    print(f"   {logger.log_file}")
    print()
    print("📖 You can view it with:")
    print(f"   cat {logger.log_file}")
    print(f"   # or")
    print(f"   tail -f {logger.log_file}")
    print("=" * 80)

if __name__ == "__main__":
    test_logging()