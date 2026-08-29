"""Genera iconos PNG PWA (192 y 512) sin dependencias externas.

Dibuja un fondo sólido con un rombo (mana-ish) centrado. Usa solo la
biblioteca estándar (zlib + struct) para emitir PNG RGBA válidos.
"""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

# Paleta Matrix
BG = (10, 15, 10)         # #0A0F0A negro con tinte verde
GREEN = (0, 255, 65)      # #00FF41 verde Matrix
GREEN_DIM = (18, 90, 36)  # verde oscuro (halo interior)
STATIC = Path(__file__).resolve().parent.parent / "static"


def _png(width: int, height: int, pixels: bytes) -> bytes:
    def chunk(tag: bytes, data: bytes) -> bytes:
        c = tag + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)  # RGBA
    raw = bytearray()
    stride = width * 4
    for y in range(height):
        raw.append(0)  # filtro None
        raw.extend(pixels[y * stride:(y + 1) * stride])
    idat = zlib.compress(bytes(raw), 9)
    return sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")


def make(size: int) -> bytes:
    """Rombo verde Matrix sobre fondo negro, con borde neón y halo interior."""
    cx = cy = size / 2
    r = size * 0.38
    inner = r * 0.62  # borde del anillo neón
    buf = bytearray()
    for y in range(size):
        for x in range(size):
            d = abs(x - cx) + abs(y - cy)  # distancia rómbica
            if d <= r:
                if d >= inner:
                    buf.extend((*GREEN, 255))      # borde neón brillante
                else:
                    buf.extend((*GREEN_DIM, 255))  # interior verde oscuro
            else:
                buf.extend((*BG, 255))
    return _png(size, size, bytes(buf))


def main() -> None:
    STATIC.mkdir(parents=True, exist_ok=True)
    for size in (192, 512):
        out = STATIC / f"icon-{size}.png"
        out.write_bytes(make(size))
        print(f"escrito {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
