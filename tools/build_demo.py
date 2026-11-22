#!/usr/bin/env python3
import argparse, math, os, re, shutil, struct, subprocess, cv2, numpy as np

def mk_ico(it, dt=None, tt=None):
    ih = struct.pack(">hhhhhIbbI", 0, 0, 48, 24, 1, 0, 1, 0, 0)
    pl = bytearray(144)
    for y in range(24):
        for xb in range(6):
            if y in (0, 1, 22, 23) or xb in (0, 5): pl[y*6+xb] = 0xff
            elif 6 <= y <= 17 and 1 <= xb <= 4: pl[y*6+xb] = 0x3c
    dh = bytearray(78)
    struct.pack_into(">HHhhhhHBIIiiI", dh, 0, 0xe310, 1, 20, 20, 48, 24, 0, it, 1 if dt else 0, 1 if tt else 0, -2147483648, -2147483648, 4096)
    out = bytearray(dh) + (bytearray(56) if it == 2 else bytearray()) + ih + pl
    bs = lambda s: struct.pack(">I", len(s)+1) + s.encode("ascii") + b"\x00"
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
            et = (bytearray([0x02]) + b"\xff".join(x.encode("ascii") for x in rd.split(os.sep)) + b"\xff\x00\x00") if rd != "." else bytearray()
            hb = bytearray(b"-lh0-") + struct.pack("<IIIB", len(et)+len(p), len(p), 0x56750000, 0x20) + b"\x01" + bytes([len(fb)]) + fb + struct.pack("<HBH", crc(p), 65, len(et))
            ar += bytes([len(hb), sum(hb)&0xff]) + hb + et + p
    open(lp, "wb").write(ar + b"\x00")
def get_hunk_layout(exe_path):
    data = open(exe_path, "rb").read()
    pos = 8
    count = struct.unpack(">I", data[pos:pos+4])[0]
    pos += 12
    fast_bytes = 0
    for _ in range(count):
        sz_flags = struct.unpack(">I", data[pos:pos+4])[0]
        pos += 4
        b_len = ((sz_flags & 0x3FFFFFFF) * 4 + 16) & ~0xF
        if not (sz_flags & 0x40000000):
            fast_bytes += b_len
    return fast_bytes

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--audio", default=None)
    ap.add_argument("--name", default="DEMO_A1200")
    ap.add_argument("--title", default="Amiga 1200 Vector Demo")
    ap.add_argument("--credits", default="Port: malek69 & Amiga1200-VectorStream-Engine")
    ap.add_argument("--fps", type=int, default=18)
    ap.add_argument("--threshold", type=int, default=120)
    ap.add_argument("--crop-43", action="store_true")
    ap.add_argument("--thin-lines", action="store_true")
    args = ap.parse_args()
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sd, od = os.path.join(repo, "src"), os.path.join(repo, "releases")
    os.makedirs(od, exist_ok=True)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", args.video], capture_output=True, text=True, check=True).stdout.strip() or 180)
    hz = max(8000, min(16497, int(1850000 / max(1.0, dur))))
    per = round(3546895 / hz)
    hz_real = 3546895.0 / per
    spf = max(1, round(hz_real / args.fps))
    print(f"[1/4] Audio: {hz_real:.1f} Hz (AUD0PER={per}) | Video: {args.fps} FPS ({spf} probek/klatke)", flush=True)
    ap_p = os.path.join(sd, "audio_player.i")
    open(ap_p, "w").write(re.sub(r"move\.w\s+#\d+,AUD(\d)PER", rf"move.w  #{per},AUD\1PER", open(ap_p).read()))
    ms_p = os.path.join(sd, "main.s")
    open(ms_p, "w").write(re.sub(r"cmp\.l\s+#\d+,d0", f"cmp.l   #{spf},d0", open(ms_p).read(), count=1))
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", args.audio or args.video, "-vn", "-af", f"aresample={int(round(hz_real))}:resampler=soxr,bass=g=4:f=65:w=0.6,treble=g=3:f=3600:w=0.7,alimiter=limit=0.96:attack=3:release=40", "-f", "s8", "-ac", "1", "-ar", str(int(round(hz_real))), os.path.join(sd, "median_audio.raw")], check=True)
    w_s, h_s = [int(x) for x in subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", args.video], capture_output=True, text=True, check=True).stdout.strip().split(",")]
    x0, y0, cw, ch = 0, 0, w_s, h_s
    if args.crop_43 and (w_s / max(1, h_s)) > 1.5:
        cw = int(round(h_s * 4.0 / 3.0))
        x0 = (w_s - cw) // 2
    sc = min(312.0 / cw, 248.0 / ch)
    ox, oy = (320.0 - cw * sc) * 0.5, (256.0 - ch * sc) * 0.5
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-i", args.video, "-vf", f"crop={cw}:{ch}:{x0}:{y0},fps={args.fps}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    fb, uniq, fl, pr_raw, pr_lbl, idx = cw * ch * 3, dict(), list(), None, None, 0
    k3 = np.ones((3, 3), dtype=np.uint8)
    c_ang = [(math.cos(2 * math.pi * k / 32), math.sin(2 * math.pi * k / 32)) for k in range(32)]
    def mpoly(pts, tol=0.35):
        m = list()
        for (x, y) in pts:
            p = (int(max(3, min(316, round(ox + x * sc)))), int(max(3, min(248, round(oy + y * sc)))))
            if not m or m[-1] != p: m.append(p)
        while len(m) >= 3 and m[0] == m[-1]: m.pop()
        ch_f = True
        while ch_f and len(m) > 3:
            ch_f, cl, n = False, list(), len(m)
            for i in range(n):
                p0, p1, p2 = m[(i - 1) % n], m[i], m[(i + 1) % n]
                if p1 == p0 or p1 == p2: ch_f = True; continue
                dx, dy = p2[0] - p0[0], p2[1] - p0[1]
                sl = (dx * dx + dy * dy) ** 0.5
                if sl < 1.0 or abs(dy * p1[0] - dx * p1[1] + p2[0] * p0[1] - p2[1] * p0[0]) / sl < tol: ch_f = True; continue
                cl.append(p1)
            m = cl
            while len(m) >= 3 and m[0] == m[-1]: m.pop()
        return tuple(m) if len(m) >= 3 else None
    while True:
        raw = proc.stdout.read(fb)
        if len(raw) < fb: break
        if raw == pr_raw: fl.append(pr_lbl); idx += 1; continue
        im = np.frombuffer(raw, dtype=np.uint8).reshape((ch, cw, 3))
        r, g, b = im[:, :, 0].astype(np.int16), im[:, :, 1].astype(np.int16), im[:, :, 2].astype(np.int16)
        rm = ((r > 135) & ((r - g) > 40) & ((r - b) > 40)).astype(np.uint8) * 255
        lum = cv2.medianBlur(((r * 30 + g * 59 + b * 11) // 100).astype(np.uint8), 3)
        any_red = ((r - g) > 20) | ((r - b) > 20)
        db = (lum < args.threshold) & (~any_red)
        if np.mean(db) > 0.65: db = (~db) & (~any_red)
        c01 = (min(13, max(1, int(lum[db].mean()) >> 4)) * 0x111) if np.any(db) else 0x0111
        rp, dp = list(), list()
        if np.any(rm):
            for c in cv2.findContours(rm, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[0]:
                a = cv2.contourArea(c)
                if a < (cw * ch) * 0.0001: continue
                pe = cv2.arcLength(c, True)
                if (4 * math.pi * a / (pe * pe) if pe > 0 else 0) > 0.89:
                    (cx, cy), rad = cv2.minEnclosingCircle(c)
                    poly = mpoly([(cx + rad * ca, cy + rad * sa) for ca, sa in c_ang], 0.1)
                else: poly = mpoly(cv2.approxPolyDP(c, 2.2, True).reshape(-1, 2), 0.25)
                if poly: rp.append((2, poly))
        if np.any(db):
            dm = db.astype(np.uint8) * 255
            if args.thin_lines:
                th = cv2.erode(dm, k3, iterations=1)
                dm = cv2.bitwise_or(th, cv2.subtract(dm, cv2.dilate(th, k3, iterations=1)))
            cnts, hier = cv2.findContours(dm, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            if hier is not None:
                hr = hier.reshape(-1, 4)
                deps = {i: 0 for i in range(len(cnts))}
                for i in range(len(cnts)):
                    p = int(hr.item(i, 3))
                    while p != -1: deps[i] += 1; p = int(hr.item(p, 3))
                for i in sorted(range(len(cnts)), key=lambda k: deps[k]):
                    d = deps[i]
                    if cv2.contourArea(cnts[i]) < (cw * ch) * (0.00004 if (d & 1) else 0.00014): continue
                    pts = cv2.approxPolyDP(cnts[i], 2.2, True).reshape(-1, 2)
                    if len(pts) > 48: pts = cv2.approxPolyDP(cnts[i], 3.0, True).reshape(-1, 2)
                    poly = mpoly(pts, 0.35)
                    if poly: dp.append((d & 1, poly))
        key = (c01, tuple(rp), tuple(dp))
        if key not in uniq: uniq[key] = f"vf_{len(uniq)}"
        pr_raw, pr_lbl = raw, uniq[key]
        fl.append(pr_lbl); idx += 1
    proc.wait()
    lines = [f"vec_frame_count: dc.w {len(fl)}", "    even", "vec_frame_table:"] + [f"    dc.l {l}" for l in fl]
    for (c01, rp, dp), l in uniq.items():
        lines += [f"{l}:", f"    dc.w ${c01:04x}"]
        for op, p in rp + dp: lines.append(f"    dc.w {op},{len(p)}," + ",".join(f"{x},{y}" for x, y in p))
        lines.append("    dc.w -1")
    open(os.path.join(sd, "scene_data.i"), "w").write("\n".join(lines) + "\n")
    exe_out = os.path.join(od, args.name)
    subprocess.run(["vasmm68k_mot", "-m68020", "-Fhunkexe", "-kick1hunks", "-nosym", "-I.", "main.s", "-o", exe_out], cwd=sd, check=True)
    os.chmod(exe_out, 0o755)
    sz = os.path.getsize(exe_out)
    fb_need = get_hunk_layout(exe_out)
    lo = (fb_need + 0x1000 + 0xF) & ~0xF
    em = ((lo + sz + 0x4000 + 0xFFFF) & ~0xFFFF)
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
    open(os.path.join(pd, f"{fn_d}.info"), "wb").write(mk_ico(4, "WHDLoad", [f"SLAVE={fn_d}.slave"]))
    lha_out = os.path.join(od, f"{fn_d}_THEA1200.lha")
    mk_lha(lha_out, pr)
    shutil.rmtree(pr)
    print(f"GOTOWE: {exe_out} ({sz/1048576:.2f} MB) oraz {lha_out}", flush=True)
if __name__ == "__main__": main()
