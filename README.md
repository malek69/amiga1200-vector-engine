[**Polski**](README.md) | [English](README_EN.md) | [Historia Zmian (PL)](CHANGELOG.md) | [Changelog (EN)](CHANGELOG_EN.md)

![Logo](docs/engine_logo.png)

# Amiga 1200 / THEA1200 Vector Stream Demo Engine v1.1.0

**Bare-metalowy silnik wektorowy M68020+ / AGA Hi-Res 640x256 @ 50.00 FPS PAL** (*malek69 & Gemini AI, 2026*)

## Pobieranie i Podglad (v1.1.0 Latest)

| Median A1200 v1.1.0 (640x256) | Bad Apple!! A1200 v1.1.0 (640x256) |
| :---: | :---: |
| ![Median](docs/preview_median.png) | ![Bad Apple](docs/preview.png) |
| **[Pobierz .LHA (THEA1200/RetroArch)](https://github.com/malek69/amiga1200-vector-engine/releases/download/v1.1.0/MedianA1200_AGA_THEA1200.lha)**<br>**[Pobierz .ZIP (FS-UAE/WinUAE)](https://github.com/malek69/amiga1200-vector-engine/releases/download/v1.1.0/MedianA1200_AGA_THEA1200_FSUAE.zip)** | **[Pobierz .LHA (THEA1200/RetroArch)](https://github.com/malek69/amiga1200-vector-engine/releases/download/v1.1.0/BadappleA1200_AGA_THEA1200.lha)**<br>**[Pobierz .ZIP (FS-UAE/WinUAE)](https://github.com/malek69/amiga1200-vector-engine/releases/download/v1.1.0/BadappleA1200_AGA_THEA1200_FSUAE.zip)** |

## Wymagania i Sterowanie
- **Sprzet:** Amiga 1200 (68EC020+ 14 MHz, AGA, **2 MB Chip RAM + 8 MB Fast RAM**), **THEA1200**, FS-UAE lub WinUAE (WHDLoad Slave v17 bez Kickstart ROM).
- **Wyjscie:** `LMB`, **Fire (Joystick Port 2 / THEA1200)** lub `ESC`.

## Mozliwosci silnika
- **Rasteryzator N-gon XOR LUT:** szybkie wypelnianie wielokatow i wycinanie otworow (cutouts) w oparciu o 512 KB tablice prefiksow w Fast RAM.
- **Potok M68020+ / AGA & Paula 4CH DMA:** podwojne buforowanie VBL `50.00 FPS PAL`, 4-kanalowe audio PCM (filtr LED wyl.) oraz konwertery wideo `tools/`.

## Co nowego w v1.1.0
- **AGA Hi-Res `640x256` (`BPLCON0 = $A200`, `DDFSTOP = $00CC`, `FMODE = $0003`):** 2x wyzsza ostrosc pozioma wektorow z 64-bitowym DMA bez dlawienia CPU.
- **Fast-RAM Backbuffer + `movem.l` Burst & THEA1200:** rysowanie w Fast RAM, transfer blokowy `48 B/iter` do Chip RAM oraz wyjscie padem THEA1200.

## Architektura i Moduly Silnika (`src/`)

| Modul | Rola w silniku | Mechanizmy sprzetowe i algorytmy |
| :--- | :--- | :--- |
| **`main.s`** | Glowna petla 50 Hz PAL | Synchronizacja VBL (`50.00 FPS`), czyszczenie Fast RAM oraz rozwiniety transfer `movem.l` (`48 B/iter`) `Fast -> Chip` |
| **`gfx_engine.i`** | Inicjalizacja AGA i Coppera | Przejecie sprzetu (`sys_takeover`), tryb **AGA Hi-Res `640x256`** (`BPLCON0 = $A200`, `DDFSTOP = $00CC`), 64-bitowe bitplany (`FMODE = $0003`), podwojne buforowanie VBL |
| **`vec3d_engine.i`** | Rasteryzator wielokatow N-gon | Skanowanie krawedzi 16-bitowych (`0..639 x 0..255`) do `edge_buf` i wypelnianie z wycinaniem otworow (cutouts) przez 512 KB tablice prefiksow `fill_lut` w Fast RAM |
| **`scene_player.i`** | Dekoder strumienia klatek | Odczyt tablicy klatek `vec_frame_table` i dyspozycja wielokatow na aktywne bitplany AGA |
| **`audio_player.i`** | Odtwarzacz Paula 4CH DMA | Strumieniowe audio PCM z Fast RAM przez podwojne bufory `2048 B` w Chip RAM (IRQ Level 4) z wylaczonym filtrem LED |
| **`whdload_slave.s`** | Loader bez Kickstart ROM | Autorski WHDLoad Slave v17 (`ws_KickSize=0`) alokujacy Chip/Fast RAM i uruchamiajacy demo bez plikow Kickstart |

---

## Narzedzia Deweloperskie (`tools/`)

- **`tools/build_median.py`** — dedykowany potok przetwarzajacy material *Median* (`624x496` -> `640x256` Hi-Res @ `50 FPS`, separacja warstw czerni i czerwieni, upraszczanie wielokatow i budowa paczek `.lha` + `*_FSUAE.zip`).
- **`tools/build_demo.py`** — uniwersalny konwerter wideo na strumien wektorowy `640x256` Hi-Res AGA (`--video`, `--fps`, `--threshold`, `--crop-43`, `--thin-lines`) automatycznie kompilujacy binarke `vasmm68k_mot`, WHDLoad Slave oraz archiwa `.lha` i `*_FSUAE.zip`.
