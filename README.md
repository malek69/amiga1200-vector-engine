[**Polski**](README.md) | [English](README_EN.md) | ...## Architektura i Moduly Silnika (`src/`)

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
