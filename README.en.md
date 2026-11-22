[Wersja Polska](README.md)

# Amiga 1200 / THEA1200 Vector Stream Demo Engine

Bare-metal demoscene vector & silhouette streaming engine for **Commodore Amiga 1200 (AGA, Motorola 68020+, 2 MB Chip RAM + 8 MB Fast RAM)** and **THEA1200** console (Kickstart-free WHDLoad / USB Media Access).

## Key Features & Repository Structure
Includes details on the pixel-exact fast-RAM LUT polygon engine, AGA double-buffering, Paula DMA audio, and structured source files like \`src/main.s\`, \`src/vec3d_engine.i\`, and \`tools/build_demo.py\`. See generated file for full documentation.

## Requirements & Usage
Requires \`vasmm68k_mot\`, \`ffmpeg\`, \`ffprobe\`, and Python 3 (\`numpy\`, \`opencv-python\`). Includes build commands for Bad Apple, State of the Art, and THEA1200 / FS-UAE deployment.
