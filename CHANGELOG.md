<p align="right"><a href="README.md">Polski</a> | <a href="README_EN.md">English</a> | <strong>Historia Zmian (PL)</strong> | <a href="CHANGELOG_EN.md">Changelog (EN)</a></p>

# Historia Zmian

## [1.1.0] - 2026-11-24
### Dodano i Naprawiono
- **Trzy obozy wydawnicze (`--profile`):** `standard` (`320x256` AGA + Blitter AA dla bazowej A1200 i RetroArch Android), `thea1200` (`640x256` AGA Hi-Res + Fast-RAM `movem.l`), `060` (`640x512` AGA Interlace `1:1` + `14.6-16.5 kHz` PCM).
- **Kompatybilnosc WHDLoad / Amiberry / Android:** zapasowy `S/startup-sequence` w `.lha`, flaga `$0026` oraz pelna synchronizacja pol `LOF`.

 — A1200 Vector Engine

## v1.1.0 — AGA + Blitter AA 320x256 (2026-11-24)
- **Natywny tryb AGA + Blitter AA `320x256` (`BPLCON0 = $A200`, `DDFSTRT = $0028, DDFSTOP = $00B8`):** 2x wyzsza ostrosc pozioma wektorow przy 50.00 FPS PAL.
- **64-bitowe bitplany (`FMODE = $0003`) i Fast-RAM Pipeline:** rasteryzacja w Fast RAM oraz szybki transfer `movem.l` (48 B/iter) do Chip RAM.
- **Obsluga pada THEA1200:** wyjscie przyciskiem Fire na Joystick Port 2 (`$BFE001` bit 7) obok LPM i `ESC`.
- **Strumienie v1.1.0:** przeliczone wektory `320x256` dla *Median A1200* (`5.62 MB`) i *Bad Apple!! A1200* (`5.06 MB`).

## v1.0.1 (2026-11-23)
- Dodanie archiwow `*_FSUAE.zip` z auto-bootem `S/startup-sequence` oraz matrycy kompatybilnosci.

## v1.0.0 (2026-11-22)
- Pierwsze wydanie silnika wektorowego M68020+ / AGA (`320x256 @ 50 FPS`) z WHDLoad Slave v17.
