#!/usr/bin/env python3
"""HTTP CONNECT → SOCKS5 bridge using raw sockets for maximum transparency.

Listens on HTTP_PROXY_PORT (default 10807) and forwards every

> Revisit: when HTTP-to-SOCKS proxy logic, async tunneling, or proxy conversion changes. Last touched: 2026-07-02.
HTTP CONNECT request through the local SOCKS5 proxy.

Unlike async-stream versions, this uses select-based raw socket I/O
to avoid buffering issues with TLS passthrough.

Set env TELEGRAM_PROXY=http://127.0.0.1:10807 for the Telegram adapter.
"""

import logging
import os
import select
import socket
import struct
import sys
import threading

logging.basicConfig(level=logging.INFO, format="%(asctime)s [http2socks] %(message)s")
log = logging.getLogger("http2socks")

SOCKS_HOST = os.getenv("SOCKS_PROXY_HOST", "127.0.0.1")
SOCKS_PORT = int(os.getenv("SOCKS_PROXY_PORT", "10806"))
LISTEN_PORT = int(os.getenv("HTTP_PROXY_PORT", "10807"))
LISTEN_HOST = os.getenv("HTTP_PROXY_HOST", "127.0.0.1")


def socks5_connect(target_host: str, target_port: int) -> socket.socket | None:
    """Create a SOCKS5 tunnel to target_host:target_port via the proxy."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(15)
    try:
        s.connect((SOCKS_HOST, SOCKS_PORT))

        # SOCKS5 greeting: version=5, auth=0 (no auth)
        s.sendall(b"\x05\x01\x00")
        resp = s.recv(2)
        if len(resp) < 2 or resp[0] != 0x05 or resp[1] != 0x00:
            log.error("SOCKS5 greeting failed: %s", resp.hex())
            s.close()
            return None

        # SOCKS5 CONNECT request
        host_bytes = target_host.encode("ascii")
        payload = b"\x05\x01\x00\x03"
        payload += struct.pack("!B", len(host_bytes)) + host_bytes
        payload += struct.pack("!H", target_port)
        s.sendall(payload)

        # Read SOCKS5 CONNECT response (variable length)
        resp = s.recv(256)
        if len(resp) < 4 or resp[0] != 0x05 or resp[1] != 0x00:
            log.error("SOCKS5 CONNECT to %s:%d failed: REP=%s", 
                      target_host, target_port, resp[1] if len(resp) > 1 else "?")
            s.close()
            return None

        # Remove timeout for the tunneled connection
        s.settimeout(None)
        log.info("SOCKS5 tunnel established to %s:%d", target_host, target_port)
        return s
    except Exception as e:
        log.error("SOCKS5 connect to %s:%d failed: %s", target_host, target_port, e)
        try:
            s.close()
        except Exception:
            pass
        return None


def bridge_sockets(client_sock: socket.socket, remote_sock: socket.socket):
    """Bidirectional relay between client and remote sockets."""
    sockets = [client_sock, remote_sock]
    try:
        while True:
            readable, _, errors = select.select(sockets, [], sockets, 30)
            if errors:
                break
            if not readable:
                break  # timeout — close connection
            for s in readable:
                try:
                    data = s.recv(65536)
                except Exception:
                    return
                if not data:
                    return
                try:
                    if s is client_sock:
                        remote_sock.sendall(data)
                    else:
                        client_sock.sendall(data)
                except Exception:
                    return
    finally:
        try:
            client_sock.close()
        except Exception:
            pass
        try:
            remote_sock.close()
        except Exception:
            pass


def handle_client(client_sock: socket.socket, addr):
    """Handle one HTTP CONNECT client."""
    try:
        client_sock.settimeout(10)
        # Read HTTP request line
        buf = b""
        while b"\r\n\r\n" not in buf and len(buf) < 8192:
            chunk = client_sock.recv(1024)
            if not chunk:
                return
            buf += chunk

        # Parse "CONNECT host:port HTTP/1.1\r\n..."
        first_line = buf.split(b"\r\n")[0].decode("ascii", errors="replace")
        parts = first_line.split(" ")
        if len(parts) < 2:
            client_sock.close()
            return

        method = parts[0].upper()
        target = parts[1]

        if method != "CONNECT":
            client_sock.close()
            return

        host, port = target.rsplit(":", 1)
        port = int(port)

        # Connect through SOCKS5
        remote_sock = socks5_connect(host, port)
        if remote_sock is None:
            client_sock.sendall(b"HTTP/1.1 502 Bad Gateway\r\n\r\n")
            client_sock.close()
            return

        # Send "200 Connection Established"
        client_sock.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")

        # Remove timeout for bridge
        client_sock.settimeout(None)

        # Now bridge raw TCP data
        bridge_sockets(client_sock, remote_sock)

    except Exception as e:
        log.error("Client %s error: %s", addr, e)
        try:
            client_sock.close()
        except Exception:
            pass


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((LISTEN_HOST, LISTEN_PORT))
    server.listen(32)
    log.info("HTTP→SOCKS5 bridge listening on %s:%d → socks5://%s:%d",
             LISTEN_HOST, LISTEN_PORT, SOCKS_HOST, SOCKS_PORT)

    try:
        while True:
            client_sock, addr = server.accept()
            t = threading.Thread(target=handle_client, args=(client_sock, addr), daemon=True)
            t.start()
    except KeyboardInterrupt:
        log.info("Shutting down")
    finally:
        server.close()


if __name__ == "__main__":
    main()
