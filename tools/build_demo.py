import argparse, math, os, re, shutil, struct, subprocess, cv2, numpy as np
def mk_ico(it, dt=None, tt=None):
    ih = struct.pack(">hhhhhIbbI", 0, 0, 48, 24, 1, 0, 1, 0, 0)
    pl = bytearray(144)
    dh = bytearray(78)
    struct.pack_into(">HHhhhhHBIIiiI", dh, 0, 0xe310, 1, 20, 20, 48, 24, 0, it, 1 if dt else 0, 1 if tt else 0, -2147483648, -2147483648, 4096)
    out = bytearray(dh) + (bytearray(56) if it == 2 else bytearray()) + ih + pl
    bs = lambda s: struct.pack(">I", len(s)+1) + s.encode("ascii") + bytes([0])
    if dt: out += bs(dt)
    if tt:
        out += struct.pack(">I", (len(tt)+1)*4)
        for t in tt: out += bs(t)
    return bytes(out)
def mk_lha(lp, rf):
    def crc(d):
        c = 0
        for b in d:
            c ^= b
            for _ in range(8): c = (c >> 1) ^ 0xa001 if (c & 1) else (c >> 1)
        return c & 0xffff
    ar = bytearray()
    for dp, _, fns in os.walk(rf):
        rd = os.path.relpath(dp, rf)
        for fn in sorted(fns):
            p = open(os.path.join(dp, fn), "rb").read()
            fb = fn.encode("ascii")
            et = (bytearray([2]) + bytes([255]).join(x.encode("ascii") for x in rd.split(os.sep)) + bytes([255, 0, 0])) if rd != "." else bytearray()
            hb = bytearray(b"-lh0-") + struct.pack("<IIIB", len(et)+len(p), len(p), 0x56750000, 0x20) + bytes([1, len(fb)]) + fb + struct.pack("<HBH", crc(p), 65, len(et))
            ar += bytes([len(hb), sum(hb)&0xff]) + hb + et + p
    open(lp, "wb").write(ar + bytes([0]))
def get_hunk_layout(ep):
    d = open(ep, "rb").read()
    n, = struct.unpack_from(">I", d, 8)
    fb = 0
    for i in range(n):
        sf, = struct.unpack_from(">I", d, 20 + i * 4)
        if not (sf & 0x40000000): fb += ((sf & 0x3FFFFFFF) * 4 + 16) & ~0xF
    return fb
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--audio", default=None)
    ap.add_argument("--name", default="DEMO_A1200")
    ap.add_argument("--title", default="Amiga 1200 Vector Demo")
    ap.add_argument("--credits", default="Port: malek69")
    ap.add_argument("--fps", type=int, default=16)
    ap.add_argument("--threshold", type=int, default=120)
    ap.add_argument("--crop-43", action="store_true")
    ap.add_argument("--thin-lines", action="store_true")
    ap.add_argument("--copper-bg", action="store_true")
    args = ap.parse_args()
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sd, od = os.path.join(repo, "src"), os.path.join(repo, "releases")
    os.makedirs(od, exist_ok=True)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", args.video], capture_output=True, text=True, check=True).stdout.strip() or 180)
    hz = max(8000, min(16497, int(1320000 / max(1.0, dur))))
    per = round(3546895 / hz)
    hz_r = 3546895.0 / per
    spf = max(1, round(hz_r / args.fps))
    print(f"[1/4] Audio: {hz_r:.1f} Hz (AUD0PER={per}) | Video: {args.fps} FPS ({spf} spf)", flush=True)
    ap_p = os.path.join(sd, "audio_player.i"); ap_t = open(ap_p).read(); open(ap_p, "w").write(re.sub(r"#\d+(?=,AUD)", f"#{per}", ap_t))
    gfx_p = os.path.join(sd, "gfx_engine.i")
    if args.fps >= 45:
        gt = open(gfx_p).read().replace("move.l  draw_bpl2(pc),a0" + chr(10) + "    bsr.w   blit_clear_full" + chr(10), "")
        open(gfx_p, "w").write(gt)
    ms_p = os.path.join(sd, "main.s")
    ms_t = open(ms_p).read().replace("move.l  pcm_played(pc),d0", "move.l  vbl_tick(pc),d0").replace("mulu.l  #10,d0", "; 50Hz").replace("divu.l  #5499,d0", "; 50Hz").replace("    ; skip AA", "    ; skip AA for 50FPS speed")
    open(ms_p, "w").write(ms_t)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", args.audio or args.video, "-vn", "-af", f"lowpass=f=3400,alimiter=limit=0.88,aresample={int(round(hz_r))}:resampler=soxr,volume=0.68", "-f", "s8", "-ac", "1", "-ar", str(int(round(hz_r))), os.path.join(sd, "median_audio.raw")], check=True)
    w_s, h_s = [int(x) for x in subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", args.video], capture_output=True, text=True, check=True).stdout.strip().split(",")]
    x0, y0, cw, ch = 0, 0, w_s, h_s
    if args.crop_43 and (w_s / max(1, h_s)) > 1.5:
        cw = int(round(h_s * 1.28))
        x0 = (w_s - cw) // 2
    sc = min(312.0 / 320.0, 248.0 / 240.0) if args.fps >= 45 else min(312.0 / cw, 248.0 / ch)
    ox, oy = ((320.0 - 640.0 * sc) * 0.5, (256.0 - 480.0 * sc) * 0.5) if args.fps >= 45 else ((320.0 - cw * sc) * 0.5, (256.0 - ch * sc) * 0.5)
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-i", args.video, "-vf", f"crop={cw}:{ch}:{x0}:{y0},scale=312:248:flags=area,fps={args.fps}", "-f", "rawvideo", "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
    fb, uniq, fl, pr_raw, pr_lbl = 312 * 248, {}, list(), None, None
    k3 = np.ones((3, 3), dtype=np.uint8)
    while True:
        raw = proc.stdout.read(fb)
        if len(raw) < fb: break
        if raw == pr_raw: fl.append(pr_lbl); continue
        g = np.frombuffer(raw, dtype=np.uint8).reshape((248, 312))
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
                for eps in (1.05, 1.55, 2.2, 3.0):
                    dp, v_tot = list(), 0
                    for d, i in items:
                        if cv2.contourArea(cnts[i]) < (22.0 if (d & 1) else 10.0): continue
                        pts = cv2.approxPolyDP(cnts[i], eps, True).reshape(-1, 2)
                        m = list()
                        for (x, y) in pts:
                            pt = (int(x) + 4, int(y) + 4)
                            if not m or m[-1] != pt: m.append(pt)
                        while len(m) >= 3 and m[0] == m[-1]: m.pop()
                        if len(m) >= 3:
                            dp.append((d & 1, tuple(m)))
                            v_tot += len(m)
                    if v_tot <= 550: break
        key = tuple(dp)
        if key not in uniq: uniq[key] = f"vf_{len(uniq)}"
        pr_raw, pr_lbl = raw, uniq[key]
        fl.append(pr_lbl)
    proc.wait()
    lines = [f"vec_frame_count: dc.w {len(fl)}", "    even", "vec_frame_table:"] + [f"    dc.l {l}" for l in fl]
    for dp, l in uniq.items():
        lines += [f"{l}:", "    dc.w $0111"]
        for op, p in dp: lines.append(f"    dc.w {op},{len(p)}," + ",".join(f"{x},{y}" for x, y in p))
        lines.append("    dc.w -1")
    open(os.path.join(sd, "scene_data.i"), "w").write(chr(10).join(lines) + chr(10))
    exe_out = os.path.join(od, args.name)
    subprocess.run(["vasmm68k_mot", "-m68020", "-Fhunkexe", "-kick1hunks", "-nosym", "-I.", "main.s", "-o", exe_out], cwd=sd, check=True)
    os.chmod(exe_out, 0o755)
    sz = os.path.getsize(exe_out)
    em = ((sz + 0x0C0000 + 0xFFFF) & ~0xFFFF)
    lo = em - sz - 256
    pr = os.path.join(od, "_tmp_pkg")
    shutil.rmtree(pr, ignore_errors=True)
    fn_d = args.name.title().replace("_", "")
    pd = os.path.join(pr, fn_d)
    os.makedirs(pd, exist_ok=True)
    shutil.copy2(exe_out, os.path.join(pd, args.name))
    sl = open(os.path.join(sd, "whdload_slave.s")).read().replace("{EXP_MEM}", f"{em:08x}").replace("{LOAD_OFF}", f"{lo:08x}").replace("{DEMO_TITLE}", args.title).replace("{DEMO_CREDITS}", args.credits).replace("{EXE_NAME}", args.name)
    ss = os.path.join(pr, "slave.s")
    open(ss, "w").write(sl)
    subprocess.run(["vasmm68k_mot", "-m68020", "-Fhunkexe", "-nosym", ss, "-o", os.path.join(pd, f"{fn_d}.slave")], check=True)
    os.remove(ss)
    open(os.path.join(pr, f"{fn_d}.info"), "wb").write(mk_ico(2))
    open(os.path.join(pd, f"{fn_d}.info"), "wb").write(mk_ico(4, "WHDLoad", [f"SLAVE={fn_d}.slave", "NoMMU"]))
    lha_out = os.path.join(od, f"{fn_d}_THEA1200.lha")
    mk_lha(lha_out, pr)
    shutil.rmtree(pr)
    print(f"ExpMem: {em/1048576:.2f} MB | GOTOWE: {exe_out} ({sz/1048576:.2f} MB) oraz {lha_out}", flush=True)
    exe_out = os.path.join(od, args.name)
    subprocess.run(["vasmm68k_mot", "-m68020", "-Fhunkexe", "-kick1hunks", "-nosym", "-I.", "main.s", "-o", exe_out], cwd=sd, check=True)
    os.chmod(exe_out, 0o755)
    sz = os.path.getsize(exe_out)
    em = ((sz + 0x0C0000 + 0xFFFF) & ~0xFFFF)
    lo = em - sz - 256
    pr = os.path.join(od, "_tmp_pkg")
    shutil.rmtree(pr, ignore_errors=True)
    fn_d = args.name.title().replace("_", "")
    pd = os.path.join(pr, fn_d)
    os.makedirs(pd, exist_ok=True)
    shutil.copy2(exe_out, os.path.join(pd, args.name))
    sl = open(os.path.join(sd, "whdload_slave.s")).read().replace("{EXP_MEM}", f"{em:08x}").replace("{LOAD_OFF}", f"{lo:08x}").replace("{DEMO_TITLE}", args.title).replace("{DEMO_CREDITS}", args.credits).replace("{EXE_NAME}", args.name)
    ss = os.path.join(pr, "slave.s")
    open(ss, "w").write(sl)
    subprocess.run(["vasmm68k_mot", "-m68020", "-Fhunkexe", "-nosym", ss, "-o", os.path.join(pd, f"{fn_d}.slave")], check=True)
    os.remove(ss)
    open(os.path.join(pr, f"{fn_d}.info"), "wb").write(mk_ico(2))
    open(os.path.join(pd, f"{fn_d}.info"), "wb").write(mk_ico(4, "WHDLoad", [f"SLAVE={fn_d}.slave", "NoMMU"]))
    lha_out = os.path.join(od, f"{fn_d}_THEA1200.lha")
    mk_lha(lha_out, pr)
    shutil.rmtree(pr)
    print(f"ExpMem: {em/1048576:.2f} MB | GOTOWE: {exe_out} ({sz/1048576:.2f} MB) oraz {lha_out}", flush=True)
if __name__ == "__main__": main()
