"""Tiny HTTP CONNECT proxy that tunnels to a SOCKS5 upstream.

Usage:
    python proxy_bridge.py [--listen 127.0.0.1:18080] [--socks5 127.0.0.1:10806]

> Revisit: when proxy bridge logic, HTTP-to-SOCKS conversion, or proxy health changes. Last touched: 2026-07-02.

This lets httpx (and any HTTP client) reach HTTPS destinations through
a SOCKS5 proxy by speaking plain HTTP CONNECT to localhost.

httpx handles HTTP CONNECT proxies flawlessly; it's the built-in
socksio transport that intermittently drops TLS handshakes.
"""

import asyncio
import argparse
import logging
import socket

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger("proxy_bridge")


async def relay(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    """Forward bytes between two streams until one side closes."""
    try:
        while True:
            data = await reader.read(65536)
            if not data:
                break
            writer.write(data)
            await writer.drain()
    except (ConnectionError, asyncio.IncompleteReadError):
        pass
    finally:
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass


async def handle_client(
    client_reader: asyncio.StreamReader,
    client_writer: asyncio.StreamWriter,
    socks5_host: str,
    socks5_port: int,
):
    """Handle one HTTP CONNECT tunnel."""
    peer = client_writer.get_extra_info("peername")
    try:
        # Read the CONNECT request
        line = await asyncio.wait_for(client_reader.readline(), timeout=30)
        method, target, _ = line.decode().split(" ", 2)
        host, port = target.rsplit(":", 1)
        port = int(port)

        # Read and discard headers until blank line
        while True:
            h = await asyncio.wait_for(client_reader.readline(), timeout=30)
            if h in (b"\r\n", b"\n", b""):
                break

        # Connect to SOCKS5 upstream and handshake
        sr, sw = await asyncio.wait_for(
            asyncio.open_connection(socks5_host, socks5_port), timeout=30
        )
        try:
            # SOCKS5 greeting
            sw.write(b"\x05\x01\x00")
            await sw.drain()
            resp = await asyncio.wait_for(sr.readexactly(2), timeout=30)
            if resp[1] != 0x00:
                raise Exception(f"SOCKS5 auth failed: {resp.hex()}")

            # SOCKS5 CONNECT request (domain name)
            domain = host.encode()
            sw.write(
                b"\x05\x01\x00\x03"
                + bytes([len(domain)])
                + domain
                + port.to_bytes(2, "big")
            )
            await sw.drain()
            resp = await asyncio.wait_for(sr.readexactly(10), timeout=30)
            if resp[1] != 0x00:
                raise Exception(f"SOCKS5 connect failed: {resp.hex()}")

            # Tell the HTTP client the tunnel is established
            client_writer.write(b"HTTP/1.1 200 Connection Established\r\n\r\n")
            await client_writer.drain()

            # Relay data in both directions
            await asyncio.gather(
                relay(client_reader, sw),
                relay(sr, client_writer),
            )
        except Exception:
            sr.close()
            sw.close()
    except Exception as e:
        log.debug("tunnel error %s: %s", peer, e)
        try:
            client_writer.write(b"HTTP/1.1 502 Bad Gateway\r\n\r\n")
            await client_writer.drain()
        except Exception:
            pass
        client_writer.close()


async def main(host: str, port: int, socks5_host: str, socks5_port: int):
    server = await asyncio.start_server(
        lambda r, w: handle_client(r, w, socks5_host, socks5_port),
        host,
        port,
    )
    log.info("HTTP CONNECT proxy on %s:%d -> socks5://%s:%d", host, port, socks5_host, socks5_port)
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="HTTP CONNECT -> SOCKS5 bridge")
    p.add_argument("--listen", default="127.0.0.1:18080", help="host:port to listen on")
    p.add_argument("--socks5", default="127.0.0.1:10806", help="host:port of SOCKS5 upstream")
    args = p.parse_args()
    lh, lp = args.listen.rsplit(":", 1)
    sh, sp = args.socks5.rsplit(":", 1)
    asyncio.run(main(lh, int(lp), sh, int(sp)))
