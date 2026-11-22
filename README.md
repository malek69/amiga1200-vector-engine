# Amiga 1200 / THEA1200 Vector Stream Demo Engine

Bare-metalowy silnik demoscenowy dla **Commodore Amiga 1200 (AGA, 68020+, 2 MB Chip + 8 MB Fast RAM)** oraz konsoli **THEA1200** (WHDLoad bez Kickstartu).

## Struktura repozytorium
- \`src/main.s\` - petla glowna i blokada synchronizacji A/V (\`pcm_played\`)
- \`src/gfx_engine.i\` - przejecie chipsetu AGA (320x256 PAL), Copperlista i double-buffering
- \`src/vec3d_engine.i\` - rasteryzator wielokatow N-katnych z tablica \`fill_lut\` (512 KB Fast RAM)
- \`src/scene_player.i\` - dekoder strumienia klatek wektorowych
- \`src/audio_player.i\` - sterownik 4 kanalow DMA Paula (IRQ Level 4) z wylaczeniem filtra LED
- \`src/whdload_slave.s\` - szablon WHDLoad Slave v17 (\`ws_KickSize=0\`) dla THEA1200 i FS-UAE
- \`tools/build_demo.py\` - uniwersalny konwerter wideo/audio -> Asembler M68020 + kompilator \`vasm\` + paczka \`.lha\`
- \`docs/MAKING_OF.md\` - dokumentacja techniczna projektu oraz gotowe prompty dla AI
- \`releases/\` - skompilowane pliki wykonywalne AmigaDOS i paczki WHDLoad \`.lha\`

## Wymagania i instalacja
1. \`vasmm68k_mot\`, \`ffmpeg\`, \`ffprobe\`
2. Python 3: \`pip install numpy opencv-python\` (Arch: \`sudo pacman -S ffmpeg python-numpy python-opencv\`)

## Uzycie
- **Bad Apple!!:** \`python3 tools/build_demo.py --video bad_apple.mp4 --name BADAPPLE_A1200 --title "Bad Apple!! A1200" --fps 20 --threshold 128\`
- **State of the Art (16:9 -> 4:3):** \`python3 tools/build_demo.py --video sota.mp4 --name SOTA_A1200 --title "State of the Art A1200" --fps 16 --threshold 120 --crop-43\`
- **Median (cienkie linie):** \`python3 tools/build_demo.py --video input.mp4 --audio music.mp3 --name MEDIAN_A1200 --thin-lines\`

## Uruchamianie (THEA1200 / FS-UAE)
Skopiuj plik \`.lha\` z \`releases/\` lub zakladki *Releases* na pendrive USB (THEA1200) lub wskaż w FS-UAE Launcher (Amiga 1200, 68020, 8 MB Fast RAM).

## Wymagania i instalacja
1. \`vasmm68k_mot\`, \`ffmpeg\`, \`ffprobe\`
2. Python 3: \`pip install numpy opencv-python\` (Arch: \`sudo pacman -S ffmpeg python-numpy python-opencv\`)

## Uzycie
- **Bad Apple!!:** \`python3 tools/build_demo.py --video bad_apple.mp4 --name BADAPPLE_A1200 --title "Bad Apple!! A1200" --fps 20 --threshold 128\`
- **State of the Art (16:9 -> 4:3):** \`python3 tools/build_demo.py --video sota.mp4 --name SOTA_A1200 --title "State of the Art A1200" --fps 16 --threshold 120 --crop-43\`
- **Median (cienkie linie):** \`python3 tools/build_demo.py --video input.mp4 --audio music.mp3 --name MEDIAN_A1200 --thin-lines\`

## Uruchamianie (THEA1200 / FS-UAE)
Skopiuj plik \`.lha\` z \`releases/\` lub zakladki *Releases* na pendrive USB (THEA1200) lub wskaż w FS-UAE Launcher (Amiga 1200, 68020, 8 MB Fast RAM).
