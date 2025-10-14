#!/usr/bin/env python3
"""
Basic test script to verify Ableton Live OSC connection.
This script tests the connection to Ableton Live via AbletonOSC.
"""

import sys
import os
# import time
# from typing import Optional

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from tools.osc.song_tools import test_connection, query_ableton, control_ableton
from tools.osc.client import OSCClient, OSC_AVAILABLE


def print_header(title: str):
    """Print a formatted header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def print_test_result(test_name: str, success: bool, message: str = ""):
    """Print formatted test result."""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if message:
        print(f"    {message}")


def test_osc_availability():
    """Test if OSC libraries are available."""
    print_header("Testing OSC Library Availability")

    success = OSC_AVAILABLE
    message = (
        "OSC libraries are available"
        if success
        else "OSC libraries not available - install python-osc"
    )
    print_test_result("OSC Library Check", success, message)

    return success


def test_osc_client_initialization():
    """Test OSC client initialization."""
    print_header("Testing OSC Client Initialization")

    try:
        osc = OSCClient()
        success = osc is not None
        message = f"Client initialized - Host: {osc.ableton_host}, Send Port: {osc.send_port}, Receive Port: {osc.receive_port}"
        print_test_result("OSC Client Initialization", success, message)
        return success
    except Exception as e:
        print_test_result("OSC Client Initialization", False, f"Error: {e}")
        return False


def test_ableton_connection():
    """Test basic connection to Ableton Live."""
    print_header("Testing Ableton Live Connection")

    try:
        result = test_connection()
        success = "✓ Connected" in result
        print_test_result("Ableton Live Connection", success, result)
        return success
    except Exception as e:
        print_test_result("Ableton Live Connection", False, f"Error: {e}")
        return False


def test_basic_queries():
    """Test basic query operations."""
    print_header("Testing Basic Query Operations")

    queries_to_test = [
        ("tempo", "Get current tempo"),
        ("is_playing", "Check if playing"),
        ("num_tracks", "Get number of tracks"),
        ("current_song_time", "Get current song time"),
    ]

    results = []
    for query_type, description in queries_to_test:
        try:
            result = query_ableton(query_type)
            success = not result.startswith("No response") and not result.startswith(
                "Error"
            )
            print_test_result(
                f"Query: {query_type}", success, f"{description} - {result}"
            )
            results.append(success)
        except Exception as e:
            print_test_result(f"Query: {query_type}", False, f"Error: {e}")
            results.append(False)

    return any(results)  # Return True if at least one query succeeded


def test_basic_controls():
    """Test basic control operations (non-destructive)."""
    print_header("Testing Basic Control Operations")

    # Test non-destructive controls
    controls_to_test = [
        ("stop_playing", None, "Stop playback (safe)"),
    ]

    results = []
    for command, value, description in controls_to_test:
        try:
            result = control_ableton(command, value)
            success = "Command executed" in result or "OK" in result
            print_test_result(
                f"Control: {command}", success, f"{description} - {result}"
            )
            results.append(success)
        except Exception as e:
            print_test_result(f"Control: {command}", False, f"Error: {e}")
            results.append(False)

    return any(results)  # Return True if at least one control succeeded


def test_environment_variables():
    """Test and display environment variable configuration."""
    print_header("Environment Configuration")

    env_vars = {
        "ABLETON_OSC_HOST": "Ableton host (default: 127.0.0.1)",
        "ABLETON_OSC_SEND_PORT": "OSC send port (default: 11000)",
        "ABLETON_OSC_RECEIVE_PORT": "OSC receive port (default: 11001)",
    }

    for var, description in env_vars.items():
        value = os.environ.get(var, "Not set (using default)")
        print(f"  {var}: {value} ({description})")


def main():
    """Run all connection tests."""
    print("🎵 Ableton Live OSC Connection Test")
    print("This script tests the connection to Ableton Live via AbletonOSC")
    print("\nPrerequisites:")
    print("1. Ableton Live must be running")
    print("2. AbletonOSC must be enabled in Live's preferences")
    print("3. AbletonOSC should be set to listen on the default ports")

    # Test environment variables
    test_environment_variables()

    # Run tests
    tests = [
        ("OSC Library Availability", test_osc_availability),
        ("OSC Client Initialization", test_osc_client_initialization),
        ("Ableton Live Connection", test_ableton_connection),
        ("Basic Query Operations", test_basic_queries),
        ("Basic Control Operations", test_basic_controls),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ ERROR in {test_name}: {e}")
            results.append((test_name, False))

    # Summary
    print_header("Test Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)

    print(f"Tests passed: {passed}/{total}")

    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"  {status} {test_name}")

    if passed == total:
        print("\n🎉 All tests passed! Ableton Live connection is working correctly.")
        return 0
    elif passed > 0:
        print(f"\n⚠️  {passed}/{total} tests passed. Some functionality may work.")
        return 1
    else:
        print(
            "\n❌ All tests failed. Please check your Ableton Live and AbletonOSC setup."
        )
        return 2


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
