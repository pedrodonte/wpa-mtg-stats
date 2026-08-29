"""Genera iconos PNG PWA (192 y 512) sin dependencias externas.

Dibuja un fondo sólido con un rombo (mana-ish) centrado. Usa solo la
biblioteca estándar (zlib + struct) para emitir PNG RGBA válidos.
"""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

# Paleta tricolor (W/U/R)
BG = (11, 18, 32)        # #0B1220 azul noche
W_COL = (245, 243, 231)  # #F5F3E7 blanco marfil (W)
U_COL = (59, 125, 216)   # #3B7DD8 azul (U)
R_COL = (232, 73, 59)    # #E8493B rojo (R)
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
    """Rombo tricolor dividido en tres franjas diagonales: W / U / R."""
    cx = cy = size / 2
    r = size * 0.36
    buf = bytearray()
    for y in range(size):
        for x in range(size):
            dx = x - cx
            dy = y - cy
            if abs(dx) + abs(dy) <= r:
                # Franjas diagonales según posición sobre el eje x normalizado.
                t = (dx + r) / (2 * r)  # 0..1 de izquierda a derecha
                if t < 0.34:
                    buf.extend((*W_COL, 255))
                elif t < 0.67:
                    buf.extend((*U_COL, 255))
                else:
                    buf.extend((*R_COL, 255))
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
