[English Version](README.en.md)

# Amiga 1200 / THEA1200 Vector Stream Demo Engine
n![Amiga 1200 AGA Vector Engine Preview](docs/preview.png)

Niskopoziomowy, bare-metalowy silnik demoscenowy dla **Commodore Amiga 1200 (AGA, Motorola 68020+, 2 MB Chip RAM + 8 MB Fast RAM)** oraz konsoli **THEA1200** (uruchamiany bez Kickstart ROM przez WHDLoad).

## Opublikowane dema (Releases)
- **Median A1200 [Retail] (v1.0.0):** Port dema *Median* (Umlaut Design, 2016) — 30 FPS, 3 kolory AGA, wygładzanie Blitter AA oraz 4-kanałowe audio Pauli 16.5 kHz.
- **Bad Apple!! A1200 [50FPS + Blitter AA] (v1.1.0):** Pełne 3:39 w zablokowanych 50.00 FPS PAL, renderowanie w buforze Fast RAM, rasteryzator LUT z wycinaniem otworów i antyaliasing Blittera.

## Architektura silnika i opis plików
- \`src/main.s\` — Punkt wejścia, pętla główna, kopiowanie bufora Fast RAM -> Chip RAM oraz synchronizacja A/V (\`vbl_tick\` / \`pcm_played\`).
- \`src/gfx_engine.i\` — Przejęcie chipsetu AGA (320x256 PAL), dynamiczna Copperlista, double-buffering oraz sprzętowy antyaliasing na Blitterze (\`apply_blitter_aa\`).
- \`src/vec3d_engine.i\` — Rasteryzator wielokątów N-kątnych z tablicą prefiksową \`fill_lut\` (512 KB Fast RAM), tablicą odwrotności \`inv_tab\` oraz wycinaniem otworów.
- \`src/scene_player.i\` — Dekoder strumienia klatek wektorowych i aktualizacja palety w Copperze.
- \`src/audio_player.i\` — Sterownik 4 kanałów DMA układu Paula (IRQ Level 4) ze sprzętowym wyłączeniem filtra dolnoprzepustowego LED (\`bset #1,\`).
- \`src/whdload_slave.s\` — Autorski WHDLoad Slave v17 (\`ws_KickSize=0\`) relokujący sekcje Hunk bez obrazów Kickstart ROM.
- \`tools/build_demo.py\` — Konwerter wideo/audio -> kod asemblera M68020, kompilator \`vasmm68k_mot\` oraz generator paczek \`.lha\`.

## Wymagania i użycie
- Narzędzia: \`vasmm68k_mot\`, \`ffmpeg\`, \`ffprobe\`, Python 3 (\`numpy\`, \`opencv-python\`).
- Budowanie: \`python3 tools/build_demo.py --video input.mp4 --name DEMO_A1200 --title "My Demo A1200" --fps 50 --threshold 128\`
