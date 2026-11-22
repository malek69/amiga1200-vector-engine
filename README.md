# Amiga 1200 / THEA1200 Vector Stream Demo Engine

Niskopoziomowy silnik demoscenowy dla **Commodore Amiga 1200 (AGA, Motorola 68020+, 2 MB Chip RAM + 8 MB Fast RAM)** oraz konsoli **THEA1200** (uruchamiany bez Kickstartu przez WHDLoad / USB Media Access).

## Architektura silnika (`src/`)
- `src/main.s` — pętla główna oraz blokada synchronizacji A/V (`pcm_played`).
- `src/gfx_engine.i` — obsługa chipsetu AGA (`320x256` PAL), Copperlista, podwójne buforowanie VBL Level 3.
- `src/vec3d_engine.i` — rasteryzator wielokątów N-katnych oparty na tablicy prefiksowej `fill_lut` w Fast RAM.
- `src/audio_player.i` — sterownik 4 kanałów DMA Paula (`16497 Hz`, IRQ Level 4) z wyłączeniem filtra LED (`bset #1,$bfe001`).
- `src/whdload_slave.s` — autorski WHDLoad Slave v17 (`ws_KickSize=0`) dla THEA1200 i FS-UAE.

## Jak zbudować własne demo (np. *Bad Apple!!*)
```bash
python3 tools/build_demo.py --video bad_apple.mp4 --name BADAPPLE_A1200 --title "Bad Apple!! A1200" --fps 30 --threshold 128
```

## Jak zbudować demo z cienkimi liniami (styl *Median*)
```bash
python3 tools/build_demo.py --video orginal.mp4 --audio ~/music.mp3 --name MEDIAN_A1200 --title "Median A1200" --thin-lines
```
