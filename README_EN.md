<p align="right"><a href="README.md">Polski</a> | <strong>English</strong> | <a href="CHANGELOG.md">Historia Zmian (PL)</a> | <a href="CHANGELOG_EN.md">Changelog (EN)</a></p>

<div align="center">
  <img src="docs/engine_logo.png" alt="A1200 Vector Engine v1.1.0" width="680" />
  <h1>Amiga 1200 / THEA1200 Vector Stream Demo Engine v1.1.0</h1>
  <p><strong>Bare-metal M68020+ / AGA Hi-Res 640x256 @ 50.00 FPS PAL Vector Demo Engine</strong></p>
  <p><em>Credits: malek69 &amp; Gemini AI (Vibe Coding Edition, 2026)</em></p>
</div>

---

## Downloads &amp; Preview (v1.1.0 Latest)

| Median A1200 v1.1.0 (Hi-Res 640x256) | Bad Apple!! A1200 v1.1.0 (Hi-Res 640x256) |
| :---: | :---: |
| ![Median](docs/preview_median.png) | ![Bad Apple](docs/preview.png) |
| **[Download .LHA — THEA1200 / RetroArch](https://github.com/malek69/amiga1200-vector-engine/releases/download/v1.1.0/MedianA1200_AGA_THEA1200.lha)**<br>**[Download .ZIP — FS-UAE / WinUAE](https://github.com/malek69/amiga1200-vector-engine/releases/download/v1.1.0/MedianA1200_AGA_THEA1200_FSUAE.zip)** | **[Download .LHA — THEA1200 / RetroArch](https://github.com/malek69/amiga1200-vector-engine/releases/download/v1.1.0/BadappleA1200_AGA_THEA1200.lha)**<br>**[Download .ZIP — FS-UAE / WinUAE](https://github.com/malek69/amiga1200-vector-engine/releases/download/v1.1.0/BadappleA1200_AGA_THEA1200_FSUAE.zip)** |

## What is New in v1.1.0
- **Native AGA Hi-Res `640x256` (`BPLCON0 = $A200`, `DDFSTOP = $00CC`):** 2x horizontal sharpness for crisp vector edges at a locked **50.00 FPS PAL**.
- **64-bit AGA Bitplane Fetch (`FMODE = $0003`):** zero DMA bus contention on stock Amiga 1200 (68EC020 14 MHz).
- **Fast-RAM Rasterization + `movem.l` Burst Copy:** polygons rasterize into 32-bit Fast RAM and burst-copy `48 B` per instruction into Chip RAM.
- **THEA1200 Gamepad Support:** clean exit via **Joystick Port 2 Fire (`$BFE001` bit 7)** alongside LMB and `ESC`.

## Hardware Requirements &amp; Engine Modules (`src/`)
- **Platform:** Commodore Amiga 1200 (68EC020+ 14 MHz, AGA, **2 MB Chip RAM + 8 MB Fast RAM**), **THEA1200**, FS-UAE, or WinUAE (no Kickstart ROM required — WHDLoad Slave v17).
- **Modules:** `main.s` (50Hz VBL loop + `movem.l`) | `gfx_engine.i` (AGA `640x256`, `FMODE=$0003`, Copper) | `vec3d_engine.i` (640-wide XOR LUT rasterizer) | `scene_player.i` | `audio_player.i` (4CH Paula DMA) | `whdload_slave.s`.
- **Documentation:** [docs/ENGINE_v1.1.md](docs/ENGINE_v1.1.md) | [Historia Zmian (PL)](CHANGELOG.md) | [Changelog (EN)](CHANGELOG_EN.md)
