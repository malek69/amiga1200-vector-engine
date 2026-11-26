import argparse, os, stat, subprocess

HOME = os.path.expanduser("~")
DESK = os.path.join(HOME, "Pulpit") if os.path.isdir(os.path.join(HOME, "Pulpit")) else os.path.join(HOME, "Desktop")

PROJECTS = {
    "game": [
        ("AetherFalcon", "Aether Falcon", os.path.join(HOME, "aether-falcon-vanguard", "docs", "logo_vanguard.png"), {
            "020": os.path.join(HOME, "aether-falcon-vanguard", "build", "AetherFalcon_AGA_020_FSUAE.zip"),
            "THEA1200": os.path.join(HOME, "aether-falcon-vanguard", "build", "AetherFalcon_AGA_THEA1200_FSUAE.zip"),
            "060": os.path.join(HOME, "aether-falcon-vanguard", "build", "AetherFalcon_AGA_060_FSUAE.zip"),
        }),
    ],
    "3d": [
        ("Aura3D", "AURA-3D", os.path.join(HOME, "aura3d-aga-engine", "docs", "logo.png"), {
            "020": os.path.join(HOME, "aura3d-aga-engine", "releases", "aura3d_demo_v2_AGA_020_FSUAE.zip"),
            "THEA1200": os.path.join(HOME, "aura3d-aga-engine", "releases", "aura3d_demo_v2_AGA_THEA1200_FSUAE.zip"),
            "060": os.path.join(HOME, "aura3d-aga-engine", "releases", "aura3d_demo_v2_AGA_060_FSUAE.zip"),
        }),
    ],
    "vector": [
        ("Median", "Median", os.path.join(HOME, "amiga1200-vector-engine", "docs", "engine_logo.png"), {
            "020": os.path.join(HOME, "amiga1200-vector-engine", "releases", "MedianA1200_AGA_THEA1200_FSUAE.zip"),
            "THEA1200": os.path.join(HOME, "amiga1200-vector-engine", "releases", "MedianA1200_AGA_HiRes640_FSUAE.zip"),
            "060": os.path.join(HOME, "amiga1200-vector-engine", "releases", "MedianA1200_AGA_060_HiRes512_FSUAE.zip"),
        }),
        ("BadApple", "Bad Apple", os.path.join(HOME, "amiga1200-vector-engine", "docs", "engine_logo.png"), {
            "020": os.path.join(HOME, "amiga1200-vector-engine", "releases", "BadappleA1200_AGA_THEA1200_FSUAE.zip"),
            "THEA1200": os.path.join(HOME, "amiga1200-vector-engine", "releases", "BadappleA1200_AGA_HiRes640_FSUAE.zip"),
            "060": os.path.join(HOME, "amiga1200-vector-engine", "releases", "BadappleA1200_AGA_060_HiRes512_FSUAE.zip"),
        }),
    ],
}

CPU_ARGS = {
    "020": "--cpu=68EC020 --chip_memory=2048 --fast_memory=8192",
    "THEA1200": "--cpu=68040 --jit_compiler=1 --chip_memory=2048 --fast_memory=8192",
    "060": "--cpu=68060-nommu --jit_compiler=1 --chip_memory=2048 --zorro_iii_memory=16384",
}

def make_entry(file_prefix, label, icon_path, prof, zip_path):
    tmp_dir = f"/tmp/amiga_run_{file_prefix.lower()}_{prof.lower()}"
    sh_path = os.path.join(DESK, f"{file_prefix}_{prof}.sh")
    dt_path = os.path.join(DESK, f"{file_prefix}_{prof}.desktop")
    sh_txt = (
        "#!/bin/sh\n"
        f"rm -rf {tmp_dir} && mkdir -p {tmp_dir}\n"
        f"unzip -q \"{zip_path}\" -d {tmp_dir}\n"
        f"exec fs-uae --amiga_model=A1200 {CPU_ARGS[prof]} --window_width=1280 --window_height=720 --keep_aspect=0 --hard_drive_0={tmp_dir}\n"
    )
    with open(sh_path, "w", encoding="utf-8") as f: f.write(sh_txt)
    os.chmod(sh_path, os.stat(sh_path).st_mode | stat.S_IEXEC)
    dt_txt = (
        "[Desktop Entry]\n"
        "Type=Application\n"
        f"Name={label} {prof}\n"
        f"Exec={sh_path}\n"
        f"Icon={icon_path}\n"
        "Terminal=false\n"
        "Categories=Game;\n"
    )
    with open(dt_path, "w", encoding="utf-8") as f: f.write(dt_txt)
    os.chmod(dt_path, os.stat(dt_path).st_mode | stat.S_IEXEC)
    subprocess.run(["gio", "set", dt_path, "metadata::trusted", "true"], stderr=subprocess.DEVNULL)
    print(f"[OK] {label} {prof} -> {dt_path}")

def main():
    p = argparse.ArgumentParser(description="Create FS-UAE desktop shortcuts (020 / THEA1200 / 060)")
    p.add_argument("--target", choices=["game", "3d", "vector", "all"], default="all")
    args = p.parse_args()
    os.makedirs(DESK, exist_ok=True)
    targets = ["game", "3d", "vector"] if args.target == "all" else [args.target]
    for t in targets:
        for file_prefix, label, icon_path, zips in PROJECTS[t]:
            for prof, zip_path in zips.items():
                make_entry(file_prefix, label, icon_path, prof, zip_path)

if __name__ == "__main__":
    main()
