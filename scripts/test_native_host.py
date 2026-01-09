#!/usr/bin/env python3
"""Test script for native messaging host."""

import struct
import json
import subprocess
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def send_message(proc, message):
    """Send a message to the native host."""
    message_json = json.dumps(message)
    message_bytes = message_json.encode('utf-8')
    length = len(message_bytes)

    # Write length (4 bytes, little-endian)
    proc.stdin.write(struct.pack('=I', length))
    # Write message
    proc.stdin.write(message_bytes)
    proc.stdin.flush()


def read_message(proc):
    """Read a message from the native host."""
    # Read length
    raw_length = proc.stdout.read(4)
    if len(raw_length) == 0:
        return None

    length = struct.unpack('=I', raw_length)[0]

    # Read message
    message_bytes = proc.stdout.read(length)
    message_json = message_bytes.decode('utf-8')
    return json.loads(message_json)


def test_ping():
    """Test ping request."""
    print("\n📌 Testing PING request...")

    host_script = project_root / "native_messaging" / "host.py"

    proc = subprocess.Popen(
        [sys.executable, str(host_script)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    try:
        # Send PING
        send_message(proc, {
            "type": "PING",
            "request_id": "test-ping-1"
        })

        # Read response
        response = read_message(proc)

        if response:
            print(f"✓ Response: {json.dumps(response, indent=2)}")
            return True
        else:
            print("✗ No response received")
            return False

    finally:
        proc.terminate()
        proc.wait(timeout=2)


def test_verify():
    """Test verification request."""
    print("\n📌 Testing VERIFY request...")

    host_script = project_root / "native_messaging" / "host.py"

    proc = subprocess.Popen(
        [sys.executable, str(host_script)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    try:
        # Send VERIFY
        send_message(proc, {
            "type": "VERIFY",
            "request_id": "test-verify-1",
            "data": {
                "text": "The Earth is flat",
                "platform": "test",
                "strategy": "local"
            }
        })

        # Read response
        response = read_message(proc)

        if response:
            print(f"✓ Response: {json.dumps(response, indent=2)}")
            return True
        else:
            print("✗ No response received")
            return False

    finally:
        proc.terminate()
        proc.wait(timeout=2)


def test_status():
    """Test status request."""
    print("\n📌 Testing GET_STATUS request...")

    host_script = project_root / "native_messaging" / "host.py"

    proc = subprocess.Popen(
        [sys.executable, str(host_script)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    try:
        # Send GET_STATUS
        send_message(proc, {
            "type": "GET_STATUS",
            "request_id": "test-status-1"
        })

        # Read response
        response = read_message(proc)

        if response:
            print(f"✓ Response: {json.dumps(response, indent=2)}")
            return True
        else:
            print("✗ No response received")
            return False

    finally:
        proc.terminate()
        proc.wait(timeout=2)


def main():
    """Run all tests."""
    print("=" * 60)
    print("Native Messaging Host Tests")
    print("=" * 60)

    results = []

    # Run tests
    results.append(("PING", test_ping()))
    results.append(("VERIFY", test_verify()))
    results.append(("STATUS", test_status()))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:20} {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
