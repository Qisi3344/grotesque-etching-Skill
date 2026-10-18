"""怪诞蚀刻 · No.05《通古斯》Siberia, 1908-06-30 07:17
一道比太阳还亮的火球砸下来，八百万棵树向四面齐齐倒下，像车轮的辐条；
诡异的是正中心那片树反而立着没倒。几百公里外的人被热浪掀翻，地上却没有坑。
倒木在地上铺成巨大的放射状辐条退向地平线；正中心立着一只苍白、半透明、
长满眼睛的巨鹿灵，一直看着这一切。全画唯一的暖色：天上那团没散尽的火。
配色 07「异质生命」：#171B20 底 / #7EAAA0 变异蓝绿(远) / #D7DFA4 突变嫩绿(倒木)
            / #B7A0C8 异形灰紫(鹿) / #D78D78 组织珊瑚(火焦点)
概念：绮思 · 代码：扶光
用法：python tunguska.py [种子]
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

HZ = 520                       # 地平线
CX, CZ = 600, 820              # 爆心（辐条消失点）在地面上的位置

# ---------- 1. 天空：横向断线，炸开处最亮；顶上留黑 ----------
L = {k: new() for k in "BGVR"}
nz = fbm(120)
for y in range(0, HZ, 3):
    x = 0
    while x < W:
        sg = rng.uniform(20, 150)
        glow = math.exp(-((x - CX) ** 2) / (2 * 320 ** 2)) * (1 - y / HZ)
        t = np.clip(.03 + .4 * (y / HZ) ** 1.8 + .5 * glow + .12 * (nz[y, min(int(x), W - 1)] - .5), 0, 1)
        if rng.random() < t * 1.3: L["B"][1].line(Pp([(x, y), (x + sg, y + rng.uniform(-.5, .5))]), fill=255, width=1)
        x += sg + rng.uniform(4, 26) * (1.2 - t)
for _ in range(90):
    x, y = rng.uniform(0, W), rng.uniform(0, HZ - 40) * rng.random() ** .4
    r = rng.uniform(.6, 1.4); L["B"][1].ellipse(Pp([(x - r, y - r), (x + r, y + r)]), fill=255)

# ---------- 2. 火球：天上那团没散尽的火（唯一的暖色焦点） ----------
FX, FY = CX, 250
for k in range(130):
    a = rng.uniform(0, 2 * math.pi); r0 = rng.uniform(6, 26); r1 = r0 + rng.uniform(10, 150) * rng.random() ** 1.4
    L["R"][1].line(Pp([(FX + r0 * math.cos(a), FY + r0 * math.sin(a)), (FX + r1 * math.cos(a), FY + r1 * math.sin(a))]), fill=int(120 + 135 * rng.random()), width=1)
for r in range(6, 30, 4): L["R"][1].ellipse(Pp([(FX - r, FY - r), (FX + r, FY + r)]), outline=255, width=1)
# 火往下砸的一道光柱，隐隐连到爆心
for _ in range(40):
    xx0 = FX + rng.normal(0, 30); L["R"][1].line(Pp([(xx0, FY + 24), (CX + rng.normal(0, 24), CZ - 180)]), fill=int(40 + 60 * rng.random()), width=1)
for k in "BR": ink(L[k][0], k, .9 if k == "B" else 1)

# ---------- 3. 地面：倒木铺成放射状辐条，退向地平线 ----------
grnd, dg = new(); dg.rectangle(Pp([(0, HZ), (W, H)]), fill=255)
cover(grnd)                                   # 地面压成底色
# 地面排线（近密远疏），营造一个大平面
gl, dgl = new()
for y in range(HZ, H, 3):
    f = (y - HZ) / (H - HZ)
    for _ in range(int(5 + 26 * f)):
        x = rng.uniform(-40, W); sg = rng.uniform(14, 90) * (1.2 - .5 * f)
        dgl.line(Pp([(x, y), (x + sg, y)]), fill=255, width=1)
ink(gl, "B", .4)

def ground(px, py):
    """把爆心平面坐标 (px,py)，py>0 朝镜头，投影到画面"""
    d = 1 + py / 420                           # 近大远小
    sx = CX + px / d
    sy = CZ + py / d * 1.0
    return sx, sy, d

tr, dtr = new()
RING = 96                                      # 更密的角度条数
for i in range(RING):
    ang = 2 * math.pi * i / RING + rng.uniform(-.03, .03)
    inner = rng.uniform(96, 140)               # 中心一圈立木不倒 → 留空
    rr = inner
    while rr < 820:
        trunk = rng.uniform(70, 150)           # 一根树干的长度
        px, py = rr * math.cos(ang), rr * math.sin(ang) - 40
        ex, ey = (rr + trunk) * math.cos(ang), (rr + trunk) * math.sin(ang) - 40
        x0, y0, d = ground(px, py)             # 根部（朝爆心）
        x1, y1, d2 = ground(ex, ey)            # 梢部（朝外）
        if py < -360 or ey < -360 or y0 < HZ or y1 < HZ:
            rr += trunk + rng.uniform(10, 30); continue
        wroot = max(2, int(7 / d))             # 根粗梢细
        wtip = max(1, int(2 / d2))
        n = 6
        for s2 in range(n):                    # 分段，模拟树干带点弯
            t0, t1 = s2 / n, (s2 + 1) / n
            ax = x0 + (x1 - x0) * t0 + rng.uniform(-2, 2); ay = y0 + (y1 - y0) * t0
            bx = x0 + (x1 - x0) * t1 + rng.uniform(-2, 2); by = y0 + (y1 - y0) * t1
            w = int(wroot + (wtip - wroot) * t0)
            dtr.line(Pp([(ax, ay), (bx, by)]), fill=int(140 + 90 * rng.random()), width=max(1, w))
        # 树根盘：根部一个翻起的圆
        if rng.random() < .5:
            rd = 7 / d
            dtr.ellipse(Pp([(x0 - rd, y0 - rd), (x0 + rd, y0 + rd)]), outline=255, width=max(1, int(2 / d)))
            for _ in range(4):
                aa = rng.uniform(0, 2 * math.pi)
                dtr.line(Pp([(x0, y0), (x0 + rd * 1.6 * math.cos(aa), y0 + rd * 1.6 * math.sin(aa))]), fill=200, width=1)
        # 几根折断的枝桠
        for _ in range(rng.integers(0, 3)):
            bt = rng.uniform(.2, .9)
            bxp = x0 + (x1 - x0) * bt; byp = y0 + (y1 - y0) * bt
            ba = ang + rng.choice([-1, 1]) * rng.uniform(.5, 1.1)
            bl = rng.uniform(14, 30) / d
            dtr.line(Pp([(bxp, byp), (bxp + bl * math.cos(ba), byp + bl * math.sin(ba))]), fill=180, width=max(1, int(2 / d)))
        rr += trunk + rng.uniform(6, 24)
ink(tr, "G", .95)

# ---------- 4. 中心立木：没倒的那一片，竖着的焦黑树桩 ----------
st, dst = new()
for _ in range(90):
    a = rng.uniform(0, 2 * math.pi); r = rng.uniform(0, 120)
    px, py = r * math.cos(a), r * math.sin(a) - 40
    x0, y0, d = ground(px, py)
    if y0 < HZ: continue
    h = rng.uniform(50, 140) / d
    dst.line(Pp([(x0, y0), (x0 + rng.uniform(-5, 5), y0 - h)]), fill=255, width=max(1, int(4 / d)))
    for _ in range(rng.integers(0, 3)):        # 立木上残留的断枝
        ty = y0 - rng.uniform(.3, .9) * h
        dst.line(Pp([(x0, ty), (x0 + rng.choice([-1, 1]) * rng.uniform(8, 20) / d, ty - rng.uniform(0, 10) / d)]), fill=255, width=max(1, int(2 / d)))
cover(st); rim(st, "G", .8)

# ---------- 5. 鹿灵：半透明，长满眼睛，立在爆心 ----------
DX, DY = CX + 150, CZ - 300    # 鹿缩小、后移，不盖住倒木
DSC = 0.62                     # 鹿整体缩放
deer, dd = new()
# 躯干：有背脊和胸腹起伏的侧身轮廓（从臀经背到肩到胸腹一圈）
body = [(DX + 118, DY + 6), (DX + 96, DY - 40), (DX + 40, DY - 54),      # 臀→背
        (DX - 36, DY - 50), (DX - 92, DY - 40),                          # 背到肩
        (DX - 128, DY - 10), (DX - 150, DY - 36),                        # 肩前转出胸
        (DX - 150, DY + 26), (DX - 120, DY + 20),                        # 胸
        (DX - 70, DY + 70), (DX + 10, DY + 76), (DX + 80, DY + 64),      # 腹（略垂）
        (DX + 120, DY + 48)]
dd.polygon(Pp(body), fill=255)
# 颈：从肩斜着往左上伸出
dd.polygon(Pp([(DX - 110, DY - 44), (DX - 150, DY - 34), (DX - 196, DY - 120),
               (DX - 170, DY - 128), (DX - 128, DY - 20)]), fill=255)
# 头：鹿的侧脸，带口鼻
HDX, HDY = DX - 196, DY - 140
dd.polygon(Pp([(HDX + 24, HDY + 6), (HDX - 6, HDY - 12), (HDX - 40, HDY - 6),
               (HDX - 46, HDY + 8), (HDX - 20, HDY + 16), (HDX + 20, HDY + 22)]), fill=255)
dd.polygon(Pp([(HDX - 2, HDY - 10), (HDX + 10, HDY - 40), (HDX + 20, HDY - 10)]), fill=255)   # 耳
# 四条细长的腿，前后错开
for lx, bend in ((DX - 104, -10), (DX - 70, 8), (DX + 72, -8), (DX + 104, 10)):
    knee = (lx + bend, DY + 150)
    dd.line(Pp([(lx, DY + 60), knee, (lx + bend * .4, DY + 320)]), fill=255, width=5)
    dd.line(Pp([(lx + bend * .4, DY + 320), (lx + bend * .4 + 6, DY + 332)]), fill=255, width=6)  # 蹄
# 短尾
dd.line(Pp([(DX + 118, DY + 2), (DX + 140, DY + 36)]), fill=255, width=5)
# 巨大的鹿角，从头顶像枯枝分叉上去
for sx in (-1, 1):
    ax, ay = HDX + 4 + sx * 6, HDY - 36
    pts = [(ax, ay)]
    for k in range(5):
        ax += sx * rng.uniform(16, 30); ay -= rng.uniform(26, 46)
        dd.line(Pp([pts[-1], (ax, ay)]), fill=255, width=max(2, 6 - k))
        pts.append((ax, ay))
        if k >= 1 and rng.random() < .9:
            bx, by = ax + sx * rng.uniform(18, 38), ay - rng.uniform(0, 28)
            dd.line(Pp([(ax, ay), (bx, by)]), fill=255, width=max(1, 4 - k))
deer_m = np.asarray(deer, np.float32) / 255
# 半透明：只落很淡的一层，再描一道亮轮廓
ink(Image.fromarray((deer_m * 90).astype(np.uint8)), "V", 1)
rim(deer, "V", .9)
# 眼睛：身上、角上，一簇簇睁开的小眼
eye, de = new()
m = deer_m > .3
ys, xs = np.where(m[::6, ::6])
idx = rng.choice(len(xs), size=min(70, len(xs)), replace=False)
for ii in idx:
    ex, ey = xs[ii] * 6 / S, ys[ii] * 6 / S
    er = rng.uniform(3, 7)
    de.ellipse(Pp([(ex - er, ey - er * .6), (ex + er, ey + er * .6)]), outline=255, width=1)
    de.ellipse(Pp([(ex - er * .35, ey - er * .35), (ex + er * .35, ey + er * .35)]), fill=255)
ink(eye, "V", .9)
# 几只眼睛是珊瑚色的，让它更活
eye2, de2 = new()
for _ in range(10):
    ii = rng.choice(idx); ex, ey = xs[ii] * 6 / S, ys[ii] * 6 / S
    de2.ellipse(Pp([(ex - 2, ey - 2), (ex + 2, ey + 2)]), fill=255)
ink(eye2, "R", .8)

# ---------- 6. 远处逃散的小人剪影 ----------
ppl, dp = new()
for _ in range(7):
    px = rng.uniform(80, W - 80); py = rng.uniform(HZ + 20, HZ + 70)
    if abs(px - CX) < 150: continue
    dp.ellipse(Pp([(px - 2, py - 10), (px + 2, py - 6)]), fill=255)
    dp.line(Pp([(px, py - 6), (px, py)]), fill=255, width=3)
    dp.line(Pp([(px - 4, py - 4), (px + 4, py - 2)]), fill=255, width=2)
cover(ppl); rim(ppl, "B", .7)

# ---------- 缩回 + 暗角 ----------
out = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)); del img
out = out.resize((W, H), Image.LANCZOS)
o = np.asarray(out, np.float32) / 255
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
vig = np.clip(1 - ((xx - W / 2) / W) ** 2 * 1.2 - ((yy - H * .5) / H) ** 2 * 1.3, 0, 1)[..., None]
o = C["N"] + (o - C["N"]) * (0.45 + 0.55 * vig)
Image.fromarray((np.clip(o, 0, 1) * 255).astype(np.uint8)).save(f"tunguska_s{SEED}.png")
print("ok")
