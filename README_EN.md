
---

## Controls (Mouse, Keyboard &amp; THEA1200 Gamepad)

| Controller / Key | Action |
| :--- | :--- |
| **`LMB` (Left Mouse Button)** | Clean exit back to AmigaOS / WHDLoad |
| **`Fire` (Joystick Port 2 / THEA1200)** | Exit demo via USB gamepad on THEA1200 (`$BFE001` bit 7) |
| **`ESC`** | Direct CIA-A keyboard exit (`$BFEC01`) |

---

## Engine Architecture &amp; Modules (`src/`)

| Module | Role | Hardware &amp; Algorithms |
| :--- | :--- | :--- |
| **`main.s`** | Main 50 Hz PAL Loop | VBL frame lock (`50.00 FPS`), Fast-RAM buffer clear, and unrolled `movem.l` (`48 B/iter`) `Fast -> Chip` burst transfer |
| **`gfx_engine.i`** | AGA &amp; Copper Setup | Hardware takeover (`sys_takeover`), native **AGA Hi-Res `640x256`** (`BPLCON0 = $A200`, `DDFSTOP = $00CC`), 64-bit bitplanes (`FMODE = $0003`), VBL double-buffering |
| **`vec3d_engine.i`** | N-gon Polygon Rasterizer | 16-bit edge stepping (`0..639 x 0..255`) into `edge_buf` and XOR span filling with hole cutouts via 512 KB `fill_lut` in Fast RAM |
| **`scene_player.i`** | Frame Stream Decoder | Reads `vec_frame_table` stream and dispatches polygons to target AGA bitplanes |
| **`audio_player.i`** | 4CH Paula DMA Audio | Streams PCM audio from Fast RAM via dual `2048 B` Chip-RAM buffers (Level 4 IRQ) with hardware LED filter disabled |
| **`whdload_slave.s`** | Kickstart-Free Loader | Custom WHDLoad Slave v17 (`ws_KickSize=0`) allocating Chip/Fast RAM and booting without external Kickstart ROMs |

---

## Developer Toolchain (`tools/`)

- **`tools/build_median.py`** — dedicated pipeline converting *Median* (`624x496` -> `640x256` Hi-Res @ `50 FPS`, dual black/red layer extraction, polygon simplification, and packaging into `.lha` + `*_FSUAE.zip`).
- **`tools/build_demo.py`** — universal video-to-vector `640x256` Hi-Res AGA converter (`--video`, `--fps`, `--threshold`, `--crop-43`, `--thin-lines`) compiling the M68020 executable (`vasmm68k_mot`), WHDLoad Slave, `.lha`, and `*_FSUAE.zip` archives.
