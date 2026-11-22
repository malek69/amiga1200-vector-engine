[English Version](README.md)

# Amiga 1200 / THEA1200 Vector Stream Demo Engine v1.0

Niskopoziomowy, bare-metalowy silnik wektorowy napisany w asemblerze Motorola 68020 dla **Commodore Amiga 1200 (AGA)** oraz konsoli **THEA1200** (uruchamiany bez Kickstart ROM przez własny WHDLoad Slave).

| Median A1200 v1.0 | Bad Apple!! A1200 v1.0 |
| :---: | :---: |
| ![Median A1200](docs/preview_median.png) | ![Bad Apple A1200](docs/preview.png) |

## Opublikowane dema (Wersja 1.0)

### 1. Median A1200 [Retail v1.0]
- **Co robi:** Port kultowego dema *Median* (Umlaut Design, 2016) działający w płynnych **50.00 FPS PAL**. Prezentuje geometryczny morphing kwadratów, scenę z czerwonym słońcem oraz architekturę 3D z zachowaniem oryginalnej estetyki 3 kolorów (`#EEE`, `#111`, `#E11`) i wygładzaniem krawędzi.
- **Używane procedury silnika:** `sys_takeover`, `setup_copper`, `init_fill_lut`, `play_vector_frame`, `draw_polygon_mode` (tryby `0` czerń, `1` wycięcia otworów, `2` czerwień `BPL2`), `apply_blitter_aa` (wygładzanie krawędzi na `BPL3`), `setup_paula` oraz `aud0_irq_handler`.
- **Wymagania:** Amiga 1200 (68EC020+, AGA), **2 MB Chip RAM + 8 MB Fast RAM** (flaga `NoMMU` w WHDLoad) lub **THEA1200**.

### 2. Bad Apple!! A1200 [50FPS + Blitter AA v1.0]
- **Co robi:** Pełny teledysk *Bad Apple!!* (3:39, ZUN / Anira) w zablokowanych **50.00 FPS PAL** (1 klatka na każde przerwanie VBL), z ostrymi sylwetkami, wewnętrznymi wycięciami (oczy, wstążki, prześwity) i wygładzaniem Blittera.
- **Używane procedury silnika:** `init_fill_lut`, `play_vector_frame`, `draw_polygon_mode` (z tablicą odwrotności `inv_tab` i buforem rysowania `fast_bpl1` w Fast RAM), 32-bitowe kopiowanie `Fast RAM -> Chip RAM`, `apply_blitter_aa` oraz `setup_paula` (4 kanały DMA).
- **Wymagania:** Amiga 1200 (68EC020+, AGA), **2 MB Chip RAM + 8 MB Fast RAM** lub **THEA1200**.

## Architektura silnika i opis procedur (`src/`)
- `src/main.s` — Punkt wejścia (`start`), pętla główna zsynchronizowana z zegarem `50 Hz VBL` (`wait_vbl`, `vbl_tick`), szybki transfer bufora `fast_bpl1` do Chip RAM oraz obsługa wyjścia (LPM / `ESC`).
- `src/gfx_engine.i` — Przejęcie chipsetu AGA (`sys_takeover`), dynamiczna Copperlista (`setup_copper`), podwójne buforowanie ekranu (`320x256 PAL`), czyszczenie bitplanów (`blit_clear_full`) oraz sprzętowy antyaliasing na Blitterze (`apply_blitter_aa`).
- `src/vec3d_engine.i` — Rasteryzator wielokątów N-kątnych (`draw_polygon_mode`): generuje tablicę prefiksową XOR w Fast RAM (`init_fill_lut`, 512 KB), rysuje krawędzie z tablicą odwrotności `inv_tab` i wycina wewnętrzne otwory.
- `src/scene_player.i` — Dekoder strumienia wektorowego (`play_vector_frame`) odczytujący listę wielokątów i aktualizujący kolory w Copperze.
- `src/audio_player.i` — 4-kanałowy sterownik audio DMA układu Paula (`setup_paula`, `aud0_irq_handler`, przerwanie Level 4) ze sprzętowym wyłączeniem filtra dolnoprzepustowego LED (`bset #1,$bfe001`).
- `src/whdload_slave.s` — Autorski WHDLoad Slave v17 (`ws_KickSize=0`), relokujący sekcje Hunk bez potrzeby posiadania plików Kickstart ROM.

## Narzędzia budowania (`tools/`)
- `tools/build_demo.py` — Uniwersalny konwerter wideo/audio (`ffmpeg` + `OpenCV`) do kodu asemblera M68020, kompilator `vasmm68k_mot` oraz generator paczek `.lha`.
- `tools/build_median.py` — Dedykowany generator wydania *Median A1200 v1.0* (separacja czerwieni `BPL2`, wygładzanie konturów, prostowanie kątów prostych).

## Wymagania sprzętowe i uruchomienie
- **Sprzęt / Emulator:** Commodore Amiga 1200 (AGA, 68020+), **2 MB Chip RAM + 8 MB Fast RAM**, konsola **THEA1200**, FS-UAE lub WinUAE.
- **Uruchomienie:** Wskaż gotowe archiwum `.lha` z katalogu `releases/` bezpośrednio w WHDLoad, na THEA1200 lub w emulatorze FS-UAE / WinUAE.
