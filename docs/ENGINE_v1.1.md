# Specyfikacja Techniczna Silnika v1.1.0 — Trzy Profile Sprzętowe

## 1. Architektura Trzech Profili (`tools/profile_patch.py`)
- **`standard` (`320x256` AGA + Blitter AA @ `50.00 FPS`):** 2 bitplany, Blitter, do `550` wierzchołków na klatkę, zgodność z stock A1200 (`68EC020`) i RetroArch `PUAE`.
- **`thea1200` (`640x256` AGA Hi-Res @ `50.00 FPS`):** natywne `640 px` (`BPLCON0 = $A200`, `DDFSTRT = $003C`, `DDFSTOP = $00D4`), rasteryzacja XOR LUT w Fast RAM i `movem.l` (`48 B/iter`).
- **`060` (`640x512` AGA Hi-Res Interlace `1:1` @ `50 Hz` pól / `25 Hz` klatek):** pełne PAL (`BPLCON0 = $A204`), do `1200` wierzchołków, `ws_ExpMem = $00780000` (`7.50 MB`).

## 2. Synchronizacja Przeplotu Interlace (`640x512`)
- Buforowanie `25 Hz` (40 ms na kopię `81 920 B` do Chip RAM) oraz odczyt bitu `LOF` (`VPOSR` `$DFF004` bit 15) w przerwaniu VBL (`50 Hz`).

## 3. Hybrydowe Paczki Dystrybucyjne (`.lha` + `*_FSUAE.zip`)
- Zawierają WHDLoad Slave v17 (`ws_Flags = $0026`) oraz zapasowy skrypt `S/startup-sequence` dla środowisk bez komendy `C:WHDLoad`.
