"""Native messaging protocol handler.

Implements the Chrome/Firefox native messaging protocol:
- Messages are JSON objects
- Each message is prefixed with 4-byte message length (little-endian)
- Reads from stdin, writes to stdout
"""

import json
import struct
import sys
from typing import Dict, Any, Optional

from utils.logger import get_logger

logger = get_logger(__name__)


class NativeMessagingProtocol:
    """Handles native messaging protocol encoding/decoding."""

    @staticmethod
    def read_message() -> Optional[Dict[str, Any]]:
        """Read a message from stdin.

        Returns:
            Parsed JSON message or None if stdin is closed
        """
        try:
            # Read 4-byte message length (little-endian unsigned int)
            raw_length = sys.stdin.buffer.read(4)

            if len(raw_length) == 0:
                # stdin closed
                return None

            if len(raw_length) != 4:
                logger.error(f"Invalid message length prefix: {len(raw_length)} bytes")
                return None

            # Unpack message length
            message_length = struct.unpack('=I', raw_length)[0]

            # Read the message
            message_text = sys.stdin.buffer.read(message_length).decode('utf-8')

            # Parse JSON
            message = json.loads(message_text)

            logger.debug(f"Received message: {message.get('type', 'unknown')}")
            return message

        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON message: {e}")
            return None
        except Exception as e:
            logger.error(f"Error reading message: {e}")
            return None

    @staticmethod
    def send_message(message: Dict[str, Any]):
        """Send a message to stdout.

        Args:
            message: Dictionary to send as JSON
        """
        try:
            # Encode message as JSON
            message_json = json.dumps(message)
            message_bytes = message_json.encode('utf-8')

            # Write message length (4 bytes, little-endian)
            length = len(message_bytes)
            sys.stdout.buffer.write(struct.pack('=I', length))

            # Write message
            sys.stdout.buffer.write(message_bytes)
            sys.stdout.buffer.flush()

            logger.debug(f"Sent message: {message.get('type', 'unknown')}")

        except Exception as e:
            logger.error(f"Error sending message: {e}")

    @staticmethod
    def send_error(error_message: str, error_code: str = "UNKNOWN_ERROR"):
        """Send an error message.

        Args:
            error_message: Error description
            error_code: Error code
        """
        NativeMessagingProtocol.send_message({
            "type": "ERROR",
            "error": {
                "code": error_code,
                "message": error_message
            }
        })

    @staticmethod
    def send_response(request_id: str, data: Dict[str, Any]):
        """Send a response to a request.

        Args:
            request_id: ID of the original request
            data: Response data
        """
        NativeMessagingProtocol.send_message({
            "type": "RESPONSE",
            "request_id": request_id,
            "data": data
        })
