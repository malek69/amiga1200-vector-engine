import re
import os, shutil, subprocess, sys, zipfile, cv2, numpy as np
sys.path.insert(0, "tools")
import build_demo as bd
vid = os.path.expanduser("~/hi.mp4")
sd, od = "src", "releases"
os.makedirs(od, exist_ok=True)
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", vid, "-vn", "-af", "highpass=f=45,lowpass=f=4600,aresample=10020:resampler=soxr,volume=0.85", "-f", "s8", "-ac", "1", "-ar", "10020", f"{sd}/median_audio.raw"], check=True)
proc = subprocess.Popen(["ffmpeg", "-v", "error", "-i", vid, "-vf", r"crop=min(iw\,ih*4/3):ih,scale=624:496:flags=lanczos,fps=50", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
fb, uniq, fl, pr_raw, pr_lbl = 624 * 496 * 3, {}, list(), None, None
k3, k5 = np.ones((3, 3), dtype=np.uint8), np.ones((5, 5), dtype=np.uint8)
def snap_poly(pts, eps):
    ap = cv2.approxPolyDP(pts, eps, True).reshape(-1, 2)
    m = [[int(round(x * 0.5)) + 4, int(round(y * 0.5)) + 4] for x, y in ap]
    for i in range(len(m)):
        x0, y0 = m[i]
        x1, y1 = m[(i + 1) % len(m)]
        m[(i + 1) % len(m)] = [x0 if abs(x0 - x1) <= 1 else x1, y0 if abs(y0 - y1) <= 1 else y1]
    res = list()
    for pt in m:
        t = tuple(pt)
        if not res or res[-1] != t: res.append(t)
    while len(res) >= 3 and res[:1] == res[-1:]: res.pop()
    return tuple(res) if len(res) >= 3 else None
while True:
    raw = proc.stdout.read(fb)
    if len(raw) < fb: break
    if raw == pr_raw: fl.append(pr_lbl); continue
    r, g, b = cv2.split(np.frombuffer(raw, dtype=np.uint8).reshape((496, 624, 3)).astype(np.int16))
    gray = ((r * 30 + g * 59 + b * 11) // 100).astype(np.uint8)
    red_m = cv2.dilate(((r > 150) & ((r - g) > 55)).astype(np.uint8) * 255, k3, iterations=1)
    blk_m = cv2.bitwise_and(cv2.bitwise_or(cv2.dilate(cv2.Canny(gray, 28, 80), k3, iterations=1), ((gray < 120).astype(np.uint8) * 255)), cv2.bitwise_not(red_m))
    layers = ((2, red_m), (0, blk_m))
    dp = list()
    for op_base, mask in layers:
        if not np.any(mask): continue
        cnts, hier = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if hier is None: continue
        hr = hier.reshape(-1, 4)
        items = list()
        for i in range(len(cnts)):
            d, par = 0, int(hr.item(i, 3))
            while par != -1: d += 1; par = int(hr.item(par, 3))
            items.append((d, i))
        items.sort()
        for eps in (1.1, 1.6, 2.2):
            cur, v_tot = list(), 0
            for d, i in items:
                if op_base == 2 and (d % 2): continue
                if cv2.contourArea(cnts[i]) < (2.0 if (d % 2) else 3.5): continue
                poly = snap_poly(cnts[i], eps)
                if poly: cur.append(((4 if (d % 2) else 3) if op_base == 3 else (2 if op_base == 2 else (d % 2)), poly)); v_tot += len(poly)
            if v_tot <= 360 or eps == 2.2: dp.extend(cur); break
    key = tuple(dp)
    if key not in uniq: uniq[key] = f"vf_{len(uniq)}"
    pr_raw, pr_lbl = raw, uniq[key]
    fl.append(pr_lbl)
    if len(fl) % 1000 == 0: print(f"  Klatka {len(fl)}...", flush=True)
proc.wait()
lines = [f"vec_frame_count: dc.w {len(fl)}", "    even", "vec_frame_table:"] + [f"    dc.l {l}" for l in fl]
for dp, l in uniq.items():
    lines += [f"{l}:", "    dc.w $0111"]
    for op, p in dp: lines.append(f"    dc.w {op},{len(p)}," + ",".join(f"{x},{y}" for x, y in p))
    lines.append("    dc.w -1")
open(f"{sd}/scene_data.i", "w").write("\n".join(lines) + "\n")
ms_t = open(f"{sd}/main.s").read().replace("move.l  pcm_played(pc),d0", "move.l  vbl_tick(pc),d0").replace("mulu.l  #10,d0", "; 50Hz").replace("divu.l  #6599,d0", "; 50Hz")
open(f"{sd}/main.s", "w").write(ms_t)
exe = os.path.abspath(f"{od}/MEDIAN_A1200")
subprocess.run(["vasmm68k_mot", "-m68020", "-Fhunkexe", "-kick1hunks", "-nosym", "-I.", "main.s", "-o", exe], cwd=sd, check=True)
os.chmod(exe, 0o755)
sz = os.path.getsize(exe)
em = ((sz + 0x088000 + 0xFFFF) & ~0xFFFF)
lo = em - sz - 256
pr = f"{od}/_tmp_med"
shutil.rmtree(pr, ignore_errors=True)
os.makedirs(f"{pr}/MedianA1200", exist_ok=True)
shutil.copy2(exe, f"{pr}/MedianA1200/MEDIAN_A1200")
sl = open(f"{sd}/whdload_slave.s").read().replace("{EXP_MEM}", f"{em:08x}").replace("{LOAD_OFF}", f"{lo:08x}").replace("{DEMO_TITLE}", "Median A1200 [Retail]").replace("{DEMO_CREDITS}", "Orig: Umlaut Design (2016) | Port: malek69").replace("{EXE_NAME}", "MEDIAN_A1200")
open(f"{pr}/slave.s", "w").write(sl)
subprocess.run(["vasmm68k_mot", "-m68020", "-Fhunkexe", "-nosym", f"{pr}/slave.s", "-o", f"{pr}/MedianA1200/MedianA1200.slave"], check=True)
os.remove(f"{pr}/slave.s")
open(f"{pr}/MedianA1200.info", "wb").write(bd.mk_ico(2))
open(f"{pr}/MedianA1200/MedianA1200.info", "wb").write(bd.mk_ico(4, "WHDLoad", ["SLAVE=MedianA1200.slave", "NoMMU"]))
bd.mk_lha(f"{od}/MedianA1200_THEA1200_Retail.lha", pr)
shutil.rmtree(pr)
with zipfile.ZipFile(f"{od}/ud_mdn_a1200_retail.zip", "w", zipfile.ZIP_DEFLATED) as zf:
    zf.write(exe, "MEDIAN_A1200")
    zf.write("README.md", "README.md")
print(f"GOTOWE: {exe} ({sz/1048576:.2f} MB) | ExpMem = {em/1048576:.2f} MB (50.00 FPS VBL-locked)!", flush=True)
