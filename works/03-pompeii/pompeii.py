"""怪诞蚀刻 · No.03《庞贝》Pompeii · 24 Aug 79
从广场上朱庇特神庙的废墟望出去，维苏威就在神庙背后——今天的游客也能站在同一个位置看见它。
那天下午，小普林尼说火山上升起一朵「像伞松」的云：一根柱子冲上天，顶上摊开，盖住整片天空。
云里打着黄色的闪电，火山口和往下淌的火是全画唯一的橙；浮石灰像雨一样斜着落下来，广场上的小人往外逃。
同一套刻法：背景刻线 → 剪影整块盖掉 → 只在受光的边上刻断续亮边。
配色 15「生态退化」：底 #1E1B17（#51483E 压深）
  #657E8C 污染蓝：夜空、石头的冷边   #8F9B78 退化灰绿：灰云、落灰
  #D4C56C 枯萎黄：闪电、被火照亮的边  #C77D53 氧化橙：火山口与熔流（唯一焦点）
  #51483E 腐殖深褐：远山、广场地面的刻线
用法：python pompeii.py [种子]
"""
import numpy as np, math, sys
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 1
rng = np.random.default_rng(SEED)
S = 2; W, H = 1200, 1500; WS, HS = W * S, H * S
def hx(h): return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.float32) / 255
C = {"N": hx("#1E1B17"), "B": hx("#657E8C"), "G": hx("#8F9B78"), "Y": hx("#D4C56C"), "R": hx("#C77D53"), "K": hx("#51483E")}
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
def fbm(scale, oct=4, shape=(H, W)):
    h, w = shape; out = np.zeros(shape, np.float32); a = 1; t = 0
    for o in range(oct):
        s = max(2, int(scale / 2 ** o))
        g = rng.random((h // s + 3, w // s + 3)).astype(np.float32)
        im = np.asarray(Image.fromarray((g * 255).astype(np.uint8)).resize((w + 3 * s, h + 3 * s), Image.BICUBIC), np.float32)[:h, :w] / 255
        out += a * im; t += a; a *= .5
    return out / t
def curve(p0, p1, p2, n=40):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in np.linspace(0, 1, n)]
def P(pts): return [(x * S, y * S) for x, y in pts]
def new():
    im = Image.new("L", (WS, HS), 0); return im, ImageDraw.Draw(im)
img = np.ones((HS, WS, 3), np.float32) * C["N"]
def ink(layer, k, amt=1.):
    global img
    a = np.asarray(layer, np.float32) / 255 * amt
    img = img * (1 - a[..., None]) + C[k] * a[..., None]
def cover(mask):
    global img
    a = np.asarray(mask, np.float32) / 255
    img = img * (1 - a[..., None]) + C["N"] * a[..., None]
DN = fbm(24, 2, (HS, WS))
def rim(mask_img, k, amt=1., dash=.6, dirs=((0, 3),), wid=2):
    """全画唯一的亮边函数：剪影朝某个方向的边，断断续续地刻一道。dirs=(dy,dx) 指向光来的方向"""
    m = ndi.binary_fill_holes(np.asarray(mask_img) > 127)
    e = np.zeros_like(m)
    for dy, dx in dirs: e |= m & ~np.roll(np.roll(m, dy, 0), dx, 1)
    e = ndi.binary_dilation(e, iterations=wid - 1) & m if wid > 1 else e
    ink(Image.fromarray(((e & (DN > 1 - dash)) * 255).astype(np.uint8)), k, amt)

HOR = 1060                      # 广场的地平线
VX, VY = 790, 640               # 维苏威火山口
LB = {k: new() for k in "BGYRK"}

# ---------- 伞松云的形状 ----------
cn = fbm(60, 3)
col_w = lambda y: 40 + 90 * np.clip((VY - y) / 360, 0, 1) ** 1.5
canopy_bot = 330 + 70 * np.sin(xx / 95) * .5 + 60 * (cn - .5) + 40 * np.exp(-((xx - VX) / 200) ** 2)
canopy = (yy < canopy_bot) & (yy > 40 + 120 * ((xx - 720) / 900) ** 2 + 50 * (cn - .5)) 
column = (np.abs(xx - VX - (VY - yy) * .12) < col_w(yy)) & (yy < VY + 10) & (yy > 150)
cloud = canopy | column
cloud = ndi.binary_opening(cloud, iterations=3)

# ---------- 夜空：云外的横向断线 ----------
nz = fbm(110)
for y in range(0, HOR + 20, 3):
    x = 0
    while x < W:
        sg = rng.uniform(20, 120); j = min(int(x), W - 1)
        t = np.clip(.04 + .55 * (y / HOR) ** 1.4 + .15 * (nz[y, j] - .5), 0, 1)
        if not cloud[min(y, H - 1), j] and rng.random() < t * 1.3:
            LB["B"][1].line(P([(x, y), (x + sg, y + rng.uniform(-.6, .6))]), fill=255, width=1)
        x += sg + rng.uniform(4, 26) * (1.2 - t)

# ---------- 灰云：curl 流线只走在云里；靠近火的下沿掺黄 ----------
gy_, gx_ = np.gradient(fbm(90, 3))
ys, xs = np.nonzero(cloud)
for _ in range(3800):
    i = rng.integers(len(ys)); y, x = float(ys[i]), float(xs[i])
    pts = [(x, y)]
    up = column[int(y), int(x)]
    for k in range(int(rng.uniform(14, 50))):
        a, b = int(np.clip(y, 0, H - 1)), int(np.clip(x, 0, W - 1))
        vx, vy = gy_[a, b] * 900, -gx_[a, b] * 900 - (1.4 if up else 0)
        n = math.hypot(vx, vy) + 1e-6; x += 3 * vx / n; y += 3 * vy / n
        if not (0 <= x < W and 0 <= y < H) or not cloud[int(y), int(x)]: break
        pts.append((x, y))
    if len(pts) < 4: continue
    x0, y0 = pts[0]
    warm = column[int(y0), int(x0)] * np.clip((y0 - 300) / 320, 0, 1) + (canopy_bot[int(y0), int(x0)] - y0 < 40) * .5
    kk = "Y" if rng.random() < .35 * warm else "G"
    LB[kk][1].line(P(pts), fill=255, width=1 if rng.random() < .75 else 2)
# 闪电：伞盖里几道折线
for _ in range(6):
    x, y = rng.uniform(150, 1100), rng.uniform(110, 200); pts = [(x, y)]
    for k in range(int(rng.uniform(6, 12))):
        x += rng.uniform(-28, 28); y += rng.uniform(10, 24); pts.append((x, y))
        if rng.random() < .3:
            bx, by = x, y; br = [(bx, by)]
            for q in range(3): bx += rng.uniform(-20, 20); by += rng.uniform(8, 16); br.append((bx, by))
            LB["Y"][1].line(P(br), fill=255, width=1)
    LB["Y"][1].line(P(pts), fill=255, width=4)

# ---------- 远山（索马山）：深褐的横刻线 ----------
def ridge_far(x): return 820 - 90 * math.exp(-((x - 260) / 260) ** 2) - 20 * math.sin(x / 70)
for y in range(700, HOR, 3):
    x = 0
    while x < W:
        sg = rng.uniform(10, 50)
        if y > ridge_far(x): LB["K"][1].line(P([(x, y), (x + sg, y)]), fill=255, width=1)
        x += sg + rng.uniform(3, 14)
# 广场地面：深褐的横线 + 往火山收拢的透视缝
for y in range(HOR, H, 3):
    f = (y - HOR) / (H - HOR); x = 0
    while x < W:
        sg = rng.uniform(10, 70) * (1 + f)
        if rng.random() < .6: LB["K"][1].line(P([(x, y), (x + sg, y)]), fill=255, width=1)
        x += sg + rng.uniform(4, 20)
for k in range(-14, 15):
    x1 = VX + k * 120
    for t in np.linspace(0, 1, 40)[::2]:
        a = (VX + (x1 - VX) * t, HOR + (H - HOR) * t); b = (VX + (x1 - VX) * (t + .02), HOR + (H - HOR) * (t + .02))
        LB["B"][1].line(P([a, b]), fill=255, width=1)
for k in "KBGY": ink(LB[k][0], k, {"B": .75, "K": 1, "G": .9, "Y": .9}[k])

# ---------- 维苏威：剪影，被下面的火照出亮边 ----------
vm, dv = new()
cone = [(VX - 470, HOR)] + curve((VX - 470, HOR), (VX - 170, 780), (VX - 46, VY), 30) + [(VX - 30, VY + 8), (VX + 28, VY + 6)] + \
       curve((VX + 44, VY), (VX + 200, 760), (VX + 520, HOR - 20), 30) + [(W + 20, HOR - 10), (W + 20, HOR)]
dv.polygon(P(cone), fill=255)
cover(vm)
vh, dvh = new()                                              # 山是远的：不做死黑剪影，用深褐的顺坡刻线排出来
mv = np.asarray(vm) > 127
for _ in range(1400):
    side = -1 if rng.random() < .5 else 1
    t = rng.random() ** .7; x = VX + side * (20 + 480 * t) + rng.normal(0, 30); y = VY + 10 + (HOR - VY) * t * rng.uniform(.3, 1.05)
    Lz = rng.uniform(8, 40); dvh.line(P([(x, y), (x + side * Lz * .55, y + Lz)]), fill=255, width=1)
for y in range(VY, HOR, 4):
    x = 0
    while x < W:
        sg = rng.uniform(10, 50)
        if rng.random() < .35: dvh.line(P([(x, y), (x + sg, y)]), fill=255, width=1)
        x += sg + rng.uniform(4, 20)
ink(Image.fromarray(((np.asarray(vh) > 0) & mv).astype(np.uint8) * 255), "K", 1)
rim(vm, "B", .9, .7, dirs=((3, 0),))
fl, df = new(); fy, dfy = new()
for k in range(220):                                         # 火山口：橙色的短刻线往外溅
    a = rng.uniform(math.pi * 1.05, math.pi * 1.95); r0 = rng.uniform(4, 16); r1 = r0 + rng.uniform(10, 70) * rng.random()
    df.line(P([(VX + r0 * math.cos(a), VY + 8 + r0 * math.sin(a) * .6), (VX + r1 * math.cos(a), VY + 8 + r1 * math.sin(a) * .8)]), fill=255, width=1)
df.ellipse(P([(VX - 30, VY + 2), (VX + 28, VY + 14)]), fill=255)
for k in range(5):                                           # 熔流：顺坡往下的断续橙线
    side = -1 if k % 2 == 0 else 1
    x, y = VX + side * rng.uniform(10, 30), VY + 14; pts = [(x, y)]
    for q in range(60):
        x += side * rng.uniform(2, 6) + rng.normal(0, 1.5); y += rng.uniform(3, 6)
        if y > HOR - 40: break
        pts.append((x, y))
    for a_, b_ in zip(pts[::2], pts[1::2]):
        if rng.random() < .8: df.line(P([a_, b_]), fill=255, width=2)
    for (px, py) in pts[::3]:
        if rng.random() < .5: dfy.line(P([(px, py), (px + rng.normal(0, 8), py + rng.uniform(2, 8))]), fill=255, width=1)
ink(fy, "Y", .7); ink(fl, "R")

# ---------- 朱庇特神庙的废墟 + 两侧柱廊 ----------
def column_(d, x, base, h, w):
    d.rectangle(P([(x - w / 2, base - h), (x + w / 2, base)]), fill=255)
    d.rectangle(P([(x - w * .8, base - h - w * .35), (x + w * .8, base - h)]), fill=255)       # 柱头
    d.rectangle(P([(x - w * .75, base - w * .25), (x + w * .75, base)]), fill=255)
tm, dt = new()
PX0, PX1, PT = 250, 690, 975
dt.rectangle(P([(PX0, PT), (PX1, HOR + 6)]), fill=255)                                          # 高台
for k in range(6): dt.rectangle(P([(PX0 + 120 + k * 10, PT + k * 15 - 90 + 90), (PX1 - 120 - k * 10, PT + 1)]), fill=0) if False else None
for k in range(7): dt.rectangle(P([(PX0 + 140 - k * 4, PT + 18 + k * 12), (PX1 - 140 + k * 4, PT + 30 + k * 12)]), fill=255)
hs = [300, 300, 210, 300, 120, 300]                                                            # 有的柱子断了
for k, xk in enumerate(np.linspace(PX0 + 40, PX1 - 40, 6)):
    column_(dt, xk, PT, hs[k], 34)
dt.rectangle(P([(PX0 + 20, PT - 300 - 40), (PX0 + 250, PT - 300 - 12)]), fill=255)               # 残存的一截额枋
dt.polygon(P([(PX0 + 20, PT - 340), (PX0 + 120, PT - 380), (PX0 + 190, PT - 352), (PX0 + 250, PT - 340)]), fill=255)
DT = [(PX1 - 40, PT - 300 - 40), (PX1 + 10, PT - 340)]
dt.rectangle(P(DT), fill=255)
for side in (-1, 1):                                                                            # 两侧往远处收的柱廊
    for k in range(9):
        t = k / 8
        x = (VX + side * 760) + (VX + side * 300 - (VX + side * 760)) * t ** .8 if side > 0 else (-80 + 270 * t ** .8)
        base = H - 120 - (H - 120 - HOR) * t ** .7
        h = 520 * (1 - .78 * t ** .7); w = 46 * (1 - .75 * t ** .7)
        if side > 0: x = 1290 - 360 * t ** .8
        column_(dt, x, base, h, w)
        if k < 8:
            t2 = (k + 1) / 8; x2 = (1290 - 360 * t2 ** .8) if side > 0 else (-80 + 270 * t2 ** .8)
            b2 = H - 120 - (H - 120 - HOR) * t2 ** .7; h2 = 520 * (1 - .78 * t2 ** .7)
            dt.polygon(P([(x, base - h - w * .35), (x2, b2 - h2 - 8), (x2, b2 - h2 + 4), (x, base - h - w * .35 + 18 * (1 - t))]), fill=255)
cover(tm)
rim(tm, "Y", .85, .6, dirs=((0, -3),))                     # 朝火山（右）的一侧被火光勾黄
rim(tm, "B", .8, .55, dirs=((3, 0),))                      # 顶面是冷的天光
# 柱身的凹槽：剪影里极稀的竖向短刻线，只在被照的一侧
fm, dfm = new()
mt = np.asarray(tm) > 127
for x in range(0, W, 6):
    for y0 in range(int(rng.uniform(600, 700)), H, int(rng.uniform(30, 80))):
        if mt[min(HS - 1, y0 * S), min(WS - 1, x * S)] and rng.random() < .22:
            dfm.line(P([(x, y0), (x, y0 + rng.uniform(6, 24))]), fill=255, width=1)
ink(Image.fromarray(((np.asarray(fm) > 0) & mt).astype(np.uint8) * 255), "B", .5)

# ---------- 广场上逃的小人 ----------
pm, dp = new()
def person(x, y, h, cloak=False, kid=None):
    hw = h * .17; lean = h * .12
    dp.ellipse(P([(x - hw * .55 - lean, y - h), (x + hw * .55 - lean, y - h + hw * 1.15)]), fill=255)
    dp.polygon(P([(x - hw - lean, y - h + hw), (x + hw - lean * .6, y - h + hw), (x + hw * 1.3, y), (x - hw * 1.3, y)]), fill=255)
    if cloak: dp.polygon(P([(x - hw * 1.1 - lean, y - h - 2), (x + hw * 1.6, y - h + hw * .5), (x + hw * 2.2, y - h * .3)]), fill=255)
    dp.line(P([(x - hw * .3, y - 2), (x - hw * 1.6, y + 1)]), fill=255, width=max(2, int(hw * .6 * S)))
    if kid:
        dp.line(P([(x - hw - lean, y - h * .55), (x - hw * 2.4 - lean, y - h * .4)]), fill=255, width=2 * S)
        person_k = (x - hw * 3.2, y, h * .6); dp.ellipse(P([(person_k[0] - 4, y - person_k[2]), (person_k[0] + 4, y - person_k[2] + 8)]), fill=255)
        dp.polygon(P([(person_k[0] - 5, y - person_k[2] + 7), (person_k[0] + 5, y - person_k[2] + 7), (person_k[0] + 7, y), (person_k[0] - 7, y)]), fill=255)
for k in range(14):
    t = rng.uniform(.15, 1) ** 1.3
    y = HOR + 20 + (H - 200 - HOR) * t; x = rng.uniform(380, 1000) - 200 * t
    person(x, y, 18 + 46 * t, cloak=rng.random() < .4, kid=rng.random() < .2)
cover(pm); rim(pm, "Y", .9, .85, dirs=((0, -3), (3, 0)))

# ---------- 前景：倒下的柱段，旁边蜷着一个人 ----------
fg, dg = new()
dg.ellipse(P([(-60, H - 170), (90, H - 20)]), fill=255)
dg.polygon(P([(10, H - 170), (430, H - 120), (440, H - 10), (10, H - 20)]), fill=255)
dg.ellipse(P([(380, H - 122), (480, H - 8)]), fill=255)
dg.rectangle(P([(0, H - 40), (W, H)]), fill=255)
dg.ellipse(P([(820, H - 150), (1000, H - 40)]), fill=255)                     # 摔下来的柱头
dg.polygon(P([(800, H - 120), (1030, H - 165), (1050, H - 130), (820, H - 85)]), fill=255)
cover(fg)
rim(fg, "Y", .8, .7, dirs=((0, -3),)); rim(fg, "B", .85, .7, dirs=((3, 0),))
hb, dh = new()                                               # 柱段上的环刻与被灰埋住的一层
for xk in range(40, 420, 14):
    dh.line(P(curve((xk, H - 165 + xk * .12), (xk + 18, H - 95), (xk, H - 25), 10)), fill=255, width=1) if rng.random() < .5 else None
ink(Image.fromarray(((np.asarray(hb) > 0) & (np.asarray(fg) > 127)).astype(np.uint8) * 255), "K", 1)

# ---------- 落下的浮石灰：斜着的短线，盖在一切之上 ----------
ash, da = new()
for _ in range(2600):
    x, y = rng.uniform(-100, W), rng.uniform(300, H)
    p = .25 + .75 * np.clip((x - 200) / 900, 0, 1)
    if rng.random() > p: continue
    Lz = rng.uniform(4, 14)
    da.line(P([(x, y), (x + Lz * .35, y + Lz)]), fill=255, width=1)
ink(ash, "G", .65)

out = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
o = np.asarray(out, np.float32) / 255
vig = np.clip(1 - ((xx - W / 2) / W) ** 2 * 1.2 - ((yy - H * .5) / H) ** 2 * 1.3, 0, 1)[..., None]
o = C["N"] + (o - C["N"]) * (0.45 + 0.55 * vig)
Image.fromarray((np.clip(o, 0, 1) * 255).astype(np.uint8)).save(f"pompeii_s{SEED}.png")
print("ok")
