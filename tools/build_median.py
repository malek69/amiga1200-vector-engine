import argparse, os, re, shutil, subprocess, sys, cv2, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_demo as bd, profile_patch as pp
ap = argparse.ArgumentParser()
ap.add_argument("--profile", choices=("standard", "thea1200", "060"), default="standard")
args = ap.parse_args()
vid = "demos/median/hi.mp4"
od = "releases/v1.1.1"
os.makedirs(od, exist_ok=True)
sd = "/tmp/_vec_median_build"
shutil.rmtree(sd, ignore_errors=True)
shutil.copytree("src", sd)
hz_t, vw, vh, ox, oy, vlim, sfx = pp.apply_profile(sd, args.profile, 16497)
sx, sy = vw / 624.0, vh / 496.0
ap_txt = open(f"{sd}/audio_player.i").read()
open(f"{sd}/audio_player.i", "w").write(re.sub(r"#[0-9]+(?=,AUD[0-3]PER)", "#215", ap_txt))
subprocess.run(("ffmpeg", "-y", "-v", "error", "-i", vid, "-vn", "-af", "highpass=f=45,lowpass=f=7200,alimiter=limit=0.85,aresample=16497:resampler=soxr,volume=0.80", "-f", "s8", "-ac", "1", "-ar", "16497", f"{sd}/median_audio.raw"), check=True)
proc = subprocess.Popen(("ffmpeg", "-v", "error", "-i", vid, "-vf", r"crop=min(iw\,ih*4/3):ih,scale=624:496:flags=lanczos,fps=50", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"), stdout=subprocess.PIPE)
fb, uniq, fl, pr_raw, pr_lbl = 624 * 496 * 3, dict(), list(), None, None
k3 = np.ones((3, 3), dtype=np.uint8)
def snap_poly(pts, eps):
    ap_p = cv2.approxPolyDP(pts, eps, True).reshape(-1, 2)
    m = list()
    for x, y in ap_p:
        pt = (int(round(x * sx)) + ox, int(round(y * sy)) + oy)
        if not m or m[-1] != pt: m.append(pt)
    while len(m) >= 3 and next(iter(m)) == m[-1]: m.pop()
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
                dp, vt = list(), 0
                for d, i in items:
                    m = snap_poly(cnts[i], eps)
                    if len(m) >= 3: dp.append((d & 1, m)); vt += len(m)
                if vt <= (vlim // 2) or eps == 3.1: break
    if np.any(red_m):
        rcnts, rhr = cv2.findContours(red_m, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
        if rhr is not None:
            ritems = list()
            for i in range(len(rcnts)):
                if cv2.contourArea(rcnts[i]) < 16.0: continue
                d, par = 0, int(rhr.item(0, i, 3))
                while par != -1: d += 1; par = int(rhr.item(0, par, 3))
                ritems.append((d, i))
            ritems.sort()
            for d, i in ritems:
                m = snap_poly(rcnts[i], 1.4)
                if len(m) >= 3: dp.append((2 + (d & 1), m))
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
open(f"{sd}/scene_data.i", "w").write(chr(10).join(lines) + chr(10))
exe = os.path.abspath(f"{od}/MEDIAN_A1200")
cpu = "-m68060" if args.profile == "060" else "-m68020"
defs = ["-DM68060"] if args.profile == "060" else list()
subprocess.run(("vasmm68k_mot", cpu, *defs, "-Fhunkexe", "-kick1hunks", "-nosym", "-I.", "main.s", "-o", exe), cwd=sd, check=True)
os.chmod(exe, 0o755)
fn_d = "MedianA1200_AGA" + sfx
pr = os.path.join(od, f"_tmp_med_{args.profile}")
shutil.rmtree(pr, ignore_errors=True)
pd = os.path.join(pr, fn_d)
os.makedirs(pd, exist_ok=True)
shutil.copy2(exe, os.path.join(pd, "MEDIAN_A1200"))
sl = open(f"{sd}/whdload_slave.s").read().replace("{DEMO_TITLE}", f"Median A1200 v1.1.1 [{args.profile}]").replace("{DEMO_CREDITS}", "Umlaut Design | Port: malek69").replace("{EXE_NAME}", "MEDIAN_A1200")
ss = os.path.join(pr, "slave.s")
open(ss, "w").write(sl)
subprocess.run(("vasmm68k_mot", cpu, *defs, "-Fhunkexe", "-nosym", ss, "-o", os.path.join(pd, f"{fn_d}.slave")), check=True)
os.remove(ss)
open(f"{pr}/{fn_d}.info", "wb").write(bd.mk_ico(4, "WHDLoad", (f"SLAVE={fn_d}.slave", "NoMMU")))
open(f"{pd}/{fn_d}.info", "wb").write(bd.mk_ico(4, "WHDLoad", (f"SLAVE={fn_d}.slave", "NoMMU")))
os.makedirs(f"{pr}/S", exist_ok=True)
open(f"{pr}/S/startup-sequence", "w").write(f"cd {fn_d}" + chr(10) + "MEDIAN_A1200" + chr(10))
tag_out = "_THEA1200" if args.profile == "standard" else ""
bd.mk_lha(f"{od}/{fn_d}{tag_out}.lha", pr)
bd.mk_zip(f"{od}/{fn_d}{tag_out}_FSUAE.zip", pr)
shutil.rmtree(pr); shutil.rmtree(sd, ignore_errors=True)
print(f"GOTOWE Median [{args.profile}]: {od}/{fn_d}{tag_out}.lha")
