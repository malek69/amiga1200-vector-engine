import os, re, shutil, subprocess, sys, zipfile, cv2, numpy as np
sys.path.insert(0, "tools")
import build_demo as bd

vid = os.path.expanduser("~/hi.mp4")
sd, od = "src", "releases/v1.1.0"
os.makedirs(od, exist_ok=True)
ap_txt = open(f"{sd}/audio_player.i").read()
open(f"{sd}/audio_player.i", "w").write(re.sub(r"#[0-9]+(?=,AUD[0-3]PER)", "#215", ap_txt))
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", vid, "-vn", "-af", "highpass=f=45,lowpass=f=7200,alimiter=limit=0.85,aresample=16497:resampler=soxr,volume=0.80", "-f", "s8", "-ac", "1", "-ar", "16497", f"{sd}/median_audio.raw"], check=True)
proc = subprocess.Popen(["ffmpeg", "-v", "error", "-i", vid, "-vf", r"crop=min(iw\,ih*4/3):ih,scale=624:496:flags=lanczos,fps=50", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
fb, uniq, fl, pr_raw, pr_lbl = 624 * 496 * 3, {}, list(), None, None
k3 = np.ones((3, 3), dtype=np.uint8)

def snap_poly(pts, eps):
    ap = cv2.approxPolyDP(pts, eps, True).reshape(-1, 2)
    m = list()
    for (x, y) in ap:
        pt = (int(round(x * 0.5)) + 4, int(round(y * 0.5)) + 4)
        if not m or m[-1] != pt: m.append(pt)
    while len(m) >= 3 and m[0] == m[-1]: m.pop()
    return tuple(m)

while True:
    raw = proc.stdout.read(fb)
    if len(raw) < fb: break
    if raw == pr_raw: fl.append(pr_lbl); continue
    rgb = np.frombuffer(raw, dtype=np.uint8).reshape((496, 624, 3))
    r, g, b = rgb[:, :, 0].astype(np.int16), rgb[:, :, 1].astype(np.int16), rgb[:, :, 2].astype(np.int16)
    red_m = cv2.morphologyEx(((r > 130) & (r - g > 55) & (r - b > 55)).astype(np.uint8), cv2.MORPH_CLOSE, k3)
    gray = (0.299 * r + 0.587 * g + 0.114 * b).astype(np.uint8)
    blk_m = ((gray < 115) & (red_m == 0)).astype(np.uint8)
    dp = list()
    if np.any(blk_m):
        cnts, hr = cv2.findContours(blk_m, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
        if hr is not None:
            items = list()
            for i in range(len(cnts)):
                if cv2.contourArea(cnts[i]) < 14.0: continue
                d, par = 0, int(hr.item(0, i, 3))
                while par != -1: d += 1; par = int(hr.item(0, par, 3))
                items.append((d, i))
            items.sort()
            for eps in (1.7, 2.3, 3.1):
                dp, v_tot = list(), 0
                for d, i in items:
                    m = snap_poly(cnts[i], eps)
                    if len(m) >= 3:
                        dp.append((d & 1, m))
                        v_tot += len(m)
                if v_tot <= 190 or eps == 3.1: break
    if np.any(red_m):
        rcnts, _ = cv2.findContours(red_m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        for c in rcnts:
            if cv2.contourArea(c) < 20.0: continue
            (cx, cy), rad = cv2.minEnclosingCircle(c)
            cx_a, cy_a, rx_a, ry_a = cx * 0.5 + 4.0, cy * 0.5 + 4.0, rad * 0.5, rad * 0.5
            pts32 = list()
            for k in range(32):
                ang = (2.0 * np.pi * k) / 32.0
                pt = (max(0, min(319, int(round(cx_a + rx_a * np.cos(ang))))), max(0, min(255, int(round(cy_a + ry_a * np.sin(ang))))))
                if not pts32 or pts32[-1] != pt: pts32.append(pt)
            while len(pts32) >= 3 and pts32[0] == pts32[-1]: pts32.pop()
            if len(pts32) >= 3: dp.append((2, tuple(pts32)))
    key = tuple(dp)
    if key not in uniq: uniq[key] = f"vf_{len(uniq)}"
    pr_raw, pr_lbl = raw, uniq[key]
    fl.append(pr_lbl)
    if len(fl) % 1000 == 0: print(f"  [Median 320x256] Klatka {len(fl)}...", flush=True)
proc.wait()

lines = [f"vec_frame_count: dc.w {len(fl)}", "    even", "vec_frame_table:"] + [f"    dc.l {l}" for l in fl]
for dp, l in uniq.items():
    lines.append(f"{l}: dc.w $0eee")
    for op, p in dp: lines.append(f"    dc.w {op},{len(p)}," + ",".join(f"{x},{y}" for x, y in p))
    lines.append("    dc.w -1")
open(f"{sd}/scene_data.i", "w").write(chr(10).join(lines) + chr(10))

exe = os.path.abspath("releases/MEDIAN_A1200")
subprocess.run(["vasmm68k_mot", "-m68020", "-Fhunkexe", "-kick1hunks", "-nosym", "-I.", "main.s", "-o", exe], cwd=sd, check=True)
os.chmod(exe, 0o755)
sz = os.path.getsize(exe)
em = 0x00680000
lo = em - sz - 256
pr = os.path.join(od, "_tmp_med")
shutil.rmtree(pr, ignore_errors=True)
pd = os.path.join(pr, "MedianA1200_AGA")
os.makedirs(pd, exist_ok=True)
shutil.copy2(exe, os.path.join(pd, "MEDIAN_A1200"))
sl = open(f"{sd}/whdload_slave.s").read().replace("{EXP_MEM}", f"{em:08x}").replace("{LOAD_OFF}", f"{lo:08x}").replace("{DEMO_TITLE}", "Median A1200 v1.1.0 [50FPS + Blitter AA]").replace("{DEMO_CREDITS}", "Umlaut Design | Port: malek69").replace("{EXE_NAME}", "MEDIAN_A1200")
ss = os.path.join(pr, "slave.s")
open(ss, "w").write(sl)
subprocess.run(["vasmm68k_mot", "-m68020", "-Fhunkexe", "-nosym", ss, "-o", os.path.join(pd, "MedianA1200_AGA.slave")], check=True)
os.remove(ss)
open(f"{pr}/MedianA1200_AGA.info", "wb").write(bd.mk_ico(4, "WHDLoad", ["SLAVE=MedianA1200_AGA.slave", "NoMMU"]))
open(f"{pd}/MedianA1200_AGA.info", "wb").write(bd.mk_ico(4, "WHDLoad", ["SLAVE=MedianA1200_AGA.slave", "NoMMU"]))
os.makedirs(f"{pr}/S", exist_ok=True)
open(f"{pr}/S/startup-sequence", "w").write("cd MedianA1200_AGA" + chr(10) + "MEDIAN_A1200" + chr(10))
bd.mk_lha(f"{od}/MedianA1200_AGA_THEA1200.lha", pr)
bd.mk_zip(f"{od}/MedianA1200_AGA_THEA1200_FSUAE.zip", pr)
shutil.rmtree(pr)
print(f"GOTOWE Median v1.1.0: {sz/1048576:.2f} MB (320x256 @ 50.00 FPS + Blitter AA)")
