#!/usr/bin/env python3
"""
Test script to verify marvin.run function and API key configuration.
"""

import os
import sys
import asyncio
from pathlib import Path

# Load .env file if it exists
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    print(f"📄 Found .env file at: {env_file}")
    print("   Loading environment variables from .env file...")

    # Try using python-dotenv if available
    try:
        from dotenv import load_dotenv

        load_dotenv(env_file, override=False)  # Don't override existing env vars
        print("   ✓ Loaded using python-dotenv")
    except ImportError:
        # Fallback: manually parse .env file
        print("   ⚠️  python-dotenv not installed, parsing manually...")
        loaded_vars = []
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue
                # Parse key=value pairs
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    # Remove quotes if present
                    value = value.strip()
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    # Only set if not already in environment
                    if key and key not in os.environ:
                        os.environ[key] = value
                        loaded_vars.append(key)
        if loaded_vars:
            print(
                f"   ✓ Loaded {len(loaded_vars)} variable(s): {', '.join(loaded_vars)}"
            )
        else:
            print("   ℹ️  No new variables loaded (all already in environment)")
    print()
else:
    print(f"ℹ️  No .env file found at: {env_file}\n")

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def check_api_key():
    """Check if API key is configured."""
    print("=" * 60)
    print("Checking API Key Configuration")
    print("=" * 60)

    # Check OpenAI API key
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print(f"✓ OPENAI_API_KEY is set (length: {len(openai_key)} chars)")
        print(f"  First 10 chars: {openai_key[:10]}...")
    else:
        print("✗ OPENAI_API_KEY is NOT set")

    # Check Marvin-specific API key
    marvin_key = os.getenv("MARVIN_API_KEY")
    if marvin_key:
        print(f"✓ MARVIN_API_KEY is set (length: {len(marvin_key)} chars)")
        print(f"  First 10 chars: {marvin_key[:10]}...")
    else:
        print("ℹ MARVIN_API_KEY is not set (using OPENAI_API_KEY if available)")

    # Check for Anthropic key (in case using Claude)
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key:
        print(f"✓ ANTHROPIC_API_KEY is set (length: {len(anthropic_key)} chars)")
        print(f"  First 10 chars: {anthropic_key[:10]}...")
    else:
        print("ℹ ANTHROPIC_API_KEY is not set")

    # Check for model configuration
    model = os.getenv("MARVIN_AGENT_MODEL")
    if model:
        print(f"✓ MARVIN_AGENT_MODEL is set: {model}")
    else:
        print("ℹ MARVIN_AGENT_MODEL is not set (using default)")

    print()
    return openai_key or marvin_key or anthropic_key


def test_marvin_run_sync():
    """Test marvin.run (synchronous version)."""
    print("=" * 60)
    print("Testing marvin.run (Synchronous)")
    print("=" * 60)

    try:
        import marvin

        # Simple test
        print("Running simple test: 'What is 2+2?'")
        result = marvin.run(
            instructions="What is 2+2? Answer with just the number.", result_type=str
        )
        print(f"✓ Success! Result: {result}")
        print()
        return True

    except Exception as e:
        print(f"✗ Error: {type(e).__name__}: {str(e)}")
        print()
        return False


async def test_marvin_run_async():
    """Test marvin.run_async (asynchronous version)."""
    print("=" * 60)
    print("Testing marvin.run_async (Asynchronous)")
    print("=" * 60)

    try:
        import marvin

        # Simple test
        print("Running simple test: 'What is 3+3?'")
        result = await marvin.run_async(
            instructions="What is 3+3? Answer with just the number.", result_type=str
        )
        print(f"✓ Success! Result: {result}")
        print()
        return True

    except Exception as e:
        print(f"✗ Error: {type(e).__name__}: {str(e)}")
        print()
        return False


def test_marvin_classify():
    """Test marvin.classify (synchronous version)."""
    print("=" * 60)
    print("Testing marvin.classify (Synchronous)")
    print("=" * 60)

    try:
        import marvin

        # Simple test
        print("Running classification test: 'turn on track 1'")
        result = marvin.classify(
            data="turn on track 1", labels=["TRACK", "CLIP", "SONG", "OTHER"]
        )
        print(f"✓ Success! Classification: {result}")
        print()
        return True

    except Exception as e:
        print(f"✗ Error: {type(e).__name__}: {str(e)}")
        print()
        return False


async def test_marvin_classify_async():
    """Test marvin.classify_async (asynchronous version)."""
    print("=" * 60)
    print("Testing marvin.classify_async (Asynchronous)")
    print("=" * 60)

    try:
        import marvin

        # Simple test
        print("Running classification test: 'create a new clip'")
        result = await marvin.classify_async(
            data="create a new clip", labels=["TRACK", "CLIP", "SONG", "OTHER"]
        )
        print(f"✓ Success! Classification: {result}")
        print()
        return True

    except Exception as e:
        print(f"✗ Error: {type(e).__name__}: {str(e)}")
        print()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Marvin API Key Test Script")
    print("=" * 60 + "\n")

    # Check API key configuration
    has_api_key = check_api_key()

    if not has_api_key:
        print("⚠️  WARNING: No API key found!")
        print("   Please set OPENAI_API_KEY or MARVIN_API_KEY environment variable.")
        print("   You can create a .env file in the project root with:")
        print("   OPENAI_API_KEY=your_key_here")
        print()
        return

    # Import config to set up marvin
    try:
        import config  # noqa: F401

        print("✓ Config loaded successfully")
        print()
    except Exception as e:
        print(f"⚠️  Warning: Could not load config: {e}")
        print()

    results = {}

    # Test synchronous functions
    print("\n" + "─" * 60)
    print("SYNCHRONOUS TESTS")
    print("─" * 60 + "\n")

    results["run_sync"] = test_marvin_run_sync()
    results["classify_sync"] = test_marvin_classify()

    # Test asynchronous functions
    print("\n" + "─" * 60)
    print("ASYNCHRONOUS TESTS")
    print("─" * 60 + "\n")

    results["run_async"] = asyncio.run(test_marvin_run_async())
    results["classify_async"] = asyncio.run(test_marvin_classify_async())

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} - {test_name}")

    all_passed = all(results.values())
    print()
    if all_passed:
        print("🎉 All tests passed! Your API key is working correctly.")
    else:
        print("❌ Some tests failed. Check the error messages above.")
        print("\nCommon issues:")
        print("  - API key is invalid or expired")
        print("  - API key doesn't have the right permissions")
        print("  - Network connectivity issues")
        print("  - Rate limiting or quota exceeded")
    print()


if __name__ == "__main__":
    main()
