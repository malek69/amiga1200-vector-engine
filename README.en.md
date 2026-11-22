[Wersja Polska](README.md)

# Amiga 1200 / THEA1200 Vector Stream Demo Engine

Bare-metal demoscene vector & silhouette streaming engine for **Commodore Amiga 1200 (AGA, Motorola 68020+, 2 MB Chip RAM + 8 MB Fast RAM)** and **THEA1200** console (Kickstart-free WHDLoad).

## Releases
- **Median A1200 [Retail] (v1.0.0):** Port of *Median* (Umlaut Design, 2016) — 30 FPS, 3 AGA colors, Blitter AA, and 16.5 kHz 4-channel Paula audio.
- **Bad Apple!! A1200 [50FPS + Blitter AA] (v1.1.0):** Full 3:39 at locked 50.00 FPS PAL using Fast-RAM backbuffer rendering, LUT polygon rasterization with hole cutting, and hardware Blitter AA.

## Engine Modules
- \`src/main.s\` — Entry point, Fast-to-Chip backbuffer copy, and A/V sync lock.
- \`src/gfx_engine.i\` — AGA chipset takeover (320x256 PAL), Copperlist, double-buffering, and Blitter AA.
- \`src/vec3d_engine.i\` — N-gon rasterizer with 512 KB Fast-RAM \`fill_lut\`, \`inv_tab\` edge stepping, and hole cutting.
- \`src/scene_player.i\` & \`src/audio_player.i\` — Vector frame stream decoder and 4-channel Paula DMA audio driver (LED filter disabled).
- \`src/whdload_slave.s\` & \`tools/build_demo.py\` — Kickstart-free WHDLoad Slave v17 and CLI video-to-Amiga \`.lha\` builder.
