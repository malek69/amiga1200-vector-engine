<p align="right"><strong>README (EN / PL)</strong> | <a href="CHANGELOG.md">Historia Zmian (PL)</a> | <a href="CHANGELOG_EN.md">Changelog (EN)</a></p>

<p align="center"><img src="docs/engine_logo.png" alt="A1200 Vector Engine v1.1.0" width="760"></p>

# Amiga 1200 / THEA1200 Vector Stream Demo Engine v1.1.0 [EN / PL]

> **Credits / Autorzy:** `malek69` & **Gemini AI** *(Vibe Coding Edition, 2026 — AI-assisted M68020 bare-metal code & Python toolchain)*

| Median A1200 v1.1.0 (Hi-Res 640x256) | Bad Apple!! A1200 v1.1.0 (Hi-Res 640x256) |
| :---: | :---: |
| ![Median](docs/preview_median.png) | ![Bad Apple](docs/preview.png) |
| **[Download .LHA — RetroArch / THEA1200](https://github.com)**<br>**[Download .ZIP — FS-UAE / WinUAE](https://github.com)** | **[Download .LHA — RetroArch / THEA1200](https://github.com)**<br>**[Download .ZIP — FS-UAE / WinUAE](https://github.com)** |

## What is New in v1.1.0
- **Native AGA Hi-Res `640x256` (`BPLCON0 = $A200`):** 2x horizontal sharpness for crisp vector edges at a locked **50.00 FPS PAL**.
- **64-bit AGA Bitplane Fetch (`FMODE = $0003`):** Zero DMA contention on 68EC020 14 MHz in `640x256` Hi-Res mode.
- **Fast-RAM Rasterization + Unrolled `movem.l` Burst Copy:** Polygons rasterize into 32-bit Fast RAM (`fast_bpl1`/`fast_bpl2`) and burst-copy 48 bytes per instruction into Chip RAM.
- **THEA1200 Gamepad Support:** Exit cleanly via **Joystick Port 2 Fire (`$BFE001` bit 7)** in addition to **LMB** and **`ESC`**.

## Hardware Requirements
- **System:** Commodore Amiga 1200 (68EC020+ 14 MHz, AGA), **THEA1200**, FS-UAE, or WinUAE.
- **Memory:** **2 MB Chip RAM + 8 MB Fast RAM** (512 KB XOR LUT + 640x256 Fast-RAM backbuffers + audio/vector stream).
- **Boot:** Custom Kickstart-Free WHDLoad Slave v17 (`ws_KickSize=0`) — no Kickstart ROM images required.
- **Controls:** Left Mouse Button (LMB), **THEA1200 / Joystick Port 2 Fire**, or `ESC` to exit cleanly back to AmigaOS/WHDLoad.

## Releases (v1.1.0)
### 1. Median A1200 [Retail v1.1.0 — Hi-Res 640x256]
- **Source & Style:** Locked **50.00 FPS PAL** port of *Median* (Umlaut Design, PC 2016) in native **AGA Hi-Res `640x256`**, 3 colors (`#EEE`, `#111`, `#E11`), `ExpMem = 5.62 MB`.
- **Frame Pipeline:** `clear_fast_buffers` -> `play_vector_frame` -> `draw_polygon_mode` (640-wide XOR LUT) -> `copy_fast_to_chip` (`movem.l` burst) -> `wait_vbl` + `aud0_irq_handler`.

### 2. Bad Apple!! A1200 [50FPS Hi-Res 640x256 v1.1.0]
- **Source & Style:** Full 3:39 *Bad Apple!!* (ZUN / Anira) in native **AGA Hi-Res `640x256`** at locked **50.00 FPS PAL** (1 frame per VBL tick) with crisp cutouts, `ExpMem = 5.06 MB`.
- **Frame Pipeline:** `init_fill_lut` (512 KB XOR LUT) -> `draw_polygon_mode` (640-wide Fast-RAM rasterizer) -> unrolled `movem.l` `Fast->Chip` transfer -> 4CH Paula DMA.

## Package Variants & Verified Compatibility (v1.1.0)
- **`.lha` (`*_AGA_THEA1200.lha` — RetroArch PUAE / THEA1200 / Real A1200):** Packed with Amiga LHA Level 1 headers and 78-byte `WBPROJECT` WHDLoad icons. Tested and verified working out-of-the-box via **Load Content** in **RetroArch (`PUAE` core)** and **THEA1200 (`Amiberry`)**.
- **`.zip` (`*_AGA_THEA1200_FSUAE.zip` — FS-UAE Launcher / WinUAE):** Standard WHDLoad ZIP archive supported natively without external `python-lhafile` plugins. 1-click auto-boot via `S/startup-sequence` — simply mount the `.zip` as Hard Drive (`DH0`) on an A1200 (8 MB Fast RAM) profile and click **Start**.

## Engine Modules (`src/`)
- `main.s` (50Hz VBL loop, Fast-RAM clear & unrolled `movem.l` Fast->Chip copy) | `gfx_engine.i` (AGA Hi-Res `640x256`, `FMODE=$0003`, Copper)
- `vec3d_engine.i` (640-wide N-gon XOR LUT rasterizer) | `scene_player.i` (frame stream decoder) | `audio_player.i` (4CH Paula DMA, LED filter off) | `whdload_slave.s` (Kickstart-free loader)

## Engine v1.1.0 Technical Overview
- **Full Specification:** See [docs/ENGINE_v1.1.md](docs/ENGINE_v1.1.md) for memory map, custom chip registers (`BPLCON0=$A200`, `FMODE=$0003`), and LUT math.
- **50.00 Hz PAL Loop:** `clear_fast_buffers` -> `play_vector_frame` -> `draw_polygon_mode` (Fast-RAM LUT) -> `copy_fast_to_chip` (`movem.l`) -> `wait_vbl`.
- **Memory Footprint:** ~86 KB Chip RAM (`2 x 40960 B` Hi-Res bitplanes + Copper + Paula buffers) + ~586 KB Fast RAM workspace + vector/audio stream (fits in stock A1200 + 8 MB Fast RAM).

---

[English Version](README.md)

# Amiga 1200 / THEA1200 Vector Stream Demo Engine v1.1.0

| Median A1200 v1.1.0 (Hi-Res 640x256) | Bad Apple!! A1200 v1.1.0 (Hi-Res 640x256) |
| :---: | :---: |
| ![Median](docs/preview_median.png) | ![Bad Apple](docs/preview.png) |
| **[Pobierz .LHA — RetroArch / THEA1200](https://github.com)**<br>**[Pobierz .ZIP — FS-UAE / WinUAE](https://github.com)** | **[Pobierz .LHA — RetroArch / THEA1200](https://github.com)**<br>**[Pobierz .ZIP — FS-UAE / WinUAE](https://github.com)** |

## Co nowego w v1.1.0
- **Natywny tryb AGA Hi-Res `640x256` (`BPLCON0 = $A200`):** 2x wyższa ostrość w poziomie i idealnie gładkie krawędzie wektorów przy sztywnych **50.00 FPS PAL**.
- **64-bitowe pobieranie bitplanów AGA (`FMODE = $0003`):** Brak dławienia szyny CPU/Blitter w trybie `640x256` na bazowej Amidze 1200 (68EC020 14 MHz).
- **Rasteryzacja w Fast RAM + szybki transfer `movem.l`:** Wielokąty rysowane są w 32-bitowym Fast RAM (`fast_bpl1`/`fast_bpl2`), a gotowa klatka kopiowana jest blokami po 48 bajtów na instrukcję do Chip RAM.
- **Obsługa pada THEA1200:** Czyste wyjście przyciskiem **Fire na Joystick Port 2 (`$BFE001` bit 7)** obok **LPM** i klawisza **`ESC`**.

## Wymagania sprzętowe
- **Komputer / Emulator:** Commodore Amiga 1200 (68EC020+ 14 MHz, AGA), **THEA1200**, FS-UAE lub WinUAE.
- **Pamięć:** **2 MB Chip RAM + 8 MB Fast RAM** (tablica LUT 512 KB + bufory Fast-RAM 640x256 + strumień A/V).
- **Uruchamianie:** Autorski WHDLoad Slave v17 (`ws_KickSize=0`) — działa bez plików Kickstart ROM. Wyjście: LPM, **Fire (Joystick Port 2 / THEA1200)** lub `ESC`.

## Wydania (v1.1.0)
### 1. Median A1200 [Retail v1.1.0 — Hi-Res 640x256]
- **Opis:** Port dema *Median* (Umlaut Design, 2016) w **AGA Hi-Res `640x256` @ 50.00 FPS PAL**, 3 kolorach AGA (`#EEE`, `#111`, `#E11`), `ExpMem = 5.62 MB`.
- **Wywołania w ramce:** `clear_fast_buffers` -> `play_vector_frame` -> `draw_polygon_mode` (LUT 640 px) -> `copy_fast_to_chip` (`movem.l`) -> `wait_vbl` + `aud0_irq_handler`.

### 2. Bad Apple!! A1200 [50FPS Hi-Res 640x256 v1.1.0]
- **Opis:** Pełne 3:39 *Bad Apple!!* (ZUN / Anira) w **AGA Hi-Res `640x256` @ 50.00 FPS PAL** (1 klatka na VBL) z wycinaniem otworów, `ExpMem = 5.06 MB`.
- **Wywołania w ramce:** `init_fill_lut` (512 KB LUT) -> `draw_polygon_mode` (rasteryzator 640 px w Fast RAM) -> transfer `movem.l` `Fast->Chip` -> 4CH DMA Paula.

## Moduły silnika (`src/`)
- `main.s` (pętla 50Hz VBL, czyszczenie Fast RAM i transfer `movem.l` Fast->Chip) | `gfx_engine.i` (AGA Hi-Res `640x256`, `FMODE=$0003`, Copper)
- `vec3d_engine.i` (rasteryzator wielokątów LUT 640 px) | `scene_player.i` (dekoder klatek) | `audio_player.i` (4CH Paula DMA, filtr LED wył.) | `whdload_slave.s` (loader bez Kickstart ROM)

## Specyfikacja Silnika v1.1.0
- **Pełna dokumentacja techniczna:** Zobacz [docs/ENGINE_v1.1.md](docs/ENGINE_v1.1.md) (mapa pamięci, rejestry AGA `BPLCON0=$A200` / `FMODE=$0003`, matematyka LUT).
- **Pętla 50.00 Hz PAL:** `clear_fast_buffers` -> `play_vector_frame` -> `draw_polygon_mode` (LUT w Fast-RAM) -> `copy_fast_to_chip` (`movem.l`) -> `wait_vbl`.
- **Zapotrzebowanie pamięci:** ~86 KB Chip RAM (`2 x 40960 B` bitplany Hi-Res + Copper + bufory Paula) + ~586 KB obszaru roboczego Fast RAM + strumień A/V (mieści się w A1200 + 8 MB Fast RAM).
