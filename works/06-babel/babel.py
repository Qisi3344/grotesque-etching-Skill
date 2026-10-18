"""怪诞蚀刻 · No.06《巴别塔》Shinar, ~2100 BCE
人类用同一种语言造一座通天的塔。塔是一层层圆柱叠起来的，每层一圈拱廊，
坡道绕着塔螺旋往上（骨架参考基歇尔 1679《Turris Babel》）。
神把语言打碎：塔从第五层错开，上半截往右滑了一截，
楔形文字的碎片从裂口飘进夜空，塔下的人往四面散开、再也听不懂彼此。
裂缝里漏出一道珊瑚色的光——全画唯一的暖色。
配色 07「异质生命」：#171B20 底 / #7EAAA0 变异蓝绿(天·平原·城) / #D7DFA4 突变嫩绿(塔身刻线)
            / #B7A0C8 异形灰紫(文字碎片) / #D78D78 组织珊瑚(裂缝·焦点)
概念：扶光 & 绮思 · 代码：扶光
用法：python babel.py [种子]
"""
import numpy as np, math, sys
from PIL import Image, ImageDraw, ImageFilter

SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 1
rng = np.random.default_rng(SEED)
S = 2; W, H = 1200, 1500; WS, HS = W * S, H * S
def hx(h): return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.float32) / 255
C = {"N": hx("#171B20"), "B": hx("#7EAAA0"), "G": hx("#D7DFA4"), "V": hx("#B7A0C8"), "R": hx("#D78D78")}

def fbm(scale, oct=4, shape=(H, W)):
    h, w = shape; out = np.zeros(shape, np.float32); a = 1; t = 0
    for o in range(oct):
        s = max(2, int(scale / 2 ** o))
        g = rng.random((h // s + 3, w // s + 3)).astype(np.float32)
        im = np.asarray(Image.fromarray((g * 255).astype(np.uint8)).resize((w + 3 * s, h + 3 * s), Image.BICUBIC), np.float32)[:h, :w] / 255
        out += a * im; t += a; a *= .5
    return out / t
def Pp(pts): return [(x * S, y * S) for x, y in pts]
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
DN = fbm(24, 2, (HS, WS)) > .45
def rim(mask_img, k, amt=1.):
    m = np.asarray(mask_img) > 127
    top = m & ~np.roll(m, 3, axis=0)
    top = np.asarray(Image.fromarray((top * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5))) > 0
    ink(Image.fromarray(((top & DN) * 255).astype(np.uint8)), k, amt)

# ================= 塔的几何：一层层圆柱 =================
HZ = 800                         # 平原地平线（俯视，地平线偏高）
E = .17                          # 椭圆扁度（从斜上方看）
SL = 12                          # 螺旋坡道：每层右侧比左侧高 SL 像素
CRK = 5                          # 从第 5 层起错开
SHIFT, LEAN, GAP = 30, 9, 14     # 上半截右滑、逐层再歪一点、裂缝高度
heights = [150, 140, 128, 118, 108, 99, 90, 82]
TIERS = []                       # (cx, yb, yt, r)
yb = 1250
for i, hh in enumerate(heights):
    r = 300 - i * 23
    cx = 600 + (SHIFT + (i - CRK) * LEAN if i >= CRK else 0)
    if i == CRK: yb -= GAP
    TIERS.append((cx, yb, yb - hh, r)); yb -= hh
def slant(x, cx, r): return -SL * (x - cx) / r          # 坡道斜度（线性随 x）
def ell(cx, cy, r, a0, a1, n=90):
    return [(cx + r * math.cos(a), cy + r * E * math.sin(a) + slant(cx + r * math.cos(a), cx, r))
            for a in np.linspace(a0, a1, n)]
def tier_poly(cx, yb, yt, r):
    return ell(cx, yt, r, math.pi, 2 * math.pi) + ell(cx, yb, r, 0, math.pi)
def surf(cx, y, r, th):          # 圆柱面上 θ 处（θ=0 正对镜头）
    x = cx + r * math.sin(th)
    return x, y + r * E * math.cos(th) + slant(x, cx, r)
def light(th): return float(np.clip(.22 + .78 * max(0, math.cos(th + .55)), 0, 1))  # 光从左前方来

# ================= 1. 夜空 =================
L = {k: new() for k in "BGVR"}
FX, FY = TIERS[CRK][0] - 10, TIERS[CRK][1] + 6   # 裂缝中心
nz = fbm(110)
for y in range(0, HZ, 3):
    x = 0
    while x < W:
        sg = rng.uniform(18, 140)
        glow = math.exp(-((x - FX) ** 2 + (y - FY) ** 2 * 2) / (2 * 300 ** 2))
        t = np.clip(.02 + .38 * (y / HZ) ** 1.8 + .38 * glow + .12 * (nz[y, min(int(x), W - 1)] - .5), 0, 1)
        if rng.random() < t * 1.3: L["B"][1].line(Pp([(x, y), (x + sg, y + rng.uniform(-.5, .5))]), fill=255, width=1)
        x += sg + rng.uniform(4, 24) * (1.2 - t)
for _ in range(80):
    x, y = rng.uniform(0, W), rng.uniform(0, HZ * .5) * rng.random() ** .5
    r = rng.uniform(.5, 1.3); L["B"][1].ellipse(Pp([(x - r, y - r), (x + r, y + r)]), fill=255)
ink(L["B"][0], "B", .85)

# ================= 2. 平原与城 =================
gr, dgr = new(); dgr.rectangle(Pp([(0, HZ), (W, H)]), fill=255); cover(gr)
gl, dgl = new()
for y in range(HZ, H, 3):
    f = (y - HZ) / (H - HZ)
    for _ in range(int(4 + 22 * f)):
        x = rng.uniform(-40, W); sg = rng.uniform(10, 80) * (1.2 - .5 * f)
        dgl.line(Pp([(x, y), (x + sg, y)]), fill=int(90 + 120 * rng.random()), width=1)
ink(gl, "B", .4)
city, dc = new(); win, dwin = new()
cdet, dcd = new()                                # 房子的刻线（近的房子先擦掉身后远房子的线）
road, drd = new()
OX, OY = 600, 1275                               # 所有的路都从塔脚出发
def gsc(y): return .3 + 1.4 * max(0, (y - HZ) / (H - HZ))   # 近大远小
ROADS = [(x, HZ + 3) for x in np.linspace(-250, 1450, 11)] + [(x, H + 40) for x in np.linspace(-700, 1900, 9)]
BLD = []
for ex, ey in ROADS:
    sx, sy = OX + (ex - OX) * .18, OY + (ey - OY) * .02
    L_ = math.hypot(ex - sx, ey - sy); ux, uy = (ex - sx) / L_, (ey - sy) / L_
    nx, ny = -uy, ux
    pts_l, pts_r = [], []
    for t in np.linspace(0, 1, 40):
        x, y = sx + (ex - sx) * t, sy + (ey - sy) * t; hw = 7 * gsc(y)
        pts_l.append((x + nx * hw, y + ny * hw)); pts_r.append((x - nx * hw, y - ny * hw))
    drd.line(Pp(pts_l), fill=150, width=1); drd.line(Pp(pts_r), fill=150, width=1)
    t = rng.uniform(.03, .08)
    while t < 1:
        x, y = sx + (ex - sx) * t, sy + (ey - sy) * t
        sc = gsc(y)
        for side in (-1, 1):
            if rng.random() < .82:
                off = (14 + rng.uniform(4, 16)) * sc
                BLD.append((x + side * nx * off, y + side * ny * off, sc))
        t += rng.uniform(26, 40) * sc / L_ * 1.6
BLD.sort(key=lambda b: b[1])                     # 远→近
for bx, by, sc in BLD:
    if not (-30 < bx < W + 30 and HZ < by < H + 20): continue
    w = rng.uniform(22, 40) * sc; h = rng.uniform(12, 30) * sc; dp_ = w * .35
    kind = rng.random()
    x0 = bx - w / 2
    front = [(x0, by), (x0 + w, by), (x0 + w, by - h), (x0, by - h)]
    topf = [(x0, by - h), (x0 + w, by - h), (x0 + w + dp_ * .6, by - h - dp_ * .5), (x0 + dp_ * .6, by - h - dp_ * .5)]
    side_ = [(x0 + w, by), (x0 + w + dp_ * .6, by - dp_ * .5), (x0 + w + dp_ * .6, by - h - dp_ * .5), (x0 + w, by - h)]
    shape = front + []
    extra = []
    if kind < .18:                               # 小穹顶
        extra = [("pie", (x0 + w * .2, by - h - w * .3, x0 + w * .8, by - h + w * .3))]
    elif kind < .32:                             # 退台小塔庙
        extra = [("rect", (x0 + w * .2, by - h - h * .5, x0 + w * .8, by - h)),
                 ("rect", (x0 + w * .35, by - h - h * .9, x0 + w * .65, by - h - h * .5))]
    # 先在刻线层上把这栋房子的范围擦黑，再画它自己的线
    for poly in (front, topf, side_):
        dc.polygon(Pp(poly), fill=255); dcd.polygon(Pp(poly), fill=0)
    for kd, bb in extra:
        if kd == "pie":
            dc.pieslice(Pp([bb[:2], bb[2:]]), 180, 360, fill=255); dcd.pieslice(Pp([bb[:2], bb[2:]]), 180, 360, fill=0)
            dcd.arc(Pp([bb[:2], bb[2:]]), 200, 300, fill=200, width=1)
        else:
            dc.rectangle(Pp([bb[:2], bb[2:]]), fill=255); dcd.rectangle(Pp([bb[:2], bb[2:]]), fill=0)
            dcd.line(Pp([(bb[0], bb[1]), (bb[2], bb[1])]), fill=210, width=1)
    dcd.line(Pp([topf[3], topf[2]]), fill=230, width=1)          # 屋顶亮沿
    dcd.line(Pp([front[3], front[2]]), fill=200, width=1)
    for k in range(int(h / max(1.5, 2.6 * sc))):                 # 正面受光：横排线
        yy = by - 1.5 - k * 2.6 * sc
        if rng.random() < .6: dcd.line(Pp([(x0 + 1, yy), (x0 + w - 1, yy)]), fill=150, width=1)
    if rng.random() < .35:
        wx, wy = x0 + rng.uniform(.2, .8) * w, by - rng.uniform(.3, .7) * h
        dwin.rectangle(Pp([(wx, wy), (wx + max(1, sc), wy + max(1, 1.6 * sc))]), fill=255)
ink(road, "B", .45)
for k in range(2):                               # 远处两根方尖碑
    ox = [905, 248][k]; oh = [70, 46][k]
    dc.polygon(Pp([(ox - 5, HZ + 14), (ox + 5, HZ + 14), (ox + 1.5, HZ + 14 - oh), (ox - 1.5, HZ + 14 - oh)]), fill=255)
cover(city); ink(cdet, "B", 1.); ink(win, "G", .5); del cdet, dcd

# ================= 3. 塔身剪影 =================
tw_, dtw = new()
for cx, yb, yt, r in TIERS: dtw.polygon(Pp(tier_poly(cx, yb, yt, r)), fill=255)
# 顶层没造完：残墙、断柱
cx, yb, yt, r = TIERS[-1]
for th in np.linspace(-1.35, 1.35, 26):
    x, y = surf(cx, yt, r * .92, th)
    if rng.random() < .75:
        hgt = rng.uniform(6, 40) * (1 - abs(th) / 2)
        dtw.rectangle(Pp([(x - 3, y - hgt), (x + 3, y + 4)]), fill=255)
cover(tw_)

# ================= 4. 塔身刻线：拱廊、檐口、坡道 =================
det, dd = new()
opn, dop = new()                 # 拱洞遮罩：墙面排线要避开拱洞
def arcade(cx, yb, r, y0, rowH, n, wscale=1.):
    ths = np.linspace(-math.pi / 2 + .04, math.pi / 2 - .04, n + 1)
    for j in range(n):
        a, b = ths[j], ths[j + 1]; m = (a + b) / 2
        lv = light(m); val = int(70 + 185 * lv)
        xa, ya = surf(cx, yb - y0, r, a); xb, yb2 = surf(cx, yb - y0, r, b)
        w = (xb - xa) * wscale
        if w < 1.2: continue
        archH = min(w * .55, rowH * .33)
        spa = ya - rowH + archH; spb = yb2 - rowH + archH
        # 柱子
        pw = 2 if abs(a) < 1. else 1
        dd.line(Pp([(xa, ya), (xa, spa)]), fill=val, width=pw)
        # 拱顶（屏幕空间半圆）
        xm = (xa + xb) / 2; hw = (xb - xa) / 2; ysp = (spa + spb) / 2
        pts = [(xm - hw * math.cos(s), ysp - archH * math.sin(s)) for s in np.linspace(0, math.pi, 9)]
        dd.line(Pp(pts), fill=val, width=1)
        dop.polygon(Pp([(xa + 1.5, ya - 1)] + pts[::-1][:0] + [(xa + 1.5, spa)] +
                       [(xm - (hw - 1.5) * math.cos(s), ysp - (archH - 1) * math.sin(s)) for s in np.linspace(0, math.pi, 9)] +
                       [(xb - 1.5, spb), (xb - 1.5, yb2 - 1)]), fill=255)
        # 亮的一侧在拱券之间刻几道排线（墙面），暗侧留黑
        if lv > .45 and rng.random() < lv:
            for k in range(int(2 + 4 * lv)):
                yy = ysp - archH - 2 - k * 2.5
                if yy < ya - rowH: break
                dd.line(Pp([(xa + 1, yy), (xb - 1, yy + (spb - spa) * .5)]), fill=int(val * .55), width=1)
    # 拱廊下沿的束带
    dd.line(Pp(ell(cx, yb - y0, r, 0, math.pi)), fill=200, width=1)

for i, (cx, yb, yt, r) in enumerate(TIERS):
    h = yb - yt
    # 底部檐口：两道亮线 + 齿饰
    dd.line(Pp(ell(cx, yb, r, 0, math.pi)), fill=255, width=3)
    dd.line(Pp(ell(cx, yb - 6, r, 0, math.pi)), fill=170, width=1)
    for th in np.linspace(-1.45, 1.45, int(r / 5)):
        x, y = surf(cx, yb - 6, r, th)
        dd.line(Pp([(x, y), (x, y + 4)]), fill=int(60 + 150 * light(th)), width=1)
    # 坡道外沿矮墙（顶面平台的前沿）
    dd.line(Pp(ell(cx, yt, r, 0, math.pi)), fill=230, width=2)
    for th in np.linspace(-1.4, 1.4, int(r / 7)):
        x, y = surf(cx, yt, r, th)
        dd.line(Pp([(x, y), (x, y - 5)]), fill=int(80 + 150 * light(th)), width=1)
    # 拱廊：高的层两排，下排大、上排小
    n = max(10, int(r / 13))
    if h > 105:
        arcade(cx, yb, r, 9, h * .58, n)
        arcade(cx, yb, r, 9 + h * .58, h * .30, int(n * 1.4))
    else:
        arcade(cx, yb, r, 9, h * .78, n)
    # 侧影边缘：圆柱两侧的竖向排线，左亮右暗
    for side, th0 in ((-1, -math.pi / 2), (1, math.pi / 2)):
        for k in range(6 if side < 0 else 3):
            th = th0 - side * k * .035
            x, y1 = surf(cx, yb - 8, r, th); _, y2 = surf(cx, yt + 6, r, th)
            dd.line(Pp([(x, y1), (x, y2)]), fill=int(200 if side < 0 else 90), width=1)
ink(det, "G", .9)

# 墙面排线：沿圆柱横走，受光侧密、背光侧疏；拱洞里留黑
hat, dh = new()
for cx, yb, yt, r in TIERS:
    y = yt + 5
    while y < yb - 4:
        th = -math.pi / 2 + .02
        while th < math.pi / 2 - .02:
            dth = rng.uniform(.04, .16)
            lv = light(th + dth / 2)
            if rng.random() < lv ** 1.3 * .95:
                pts = [surf(cx, y, r, a) for a in np.linspace(th, min(th + dth, math.pi / 2), 4)]
                dh.line(Pp(pts), fill=int(60 + 170 * lv), width=1)
            th += dth + rng.uniform(.01, .07) * (1.4 - lv)
        y += rng.uniform(2.6, 3.6)
hm = np.asarray(hat, np.float32) * (1 - np.asarray(opn, np.float32) / 255)
ink(Image.fromarray(hm.astype(np.uint8)), "G", .55); del hm
# 拱洞深处：极淡的几道竖线，让洞有进深
dl, ddl = new()
om = np.asarray(opn) > 0
ys_, xs_ = np.where(om[::5, ::5])
for ii in rng.choice(len(xs_), size=min(2500, len(xs_)), replace=False):
    x, y = xs_[ii] * 5 / S, ys_[ii] * 5 / S
    ddl.line(Pp([(x, y), (x, y + rng.uniform(2, 6))]), fill=120, width=1)
ink(dl, "B", .35)

# 顶层的脚手架：没造完的塔
sc_, dsc = new()
cx, yb, yt, r = TIERS[-1]
for k in range(9):
    x0 = cx - r * .8 + k * r * .2; y0 = surf(cx, yt, r * .9, 0)[1] - 6
    dsc.line(Pp([(x0, y0), (x0 + rng.uniform(-4, 4), y0 - rng.uniform(40, 90))]), fill=200, width=1)
for k in range(5):
    yy = yt - 12 - k * 15
    dsc.line(Pp([(cx - r * .8, yy + rng.uniform(-3, 3)), (cx + r * .8, yy + rng.uniform(-3, 3))]), fill=140, width=1)
ink(sc_, "G", .7)

# ================= 5. 裂缝：唯一的暖色 =================
cx4, yb4, yt4, r4 = TIERS[CRK - 1]; cx5, yb5, _, r5 = TIERS[CRK]
cr, dcr = new()
# 裂缝本身：上下两层之间的那道缝，沿椭圆前沿
top_edge = ell(cx4, yt4, r4, 0, math.pi)
bot_edge = ell(cx5, yb5, r5, 0, math.pi)
for k in range(int(GAP)):
    f = k / GAP
    pts = [(a[0] * (1 - f) + b[0] * f, a[1] * (1 - f) + b[1] * f) for a, b in zip(top_edge, bot_edge)]
    dcr.line(Pp(pts), fill=int(255 * (1 - abs(f - .5) * 1.4)), width=1)
# 一道往下劈的裂纹，劈进下面两层
x, y = cx4 + 38, yt4 + r4 * E
for k in range(26):
    nx, ny = x + rng.uniform(-9, 9), y + rng.uniform(8, 13)
    dcr.line(Pp([(x, y), (nx, ny)]), fill=255, width=3 if k < 12 else 2)
    if rng.random() < .3:
        bx, by = nx + rng.choice([-1, 1]) * rng.uniform(8, 22), ny + rng.uniform(2, 12)
        dcr.line(Pp([(nx, ny), (bx, by)]), fill=200, width=1)
    x, y = nx, ny
# 光从缝里往外漏：横向放射的细线，越过塔身边缘打进夜空
for _ in range(420):
    th = rng.uniform(-math.pi / 2, math.pi / 2)
    sx, sy = surf(cx4, yt4 - GAP / 2, r4, th)
    side = math.sin(th) + rng.normal(0, .15)
    ln = rng.uniform(10, 380) * rng.random() ** 1.3
    ex = sx + side * ln * rng.uniform(.8, 1.2) + rng.normal(0, 8)
    ey = sy + rng.normal(0, 1) * ln * .12
    dcr.line(Pp([(sx, sy), (ex, ey)]), fill=int(40 + 200 * (1 - ln / 260) * rng.random()), width=1)
# 裂缝下几扇拱被照亮
for th in np.linspace(-.6, .9, 7):
    x, y = surf(cx4, yt4 + 26, r4, th)
    for k in range(5):
        dcr.line(Pp([(x - 3, y - k * 3), (x + 3, y - k * 3)]), fill=150, width=1)
ink(cr.filter(ImageFilter.GaussianBlur(22 * S)).point(lambda v: min(255, v * 3)), "R", .28)
ink(cr, "R", 1.)

# ================= 6. 文字碎片：从裂口飘散 =================
gs, dgs = new()
for _ in range(190):
    side = rng.choice([-1, 1])
    dist = rng.uniform(r4 * .9, r4 + 420) * rng.random() ** .5 + r4 * .7
    fx = cx4 + side * dist
    fy = yt4 - rng.uniform(-60, 300) * (dist / 500) ** 1.2 - rng.normal(0, 25)
    if not (10 < fx < W - 10 and 10 < fy < HZ - 10): continue
    sz = rng.uniform(7, 18) * max(.4, 1.25 - dist / 650)
    rot = rng.uniform(0, math.pi)
    for _ in range(int(rng.integers(2, 5))):      # 楔形：一根横线 + 三角头
        a = rot + rng.choice([0, math.pi / 2]) + rng.uniform(-.25, .25)
        ox, oy = fx + rng.uniform(-sz, sz) * .6, fy + rng.uniform(-sz, sz) * .6
        ex, ey = ox + sz * math.cos(a), oy + sz * math.sin(a)
        dgs.line(Pp([(ox, oy), (ex, ey)]), fill=int(130 + 120 * rng.random()), width=1)
        hw = sz * .22
        dgs.polygon(Pp([(ox, oy), (ox - hw * math.sin(a) - hw * math.cos(a), oy + hw * math.cos(a) - hw * math.sin(a)),
                        (ox + hw * math.sin(a) - hw * math.cos(a), oy - hw * math.cos(a) - hw * math.sin(a))]), fill=230)
ink(gs, "V", .9)


# ================= 7. 掉落的碎石 =================
rb, drb = new()
for _ in range(12):
    th = rng.choice([-1, 1]) * rng.uniform(1.3, 1.7)
    x, y = surf(cx4, yt4, r4 * 1.05, th)
    x += math.sin(th) * rng.uniform(10, 60); y += rng.uniform(10, 260)
    s = rng.uniform(2, 7)
    pts = [(x + s * math.cos(a) * rng.uniform(.6, 1.2), y + s * math.sin(a) * rng.uniform(.6, 1.2)) for a in np.linspace(0, 2 * math.pi, 6)[:-1]]
    drb.polygon(Pp(pts), fill=255)
cover(rb); rim(rb, "B", .5)

# ================= 8. 前景圆殿 + 四散的小人 =================
fg, dfg = new(); fgd, dfgd = new()
RX, RY, RR, RH = 450, 1395, 78, 64          # 塔脚下的圆殿（参考里的那座）
dfg.polygon(Pp(tier_poly(RX, RY, RY - RH, RR)), fill=255)
dfg.pieslice(Pp([(RX - RR * .8, RY - RH - RR * .55), (RX + RR * .8, RY - RH + RR * .55)]), 180, 360, fill=255)
cover(fg)
for th in np.linspace(-1.4, 1.4, 14):
    x, y = surf(RX, RY - 6, RR, th)
    dfgd.line(Pp([(x, y), (x, y - RH * .62)]), fill=int(60 + 180 * light(th)), width=1)
dfgd.line(Pp(ell(RX, RY - RH, RR, 0, math.pi)), fill=220, width=2)
dfgd.line(Pp(ell(RX, RY, RR, 0, math.pi)), fill=220, width=2)
ink(fgd, "G", .75); rim(fg, "G", .6)

pp, dp = new()
LX, LY = 752, 1372                               # 牵手的两个人站的位置
for _ in range(60):
    a = rng.uniform(0, 2 * math.pi); d = rng.uniform(320, 640)
    px = 600 + d * math.cos(a); py = 1270 + d * .3 * math.sin(a) + 60
    if not (20 < px < W - 20 and HZ + 30 < py < H - 20): continue
    if math.hypot(px - LX, py - LY) < 90: continue
    sc = .6 + (py - HZ) / (H - HZ) * 1.1
    lean = 2.5 * sc * (1 if math.cos(a) > 0 else -1)
    dp.ellipse(Pp([(px - 1.6 * sc, py - 11 * sc), (px + 1.6 * sc, py - 7.5 * sc)]), fill=255)
    dp.line(Pp([(px, py - 7.5 * sc), (px + lean, py)]), fill=255, width=max(2, int(2.4 * sc)))
    dp.line(Pp([(px + lean * .3, py - 5 * sc), (px + lean * 1.4, py - 6.5 * sc)]), fill=255, width=1)
cover(pp); rim(pp, "B", .8)

# ================= 9. 两个没走的人：面对面，牵着手 =================
# 所有人都在往外逃、谁也听不懂谁了；只有这两个站在裂缝的光里，还牵着。
lp, dlp = new(); lv_, dlv = new()
for k in range(130):                             # 脚下一小圈淡淡的珊瑚光
    a = rng.uniform(0, 2 * math.pi); rr = rng.uniform(4, 64) * rng.random() ** .5
    x, y = LX + rr * math.cos(a) * 1.4, LY + rr * math.sin(a) * .32
    dlp.line(Pp([(x - rng.uniform(2, 7), y), (x + rng.uniform(2, 7), y)]), fill=int(60 + 150 * (1 - rr / 64)), width=1)
ink(lp, "R", .9)
def person(x, y, h, face, hair=False):
    hr = h * .12
    dlv.ellipse(Pp([(x - hr, y - h), (x + hr, y - h + 2 * hr)]), fill=255)                  # 头
    if hair:
        dlv.polygon(Pp([(x - hr * 1.1, y - h + hr), (x - face * hr * 1.6, y - h + hr * 4.2), (x + face * hr * .2, y - h + hr * 2)]), fill=255)
    dlv.polygon(Pp([(x - h * .1, y - h + 2.2 * hr), (x + h * .1, y - h + 2.2 * hr),        # 长袍
                    (x + h * .2, y), (x - h * .2, y)]), fill=255)
    hx_, hy_ = x + face * h * .36, y - h * .48                                               # 伸出去的手
    dlv.line(Pp([(x + face * h * .05, y - h * .7), (hx_, hy_)]), fill=255, width=3)
    return hx_, hy_
a1 = person(LX - 15, LY, 44, 1)
a2 = person(LX + 15, LY, 37, -1, hair=True)
dlv.ellipse(Pp([((a1[0] + a2[0]) / 2 - 2.2, (a1[1] + a2[1]) / 2 - 2.2), ((a1[0] + a2[0]) / 2 + 2.2, (a1[1] + a2[1]) / 2 + 2.2)]), fill=255)
cover(lv_); rim(lv_, "R", .95)
ed = (np.asarray(lv_.filter(ImageFilter.MaxFilter(5)), np.float32) - np.asarray(lv_, np.float32)).clip(0, 255)
ink(Image.fromarray(ed.astype(np.uint8)), "R", .55); del ed

# ================= 塔身亮边 + 缩回 + 暗角 =================
rim(tw_, "G", .55)
out = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)); del img
out = out.resize((W, H), Image.LANCZOS)
o = np.asarray(out, np.float32) / 255
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
vig = np.clip(1 - ((xx - W / 2) / W) ** 2 * 1.2 - ((yy - H * .5) / H) ** 2 * 1.3, 0, 1)[..., None]
o = C["N"] + (o - C["N"]) * (0.45 + 0.55 * vig)
Image.fromarray((np.clip(o, 0, 1) * 255).astype(np.uint8)).save(f"babel_s{SEED}.png")
print("ok")
