# Amiga 1200 / THEA1200 Bare-Metal Vector Engine v1.0

> **Credits / Autorzy:** `malek69` & **Gemini AI** *(Vibe Coding Edition, 2026 — AI-assisted M68020 bare-metal code & Python toolchain)*


## 1. Architecture & Memory Map
- **CPU Target:** Motorola 68020+ (14 MHz stock A1200 / THEA1200), 32-bit aligned loops.
- **Chip RAM (~66 KB):** Double-buffered 3-bitplane PAL screens (`320x256`, `3 x 10240 B` x 2), dynamic Copperlist, and dual 2048 B Paula DMA audio buffers.
- **Fast RAM (~545 KB BSS + Stream):** 512 KB XOR prefix table (`fill_lut`), `320x256` CPU backbuffer (`fast_bpl1`), `edge_buf` (`10240 B`), and compressed polygon/PCM stream.

## 2. Locked 50.00 Hz PAL Frame Pipeline
1. `wait_vbl` — Waits for raster beam line `Y=260` and swaps `draw_bpl` / `view_bpl` pointers in Copper.
2. `blit_clear_full` — Clears `draw_bpl2` (red accent plane) asynchronously via Blitter.
3. `play_vector_frame` — Reads frame stream (`cur_frame = vbl_tick`), updates foreground AGA color, and dispatches polygons.
4. `draw_polygon_mode` — Clips edges (`0..319 x 0..255`), steps X via 32-bit `inv_tab` (`1/dy`), toggles `edge_buf` bits, and resolves scanlines via `fill_lut` (`op=0` fill, `op=1` cutout, `op=2` BPL2).
5. `Fast -> Chip Copy` — Unrolled `move.l (a0)+,(a1)+` loop transfers `fast_bpl1` to `draw_bpl1` and clears Fast-RAM backbuffer.
6. `apply_blitter_aa` — Blitter shifts `draw_bpl1` by 1px (`BLTCON0=$1dfc`) into `draw_bpl3` (`COLOR04`) for hardware anti-aliasing.

## 3. Audio & Kickstart-Free Boot
- **Paula 4CH DMA (`audio_player.i`):** Channels 0-3 driven in lockstep from Fast-RAM PCM via Level 4 IRQ (`AUD0`), hardware low-pass LED filter disabled (`bset #1,$bfe001`).
- **WHDLoad Slave v17 (`whdload_slave.s`):** `ws_KickSize=0` relocates Hunk segments directly into Fast/Chip RAM without Kickstart ROM files.
