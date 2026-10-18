"""怪诞蚀刻 · No.02 FIG. II《黑死病 · 尸岸》Firenze 1348
和 No.01 同一套刻法：背景刻线 → 剪影一件件盖上去 → 每件只在上沿刻断续的亮边。
上：佛罗伦萨，穹顶、乔托钟楼、旧宫的塔，几扇暖窗；中：阿诺河，一条运尸船；
下三分之一：病死的人和枯骨堆成的岸，骷髅、肋骨、裹尸布、耷拉的胳膊，缝里透出河面一样的横向断线。
全画唯一的粉色：船头那盏灯和它在水里的倒影。
配色 13「寄生生物」：#1E191C 底 / #7A91A0 冷刻线 / #9BAA87 副色 / #D7B66D 窗光 / #C98C9A 船灯
用法：python plague_pile.py [种子]
"""
import numpy as np, math, sys
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 1
rng = np.random.default_rng(SEED)
S = 2; W, H = 1200, 1500; WS, HS = W * S, H * S
def hx(h): return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.float32) / 255
C = {"N": hx("#1E191C"), "B": hx("#7A91A0"), "G": hx("#9BAA87"), "Y": hx("#D7B66D"), "R": hx("#C98C9A")}
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

BANK = 560          # 城脚＝河的上岸
PILE = 1000         # 尸堆的岸线（下三分之一）
EX, EY, ER = 640, 1205, 34
LB = {k: new() for k in "BGY"}

# ---------- 夜空 ----------
nz = fbm(110)
for y in range(0, BANK, 3):
    x = 0
    while x < W:
        sg = rng.uniform(20, 140); t = np.clip(.03 + .55 * (y / BANK) ** 1.7 + .18 * (nz[y, min(int(x), W - 1)] - .5), 0, 1)
        if rng.random() < t * 1.3: LB["B"][1].line(P([(x, y), (x + sg, y + rng.uniform(-.6, .6))]), fill=255, width=1)
        x += sg + rng.uniform(4, 30) * (1.2 - t)
for _ in range(70):
    x, y = rng.uniform(0, W), rng.uniform(0, 300); r = rng.uniform(.6, 1.4)
    LB["G"][1].ellipse(P([(x - r, y - r), (x + r, y + r)]), fill=255)

# ---------- 瘴气：从尸堆里升起，穿过河，爬进城和夜空 ----------
gy_, gx_ = np.gradient(fbm(150, 3))
def plume(x, y):
    if y > PILE + 80: return 0.
    t = np.clip((PILE + 80 - y) / 1050, 0, 1)
    cx = 600 - 220 * math.sin(t * 2.6) + 260 * t
    w = 230 + 260 * t
    return max(0., 1 - abs(x - cx) / w)
for _ in range(0):
    t0 = rng.random() ** .9; y = PILE + 80 - t0 * 1050
    x = 600 - 220 * math.sin(t0 * 2.6) + 260 * t0 + rng.normal(0, 170 + 230 * t0)
    if plume(x, y) < rng.random() * .6: continue
    pts = [(x, y)]
    for k in range(int(rng.uniform(20, 70))):
        i, j = int(np.clip(y, 0, H - 1)), int(np.clip(x, 0, W - 1))
        vx, vy = gy_[i, j] * 900, -gx_[i, j] * 900 - 1.1
        n = math.hypot(vx, vy) + 1e-6; x += 3 * vx / n; y += 3 * vy / n
        if plume(x, y) <= 0 or y < 20: break
        pts.append((x, y))
    if len(pts) > 4:
        LB["G" if rng.random() < .3 + .5 * plume(*pts[0]) else "B"][1].line(P(pts), fill=255, width=1 if rng.random() < .7 else 2)

# ---------- 河：横向碎刻线，窗光竖着碎在水里 ----------
for y in range(BANK + 6, PILE + 60, 3):
    f = (y - BANK) / (PILE - BANK)
    for _ in range(int(14 + 22 * f)):
        x = rng.uniform(-40, W); sg = rng.uniform(10, 70) * (1.3 - .6 * f)
        LB["G" if rng.random() < .12 else "B"][1].line(P([(x, y), (x + sg, y)]), fill=255, width=1)
for y in range(BANK - 70, BANK + 14, 3):                      # 城脚的雾
    for _ in range(int(4 + 26 * max(0, (y - BANK + 70) / 84) ** 1.6)):
        x = rng.uniform(0, W); LB["B"][1].line(P([(x, y), (x + rng.uniform(40, 200), y)]), fill=255, width=1)
for k in "BGY": ink(LB[k][0], k, .75 if k == "B" else 1)

# ---------- 上：佛罗伦萨的剪影（小，远） ----------
city, dc = new(); Lc = {k: new() for k in "BY"}
x = -10; roofs = []
while x < W:
    w_ = rng.uniform(26, 52); h_ = rng.uniform(40, 110); top = BANK - h_
    dc.rectangle(P([(x, top), (x + w_, BANK + 4)]), fill=255)
    if rng.random() < .6: dc.polygon(P([(x - 2, top + 1), (x + w_ / 2, top - w_ * .45), (x + w_ + 2, top + 1)]), fill=255)
    for wy in range(int(top + 10), BANK - 12, 16):
        for wx in range(int(x + 6), int(x + w_ - 8), 12):
            if rng.random() < .06: Lc["Y"][1].rectangle(P([(wx, wy), (wx + 4, wy + 6)]), fill=255)
    x += w_ - 2
DX, DY = 420, BANK - 120                                      # 圣母百花大教堂的穹顶
dc.rectangle(P([(DX - 150, DY), (DX + 150, BANK + 4)]), fill=255)
dc.rectangle(P([(DX - 70, DY - 70), (DX + 70, DY)]), fill=255)
dc.chord(P([(DX - 75, DY - 210), (DX + 75, DY - 10)]), 180, 360, fill=255)
dc.polygon(P([(DX - 75, DY - 110), (DX - 75, DY - 70), (DX + 75, DY - 70), (DX + 75, DY - 110)]), fill=255)
dc.rectangle(P([(DX - 10, DY - 250), (DX + 10, DY - 205)]), fill=255)
dc.polygon(P([(DX - 6, DY - 250), (DX, DY - 272), (DX + 6, DY - 250)]), fill=255)
for a in range(0, 180, 30):                                   # 穹顶的肋
    pass
for xr in (-45, 0, 45):
    Lc["B"][1].line(P(curve((DX + xr * .2, DY - 205), (DX + xr * 1.15, DY - 170), (DX + xr * 1.4, DY - 110), 14)), fill=255, width=1)
Lc["B"][1].arc(P([(DX - 75, DY - 210), (DX + 75, DY - 10)]), 200, 340, fill=255, width=2)
TX = 560                                                      # 乔托钟楼
dc.rectangle(P([(TX - 24, BANK - 330), (TX + 24, BANK + 4)]), fill=255)
dc.polygon(P([(TX - 28, BANK - 330), (TX, BANK - 380), (TX + 28, BANK - 330)]), fill=255)
Lc["B"][1].line(P([(TX + 24, BANK - 330), (TX + 24, BANK - 60)]), fill=255, width=1)
for yk in range(BANK - 320, BANK - 40, 60):
    Lc["Y"][1].rectangle(P([(TX - 5, yk), (TX + 5, yk + 18)]), fill=255) if rng.random() < .35 else None
VX = 930                                                      # 旧宫的塔
dc.rectangle(P([(VX - 18, BANK - 300), (VX + 18, BANK + 4)]), fill=255)
dc.rectangle(P([(VX - 26, BANK - 330), (VX + 26, BANK - 290)]), fill=255)
for k in range(5): dc.rectangle(P([(VX - 26 + k * 12, BANK - 342), (VX - 20 + k * 12, BANK - 330)]), fill=255)
dc.rectangle(P([(VX - 6, BANK - 380), (VX + 6, BANK - 342)]), fill=255)
Lc["B"][1].line(P([(VX + 18, BANK - 290), (VX + 18, BANK - 80)]), fill=255, width=1)
cover(city)
# 城的上沿：一道断续亮边（全画同一个函数）
DN = fbm(24, 2, (HS, WS)); HN = fbm(30, 3, (HS, WS))
def rim(mask_img, k, amt=1., dash=.55, depth=0):
    m = np.asarray(mask_img) > 127
    mf = ndi.binary_fill_holes(m)
    top = mf & ~np.roll(mf, 3, axis=0)
    top = ndi.binary_dilation(top, iterations=2)
    dn = DN > (1 - dash)
    a = (top & dn).astype(np.float32)
    if depth:                                                 # 上沿往下几道越来越稀的短横线
        d = ndi.distance_transform_edt(mf)
        rows = (np.arange(HS)[:, None] % 6 < 2)
        hat = rows & m & (d > 4) & (d < depth) & (HN > .45 + .35 * (d / depth))
        a = np.maximum(a, hat.astype(np.float32) * .7)
    ink(Image.fromarray((a * 255).astype(np.uint8)), k, amt)
rim(city, "B", .8)
for k in "BY": ink(Lc[k][0], k)

# 河上岸：小小的鸟嘴医生和运尸船
fig, df = new()
for x0 in ():
    h = 26; df.ellipse(P([(x0 - 3, BANK - h - 6), (x0 + 3, BANK - h)]), fill=255)
    df.polygon(P([(x0 + 2, BANK - h - 4), (x0 + 12, BANK - h + 1), (x0 + 2, BANK - h - 1)]), fill=255)
    df.polygon(P([(x0 - 5, BANK - h), (x0 + 5, BANK - h), (x0 + 8, BANK), (x0 - 8, BANK)]), fill=255)
    df.ellipse(P([(x0 - 8, BANK - h - 9), (x0 + 8, BANK - h - 5)]), fill=255)
BX0, BY0 = 690, 790                                           # 河心一条运尸船
df.polygon(P([(BX0 - 70, BY0), (BX0 + 70, BY0), (BX0 + 55, BY0 + 14), (BX0 - 55, BY0 + 14)]), fill=255)
for k in range(6): df.ellipse(P([(BX0 - 50 + k * 18, BY0 - 9), (BX0 - 34 + k * 18, BY0 + 2)]), fill=255)
df.ellipse(P([(BX0 + 46, BY0 - 36), (BX0 + 54, BY0 - 28)]), fill=255)
df.polygon(P([(BX0 + 44, BY0 - 28), (BX0 + 56, BY0 - 28), (BX0 + 60, BY0), (BX0 + 40, BY0)]), fill=255)
df.line(P([(BX0 + 58, BY0 - 30), (BX0 + 90, BY0 + 20)]), fill=255, width=2 * S)
cover(fig); rim(fig, "B", .8, .8)
wk, dwk = new()
for y in range(BY0 + 16, BY0 + 40, 4): dwk.line(P([(BX0 - 60 + rng.uniform(-8, 8), y), (BX0 + 60 + rng.uniform(-8, 8), y)]), fill=255, width=1)
ink(wk, "B", .5)
pk, dpk = new()                                                # 船夫的灯：全画唯一的粉色
LX, LY = BX0 + 90, BY0 + 20
dpk.ellipse(P([(LX - 5, LY - 6), (LX + 5, LY + 6)]), fill=255)
for k in range(60):
    a_ = rng.uniform(0, 2 * math.pi); r0 = 10; r1 = r0 + rng.uniform(4, 40) * rng.random()
    dpk.line(P([(LX + r0 * math.cos(a_), LY + r0 * math.sin(a_)), (LX + r1 * math.cos(a_), LY + r1 * math.sin(a_))]), fill=255, width=1)
for y in range(LY + 14, PILE - 20, 4):                         # 倒影：竖着碎在水里
    w_ = 14 * (1 - (y - LY) / (PILE - LY)) + 3
    dpk.line(P([(LX - w_ * rng.random(), y), (LX + w_ * rng.random(), y)]), fill=255, width=1)
ink(pk, "R")

# ---------- 下三分之一：尸堆，分层由远到近盖上去 ----------
def R(pts, x, y, s, a):
    ca, sa = math.cos(a), math.sin(a)
    return [(x + s * (px * ca - py * sa), y + s * (px * sa + py * ca)) for px, py in pts]
def limb(d, pts, w):
    for a_, b_ in zip(pts, pts[1:]):
        d.line(P([a_, b_]), fill=255, width=max(2, int(w * S)))
        d.ellipse(P([(b_[0] - w / 2, b_[1] - w / 2), (b_[0] + w / 2, b_[1] + w / 2)]), fill=255)
def ell(d, x, y, rx, ry, f=255): d.ellipse(P([(x - rx, y - ry), (x + rx, y + ry)]), fill=f)
def skull(d, x, y, s, a):
    flip = 1 if rng.random() < .5 else -1
    cr = R([(flip * px, py) for px, py in [(-30, -10), (-22, -32), (0, -40), (24, -32), (32, -8), (28, 14), (16, 22), (-14, 22), (-28, 10)]], x, y, s, a)
    d.polygon(P(cr), fill=255)
    d.polygon(P(R([(flip * px, py) for px, py in [(-14, 18), (16, 18), (14, 34), (-12, 34)]], x, y, s, a)), fill=255)
    for ex in (-12, 12):
        cx, cy = R([(flip * ex, 2)], x, y, s, a)[0]; ell(d, cx, cy, 8 * s, 7 * s, 0)
    cx, cy = R([(0, 15)], x, y, s, a)[0]; ell(d, cx, cy, 3 * s, 4 * s, 0)
    for t in range(-10, 12, 5):
        p1, p2 = R([(t, 25), (t, 32)], x, y, s, a); d.line(P([p1, p2]), fill=0, width=max(1, int(1.2 * s * S)))
def ribcage(d, x, y, s, a):
    sp = R([(px, 0) for px in np.linspace(-60, 60, 16)], x, y, s, a)
    limb(d, sp, 7 * s)
    for k, px in enumerate(np.linspace(-42, 42, 7)):
        Lr = 40 - abs(px) * .3
        for side in (-1, 1):
            pts = R(curve((px, 0), (px + 14, side * Lr * .9), (px + 4, side * Lr * 1.15), 10), x, y, s, a)
            limb(d, pts, 3.6 * s)
    p = R([(-60, 0)], x, y, s, a)[0]; ell(d, p[0], p[1], 14 * s, 11 * s)
def longbone(d, x, y, s, a):
    p1, p2 = R([(-45, 0), (45, 0)], x, y, s, a)
    d.line(P([p1, p2]), fill=255, width=int(7 * s * S))
    for p in (p1, p2):
        for o in (-1, 1):
            q = R([(0, o * 4)], 0, 0, s, a)[0]; ell(d, p[0] + q[0], p[1] + q[1], 6 * s, 6 * s)
def corpse(d, x, y, s, a):
    flip = 1 if rng.random() < .5 else -1
    body = [(-55, -16), (-10, -22), (40, -14), (60, -2), (40, 14), (-10, 20), (-55, 14)]
    d.polygon(P(R([(flip * px, py) for px, py in body], x, y, s, a)), fill=255)
    hx_, hy_ = R([(flip * 80, -4)], x, y, s, a)[0]; ell(d, hx_, hy_, 16 * s, 14 * s)
    jx, jy = R([(flip * 92, 6)], x, y, s, a)[0]; ell(d, jx, jy, 5 * s, 5 * s, 0)           # 张开的嘴
    for k in range(2):                                                                    # 胳膊耷拉下来
        base = R([(flip * (30 - k * 10), (-1) ** k * 12)], x, y, s, a)[0]
        tip1 = R([(flip * rng.uniform(-10, 40), (-1) ** k * rng.uniform(40, 60))], x, y, s, a)[0]
        tip2 = (tip1[0] + rng.uniform(-20, 20) * s, tip1[1] + rng.uniform(10, 30) * s)
        limb(d, [base, tip1, tip2], 7 * s)
        for f in range(4): d.line(P([tip2, (tip2[0] + rng.uniform(-9, 9) * s, tip2[1] + rng.uniform(4, 11) * s)]), fill=255, width=max(2, int(1.6 * s * S)))
    for k in range(2):
        base = R([(flip * -50, (-1) ** k * 8)], x, y, s, a)[0]
        k1 = R([(flip * rng.uniform(-110, -80), (-1) ** k * rng.uniform(5, 30))], x, y, s, a)[0]
        k2 = R([(flip * rng.uniform(-160, -120), (-1) ** k * rng.uniform(10, 50))], x, y, s, a)[0]
        limb(d, [base, k1, k2], 9 * s)
    for k in range(int(rng.integers(2, 5))):                                             # 烂穿的洞：透出后面的东西
        px, py = R([(rng.uniform(-45, 35), rng.uniform(-10, 10))], x, y, s, a)[0]
        ell(d, px, py, rng.uniform(3, 7) * s, rng.uniform(2, 4) * s, 0)
def shroud(d, x, y, s, a):
    pts = [(-90, -10), (-60, -20), (60, -22), (95, -8), (95, 8), (60, 20), (-60, 18), (-90, 8)]
    d.polygon(P(R(pts, x, y, s, a)), fill=255)
    for k, px in enumerate(np.linspace(-65, 75, 6)):                                       # 裹尸布的绳：剪影里刻出的缝
        p1, p2 = R([(px, -22), (px + 6, 22)], x, y, s, a)
        d.line(P([p1, p2]), fill=0, width=max(1, int(1.4 * s * S)))
KINDS = [(skull, .34), (ribcage, .22), (longbone, .12), (corpse, .26), (shroud, .06)]
def pick():
    r = rng.random(); acc = 0
    for f, w in KINDS:
        acc += w
        if r < acc: return f
    return KINDS[-1][0]
def ridge(x): return PILE + 30 * math.sin(x / 140 + 1) + 20 * math.sin(x / 57) - 40 * math.exp(-((x - 620) / 220) ** 2)

# 尸堆缝里的底：满满的瘴气流线，让每一块剪影都有亮的东西衬着
bz, dbz = new()                                                # 尸堆缝里的底：和河面同一种横向断线，越往下越密
for y in range(PILE - 60, H, 3):
    f = (y - PILE + 60) / (H - PILE + 60)
    x = rng.uniform(-30, 0)
    while x < W:
        sg = rng.uniform(10, 60)
        if y > ridge(x) - 40 and rng.random() < .55 + .3 * f:
            dbz.line(P([(x, y), (x + sg, y)]), fill=255, width=1)
        x += sg + rng.uniform(2, 14)
ink(bz, "B", .55)
BANDS = 3
for b in range(BANDS):
    lay, dl = new()
    s = (1.05, 1.5, 2.1)[b]
    y0 = ridge(0) + b * (H - PILE + 40) / BANDS
    n = (24, 15, 9)[b]
    for i in range(n):
        x = rng.uniform(-60, W + 60)
        y = ridge(x) + 20 + b * (H - PILE) / BANDS + rng.uniform(-20, 50) * s
        ob, do = new()
        pick()(do, x, y, s * rng.uniform(.85, 1.2), rng.uniform(-.7, .7) + (math.pi if rng.random() < .15 else 0))
        cover(ob); rim(ob, "B", .85, .8, depth=12 + 8 * b)     # 一件一件盖上去，后盖的压住先盖的亮边
    if False:                                                 # 半埋的鸟嘴面具：全画唯一的粉色
        ell(dl, EX, EY, 92, 80)
        dl.polygon(P(curve((EX + 60, EY - 40), (EX + 210, EY - 10), (EX + 300, EY + 70), 20) + curve((EX + 290, EY + 80), (EX + 190, EY + 50), (EX + 70, EY + 45), 20)), fill=255)
        dl.ellipse(P([(EX - 180, EY - 120), (EX + 140, EY - 70)]), fill=255)             # 压扁的帽檐
        ell(dl, EX, EY, ER, ER, 0)
    if b == BANDS - 1:
        dl.rectangle(P([(0, H - 40), (W, H)]), fill=255)
    cover(lay)
    rim(lay, "B", .85, .8, depth=12 + 8 * b)
    if False:
        Lr_, dr = new(); Ly_, dy = new(); Lb_, db = new()
        db.ellipse(P([(EX - ER - 9, EY - ER - 9), (EX + ER + 9, EY + ER + 9)]), outline=255, width=2)
        for r in range(4, ER, 5): dr.ellipse(P([(EX - r, EY - r), (EX + r, EY + r)]), outline=255, width=2 if r < ER * .6 else 1)
        dy.arc(P([(EX - ER + 8, EY - ER + 8), (EX + ER - 8, EY + ER - 8)]), 200, 255, fill=255, width=3)
        for k in range(170):                                   # 镜片的光溅在周围的尸骨上
            a = rng.uniform(0, 2 * math.pi); r0 = ER + rng.uniform(14, 22); r1 = r0 + rng.uniform(8, 110) * rng.random()
            (dr if rng.random() < .45 else dy).line(P([(EX + r0 * math.cos(a), EY + r0 * math.sin(a)), (EX + r1 * math.cos(a), EY + r1 * math.sin(a))]), fill=255, width=1)
        ink(Lb_, "B"); ink(Lr_, "R"); ink(Ly_, "Y", .8)
        lit = new()                                            # 前一层尸骨被镜片照到的那一点点边
    if b < BANDS - 1:                                          # 层与层之间夹一层贴着尸堆往上冒的瘴气
        mz, dm = new()
        for y in range(PILE - 40, H, 3):
            x = rng.uniform(-30, 0)
            while x < W:
                sg = rng.uniform(8, 40)
                if y > ridge(x) + b * (H - PILE) / BANDS + 30 and rng.random() < .35:
                    dm.line(P([(x, y), (x + sg, y)]), fill=255, width=1)
                x += sg + rng.uniform(6, 30)
        ink(mz, "B", .45)

out = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
o = np.asarray(out, np.float32) / 255
vig = np.clip(1 - ((xx - W / 2) / W) ** 2 * 1.2 - ((yy - H * .5) / H) ** 2 * 1.3, 0, 1)[..., None]
o = C["N"] + (o - C["N"]) * (0.45 + 0.55 * vig)
Image.fromarray((np.clip(o, 0, 1) * 255).astype(np.uint8)).save(f"plague_pile_s{SEED}.png")
print("ok")
