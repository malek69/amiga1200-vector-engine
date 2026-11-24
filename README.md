[**Polski**](README.md) | [English](README_EN.md) | [Historia Zmian (PL)](CHANGELOG.md) | [Changelog (EN)](CHANGELOG_EN.md)

![Logo](docs/engine_logo.png)

# Amiga 1200 / THEA1200 Vector Stream Demo Engine v1.1.0

**Bare-metalowy silnik wektorowy M68020+ / AGA + Blitter AA 320x256 @ 50.00 FPS PAL** (*malek69 & Gemini AI, 2026*)

## Pobieranie i Podglad (v1.1.0 — 3 Obozy Wydawnicze)

| Median A1200 v1.1.0 | Bad Apple!! A1200 v1.1.0 |
| :---: | :---: |
| ![Median](docs/preview_median.png) | ![Bad Apple](docs/preview.png) |
| **1. Standard `020` (`320x256` + Blitter AA):**<br>[.LHA](https://github.commalek69/amiga1200-vector-engine/releases/download/v1.1.0/MedianA1200_AGA_THEA1200.lha) · [.ZIP](https://github.commalek69/amiga1200-vector-engine/releases/download/v1.1.0/MedianA1200_AGA_THEA1200_FSUAE.zip)<br>**2. THEA1200 (`640x256` AGA Hi-Res):**<br>[.LHA](https://github.commalek69/amiga1200-vector-engine/releases/download/v1.1.0/MedianA1200_AGA_HiRes640.lha) · [.ZIP](https://github.commalek69/amiga1200-vector-engine/releases/download/v1.1.0/MedianA1200_AGA_HiRes640_FSUAE.zip)<br>**3. Turbo `MC68060` (`640x512` Interlace):**<br>[.LHA](https://github.commalek69/amiga1200-vector-engine/releases/download/v1.1.0/MedianA1200_AGA_060_HiRes512.lha) · [.ZIP](https://github.commalek69/amiga1200-vector-engine/releases/download/v1.1.0/MedianA1200_AGA_060_HiRes512_FSUAE.zip) | **1. Standard `020` (`320x256` + Blitter AA):**<br>[.LHA](https://github.commalek69/amiga1200-vector-engine/releases/download/v1.1.0/BadappleA1200_AGA_THEA1200.lha) · [.ZIP](https://github.commalek69/amiga1200-vector-engine/releases/download/v1.1.0/BadappleA1200_AGA_THEA1200_FSUAE.zip)<br>**2. THEA1200 (`640x256` AGA Hi-Res):**<br>[.LHA](https://github.commalek69/amiga1200-vector-engine/releases/download/v1.1.0/BadappleA1200_AGA_HiRes640.lha) · [.ZIP](https://github.commalek69/amiga1200-vector-engine/releases/download/v1.1.0/BadappleA1200_AGA_HiRes640_FSUAE.zip)<br>**3. Turbo `MC68060` (`640x512` Interlace):**<br>[.LHA](https://github.commalek69/amiga1200-vector-engine/releases/download/v1.1.0/BadappleA1200_AGA_060_HiRes512.lha) · [.ZIP](https://github.commalek69/amiga1200-vector-engine/releases/download/v1.1.0/BadappleA1200_AGA_060_HiRes512_FSUAE.zip) |

## Trzy Obozy Wydawnicze (3 Target Profiles)
| Profil (`--profile`) | Platforma docelowa | Rozdzielczosc i potok | Audio i detale |
| :--- | :--- | :--- | :--- |
| **`standard`** | Bazowa **Amiga 1200 (`68020`)**, **RetroArch (Android)** | `320x256` AGA + 8-odcieniowy **Blitter AA** @ `50 FPS` | `8–16.5 kHz` PCM, do `550` wierzcholkow |
| **`thea1200`** | Konsola **THEA1200**, **Amiberry (PC)**, **FS-UAE** | Natywne **`640x256` AGA Hi-Res** + Fast-RAM `movem.l` @ `50 FPS` | `12.1–16.5 kHz` PCM, do `650` wierzcholkow |
| **`060`** | Karty turbo **`MC68060` (50+ MHz, Z3 Fast RAM)** | **`640x512` AGA Hi-Res Interlace** (`1:1`, 0 schodkow) | `16.5 kHz` PCM, do `1200` wierzcholkow |

## Wymagania i Sterowanie
- **Sprzet:** Amiga 1200 (68EC020+ 14 MHz, AGA, **2 MB Chip RAM + 8 MB Fast RAM**), **THEA1200**, FS-UAE lub WinUAE (WHDLoad Slave v17 bez Kickstart ROM).
- **Wyjscie:** `LMB`, **Fire (Joystick Port 2 / THEA1200)** lub `ESC`.

## Mozliwosci silnika
- **Rasteryzator N-gon XOR LUT:** szybkie wypelnianie wielokatow i wycinanie otworow (cutouts) w oparciu o 512 KB tablice prefiksow w Fast RAM.
- **Potok M68020+ / AGA & Paula 4CH DMA:** podwojne buforowanie VBL `50.00 FPS PAL`, 4-kanalowe audio PCM (filtr LED wyl.) oraz konwertery wideo `tools/`.

## Co nowego w v1.1.0
- **AGA + Blitter AA `320x256` (`BPLCON0 = $A200`, `DDFSTRT = $0028, DDFSTOP = $00B8`, `FMODE = $0003`):** 2x wyzsza ostrosc pozioma wektorow z 64-bitowym DMA bez dlawienia CPU.
- **Fast-RAM Backbuffer + `movem.l` Burst & THEA1200:** rysowanie w Fast RAM, transfer blokowy `48 B/iter` do Chip RAM oraz wyjscie padem THEA1200.

## Architektura i Moduly Silnika (`src/`)

| Modul | Rola w silniku | Mechanizmy sprzetowe i algorytmy |
| :--- | :--- | :--- |
| **`main.s`** | Glowna petla 50 Hz PAL | Synchronizacja VBL (`50.00 FPS`), czyszczenie Fast RAM oraz rozwiniety transfer `movem.l` (`48 B/iter`) `Fast -> Chip` |
| **`gfx_engine.i`** | Inicjalizacja AGA i Coppera | Przejecie sprzetu (`sys_takeover`), tryb **AGA + Blitter AA `320x256`** (`BPLCON0 = $A200`, `DDFSTRT = $0028, DDFSTOP = $00B8`), 64-bitowe bitplany (`FMODE = $0003`), podwojne buforowanie VBL |
| **`vec3d_engine.i`** | Rasteryzator wielokatow N-gon | Skanowanie krawedzi 16-bitowych (`0..639 x 0..255`) do `edge_buf` i wypelnianie z wycinaniem otworow (cutouts) przez 512 KB tablice prefiksow `fill_lut` w Fast RAM |
| **`scene_player.i`** | Dekoder strumienia klatek | Odczyt tablicy klatek `vec_frame_table` i dyspozycja wielokatow na aktywne bitplany AGA |
| **`audio_player.i`** | Odtwarzacz Paula 4CH DMA | Strumieniowe audio PCM z Fast RAM przez podwojne bufory `2048 B` w Chip RAM (IRQ Level 4) z wylaczonym filtrem LED |
| **`whdload_slave.s`** | Loader bez Kickstart ROM | Autorski WHDLoad Slave v17 (`ws_KickSize=0`) alokujacy Chip/Fast RAM i uruchamiajacy demo bez plikow Kickstart |

---

## Narzedzia Deweloperskie (`tools/`)

- **`tools/build_median.py`** — dedykowany potok przetwarzajacy material *Median* (`624x496` -> `320x256` AGA + Blitter AA @ `50 FPS`, separacja warstw czerni i czerwieni, upraszczanie wielokatow i budowa paczek `.lha` + `*_FSUAE.zip`).
- **`tools/build_demo.py`** — uniwersalny konwerter wideo na strumien wektorowy `320x256` AGA + Blitter AA AGA (`--video`, `--fps`, `--threshold`, `--crop-43`, `--thin-lines`) automatycznie kompilujacy binarke `vasmm68k_mot`, WHDLoad Slave oraz archiwa `.lha` i `*_FSUAE.zip`.

---

## Warianty Paczek i Kompatybilnosc (v1.1.0)
- **`.lha` (`*_AGA_THEA1200.lha` — RetroArch PUAE / THEA1200 / Real A1200):** spakowane z naglowkami Amiga LHA Level 1 oraz 78-bajtowymi ikonami WHDLoad `WBPROJECT`. Przetestowane przez **Load Content** w **RetroArch (`PUAE`)** oraz **THEA1200 (`Amiberry`)**.
- **`.zip` (`*_AGA_THEA1200_FSUAE.zip` — FS-UAE Launcher / WinUAE):** archiwum WHDLoad ZIP obslugiwane natywnie bez zewnetrznych wtyczek `python-lhafile`. Auto-boot jednym kliknieciem przez `S/startup-sequence` — zamontuj `.zip` jako dysk twardy (`DH0`) na profilu A1200 (8 MB Fast RAM) i kliknij **Start**.

---


## Prompty dla AI (Vibe Coding Edition — Odtworzenie i Rozbudowa)
Pelna dokumentacja procesu powstawania projektu znajduje sie w [docs/MAKING_OF.md](docs/MAKING_OF.md) oraz [docs/ENGINE_v1.1.md](docs/ENGINE_v1.1.md). Ponizsze prompty pozwalaja odtworzyc lub rozbudowac poszczegolne moduly silnika:

- **[PROMPT 1 — Ekstrakcja wektorow HD i audio z wideo PC -> Asembler M68020]:** *"Napisz skrypt w Pythonie (OpenCV + NumPy + FFmpeg), ktory wyciagnie z pliku wideo 50 FPS sciezke dzwiekowa 8-bit signed PCM (z filtrem dolnoprzepustowym i limiterem) oraz strumien zamknietych wielokatow N-katnych w rozdzielczosci Amigi AGA + Blitter AA 320x256 z zachowaniem proporcji. Otwory wewnetrzne oznacz jako tryb wycinania (HIERARCHY depth & 1), a czerwone warstwy zapisz na drugim bitplanie. Wygeneruj plik scene_data.i w skladni vasm z deduplikacja klatek."*
- **[PROMPT 2 — Rasteryzator wielokatow N-gon z 512 KB XOR LUT w Fast RAM]:** *"Napisz w asemblerze M68020 (vasmm68k_mot) szybki rasteryzator wielokatow dla Amigi 1200 (AGA + Blitter AA 320x256 PAL, double-buffering). Prekompiluj w Fast RAM 512 KB tablice wypelniania XOR scanline (fill_lut), rysuj krawedzie metoda bchg do edge_buf, wypelniaj wielokaty w Fast RAM i kopiuj gotowe bitplany rozwinietymi instrukcjami movem.l (48 B/iter) do Chip RAM."*
- **[PROMPT 3 — Dzwiek Paula DMA IRQ Level 4 i filtr LED]:** *"Napisz sterownik audio w asemblerze M68020 dla ukladu Paula (4 kanaly DMA, podwojny bufor 2048 bajtow w Chip RAM) obslugiwany sprzetowym przerwaniem Audio Level 4 ($70) z wylaczeniem sprzetowego filtra dolnoprzepustowego LED ($BFE001 bit 1)."*
- **[PROMPT 4 — Autorski WHDLoad Slave v17 bez Kickstart ROM + THEA1200 Joy2]:** *"Napisz od zera w asemblerze M68020 plik WHDLoad Slave (WHDLOADS v17, ws_KickSize=0, bez wymaganego obrazu Kickstartu), ktory wczyta plik AmigaDOS Hunk, przydzieli sekcje CHIP i FAST, wykona relokacje HUNK_RELOC32, wlaczy cache M68020 (CACR) i pozwoli wyjsc przez LMB, Fire na Joystick Port 2 (THEA1200) lub ESC."*
