<p align="right"><a href="README.md">Polski</a> | <a href="README_EN.md">English</a> | <a href="CHANGELOG.md">Historia Zmian (PL)</a> | <strong>Changelog (EN)</strong></p>

# Changelog — A1200 Vector Engine

## v1.1.2 — Eon (TBL) Cutscenes & Native MC68060 (2026-11-25)

- **Rotoscoped *Eon* (TBL) Cutscene Module (`src/eon_poly_player.i`):** borderless 256-color AGA multi-tone N-gon polygon player (`af_play_eon_scene`) ported from *Aether Falcon: Vanguard*.
- **Native MC68060 Support (`src/whdload_slave.s`, `tools/build_demo.py`, `tools/build_median.py`):** WHDLoad `$0026` flags, **7.5 MB Fast RAM** (`$00780000`), 32-bit **`CACR = $A0808000`**, and `-DM68060` compiler flags across `060` builds.

---

## v1.1.0 — AGA + Blitter AA 320x256 (2026-11-24)
- **Native AGA + Blitter AA `320x256` (`BPLCON0 = $A200`, `DDFSTRT = $0028, DDFSTOP = $00B8`):** 2x horizontal vector sharpness at locked 50.00 FPS PAL.
- **64-bit Bitplanes (`FMODE = $0003`) & Fast-RAM Pipeline:** Fast-RAM rasterization with unrolled `movem.l` (48 B/iter) burst copy to Chip RAM.
- **THEA1200 Gamepad Support:** exit via Joystick Port 2 Fire (`$BFE001` bit 7) alongside LMB and `ESC`.
- **v1.1.0 Vector Streams:** re-encoded `320x256` streams for *Median A1200* (`5.62 MB`) and *Bad Apple!! A1200* (`5.06 MB`).

## v1.0.1 (2026-11-23)
- Added 1-click auto-boot `*_FSUAE.zip` archives and platform compatibility matrix.

## v1.0.0 (2026-11-22)
- Initial M68020+ / AGA (`320x256 @ 50 FPS`) vector engine release with Kickstart-free WHDLoad Slave v17.
