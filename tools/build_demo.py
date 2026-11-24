import argparse, os, re, shutil, struct, subprocess, sys, zipfile, cv2, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import profile_patch as pp
def mk_ico(it, dt=None, tt=None):
    hdr = struct.pack(">HH", 0xE310, 1)
    gad = struct.pack(">IhhhhHHHIIIIIHI", 0, 0, 0, 32, 16, 4, 3, 1, 1, 0, 0, 0, 0, 0, 0)
    body = struct.pack(">BBIIIIIII", it, 0, 1, 1, 0x80000000, 0x80000000, 0, 0, 8192)
    img = struct.pack(">hhhhhIBBI", 0, 0, 32, 16, 1, 1, 1, 0, 0) + (bytes((255, 0, 255, 0)) * 16)
    out = bytearray(hdr + gad + body + img)
    bs = lambda s: struct.pack(">I", len(s) + 1) + s.encode("ascii") + b"\x00"
    if dt: out += bs(dt)
    if tt:
        out += struct.pack(">I", (len(tt) + 1) * 4)
        for t in tt: out += bs(t)
    return bytes(out)
def mk_lha(lp, rf):
    if os.path.exists(lp): os.remove(lp)
    items = sorted(os.listdir(rf))
    subprocess.run(("lha", "ao1w=/tmp", os.path.abspath(lp)) + tuple(items), cwd=rf, check=True)
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
    ap.add_argument("--title", default="Bad Apple!! A1200 v1.1.0")
    ap.add_argument("--credits", default="ZUN / Anira | Port: malek69")
    ap.add_argument("--fps", type=int, default=50)
    ap.add_argument("--threshold", type=int, default=120)
    ap.add_argument("--crop-43", action="store_true")
    ap.add_argument("--profile", choices=("standard", "thea1200", "060"), default="standard")
    args = ap.parse_args()
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    od = os.path.join(repo, "releases/v1.1.0")
    os.makedirs(od, exist_ok=True)
    sd = "/tmp/_vec_demo_build"
    shutil.rmtree(sd, ignore_errors=True)
    shutil.copytree(os.path.join(repo, "src"), sd)
    dur = float(subprocess.check_output(("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", args.video), text=True).strip() or 180)
    hz_cap = 16497 if args.profile == "060" else (12105 if args.profile == "thea1200" else 8007)
    hz_t, vw, vh, ox, oy, vlim, sfx = pp.apply_profile(sd, args.profile, hz_cap)
    hz = max(8000, min(hz_t, int((3200000 if args.profile == "060" else 1550000) / max(1.0, dur))))
    per = round(3546895 / hz)
    hz_r = 3546895.0 / per
    print(f"[1/4] Profil={args.profile} | Audio={hz_r:.1f}Hz (PER={per}) | {vw+ox*2}x{vh+oy*2}@{args.fps}FPS", flush=True)
    ap_p = os.path.join(sd, "audio_player.i")
    open(ap_p, "w").write(re.sub(r"#[0-9]+(?=,AUD[0-3]PER)", f"#{per}", open(ap_p).read()))
    subprocess.run(("ffmpeg", "-y", "-v", "error", "-i", args.audio or args.video, "-vn", "-af", f"highpass=f=40,lowpass=f=5200,alimiter=limit=0.82,aresample={int(round(hz_r))}:resampler=soxr,volume=0.80", "-f", "s8", "-ac", "1", "-ar", str(int(round(hz_r))), os.path.join(sd, "median_audio.raw")), check=True)
    w_s, h_s = map(int, subprocess.check_output(("ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", args.video), text=True).strip().split(","))
    cw = int(round(h_s * 1.28)) if (args.crop_43 and (w_s / max(1, h_s)) > 1.5) else w_s
    x0 = (w_s - cw) // 2
    proc = subprocess.Popen(("ffmpeg", "-v", "error", "-i", args.video, "-vf", f"crop={cw}:{h_s}:{x0}:0,scale={vw}:{vh}:flags=lanczos,fps={args.fps}", "-f", "rawvideo", "-pix_fmt", "gray", "-"), stdout=subprocess.PIPE)
    fb, uniq, fl, pr_raw, pr_lbl = vw * vh, dict(), list(), None, None
    k3 = np.ones((3, 3), dtype=np.uint8)
    eps_seq = (1.1, 1.6, 2.3, 3.2) if args.profile == "060" else ((1.5, 2.1, 2.9, 3.8) if args.profile == "thea1200" else (1.05, 1.55, 2.2, 3.0))
    while True:
        raw = proc.stdout.read(fb)
        if len(raw) < fb: break
        if raw == pr_raw: fl.append(pr_lbl); continue
        g = np.frombuffer(raw, dtype=np.uint8).reshape((vh, vw))
        db = cv2.morphologyEx((cv2.medianBlur(g, 3) < args.threshold).astype(np.uint8), cv2.MORPH_CLOSE, k3)
        dp = list()
        if np.any(db):
            cnts, hr = cv2.findContours(db, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
            if hr is not None:
                items = list()
                for i in range(len(cnts)):
                    if cv2.contourArea(cnts[i]) < 14.0: continue
                    d, par = 0, int(hr.item(0, i, 3))
                    while par != -1: d += 1; par = int(hr.item(0, par, 3))
                    items.append((d, i))
                items.sort()
                for eps in eps_seq:
                    dp, vt = list(), 0
                    for d, i in items:
                        if cv2.contourArea(cnts[i]) < (26.0 if (d & 1) else 14.0): continue
                        pts = cv2.approxPolyDP(cnts[i], eps, True).reshape(-1, 2)
                        m = list()
                        for x, y in pts:
                            pt = (int(x) + ox, int(y) + oy)
                            if not m or m[-1] != pt: m.append(pt)
                        while len(m) >= 3 and next(iter(m)) == m[-1]: m.pop()
                        if len(m) >= 3: dp.append((d & 1, tuple(m))); vt += len(m)
                    if vt <= vlim: break
        key = tuple(dp)
        if key not in uniq: uniq[key] = f"vf_{len(uniq)}"
        pr_raw, pr_lbl = raw, uniq[key]
        fl.append(pr_lbl)
    proc.wait()
    lines = list((f"vec_frame_count: dc.w {len(fl)}", "    even", "vec_frame_table:")) + list(f"    dc.l {l}" for l in fl)
    for dp, l in uniq.items():
        lines.append(f"{l}: dc.w $0eee")
        for op, p in dp: lines.append(f"    dc.w {op},{len(p)}," + ",".join(f"{x},{y}" for x, y in p))
        lines.append("    dc.w -1")
    if args.profile == "standard":
        gt = open(os.path.join(sd, "gfx_engine.i")).read().replace("move.l  draw_bpl2(pc),a0" + chr(10) + "    bsr.w   blit_clear_full" + chr(10), "")
        open(os.path.join(sd, "gfx_engine.i"), "w").write(gt)
    mt = open(os.path.join(sd, "main.s")).read().replace("move.l  pcm_played(pc),d0", "move.l  vbl_tick(pc),d0").replace("mulu.l  #10,d0", "; 50Hz").replace("divu.l  #5499,d0", "; 50Hz")
    open(os.path.join(sd, "main.s"), "w").write(mt)
    open(os.path.join(sd, "scene_data.i"), "w").write(chr(10).join(lines) + chr(10))
    exe = os.path.join(od, args.name)
    cpu = "-m68060" if args.profile == "060" else "-m68020"
    subprocess.run(("vasmm68k_mot", cpu, "-Fhunkexe", "-kick1hunks", "-nosym", "-I.", "main.s", "-o", exe), cwd=sd, check=True)
    os.chmod(exe, 0o755)
    fn_d = args.name.title().replace("_", "").replace("A1200", "A1200_AGA") + sfx
    pr = os.path.join(od, f"_tmp_{args.profile}")
    shutil.rmtree(pr, ignore_errors=True)
    pd = os.path.join(pr, fn_d)
    os.makedirs(pd, exist_ok=True)
    shutil.copy2(exe, os.path.join(pd, args.name))
    sl = open(os.path.join(sd, "whdload_slave.s")).read().replace("{DEMO_TITLE}", f"{args.title} [{args.profile}]").replace("{DEMO_CREDITS}", args.credits).replace("{EXE_NAME}", args.name)
    ss = os.path.join(pr, "slave.s")
    open(ss, "w").write(sl)
    subprocess.run(("vasmm68k_mot", cpu, "-Fhunkexe", "-nosym", ss, "-o", os.path.join(pd, f"{fn_d}.slave")), check=True)
    os.remove(ss)
    open(os.path.join(pr, f"{fn_d}.info"), "wb").write(mk_ico(4, "WHDLoad", (f"SLAVE={fn_d}.slave", "NoMMU")))
    open(os.path.join(pd, f"{fn_d}.info"), "wb").write(mk_ico(4, "WHDLoad", (f"SLAVE={fn_d}.slave", "NoMMU")))
    os.makedirs(os.path.join(pr, "S"), exist_ok=True)
    open(os.path.join(pr, "S/startup-sequence"), "w").write(f"cd {fn_d}" + chr(10) + args.name + chr(10))
    tag_out = "_THEA1200" if args.profile == "standard" else ""
    mk_lha(os.path.join(od, f"{fn_d}{tag_out}.lha"), pr)
    mk_zip(os.path.join(od, f"{fn_d}{tag_out}_FSUAE.zip"), pr)
    shutil.rmtree(pr); shutil.rmtree(sd, ignore_errors=True)
    print(f"GOTOWE [{args.profile}]: {od}/{fn_d}{tag_out}.lha")
if __name__ == "__main__": main()
