"""
OSC client and response handling for AbletonOSC.
"""
from __future__ import annotations

import os
import threading
import time
from typing import Any, List, Optional

from pythonosc import udp_client
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer

OSC_AVAILABLE = False # Set to False to run in simulation mode


class OSCResponse:
    def __init__(self):
        self.data: Any = None
        self.received: bool = False
        self.address: Optional[str] = None

    def set(self, address: str, *args):
        self.address = address
        self.data = args
        self.received = True


class OSCClient:
    _instance: Optional['OSCClient'] = None
    _lock: threading.Lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, '_initialized', False):
            return

        # Configurable via env, with safe defaults
        self.ableton_host = os.environ.get('ABLETON_OSC_HOST', '127.0.0.1')
        self.send_port = int(os.environ.get('ABLETON_OSC_SEND_PORT', '11000'))
        self.receive_port = int(os.environ.get(
            'ABLETON_OSC_RECEIVE_PORT', '11001'))

        self.client = None
        self.server = None
        self.dispatcher = None
        self.response = OSCResponse()
        self._initialized = True

        if OSC_AVAILABLE:
            self._setup_client()
            self._setup_server()

    def _setup_client(self):
        self.client = udp_client.SimpleUDPClient(
            self.ableton_host, self.send_port)

    def _setup_server(self):
        self.dispatcher = Dispatcher()
        self.dispatcher.map('/live/*', self._response_handler,
                            needs_reply_address=True)
        try:
            self.server = ThreadingOSCUDPServer(
                (self.ableton_host, self.receive_port), self.dispatcher)
            server_thread = threading.Thread(
                target=self.server.serve_forever, daemon=True)
            server_thread.start()
        except OSError:
            self.server = None

    def _response_handler(self, client_address, address: str, *args):
        self.response.set(address, *args)

    def send_and_wait(self, address: str, args: Optional[List] = None, timeout: float = 2.0):
        if not OSC_AVAILABLE or not self.client:
            return f"[SIMULATION MODE] Would send OSC: {address} {args or []}"

        # Reset response state
        self.response.received = False
        self.response.data = None

        try:
            if args:
                self.client.send_message(address, args)
            else:
                self.client.send_message(address, [])
        except Exception as e:
            return f"Error sending OSC message: {e}"

        start_time = time.time()
        while not self.response.received and (time.time() - start_time) < timeout:
            time.sleep(0.01)

        if self.response.received:
            if self.response.data is None:
                return 'OK'
            data = self.response.data
            if len(data) == 0:
                return 'OK'
            if len(data) == 1:
                return data[0]
            return data
        return None
