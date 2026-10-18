"""怪诞蚀刻 · No.04《泰坦尼克》North Atlantic, 1912-04-15 02:10
那晚没有月亮，海面平得像玻璃，幸存者说从没见过那么亮的星。
冰山长成一座苍白的鲸骨大教堂，肋骨一道道拱起戳进星空；水下那一大半只用虚线刻出来。
船很小，船头先沉，舷窗还亮着最后几排暖光，船尾上几个小人还在拉琴。
全画唯一的玫瑰色：前景救生艇上的一盏灯，和它碎在玻璃海里的倒影。
配色 16「液态组织」：#1E252D 底 / #526579 冷刻线 / #83B9B0 冰 / #E5DCCB 骨白与星 / #D7A66D 舷窗 / #B97B8C 灯
概念：绮思 · 代码：扶光
用法：python titanic.py [种子]
"""
import numpy as np, math, sys
from PIL import Image, ImageDraw, ImageFilter

SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 1
rng = np.random.default_rng(SEED)
S = 2; W, H = 1200, 1500; WS, HS = W * S, H * S
def hx(h): return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.float32) / 255
C = {"N": hx("#1E252D"), "B": hx("#526579"), "T": hx("#83B9B0"), "W": hx("#E5DCCB"),
     "Y": hx("#D7A66D"), "R": hx("#B97B8C")}

def fbm(scale, oct=4, shape=(H, W)):
    h, w = shape; out = np.zeros(shape, np.float32); a = 1; t = 0
    for o in range(oct):
        s = max(2, int(scale / 2 ** o))
        g = rng.random((h // s + 3, w // s + 3)).astype(np.float32)
        im = np.asarray(Image.fromarray((g * 255).astype(np.uint8)).resize((w + 3 * s, h + 3 * s), Image.BICUBIC), np.float32)[:h, :w] / 255
        out += a * im; t += a; a *= .5
    return out / t
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
DN = fbm(24, 2, (HS, WS)) > .45
def rim(mask_img, k, amt=1.):
    """只在剪影上沿刻一道断续亮边（全画同一个函数）"""
    m = np.asarray(mask_img) > 127
    top = m & ~np.roll(m, 3, axis=0)
    top = np.asarray(Image.fromarray((top * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5))) > 0
    ink(Image.fromarray(((top & DN) * 255).astype(np.uint8)), k, amt)

HY = 900                                     # 海平线
VX, VY = 430, 760                            # 鲸骨教堂的消失点

# ---------- 星空：顶上留黑，越往下横线越密；星星特别多 ----------
L = {k: new() for k in "BTW"}
nz = fbm(120)
for y in range(0, HY, 3):
    x = 0
    while x < W:
        sg = rng.uniform(20, 140)
        t = np.clip(.02 + .5 * (y / HY) ** 2.2 + .15 * (nz[y, min(int(x), W - 1)] - .5), 0, 1)
        if rng.random() < t * 1.3: L["B"][1].line(P([(x, y), (x + sg, y + rng.uniform(-.5, .5))]), fill=255, width=1)
        x += sg + rng.uniform(4, 30) * (1.2 - t)
stars = []
for _ in range(520):
    x, y = rng.uniform(0, W), rng.uniform(0, HY - 30) * rng.random() ** .3
    r = rng.choice([.6, .8, 1.0, 1.4, 2.2], p=[.35, .3, .2, .11, .04])
    L["W" if r > .9 else "T"][1].ellipse(P([(x - r, y - r), (x + r, y + r)]), fill=255)
    if r > 2: L["W"][1].line(P([(x - 7, y), (x + 7, y)]), fill=255); L["W"][1].line(P([(x, y - 7), (x, y + 7)]), fill=255)
    stars.append((x, y, r))
# ---------- 玻璃海：稀疏横线，星星的倒影竖着落进去 ----------
for y in range(HY + 4, H, 3):
    f = (y - HY) / (H - HY)
    for _ in range(int(6 + 20 * f)):
        x = rng.uniform(-40, W); sg = rng.uniform(10, 80) * (1.3 - .5 * f)
        L["B"][1].line(P([(x, y), (x + sg, y)]), fill=255, width=1)
for x, y, r in stars:
    if r > 1.2 and rng.random() < .4:
        ry = HY + (HY - y) * .35
        if ry < H: L["T"][1].line(P([(x, ry), (x, ry + 4 + 6 * r)]), fill=255, width=1)
for k in "BTW": ink(L[k][0], k, .7 if k == "B" else .9)

# ---------- 水下：冰山更大的那一半，只用虚线刻 ----------
uw, du = new()
for k in range(9):
    s = 1 - k * .07
    pts = [(VX + 380 * s * math.cos(a), HY + 20 + 520 * s * math.sin(a) ** .8) for a in np.linspace(0, math.pi, 80)]
    for i in range(0, len(pts) - 1, 2): du.line(P([pts[i], pts[i + 1]]), fill=255, width=1)
ink(uw, "T", .35)

# ---------- 冰山本体：参差的冰崖 ----------
berg = [(40, HY + 6), (70, 760), (110, 720), (130, 600), (180, 560), (210, 430), (260, 400), (300, 300),
        (360, 250), (400, 140), (430, 60), (460, 150), (500, 240), (560, 290), (600, 400), (650, 430),
        (690, 560), (740, 600), (780, 720), (820, 760), (850, HY + 6)]
bm, db = new(); db.polygon(P(berg), fill=255)
cover(bm)
hat, dh = new()                              # 冰面：沿 75° 的细排线，越近水线越密
for i in range(-300, 1300, 5):
    x0 = i; y0 = HY
    pts = [(x0 + t * math.cos(math.radians(-75)), y0 + t * math.sin(math.radians(-75))) for t in range(0, 900, 8)]
    for j in range(len(pts) - 1):
        yy = pts[j][1]
        if rng.random() < .25 + .55 * max(0., (yy - 60) / (HY - 60)) ** 1.5:
            dh.line(P([pts[j], pts[j + 1]]), fill=255, width=1)
hat_a = np.asarray(hat, np.float32) * (np.asarray(bm, np.float32) / 255)
ink(Image.fromarray(hat_a.astype(np.uint8)), "T", .55)
rim(bm, "W", .9)

# ---------- 鲸骨肋：一道道尖拱往消失点退，像教堂中殿 ----------
rb, dr = new(); rt, drt = new()
for k in range(8):
    s = .82 ** k
    hw = 300 * s; base = VY + (HY - VY) * s + 10 * (1 - s); top = VY - 560 * s
    def arch(off):
        R = hw * 1.5; c = R - hw
        out = []
        for t in np.linspace(0, 1, 40):
            y = base + (top - base) * t
            yy0 = base - (base - top) * 0  # 直段 + 尖拱
            if t < .35: x = hw
            else:
                u = (t - .35) / .65
                x = hw - (R - math.sqrt(max(R * R - (u * R * .93) ** 2, 0)))
            out.append((x + off, y))
        return out
    for side in (-1, 1):
        o = arch(0); i = arch(-22 * s)
        po = [(VX + side * x, y) for x, y in o]; pi = [(VX + side * x, y) for x, y in i]
        dr.line(P(po), fill=255, width=max(2, int(6 * s)))
        drt.line(P(pi), fill=255, width=max(1, int(3 * s)))
        for j in range(2, len(po) - 1, 1):          # 骨节之间的短横刻线
            dr.line(P([po[j], pi[j]]), fill=200, width=1)
    if k < 6:                                       # 椎骨：拱顶上一颗颗骨节
        ty = VY - 560 * s
        dr.ellipse(P([(VX - 12 * s, ty - 16 * s), (VX + 12 * s, ty + 6 * s)]), outline=255, width=2)
ink(rb, "W", .95); ink(rt, "T", .8)
inner, di = new()                                   # 中殿最深处：黑，只有几道冷线
s = .82 ** 7
di.rectangle(P([(VX - 300 * s + 8, VY - 300 * s), (VX + 300 * s - 8, VY + (HY - VY) * s)]), fill=255)
cover(inner)
for y in range(int(VY - 120 * s), int(VY + (HY - VY) * s), 6):
    L2, d2 = new(); d2.line(P([(VX - 60 * s, y), (VX + 60 * s, y)]), fill=255); ink(L2, "B", .5); break

# ---------- 船：很小，船头先沉，船尾翘起 ----------
sh, ds = new(); Lw, dw = new(); Lf, dff = new()
SX0, SA, SK = 925, math.radians(11), 1.3
def R(px, py):
    px, py = px * SK, py * SK
    return (SX0 + px * math.cos(SA) - py * math.sin(SA), HY - 8 + px * math.sin(SA) + py * math.cos(SA))
hull = [R(-110, -4), R(150, -4), R(158, -16), R(150, 0), R(-120, 6)]
ds.polygon(P(hull), fill=255)
ds.polygon(P([R(-90, -4), R(120, -4), R(118, -14), R(-86, -14)]), fill=255)               # 上层建筑
for k, fx in enumerate((-60, -20, 20, 60)):
    if k == 0:  # 第一根烟囱已经倒了
        ds.polygon(P([R(fx - 6, -14), R(fx + 34, -26), R(fx + 36, -20), R(fx - 2, -10)]), fill=255)
    else:
        ds.polygon(P([R(fx - 6, -14), R(fx + 6, -14), R(fx + 4, -40), R(fx - 8, -40)]), fill=255)
ds.line(P([R(-95, -14), R(-95, -60)]), fill=255, width=2); ds.line(P([R(130, -16), R(130, -55)]), fill=255, width=2)
for fx in (124, 132, 140):                                                                   # 船尾拉琴的小人
    ds.ellipse(P([R(fx - 1.6, -24), R(fx + 1.6, -20)]), fill=255); ds.line(P([R(fx, -20), R(fx, -16)]), fill=255, width=3)
for row in (-8, -12):
    for px in range(-40, 146, 7):
        if rng.random() < .55: dw.rectangle(P([R(px, row), R(px + 2.4, row + 1.8)]), fill=255)
cover(sh); rim(sh, "W", .7)
ink(Lw, "Y")
for _ in range(1):                                                                           # 船尾往上冒的一缕蒸汽
    pts = [R(30, -42)]
    for j in range(40): x, y = pts[-1]; pts.append((x + math.sin(j * .4) * 1.8 + .6, y - 5))
    dff.line(P(pts), fill=255, width=1)
ink(Lf, "T", .6)

# ---------- 前景：一艘救生艇，一盏灯 ----------
lb, dl = new(); Lr, dlr = new()
BX, BY = 300, 1240
dl.polygon(P([(BX - 95, BY), (BX + 95, BY), (BX + 78, BY + 22), (BX - 78, BY + 22)]), fill=255)
for k in range(9):
    hx_ = BX - 76 + k * 19 + rng.uniform(-3, 3); hy = BY - 10 - rng.uniform(0, 6)
    dl.ellipse(P([(hx_ - 6, hy - 7), (hx_ + 6, hy + 5)]), fill=255)
    dl.polygon(P([(hx_ - 8, hy + 3), (hx_ + 8, hy + 3), (hx_ + 10, BY + 2), (hx_ - 10, BY + 2)]), fill=255)
dl.line(P([(BX - 70, BY + 8), (BX - 150, BY + 50)]), fill=255, width=3 * S)                  # 桨
dl.line(P([(BX + 70, BY + 8), (BX + 150, BY + 46)]), fill=255, width=3 * S)
LX, LY = BX + 60, BY - 70
dl.line(P([(LX, LY + 6), (LX, BY)]), fill=255, width=2 * S)
cover(lb); rim(lb, "B", .8)
dlr.ellipse(P([(LX - 6, LY - 8), (LX + 6, LY + 6)]), fill=255)
for k in range(90):
    a = rng.uniform(0, 2 * math.pi); r0 = 12; r1 = r0 + rng.uniform(5, 60) * rng.random()
    dlr.line(P([(LX + r0 * math.cos(a), LY + r0 * math.sin(a)), (LX + r1 * math.cos(a), LY + r1 * math.sin(a))]), fill=255, width=1)
for y in range(BY + 26, H, 4):                                                               # 倒影碎在玻璃海里
    w_ = 16 * (1 - (y - BY) / (H - BY)) + 3
    dlr.line(P([(LX - w_ * rng.random(), y), (LX + w_ * rng.random(), y)]), fill=255, width=1)
ink(Lr, "R")

# ---------- 缩回原尺寸 + 暗角 ----------
out = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)); del img
out = out.resize((W, H), Image.LANCZOS)
o = np.asarray(out, np.float32) / 255
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
vig = np.clip(1 - ((xx - W / 2) / W) ** 2 * 1.2 - ((yy - H * .5) / H) ** 2 * 1.3, 0, 1)[..., None]
o = C["N"] + (o - C["N"]) * (0.45 + 0.55 * vig)
Image.fromarray((np.clip(o, 0, 1) * 255).astype(np.uint8)).save(f"titanic_s{SEED}.png")
print("ok")
