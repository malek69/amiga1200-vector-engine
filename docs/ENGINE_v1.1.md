# Amiga 1200 / THEA1200 Bare-Metal Vector Engine v1.1.0

> **Credits / Autorzy:** `malek69` & **Gemini AI** *(Vibe Coding Edition, 2026 — AI-assisted M68020 bare-metal code & Python toolchain)*

## 1. Architecture & Memory Map (Hi-Res 640x256)
- **CPU Target:** Motorola 68020+ (14 MHz stock A1200 / THEA1200), 32-bit aligned `movem.l` burst loops.
- **AGA Video Mode:** Native **Hi-Res `640x256`** (`BPLCON0 = $A200`, `DDFSTRT = $003C`, `DDFSTOP = $00D4`, `80 bytes/line`, `20,480 B/bitplane`) with **64-bit bitplane DMA fetch (`FMODE = $0003`)**.
- **Chip RAM (~86 KB):** Double-buffered 2-bitplane Hi-Res PAL screens (`640x256`, `2 x 20,480 B` x 2 = `81,920 B`), Copperlist (`80 B`), and dual `2048 B` Paula DMA audio buffers (`4,096 B`).
- **Fast RAM (~586 KB BSS + Stream):** 512 KB XOR prefix table (`fill_lut`), `640x256` CPU backbuffers (`fast_bpl1` + `fast_bpl2` = `40,960 B`), `edge_buf` (`20,480 B`), and compressed 16-bit polygon/PCM stream.

## 2. Locked 50.00 Hz PAL Frame Pipeline
1. `clear_fast_buffers` — Clears both `640x256` Fast-RAM bitplanes (`40,960 B`) using unrolled `movem.l` (`48 B/iter`).
2. `play_vector_frame` — Reads frame stream (`cur_frame = vbl_tick`) and dispatches polygons to `draw_polygon_mode`.
3. `draw_polygon_mode` — Scans 16-bit edges (`0..639` x `0..255`) into `edge_buf` and XOR-fills spans into Fast RAM via `fill_lut`.
4. `copy_fast_to_chip` — Transfers both `20,480 B` bitplanes from Fast RAM to active Chip-RAM draw buffers via unrolled `movem.l` (`48 B/iter`).
5. `wait_vbl` — Synchronizes to vertical blank IRQ and swaps Copper bitplane pointers atomically.
