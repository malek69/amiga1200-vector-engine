[Wersja Polska](README.pl.md)

# Amiga 1200 / THEA1200 Vector Stream Demo Engine v1.0

Bare-metal demoscene vector streaming engine written in Motorola 68020 assembly for **Commodore Amiga 1200 (AGA)** and **THEA1200** (Kickstart-free WHDLoad boot).

| Median A1200 v1.0 | Bad Apple!! A1200 v1.0 |
| :---: | :---: |
| ![Median A1200](docs/preview_median.png) | ![Bad Apple A1200](docs/preview.png) |

## Releases (v1.0)

### 1. Median A1200 [Retail v1.0]
- **Overview:** Locked **50.00 FPS PAL** port of *Median* (Umlaut Design, 2016) featuring geometric morphing, the red sun sequence, and 3D architecture in authentic 3-color AGA styling (`#EEE`, `#111`, `#E11`) with hardware edge smoothing.
- **Engine Procedures Used:** `sys_takeover`, `setup_copper`, `init_fill_lut`, `play_vector_frame`, `draw_polygon_mode` (modes `0` black fill, `1` hole cutting, `2` red `BPL2`), `apply_blitter_aa`, `setup_paula`, and `aud0_irq_handler`.
- **Requirements:** Amiga 1200 (68EC020+, AGA), **2 MB Chip RAM + 8 MB Fast RAM** (`NoMMU` ToolType enabled), or **THEA1200**.

### 2. Bad Apple!! A1200 [50FPS + Blitter AA v1.0]
- **Overview:** Full 3:39 *Bad Apple!!* animation (ZUN / Anira) running at locked **50.00 FPS PAL** (1 frame per VBL tick) with crisp silhouettes, interior cutouts, and Blitter anti-aliasing.
- **Engine Procedures Used:** `init_fill_lut`, `play_vector_frame`, `draw_polygon_mode` (`inv_tab` edge stepping into `fast_bpl1` Fast-RAM backbuffer), 32-bit `Fast RAM -> Chip RAM` copy, `apply_blitter_aa`, and 4-channel `setup_paula` DMA audio.
- **Requirements:** Amiga 1200 (68EC020+, AGA), **2 MB Chip RAM + 8 MB Fast RAM**, or **THEA1200**.

## Engine Architecture & Procedures (`src/`)
- `src/main.s` — Entry point (`start`), `50 Hz VBL` main loop (`wait_vbl`, `vbl_tick`), 32-bit `fast_bpl1` to Chip RAM transfer, and LMB / `ESC` exit handling.
- `src/gfx_engine.i` — AGA chipset takeover (`sys_takeover`), Copperlist setup (`setup_copper`), `320x256 PAL` double-buffering, Blitter screen clear (`blit_clear_full`), and hardware Blitter anti-aliasing (`apply_blitter_aa`).
- `src/vec3d_engine.i` — N-gon polygon rasterizer (`draw_polygon_mode`) using a 512 KB Fast-RAM XOR prefix table (`init_fill_lut`), `inv_tab` edge interpolation, and interior hole cutting.
- `src/scene_player.i` — Vector frame stream decoder (`play_vector_frame`) and dynamic Copper palette updater.
- `src/audio_player.i` — 4-channel Paula DMA audio driver (`setup_paula`, `aud0_irq_handler`, Level 4 IRQ) with hardware audio LED filter disabled (`bset #1,$bfe001`).
- `src/whdload_slave.s` — Custom Kickstart-free WHDLoad Slave v17 (`ws_KickSize=0`) relocating Hunk segments into Fast/Chip RAM.

## Build Tools (`tools/`)
- `tools/build_demo.py` — General-purpose video/audio (`ffmpeg` + `OpenCV`) to M68020 assembly converter, `vasmm68k_mot` builder, and `.lha` packager.
- `tools/build_median.py` — Dedicated *Median A1200 v1.0* builder with `BPL2` red channel separation and right-angle vertex snapping.

## System Requirements & Running
- **Hardware / Emulator:** Commodore Amiga 1200 (AGA, 68020+), **2 MB Chip RAM + 8 MB Fast RAM**, **THEA1200**, FS-UAE, or WinUAE.
- **Running:** Mount or launch the `.lha` packages from `releases/` directly in WHDLoad, THEA1200, FS-UAE, or WinUAE.
