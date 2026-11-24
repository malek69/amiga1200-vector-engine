<p align="right"><a href="README.md">README (EN / PL)</a> | <strong>Historia Zmian (PL)</strong> | <a href="CHANGELOG_EN.md">Changelog (EN)</a></p>

# Historia Zmian — A1200 / THEA1200 Vector Stream Demo Engine

Chronologiczny rejestr rozwoju silnika wektorowego **A1200 Vector Engine** dla Commodore Amiga 1200 (M68020+ / AGA) oraz konsoli THEA1200.

---

## v1.1.0 — AGA Hi-Res 640x256 & Fast-RAM Pipeline (2026-11-24)

- **Natywny tryb AGA Hi-Res `640x256`:** 2x wyższa ostrość pozioma krawędzi wektorów przy sztywnych 50.00 FPS PAL.
- **64-bitowe pobieranie bitplanów i szybki transfer w Fast RAM:** eliminacja rywalizacji o Chip RAM oraz buforowanie w Fast RAM z kopiowaniem przez `movem.l`.
- **Obsługa pada THEA1200:** wyjście z dema przyciskiem Fire na Joystick Port 2.

---

## v1.0.1 & v1.0.0 — Podstawowe wydania i kompatybilność WHDLoad (2026-11-22 – 2026-11-23)

- Wprowadzenie pakietów `.lha` (WHDLoad) oraz `*_FSUAE.zip` bez wymagań Kickstart ROM oraz bazowego silnika wektorowego M68020+ / AGA z obsługą *Median A1200* i *Bad Apple!! A1200*.
