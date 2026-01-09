#!/usr/bin/env python3
"""Native messaging host for CircleNClick browser extension.

This script runs as a native messaging host, communicating with the browser
extension via stdin/stdout using the native messaging protocol.
"""

import asyncio
import sys
import os
from pathlib import Path
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from native_messaging.protocol import NativeMessagingProtocol
from core.verification_engine import VerificationEngine
from core.hybrid_decisor import VerificationStrategy
from utils.logger import get_logger, setup_logger
from utils.config import settings

# Ensure logs directory exists
settings.ensure_directories()

# Setup logger for native host (log to file, not stdout)
logger = setup_logger(name="native_host", log_file="logs/native_host.log")


class NativeMessagingHost:
    """Native messaging host that handles extension requests."""

    def __init__(self):
        """Initialize the native messaging host."""
        self.protocol = NativeMessagingProtocol()
        self.engine = VerificationEngine()
        self.logger = logger
        self.logger.info("Native messaging host started")

    async def handle_message(self, message: Dict[str, Any]):
        """Handle a message from the extension.

        Args:
            message: Message from extension
        """
        try:
            message_type = message.get("type")
            request_id = message.get("request_id", "unknown")

            self.logger.info(f"Handling message type: {message_type} (ID: {request_id})")

            if message_type == "VERIFY":
                await self.handle_verify_request(request_id, message.get("data", {}))
            elif message_type == "PING":
                self.handle_ping_request(request_id)
            elif message_type == "GET_STATUS":
                self.handle_status_request(request_id)
            else:
                self.protocol.send_error(
                    f"Unknown message type: {message_type}",
                    "UNKNOWN_MESSAGE_TYPE"
                )

        except Exception as e:
            self.logger.error(f"Error handling message: {e}", exc_info=True)
            self.protocol.send_error(str(e), "INTERNAL_ERROR")

    async def handle_verify_request(self, request_id: str, data: Dict[str, Any]):
        """Handle a verification request.

        Args:
            request_id: Request ID
            data: Request data containing text, url, platform, etc.
        """
        try:
            text = data.get("text")
            if not text:
                self.protocol.send_error("Missing 'text' field", "MISSING_FIELD")
                return

            url = data.get("url")
            platform = data.get("platform")
            author = data.get("author")
            strategy_str = data.get("strategy", "hybrid")

            # Map strategy string to enum
            strategy_map = {
                "local": VerificationStrategy.LOCAL_ONLY,
                "cloud": VerificationStrategy.CLOUD_ONLY,
                "hybrid": VerificationStrategy.HYBRID
            }
            strategy = strategy_map.get(strategy_str, VerificationStrategy.HYBRID)

            # Run verification
            result = await self.engine.verify(
                text=text,
                url=url,
                platform=platform,
                author=author,
                user_preference=strategy
            )

            # Send response
            self.protocol.send_response(request_id, result.to_dict())

        except Exception as e:
            self.logger.error(f"Verification error: {e}", exc_info=True)
            self.protocol.send_error(str(e), "VERIFICATION_ERROR")

    def handle_ping_request(self, request_id: str):
        """Handle a ping request.

        Args:
            request_id: Request ID
        """
        self.protocol.send_response(request_id, {
            "status": "ok",
            "message": "pong"
        })

    def handle_status_request(self, request_id: str):
        """Handle a status request.

        Args:
            request_id: Request ID
        """
        from utils.config import settings
        from storage.cache import cache

        cache_stats = cache.stats()

        self.protocol.send_response(request_id, {
            "status": "running",
            "cloud_apis_configured": settings.has_cloud_apis(),
            "cache": cache_stats
        })

    async def run(self):
        """Run the native messaging host main loop."""
        self.logger.info("Starting message loop")

        try:
            while True:
                # Read message from stdin
                message = self.protocol.read_message()

                if message is None:
                    # stdin closed, exit
                    self.logger.info("stdin closed, exiting")
                    break

                # Handle message
                await self.handle_message(message)

        except KeyboardInterrupt:
            self.logger.info("Interrupted by user")
        except Exception as e:
            self.logger.error(f"Fatal error in message loop: {e}", exc_info=True)
        finally:
            self.logger.info("Native messaging host stopped")


def main():
    """Main entry point for native messaging host."""
    try:
        host = NativeMessagingHost()
        asyncio.run(host.run())
    except Exception as e:
        logger.error(f"Failed to start native messaging host: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
