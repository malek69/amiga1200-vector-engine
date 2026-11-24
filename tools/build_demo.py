import argparse, os, re, shutil, struct, subprocess, zipfile, cv2, numpy as np

def mk_ico(it, dt=None, tt=None):
    hdr = struct.pack(">HH", 0xE310, 1)
    gad = struct.pack(">IhhhhHHHIIIIIHI", 0, 0, 0, 32, 16, 4, 3, 1, 1, 0, 0, 0, 0, 0, 0)
    body = struct.pack(">BBIIIIIII", it, 0, 1 if dt else 0, 1 if tt else 0, 0x80000000, 0x80000000, 0, 0, 8192)
    img = struct.pack(">hhhhhIBBI", 0, 0, 32, 16, 1, 1, 1, 0, 0) + (bytes((255, 0, 255, 0)) * 16)
    out = bytearray(hdr + gad + body + img)
    if it == 2:
        out += bytearray(56)
    bs = lambda x: struct.pack(">I", len(x) + 1) + x.encode("ascii") + bytes(1)
    if dt:
        out += bs(dt)
    if tt:
        out += struct.pack(">I", (len(tt) + 1) * 4)
        for t in tt:
            out += bs(t)
    return bytes(out)

def mk_lha(lp, rf):
    if os.path.exists(lp): os.remove(lp)
    items = sorted(os.listdir(rf))
    subprocess.run(["lha", "ao1w=/tmp", os.path.abspath(lp)] + items, cwd=rf, check=True)

def mk_zip(zp, rf):
    if os.path.exists(zp): os.remove(zp)
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(rf):
            dirs.sort()
            for fn in sorted(files):
                fp = os.path.join(root, fn)
                zf.write(fp, os.path.relpath(fp, rf))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--audio", default=None)
    ap.add_argument("--name", default="BADAPPLE_A1200")
    ap.add_argument("--title", default="Bad Apple!! A1200 v1.1.0 [Hi-Res 640x256]")
    ap.add_argument("--credits", default="ZUN / Anira | Port: malek69")
    ap.add_argument("--fps", type=int, default=50)
    ap.add_argument("--threshold", type=int, default=120)
    ap.add_argument("--crop-43", action="store_true")
    ap.add_argument("--thin-lines", action="store_true")
    args = ap.parse_args()
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sd, od = os.path.join(repo, "src"), os.path.join(repo, "releases/v1.1.0")
    os.makedirs(od, exist_ok=True)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", args.video], capture_output=True, text=True, check=True).stdout.strip() or 180)
    hz = max(8000, min(16497, int(1550000 / max(1.0, dur))))
    per = round(3546895 / hz)
    hz_r = 3546895.0 / per
    print(f"[1/4] Audio: {hz_r:.1f} Hz (AUD0PER={per}) | Video: {args.fps} FPS @ 640x256 Hi-Res", flush=True)
    ap_p = os.path.join(sd, "audio_player.i")
    ap_t = open(ap_p).read()
    open(ap_p, "w").write(re.sub(r"#[0-9]+(?=,AUD[0-3]PER)", f"#{per}", ap_t))
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", args.audio or args.video, "-vn", "-af", f"highpass=f=40,lowpass=f=4400,alimiter=limit=0.82,aresample={int(round(hz_r))}:resampler=soxr,volume=0.80", "-f", "s8", "-ac", "1", "-ar", str(int(round(hz_r))), os.path.join(sd, "median_audio.raw")], check=True)
    w_s, h_s = [int(x) for x in subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", args.video], capture_output=True, text=True, check=True).stdout.strip().split(",")]
    x0, y0, cw, ch = 0, 0, w_s, h_s
    if args.crop_43 and (w_s / max(1, h_s)) > 1.5:
        cw = int(round(h_s * 1.28))
        x0 = (w_s - cw) // 2
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-i", args.video, "-vf", f"crop={cw}:{ch}:{x0}:{y0},scale=624:248:flags=lanczos,fps={args.fps}", "-f", "rawvideo", "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
    fb, uniq, fl, pr_raw, pr_lbl = 624 * 248, {}, list(), None, None
    k3 = np.ones((3, 3), dtype=np.uint8)
    while True:
        raw = proc.stdout.read(fb)
        if len(raw) < fb: break
        if raw == pr_raw: fl.append(pr_lbl); continue
        g = np.frombuffer(raw, dtype=np.uint8).reshape((248, 624))
        db = cv2.medianBlur(g, 3) < args.threshold
        dp = list()
        if np.any(db):
            dm = db.astype(np.uint8) * 255
            if args.thin_lines:
                th = cv2.erode(dm, k3, iterations=1)
                dm = cv2.bitwise_or(th, cv2.subtract(dm, cv2.dilate(th, k3, iterations=1)))
            cnts, hier = cv2.findContours(dm, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            if hier is not None:
                hr = hier.reshape(-1, 4)
                items = list()
                for i in range(len(cnts)):
                    d, par = 0, int(hr.item(i, 3))
                    while par != -1: d += 1; par = int(hr.item(par, 3))
                    items.append((d, i))
                items.sort()
                for eps in (1.5, 2.1, 2.9, 3.8):
                    dp, v_tot = list(), 0
                    for d, i in items:
                        if cv2.contourArea(cnts[i]) < (36.0 if (d & 1) else 18.0): continue
                        pts = cv2.approxPolyDP(cnts[i], eps, True).reshape(-1, 2)
                        m = list()
                        for (x, y) in pts:
                            pt = (int(x) + 8, int(y) + 4)
                            if not m or m[-1] != pt: m.append(pt)
                        while len(m) >= 3 and m[0] == m[-1]: m.pop()
                        if len(m) >= 3:
                            dp.append((d & 1, tuple(m)))
                            v_tot += len(m)
                    if v_tot <= 460: break
        key = tuple(dp)
        if key not in uniq: uniq[key] = f"vf_{len(uniq)}"
        pr_raw, pr_lbl = raw, uniq[key]
        fl.append(pr_lbl)
        if len(fl) % 1000 == 0: print(f"  [BadApple 640x256] Klatka {len(fl)}...", flush=True)
    proc.wait()
    lines = [f"vec_frame_count: dc.w {len(fl)}", "    even", "vec_frame_table:"] + [f"    dc.l {l}" for l in fl]
    for dp, l in uniq.items():
        lines += [f"{l}:", "    dc.w $0111"]
        for op, p in dp: lines.append(f"    dc.w {op},{len(p)}," + ",".join(f"{x},{y}" for x, y in p))
        lines.append("    dc.w -1")
    open(os.path.join(sd, "scene_data.i"), "w").write(chr(10).join(lines) + chr(10))
    exe_out = os.path.join(repo, "releases", args.name)
    subprocess.run(["vasmm68k_mot", "-m68020", "-Fhunkexe", "-kick1hunks", "-nosym", "-I.", "main.s", "-o", exe_out], cwd=sd, check=True)
    os.chmod(exe_out, 0o755)
    sz = os.path.getsize(exe_out)
    em = 0x00680000
    lo = em - sz - 256
    pr = os.path.join(od, "_tmp_pkg")
    shutil.rmtree(pr, ignore_errors=True)
    fn_d = args.name.title().replace("_", "").replace("A1200", "A1200_AGA")
    pd = os.path.join(pr, fn_d)
    os.makedirs(pd, exist_ok=True)
    shutil.copy2(exe_out, os.path.join(pd, args.name))
    sl = open(os.path.join(sd, "whdload_slave.s")).read().replace("{EXP_MEM}", f"{em:08x}").replace("{LOAD_OFF}", f"{lo:08x}").replace("{DEMO_TITLE}", args.title).replace("{DEMO_CREDITS}", args.credits).replace("{EXE_NAME}", args.name)
    ss = os.path.join(pr, "slave.s")
    open(ss, "w").write(sl)
    subprocess.run(["vasmm68k_mot", "-m68020", "-Fhunkexe", "-nosym", ss, "-o", os.path.join(pd, f"{fn_d}.slave")], check=True)
    os.remove(ss)
    open(os.path.join(pr, f"{fn_d}.info"), "wb").write(mk_ico(4, "WHDLoad", [f"SLAVE={fn_d}.slave", "NoMMU"]))
    open(os.path.join(pd, f"{fn_d}.info"), "wb").write(mk_ico(4, "WHDLoad", [f"SLAVE={fn_d}.slave", "NoMMU"]))
    lha_out = os.path.join(od, f"{fn_d}_THEA1200.lha")
    mk_lha(lha_out, pr)
    os.makedirs(os.path.join(pr, "S"), exist_ok=True)
    open(os.path.join(pr, "S/startup-sequence"), "w").write(f"cd {fn_d}" + chr(10) + f"{args.name}" + chr(10))
    zip_out = os.path.join(od, f"{fn_d}_THEA1200_FSUAE.zip")
    mk_zip(zip_out, pr)
    shutil.rmtree(pr)
    print(f"GOTOWE BadApple v1.1.0: {sz/1048576:.2f} MB | ExpMem = {em/1048576:.2f} MB -> {lha_out} oraz {zip_out}", flush=True)

if __name__ == "__main__":
    main()
