<p align="center"><img src="docs/engine_logo.png" alt="A1200 Vector Engine v1.0.1" width="760"></p>

# Amiga 1200 / THEA1200 Vector Stream Demo Engine v1.0.1 [EN / PL]

> **Credits / Autorzy:** `malek69` & **Gemini AI** *(Vibe Coding Edition, 2026 — AI-assisted M68020 bare-metal code & Python toolchain)*

| Median A1200 v1.0.1 | Bad Apple!! A1200 v1.0.1 |
| :---: | :---: |
| ![Median](docs/preview_median.png) | ![Bad Apple](docs/preview.png) |
| **[Download .LHA — RetroArch / THEA1200](https://github.com/malek69/amiga1200-vector-engine/releases/download/median-v1.0.1/MedianA1200_AGA_THEA1200.lha)**<br>**[Download .ZIP — FS-UAE / WinUAE](https://github.com/malek69/amiga1200-vector-engine/releases/download/median-v1.0.1/MedianA1200_AGA_THEA1200_FSUAE.zip)** | **[Download .LHA — RetroArch / THEA1200](https://github.com/malek69/amiga1200-vector-engine/releases/download/badapple-v1.0.1/BadappleA1200_AGA_THEA1200.lha)**<br>**[Download .ZIP — FS-UAE / WinUAE](https://github.com/malek69/amiga1200-vector-engine/releases/download/badapple-v1.0.1/BadappleA1200_AGA_THEA1200_FSUAE.zip)** |
## Hardware Requirements
- **System:** Commodore Amiga 1200 (68EC020+ 14 MHz, AGA), **THEA1200**, FS-UAE, or WinUAE.
- **Memory:** **2 MB Chip RAM + 8 MB Fast RAM** (512 KB XOR LUT + Fast-RAM backbuffer + audio/vector stream).
- **Boot:** Custom Kickstart-Free WHDLoad Slave v17 (`ws_KickSize=0`) — no Kickstart ROM images required.
- **Controls:** Left Mouse Button (LMB) or `ESC` to exit cleanly back to AmigaOS/WHDLoad.
## Releases (v1.0.1)
### 1. Median A1200 [Retail v1.0.1]
- **Source & Style:** Locked **50.00 FPS PAL** port of *Median* (Umlaut Design, PC 2016) in 3 AGA colors (`#EEE`, `#111`, `#E11`) with Blitter edge smoothing (`NoMMU`).
- **Frame Pipeline:** `wait_vbl` -> `blit_clear_full` (`BPL2`) -> `play_vector_frame` -> `draw_polygon_mode` -> `fast_bpl1` copy -> `apply_blitter_aa` + `aud0_irq_handler`.
### 2. Bad Apple!! A1200 [50FPS + Blitter AA v1.0.1]
- **Source & Style:** Full 3:39 *Bad Apple!!* (ZUN / Anira) at locked **50.00 FPS PAL** (1 frame per VBL tick) with crisp cutouts and Blitter AA.
- **Frame Pipeline:** `init_fill_lut` (512 KB XOR LUT) -> `draw_polygon_mode` (`inv_tab` stepping) -> 32-bit `Fast->Chip` transfer -> `apply_blitter_aa` + 4CH Paula DMA.

## Package Variants & Verified Compatibility (v1.0.1)
- **`.lha` (`*_AGA_THEA1200.lha` — RetroArch PUAE / THEA1200 / Real A1200):** Packed with Amiga LHA Level 1 headers and 78-byte `WBPROJECT` WHDLoad icons. Tested and verified working out-of-the-box via **Load Content** in **RetroArch (`PUAE` core)** and **THEA1200 (`Amiberry`)**.
- **`.zip` (`*_AGA_THEA1200_FSUAE.zip` — FS-UAE Launcher / WinUAE):** Standard WHDLoad ZIP archive supported natively without external `python-lhafile` plugins. 1-click auto-boot via `S/startup-sequence` — simply mount the `.zip` as Hard Drive (`DH0`) on an A1200 (8 MB Fast RAM) profile and click **Start**.

## Engine Modules (`src/`)
- `main.s` (50Hz VBL loop & Fast->Chip copy) | `gfx_engine.i` (AGA takeover, Copper, Blitter AA) | `vec3d_engine.i` (N-gon LUT rasterizer)
- `scene_player.i` (frame stream decoder) | `audio_player.i` (4CH Paula DMA, LED filter off) | `whdload_slave.s` (Kickstart-free loader)

## Engine v1.0.1 Technical Overview
- **Full Specification:** See [docs/ENGINE_v1.0.md](docs/ENGINE_v1.0.md) for memory map, custom chip registers, and LUT math.
- **50.00 Hz PAL Loop:** `wait_vbl` -> `blit_clear_full (BPL2)` -> `play_vector_frame` -> `draw_polygon_mode (Fast-RAM LUT)` -> `32-bit Fast->Chip Copy` -> `apply_blitter_aa (BPL3)`.
- **Memory Footprint:** ~66 KB Chip RAM + ~545 KB Fast RAM workspace + vector/audio stream (fits in stock A1200 + 8 MB Fast RAM).

---

[English Version](README.md)
# Amiga 1200 / THEA1200 Vector Stream Demo Engine v1.0.1
| Median A1200 v1.0.1 | Bad Apple!! A1200 v1.0.1 |
| :---: | :---: |
| ![Median](docs/preview_median.png) | ![Bad Apple](docs/preview.png) |
| **[Pobierz .LHA — RetroArch / THEA1200](https://github.com/malek69/amiga1200-vector-engine/releases/download/v1.0.1/MedianA1200_AGA_THEA1200.lha)**<br>**[Pobierz .ZIP — FS-UAE / WinUAE](https://github.com/malek69/amiga1200-vector-engine/releases/download/v1.0.1/MedianA1200_AGA_THEA1200_FSUAE.zip)** | **[Pobierz .LHA — RetroArch / THEA1200](https://github.com/malek69/amiga1200-vector-engine/releases/download/v1.0.1/BadappleA1200_AGA_THEA1200.lha)**<br>**[Pobierz .ZIP — FS-UAE / WinUAE](https://github.com/malek69/amiga1200-vector-engine/releases/download/v1.0.1/BadappleA1200_AGA_THEA1200_FSUAE.zip)** |
## Wymagania sprzętowe
- **Komputer / Emulator:** Commodore Amiga 1200 (68EC020+ 14 MHz, AGA), **THEA1200**, FS-UAE lub WinUAE.
- **Pamięć:** **2 MB Chip RAM + 8 MB Fast RAM** (tablica LUT 512 KB + bufor Fast-RAM + strumień A/V).
- **Uruchamianie:** Autorski WHDLoad Slave v17 (`ws_KickSize=0`) — działa bez plików Kickstart ROM. Wyjście: LPM lub `ESC`.
## Wydania (v1.0.1)
### 1. Median A1200 [Retail v1.0.1]
- **Opis:** Port dema *Median* (Umlaut Design, 2016) w **50.00 FPS PAL**, 3 kolorach AGA (`#EEE`, `#111`, `#E11`) z wygładzaniem Blittera (`NoMMU`).
- **Wywołania w ramce:** `wait_vbl` -> `blit_clear_full` (`BPL2`) -> `play_vector_frame` -> `draw_polygon_mode` -> `fast_bpl1` -> `apply_blitter_aa` + `aud0_irq_handler`.
### 2. Bad Apple!! A1200 [50FPS + Blitter AA v1.0.1]
- **Opis:** Pełne 3:39 *Bad Apple!!* (ZUN / Anira) w **50.00 FPS PAL** (1 klatka na VBL) z wycinaniem otworów i antyaliasingiem Blittera.
- **Wywołania w ramce:** `init_fill_lut` (512 KB LUT) -> `draw_polygon_mode` (`inv_tab`) -> transfer `Fast->Chip` -> `apply_blitter_aa` + 4CH DMA Paula.
## Moduły silnika (`src/`)
- `main.s` (pętla 50Hz VBL i transfer Fast->Chip) | `gfx_engine.i` (AGA, Copper, Blitter AA) | `vec3d_engine.i` (rasteryzator wielokątów LUT)
- `scene_player.i` (dekoder klatek) | `audio_player.i` (4CH Paula DMA, filtr LED wył.) | `whdload_slave.s` (loader bez Kickstart ROM)

## Specyfikacja Silnika v1.0.1
- **Pełna dokumentacja techniczna:** Zobacz [docs/ENGINE_v1.0.md](docs/ENGINE_v1.0.md) (mapa pamięci, rejestry AGA/Blitter/Paula, matematyka LUT).
- **Pętla 50.00 Hz PAL:** `wait_vbl` -> `blit_clear_full (BPL2)` -> `play_vector_frame` -> `draw_polygon_mode (LUT w Fast-RAM)` -> `kopia 32-bit Fast->Chip` -> `apply_blitter_aa (BPL3)`.
- **Zapotrzebowanie pamięci:** ~66 KB Chip RAM + ~545 KB obszaru roboczego Fast RAM + strumień A/V (mieści się w A1200 + 8 MB Fast RAM).
