<p align="right"><a href="README.md">README (EN / PL)</a> | <a href="CHANGELOG.md">Historia Zmian (PL)</a> | <strong>Changelog (EN)</strong></p>

# Changelog — A1200 / THEA1200 Vector Stream Demo Engine

Chronological development log of the **A1200 Vector Engine** for Commodore Amiga 1200 (M68020+ / AGA) and THEA1200.

---

## v1.1.0 — AGA Hi-Res 640x256 & Fast-RAM Pipeline (2026-11-24)

- **Native AGA Hi-Res `640x256`:** 2x horizontal vector sharpness at locked 50.00 FPS PAL.
- **64-bit AGA Bitplane Fetch & Fast-RAM Rasterization:** eliminates Chip-RAM DMA contention and utilizes unrolled `movem.l` bursts.
- **THEA1200 Gamepad Support:** clean exit via Joystick Port 2 Fire button.

---

## v1.0.1 & v1.0.0 — Initial Releases & WHDLoad Compatibility (2026-11-22 – 2026-11-23)

- Introduction of `.lha` (WHDLoad) and `*_FSUAE.zip` packages without external Kickstart ROMs, alongside the core M68020+ / AGA vector engine supporting *Median A1200* and *Bad Apple!! A1200*.
