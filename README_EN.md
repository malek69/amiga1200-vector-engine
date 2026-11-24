[Polski](README.md) | [**English**](README_EN.md) | [Historia Zmian (PL)](CHANGELOG.md) | [Changelog (EN)](CHANGELOG_EN.md)

![Logo](docs/engine_logo.png)

# Amiga 1200 / THEA1200 Vector Stream Demo Engine v1.1.0

**Bare-metal M68020+ / AGA Hi-Res 640x256 @ 50.00 FPS PAL Vector Demo Engine** (*malek69 & Gemini AI, 2026*)

## Downloads & Preview (v1.1.0 Latest)

| Median A1200 v1.1.0 (640x256) | Bad Apple!! A1200 v1.1.0 (640x256) |
| :---: | :---: |
| ![Median](docs/preview_median.png) | ![Bad Apple](docs/preview.png) |
| **[Download .LHA (THEA1200/RetroArch)](https://github.com/malek69/amiga1200-vector-engine/releases/download/v1.1.0/MedianA1200_AGA_THEA1200.lha)**<br>**[Download .ZIP (FS-UAE/WinUAE)](https://github.com/malek69/amiga1200-vector-engine/releases/download/v1.1.0/MedianA1200_AGA_THEA1200_FSUAE.zip)** | **[Download .LHA (THEA1200/RetroArch)](https://github.com/malek69/amiga1200-vector-engine/releases/download/v1.1.0/BadappleA1200_AGA_THEA1200.lha)**<br>**[Download .ZIP (FS-UAE/WinUAE)](https://github.com/malek69/amiga1200-vector-engine/releases/download/v1.1.0/BadappleA1200_AGA_THEA1200_FSUAE.zip)** |

## Requirements & Controls
- **Hardware:** Amiga 1200 (68EC020+ 14 MHz, AGA, **2 MB Chip RAM + 8 MB Fast RAM**), **THEA1200**, FS-UAE, or WinUAE (Kickstart-free WHDLoad Slave v17).
- **Exit:** `LMB`, **Fire (Joystick Port 2 / THEA1200)**, or `ESC`.

## Engine Capabilities
- **N-gon XOR LUT Rasterizer:** fast arbitrary-vertex polygon filling and hole cutouts via a 512 KB prefix table in Fast RAM.
- **M68020+ / AGA & 4CH Paula DMA:** VBL-locked `50.00 FPS PAL` double-buffering, 4CH PCM audio (LED filter off), and Python video converters (`tools/`).

## What is New in v1.1.0
- **AGA Hi-Res `640x256` (`BPLCON0 = $A200`, `DDFSTOP = $00CC`, `FMODE = $0003`):** 2x horizontal sharpness with 64-bit DMA and zero CPU contention.
- **Fast-RAM Backbuffer + `movem.l` Burst & THEA1200:** Fast-RAM rasterization, `48 B/iter` Chip-RAM copy, and THEA1200 gamepad exit.

## Engine Architecture &amp; Modules (`src/`)

| Module | Role | Hardware &amp; Algorithms |
| :--- | :--- | :--- |
| **`main.s`** | Main 50 Hz PAL Loop | VBL frame lock (`50.00 FPS`), Fast-RAM buffer clear, and unrolled `movem.l` (`48 B/iter`) `Fast -> Chip` burst transfer |
| **`gfx_engine.i`** | AGA &amp; Copper Setup | Hardware takeover (`sys_takeover`), native **AGA Hi-Res `640x256`** (`BPLCON0 = $A200`, `DDFSTOP = $00CC`), 64-bit bitplanes (`FMODE = $0003`), VBL double-buffering |
| **`vec3d_engine.i`** | N-gon Polygon Rasterizer | 16-bit edge stepping (`0..639 x 0..255`) into `edge_buf` and XOR span filling with hole cutouts via 512 KB `fill_lut` in Fast RAM |
| **`scene_player.i`** | Frame Stream Decoder | Reads `vec_frame_table` stream and dispatches polygons to target AGA bitplanes |
| **`audio_player.i`** | 4CH Paula DMA Audio | Streams PCM audio from Fast RAM via dual `2048 B` Chip-RAM buffers (Level 4 IRQ) with hardware LED filter disabled |
| **`whdload_slave.s`** | Kickstart-Free Loader | Custom WHDLoad Slave v17 (`ws_KickSize=0`) allocating Chip/Fast RAM and booting without external Kickstart ROMs |

---

## Developer Toolchain (`tools/`)

- **`tools/build_median.py`** — dedicated pipeline converting *Median* (`624x496` -> `640x256` Hi-Res @ `50 FPS`, dual black/red layer extraction, polygon simplification, and packaging into `.lha` + `*_FSUAE.zip`).
- **`tools/build_demo.py`** — universal video-to-vector `640x256` Hi-Res AGA converter (`--video`, `--fps`, `--threshold`, `--crop-43`, `--thin-lines`) compiling the M68020 executable (`vasmm68k_mot`), WHDLoad Slave, `.lha`, and `*_FSUAE.zip` archives.

---

## Package Variants & Verified Compatibility (v1.1.0)
- **`.lha` (`*_AGA_THEA1200.lha` — RetroArch PUAE / THEA1200 / Real A1200):** packed with Amiga LHA Level 1 headers and 78-byte `WBPROJECT` WHDLoad icons. Tested and verified out-of-the-box via **Load Content** in **RetroArch (`PUAE` core)** and **THEA1200 (`Amiberry`)**.
- **`.zip` (`*_AGA_THEA1200_FSUAE.zip` — FS-UAE Launcher / WinUAE):** standard WHDLoad ZIP archive supported natively without external `python-lhafile` plugins. 1-click auto-boot via `S/startup-sequence` — simply mount the `.zip` as Hard Drive (`DH0`) on an A1200 (8 MB Fast RAM) profile and click **Start**.

---

## Making Of & AI Prompts (Vibe Coding Edition)
This bare-metal vector engine and both full-length demos (*Median A1200* and *Bad Apple!! A1200*) were built through iterative **Vibe Coding** (`malek69` & **Gemini AI**, 2026) — see full details in [docs/MAKING_OF.md](docs/MAKING_OF.md) and [docs/ENGINE_v1.1.md](docs/ENGINE_v1.1.md).

### Engineering Prompts Used to Build & Extend the Engine
- *"Write a bare-metal M68020 subroutine for Amiga AGA that precomputes a 512 KB XOR scanline fill LUT in Fast RAM (`section vec_fast,bss_p`) with 16-bit carry propagation across word boundaries."*
- *"Optimize an Amiga 1200 50 Hz PAL frame loop in native AGA Hi-Res `640x256` (`BPLCON0=$A200`, `FMODE=$0003`): clear Fast-RAM backbuffers with unrolled `movem.l`, rasterize N-gons with hole cutouts, and burst-copy 48 bytes per instruction into Chip RAM."*
- *"Create a minimal Kickstart-free WHDLoad v17 slave (`ws_KickSize=0`) in M68020 assembly that loads a multi-hunk executable into Chip/Fast RAM, enables the 68020 cache (`CACR`), and exits cleanly via LMB, Joystick Port 2 Fire (THEA1200), or ESC."*
