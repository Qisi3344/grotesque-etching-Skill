"""怪诞蚀刻 · No.02《黑死病》
鸟嘴面具长成钟塔，喙伸进夜空；屋顶上的巨蚤和它对望；
黑家鼠的骨架横跨黑水当桥，运尸的小人走在脊椎上；鼠疫杆菌像灯笼从城里飘起。
唯一的焦点：面具的镜片。
用法：python plague_tower.py [种子] [配色 parasite|fossil]
"""
import numpy as np, math, sys
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import distance_transform_edt, gaussian_filter

SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 1
PAL = sys.argv[2] if len(sys.argv) > 2 else "parasite"
rng = np.random.default_rng(SEED)
S = 2; W, H = 1200, 1500; WS, HS = W * S, H * S

def hx(h): return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.float32) / 255
# 角色：A 主刻线（骨、面具亮部） B 次刻线 C 冷/暗刻线 F 唯一焦点
PALETTES = {
    # 10 古生物化石：底 = 地层深灰 #4F514A 压到约 37%
    "fossil":   dict(N="#1D1E1B", A="#E8D9B9", B="#C6AA7D", C="#85816D", D="#4F514A", F="#A17F61"),
    # 13 寄生生物：底 = 寄生深棕 #51434B 压到约 37%
    "parasite": dict(N="#1E191C", A="#D7B66D", B="#9BAA87", C="#7A91A0", D="#51434B", F="#C98C9A"),
}
C = {k: hx(v) for k, v in PALETTES[PAL].items()}
img = np.ones((HS, WS, 3), np.float32) * C["N"]
def lay(alpha, col, k=1.0):
    global img
    a = np.clip(alpha * k, 0, 1)[..., None]; img = img * (1 - a) + C[col] * a
def P(pts): return [(x * S, y * S) for x, y in pts]
def canvas(): im = Image.new("L", (WS, HS), 0); return im, ImageDraw.Draw(im)
def arr(im): return np.asarray(im, np.float32) / 255
def curve(p0, p1, p2, n=40):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in np.linspace(0, 1, n)]
LIGHT = np.array([-.55, -.65, .52]); LIGHT /= np.linalg.norm(LIGHT)

def engrave(mask, spacing=7, mode="contour", angle=0., gain=1., rim=True, wob=1.5, gamma=1., smooth=3.5, phase=None, noise=.8):
    """mask: 0/1 数组（2× 画布）→ 刻线的 alpha。线沿轮廓走，受光越强线越粗。"""
    ys, xs = np.nonzero(mask > .5)
    if len(ys) == 0: return np.zeros((HS, WS), np.float32)
    y0, y1, x0, x1 = max(ys.min() - 8, 0), min(ys.max() + 8, HS), max(xs.min() - 8, 0), min(xs.max() + 8, WS)
    m = mask[y0:y1, x0:x1] > .5
    d = gaussian_filter(distance_transform_edt(m), smooth) * m
    hgt = gaussian_filter(np.sqrt(d) * 6, 3 + smooth * .5)
    gy, gx = np.gradient(hgt)
    n = np.dstack([-gx, -gy, np.ones_like(gx)]); n /= np.linalg.norm(n, axis=2, keepdims=True)
    tone = np.clip(n @ LIGHT, 0, 1) ** gamma * gain
    tone = np.clip(tone * (.55 + .45 * np.clip(d / 18, 0, 1)) + .0, 0, 1)
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    if phase is not None: ph = phase[y0:y1, x0:x1]
    elif mode == "contour": ph = d
    else: ph = xx * math.cos(angle) + yy * math.sin(angle)
    ph = ph + wob * np.sin(xx / 23 + yy / 31) + noise * gaussian_filter(rng.standard_normal(m.shape).astype(np.float32), 3) * 6
    v = .5 + .5 * np.cos(2 * math.pi * ph / spacing)
    a = np.clip((v - (1 - tone * .95)) / .14, 0, 1)
    if rim:                                              # 轮廓：受光一侧刻一道实线
        edge = m & (distance_transform_edt(m) < 2.4)
        lit = np.clip((-gx * LIGHT[0] - gy * LIGHT[1]) * 3 + .25, 0, 1)
        a = np.maximum(a, edge * (.35 + .65 * lit))
    out = np.zeros((HS, WS), np.float32); out[y0:y1, x0:x1] = a * m
    return out

# ---------- 底版：铜版的细擦痕 + 双线框 ----------
yyF, xxF = np.mgrid[0:H, 0:W].astype(np.float32)
pl, dp = canvas()
for _ in range(900):
    x, y = rng.uniform(0, W), rng.uniform(0, H); L_ = rng.uniform(20, 160); a = rng.normal(0, .06)
    dp.line(P([(x, y), (x + L_ * math.cos(a), y + L_ * math.sin(a))]), fill=255, width=1)
lay(arr(pl), "D", .55)
fr, df = canvas()
df.rectangle(P([(40, 40), (W - 40, H - 40)]), outline=255, width=3)
df.rectangle(P([(52, 52), (W - 52, H - 52)]), outline=255, width=1)
for t in range(52, W - 52, 24):
    df.line(P([(t, 40), (t, 46)]), fill=255, width=1); df.line(P([(t, H - 46), (t, H - 40)]), fill=255, width=1)
lay(arr(fr), "C", .8)

# ---------- FIG. I 鼠蚤（侧面，高高拱起的背，巨大的后腿） ----------
FX, FY = 300, 320
fl, d1 = canvas(); legs, d2 = canvas()
back = curve((FX - 165, FY + 20), (FX - 110, FY - 175), (FX + 120, FY - 130), 30) + curve((FX + 120, FY - 130), (FX + 215, FY - 70), (FX + 175, FY + 60), 20)[1:]
belly = curve((FX + 175, FY + 60), (FX + 60, FY + 140), (FX - 80, FY + 95), 20)[1:] + curve((FX - 80, FY + 95), (FX - 150, FY + 80), (FX - 200, FY + 60), 12)[1:]
d1.polygon(P(back + belly + [(FX - 205, FY + 40)]), fill=255)              # 侧扁、拱背、头尖尖地贴在身上

# ======================= 构图 =======================
# 左：鸟嘴面具长成的钟塔，喙横伸进夜空；右：屋顶上蹲着一只巨蚤，两者隔空对望
# 下：黑家鼠的骨架横跨黑水当桥，运尸的小人走在脊椎上；鼠疫杆菌像灯笼一样从城里飘起
yyS, xxS = np.mgrid[0:HS, 0:WS].astype(np.float32)
def fbm(scale, oct=4):
    out = np.zeros((H, W), np.float32); a = 1; t = 0
    for o in range(oct):
        s = max(2, int(scale / 2 ** o))
        g = rng.random((H // s + 3, W // s + 3)).astype(np.float32)
        im = np.asarray(Image.fromarray((g * 255).astype(np.uint8)).resize((W + 3 * s, H + 3 * s), Image.BICUBIC), np.float32)[:H, :W] / 255
        out += a * im; t += a; a *= .5
    return out / t
WATER = 1250

# ---------- 夜空：横向断续刻线，顶上几乎纯黑，越往下越密 ----------
sk, dsk = canvas()
nz = fbm(140)
for y in range(0, WATER, 3):
    x = 0
    while x < W:
        L_ = rng.uniform(15, 120); t = np.clip(.02 + .55 * (y / WATER) ** 2.2 + .25 * (nz[y, min(int(x), W - 1)] - .5), 0, 1)
        if rng.random() < t: dsk.line(P([(x, y + rng.uniform(-.5, .5)), (x + L_, y + rng.uniform(-.5, .5))]), fill=255, width=1)
        x += L_ + rng.uniform(5, 40) * (1.3 - t)
for _ in range(70):
    x, y = rng.uniform(60, W - 60), rng.uniform(60, 600); r = rng.uniform(.6, 1.5)
    dsk.ellipse(P([(x - r, y - r), (x + r, y + r)]), fill=255)
lay(arr(sk), "C", .75)

# ---------- 薄雾：curl noise 流线，横着漂 ----------
gy_, gx_ = np.gradient(fbm(150, 3))
def mist(n, y0, y1, col, k, seedx=0):
    m_, dm_ = canvas()
    for _ in range(n):
        x, y = rng.uniform(-50, W), rng.uniform(y0, y1); pts = [(x, y)]
        for _k in range(int(rng.uniform(25, 80))):
            i, j = int(np.clip(y, 0, H - 1)), int(np.clip(x, 0, W - 1))
            vx, vy = gy_[i, j] * 900 + 1.6, -gx_[i, j] * 900 - .15
            nn = math.hypot(vx, vy) + 1e-6; x += 3 * vx / nn; y += 3 * vy / nn
            if not (0 < x < W and y0 - 60 < y < y1 + 40): break
            pts.append((x, y))
        if len(pts) > 4: dm_.line(P(pts), fill=255, width=1)
    lay(arr(m_), col, k)
mist(700, 900, 1240, "C", .55)

# ---------- 鼠疫杆菌灯笼（画在建筑后面的一批） ----------
def bacilli(n, region, scale, k, avoid):
    rd, drd = canvas(); en, den = canvas(); placed = []
    for _ in range(600):
        if len(placed) >= n: break
        x, y = rng.uniform(*region[0]), rng.uniform(*region[1])
        if any(math.hypot(x - px, y - py) < 70 for px, py in placed) or avoid(x, y): continue
        a = rng.uniform(0, math.pi); L_ = rng.uniform(.8, 1.3) * scale; w = L_ * .42
        ux, uy = math.cos(a) * L_ / 2, math.sin(a) * L_ / 2
        drd.line(P([(x - ux, y - uy), (x + ux, y + uy)]), fill=255, width=int(w * S))
        for s_ in (-1, 1):
            ex, ey = x + s_ * ux, y + s_ * uy
            drd.ellipse(P([(ex - w / 2, ey - w / 2), (ex + w / 2, ey + w / 2)]), fill=255)
            e2x, e2y = x + s_ * ux * .6, y + s_ * uy * .6
            den.ellipse(P([(e2x - w * .28, e2y - w * .28), (e2x + w * .28, e2y + w * .28)]), fill=255)
        # 挂着的细丝（像灯笼的线，往下垂）
        drd.line(P(curve((x, y + w * .4), (x + rng.normal(0, 8), y + 30), (x + rng.normal(0, 14), y + rng.uniform(40, 80)), 10)), fill=128, width=1)
        placed.append((x, y))
    rm = arr(rd); em = arr(en)
    halo = gaussian_filter(em, 14 * S)
    lay(halo / (halo.max() + 1e-6), "B", .22 * k)
    lay(engrave((rm > .9).astype(np.float32), 3.5, gain=1.2, smooth=1.5), "B", k)
    lay((rm > .3) * (rm < .9) * 1.0, "C", .6 * k)
    lay(gaussian_filter(em, .8), "A", .9 * k)
    return placed

# ---------- 右岸：窄高的山墙房 ----------
houses, dhs = canvas(); hwin, dhw = canvas()
roofs = []
x = 930
for w_, h_ in ((70, 210), (95, 330), (60, 250), (90, 290)):
    top = WATER - h_
    dhs.rectangle(P([(x, top), (x + w_, WATER + 4)]), fill=255)
    pk = top - w_ * .9; dhs.polygon(P([(x - 6, top + 2), (x + w_ / 2, pk), (x + w_ + 6, top + 2)]), fill=255)
    roofs.append((x + w_ / 2, pk, w_))
    for wy in range(int(top + 18), WATER - 30, 26):
        for wx in range(int(x + 10), int(x + w_ - 14), 18):
            if rng.random() < .18: dhw.rectangle(P([(wx, wy), (wx + 5, wy + 9)]), fill=255)
    x += w_ - 4
hsm = arr(houses)

# ---------- 左：鸟嘴面具钟塔 ----------
HX, HY = 320, 560
tw, dtw = canvas()
dtw.ellipse(P([(HX - 200, HY - 215), (HX + 190, HY + 200)]), fill=255)                       # 头罩
dtw.polygon(P(curve((HX - 175, HY + 90), (HX - 210, HY + 400), (HX - 260, WATER + 4), 30) + [(HX + 260, WATER + 4)] +
              curve((HX + 260, WATER + 4), (HX + 200, HY + 400), (HX + 160, HY + 110), 30)), fill=255)  # 斗篷长成塔身
for bx_ in (HX - 300, HX + 240):                                                              # 扶壁
    dtw.polygon(P([(bx_, WATER + 4), (bx_ + 30, WATER - 330), (bx_ + 62, WATER - 330), (bx_ + 70, WATER + 4)]), fill=255)
    dtw.polygon(P([(bx_ + 30, WATER - 330), (bx_ + 46, WATER - 420), (bx_ + 62, WATER - 330)]), fill=255)
twm = arr(tw)
hat, dht = canvas()
dht.ellipse(P([(HX - 300, HY - 260), (HX + 280, HY - 195)]), fill=255)                      # 宽檐
dht.polygon(P(curve((HX - 150, HY - 235), (HX - 165, HY - 360), (HX - 120, HY - 400), 16) + curve((HX + 110, HY - 405), (HX + 155, HY - 360), (HX + 140, HY - 235), 16)), fill=255)
dht.ellipse(P([(HX - 125, HY - 425), (HX + 115, HY - 382)]), fill=255)
dht.polygon(P([(HX - 14, HY - 410), (HX - 3, HY - 560), (HX + 8, HY - 410)]), fill=255)        # 帽顶的尖塔
hatm = arr(hat)
brim_, dbr = canvas(); dbr.ellipse(P([(HX - 300, HY - 260), (HX + 280, HY - 195)]), fill=255); brm = arr(brim_)
TIP = (905, 735)
top_e = curve((HX + 150, HY - 95), (HX + 430, HY - 60), TIP, 44)
bot_e = curve((TIP[0] - 8, TIP[1] + 10), (HX + 420, HY + 120), (HX + 140, HY + 120), 44)
bk, dbk = canvas(); dbk.polygon(P(top_e + bot_e), fill=255); bkm = arr(bk) * (1 - twm)
twm = twm * (1 - hatm)

lay(np.clip(twm + hatm + bkm + hsm, 0, 1), "N")                                               # 剪影盖掉后面的刻线
# 塔身：竖向排线；头罩：沿轮廓
body = twm * (yyS > (HY + 150) * S)
head = twm * (1 - body)
seam, dsm = canvas()
for t in (.2, .45, .7):                                                                       # 喙上的缝线
    i = int(t * 43); (ax, ay), (bx2, by2) = top_e[i], bot_e[43 - i]
    dsm.line(P(curve((ax, ay), ((ax + bx2) / 2 + 16, (ay + by2) / 2), (bx2, by2), 12)), fill=255, width=7 * S)
dsm.line(P(curve((HX - 190, HY - 60), (HX, HY + 20), (HX + 175, HY - 30), 20)), fill=255, width=11 * S)   # 头带
sm = arr(seam)
lay(engrave(np.clip(head - sm, 0, 1), 6.5, gain=1.0, gamma=2.0, smooth=18, mode="angle", angle=1.0), "B")
lay(engrave(body, 6, mode="angle", angle=math.pi / 2 - .03, gain=.95, gamma=2.4, smooth=30), "B", .9)
lay(engrave(brm, 4.5, mode="angle", angle=math.pi / 2 - .04, gain=.95, gamma=1.8, smooth=4), "C")
lay(engrave(hatm * (1 - brm), 6, mode="angle", angle=0., gain=.95, gamma=2.0, smooth=14), "C")
_ab, _dab = canvas(); _dab.polygon(P(top_e + [(TIP[0] + 60, 0), (HX, 0)]), fill=255)
beak_ph = distance_transform_edt(arr(_ab) < .5).astype(np.float32)
lay(engrave(np.clip(bkm - sm, 0, 1), 5.5, gain=1.1, gamma=1.6, smooth=9, phase=beak_ph), "A")
lay(engrave(np.clip(sm * (twm + bkm), 0, 1), 4, gain=1.1, rim=False), "C", .9)
# 塔身的拱窗：几扇暖黄，大多是黑的
aw, daw = canvas(); awl, dawl = canvas()
for row, yw in enumerate(range(HY + 260, WATER - 60, 110)):
    half = 70 + row * 22
    for xw in np.arange(HX - half, HX + half + 1, 46):
        lit = rng.random() < .22
        dd = dawl if lit else daw
        dd.rectangle(P([(xw - 7, yw), (xw + 7, yw + 30)]), fill=255); dd.ellipse(P([(xw - 7, yw - 7), (xw + 7, yw + 7)]), fill=255)
lay(arr(aw), "N"); lay(arr(awl), "A", .9)
# 塔脚下的小城
tn, dtn = canvas(); tnw, dtnw = canvas()
x = 40
while x < 640:
    w_ = rng.uniform(34, 60); h_ = rng.uniform(40, 95); top = WATER - h_
    dtn.rectangle(P([(x, top), (x + w_, WATER + 4)]), fill=255)
    dtn.polygon(P([(x - 3, top + 1), (x + w_ / 2, top - w_ * .8), (x + w_ + 3, top + 1)]), fill=255)
    if rng.random() < .35: dtnw.rectangle(P([(x + w_ / 2 - 3, top + 14), (x + w_ / 2 + 3, top + 24)]), fill=255)
    x += w_ + rng.uniform(-6, 6)
tnm = arr(tn)
lay(tnm, "N"); lay(engrave(tnm, 4, mode="angle", angle=math.pi / 2, gain=.7, gamma=2.0, smooth=2), "C", .6); lay(arr(tnw), "A", .9)
# 右岸房子
lay(engrave(hsm, 5, mode="angle", angle=math.pi / 2 - .02, gain=.85, gamma=2.2, smooth=8), "C")
lay(arr(hwin), "A", .9)

# ---------- 镜片：全图唯一的焦点 ----------
EX, EY, ER = HX + 85, HY - 10, 58
ln, dln = canvas(); dln.ellipse(P([(EX - ER - 14, EY - ER - 14), (EX + ER + 14, EY + ER + 14)]), fill=255)
gl, dgl = canvas(); dgl.ellipse(P([(EX - ER, EY - ER), (EX + ER, EY + ER)]), fill=255)
lay(arr(ln), "N"); lay(engrave(np.clip(arr(ln) - arr(gl), 0, 1), 3.5, gain=1.2), "B")
rr = np.hypot(xxS - EX * S, yyS - EY * S) / S
glass = (rr < ER).astype(np.float32)
conc = (.5 + .5 * np.cos(2 * math.pi * rr / 6)) > .75 - .5 * np.exp(-rr / 24)
lay(glass * conc * np.clip(1.15 - rr / ER, 0, 1), "F")
lay(gaussian_filter(glass, 18 * S) * (1 - glass) * (1 - twm * 0), "F", .18)
hl, dhl = canvas(); dhl.arc(P([(EX - ER + 10, EY - ER + 10), (EX + ER - 10, EY + ER - 10)]), 200, 260, fill=255, width=4 * S)
lay(arr(hl), "A")

# ---------- 屋顶上的巨蚤（侧面，头朝左对着喙尖） ----------
rx, ry, rw = max(roofs, key=lambda r: -r[1] * 0 + r[2])[:3]
rx, ry, rw = roofs[1]
FX, FY, FS = rx + 10, ry - 70, .62
def F_(x, y): return (FX + (x) * FS, FY + (y) * FS)
fl, d1 = canvas(); lg, d2 = canvas()
back = curve(F_(-165, 20), F_(-110, -175), F_(120, -130), 30) + curve(F_(120, -130), F_(215, -70), F_(175, 60), 20)[1:]
belly = curve(F_(175, 60), F_(60, 140), F_(-80, 95), 20)[1:] + curve(F_(-80, 95), F_(-150, 80), F_(-200, 60), 12)[1:]
d1.polygon(P(back + belly + [F_(-205, 40)]), fill=255)
def seg(dr, pts, w0, w1):
    for i in range(len(pts) - 1):
        w = w0 + (w1 - w0) * i / max(1, len(pts) - 2)
        dr.line(P([pts[i], pts[i + 1]]), fill=255, width=int(w * S)); x, y = pts[i + 1]
        dr.ellipse(P([(x - w / 2, y - w / 2), (x + w / 2, y + w / 2)]), fill=255)
LEGS = [[F_(-140, 70), F_(-175, 125), F_(-150, 175), F_(-190, 205), F_(-205, 212)],
        [F_(-40, 105), F_(-70, 165), F_(-40, 205), F_(-75, 230), F_(-90, 235)],
        [F_(70, 95), F_(165, 150), F_(75, 175), F_(190, 235), F_(250, 248)]]
for (a_, b_) in ((F_(-165, 30), F_(-105, 110)), (F_(-70, 60), F_(-10, 130)), (F_(20, 30), F_(130, 135))):
    d2.ellipse(P([a_, b_]), fill=255)
for k, L in enumerate(LEGS): seg(d2, L, (14, 16, 26)[k] * FS, (5, 5, 7)[k] * FS)
fm, lm = arr(fl), arr(lg)
lay(lm, "N"); lay(engrave(lm, 4, gain=1.1, smooth=1.5), "B")
lay(fm, "N"); lay(engrave(fm, 4.5, mode="angle", angle=.12, gain=1.0, gamma=1.6, smooth=6), "B")
gp, dg = canvas()
for k in range(1, 10):
    x = FX + (-150 + k / 10 * 330) * FS
    dg.line(P(curve((x - 25 * FS, FY - 200 * FS), (x + 10 * FS, FY - 30 * FS), (x - 15 * FS, FY + 150 * FS), 16)), fill=255, width=int(2.2 * S))
lay(arr(gp) * fm, "N")
br, db = canvas()
for k in range(120):
    i = rng.integers(2, len(back) - 2); bx, by = back[i]; bx += rng.normal(0, 3); by += rng.uniform(3, 55)
    L_ = rng.uniform(5, 13); a = math.radians(rng.uniform(15, 45))
    db.line(P([(bx, by), (bx + L_ * math.cos(a), by - L_ * math.sin(a) * .5)]), fill=255, width=1)
db.line(P(curve(F_(-160, -20), F_(-150, -55), F_(-120, -60), 10)), fill=255, width=2)
db.line(P([F_(-200, 50), F_(-212, 100)]), fill=255, width=2)
lay(arr(br), "A", .85)

# ---------- 鼠骨桥：脊椎横跨黑水，肋骨垂成拱 ----------
bn, dbn = canvas()
def bone(dr, a, b, w, knob=1.5):
    dr.line(P([a, b]), fill=255, width=int(w * S))
    for (x, y) in (a, b): dr.ellipse(P([(x - w * knob / 2, y - w * knob / 2), (x + w * knob / 2, y + w * knob / 2)]), fill=255)
spine = curve((560, 1236), (760, 1060), (960, 1180), 40)
for i, (x, y) in enumerate(spine):
    s_ = 22 - 6 * abs(i / 39 - .55)
    dbn.ellipse(P([(x - s_ * .55, y - s_ * .42), (x + s_ * .55, y + s_ * .42)]), fill=255)
    if i % 2 == 0: dbn.line(P([(x, y), (x - 4, y - s_ * .95)]), fill=255, width=3 * S)
for i in range(18, 33):
    x, y = spine[i]; L_ = WATER - y + 25 + 30 * math.sin((i - 18) / 14 * math.pi)
    dbn.line(P(curve((x, y + 5), (x - 6 - L_ * .08, y + L_ * .6), (x - 26 - (i - 18) * 1.3, y + L_), 16)), fill=255, width=6 * S)
SK = (950, 1170); k_ = 1.15
def K(x, y): return (SK[0] + x * k_, SK[1] + y * k_)
dbn.polygon(P([K(-20, -25), K(40, -48), K(110, -30), K(150, -10), K(158, 6), K(90, 20), K(20, 30), K(-20, 18)]), fill=255)
dbn.polygon(P([K(20, 32), K(130, 24), K(140, 34), K(40, 56), K(10, 50)]), fill=255)
dbn.line(P(curve(K(152, 4), K(166, 26), K(150, 44), 10)), fill=255, width=7 * S)
hole, dho = canvas()
dho.ellipse(P([K(55, -26), K(98, 6)]), fill=255); dho.ellipse(P([K(118, -8), K(130, 2)]), fill=255)
bone(dbn, (880, 1160), (860, 1215), 16); bone(dbn, (860, 1215), (875, WATER + 6), 12)            # 前肢＝桥墩
bone(dbn, (620, 1210), (690, 1250), 15)
tail = curve((560, 1236), (470, 1300), (420, 1360), 24) + curve((420, 1360), (390, 1420), (450, 1440), 14)[1:]
for i, (x, y) in enumerate(tail):
    s_ = 14 * (1 - i / len(tail)) + 3
    dbn.ellipse(P([(x - s_ * .6, y - s_ * .38), (x + s_ * .6, y + s_ * .38)]), fill=255)
bm = np.clip(arr(bn) - arr(hole), 0, 1)
lay((arr(bn) > .5) * 1.0, "N"); lay(engrave(bm, 5, gain=1.25, smooth=2), "A")

# ---------- 脊背上的小人：推运尸车、提灯、拄杖 ----------
fg, dfg = canvas()
def person(x, y, h, lean=0):
    dfg.ellipse(P([(x - h * .09 + lean, y - h), (x + h * .09 + lean, y - h * .8)]), fill=255)
    dfg.polygon(P([(x - h * .08 + lean, y - h * .8), (x + h * .1 + lean, y - h * .8), (x + h * .16, y), (x - h * .16, y)]), fill=255)
def on_spine(t):
    i = int(t * 39); x, y = spine[i]; return x, y - 20
for t, h, ln_ in ((.3, 34, 3), (.52, 32, -2), (.68, 33, 4)):
    x, y = on_spine(t); person(x, y, h, ln_)
x, y = on_spine(.42)                                                                         # 运尸车
dfg.rectangle(P([(x - 24, y - 16), (x + 22, y - 5)]), fill=255)
dfg.ellipse(P([(x - 18, y - 8), (x - 6, y + 4)]), fill=255); dfg.ellipse(P([(x + 6, y - 8), (x + 18, y + 4)]), fill=255)
for k in range(4): dfg.line(P([(x - 20 + k * 11, y - 16), (x - 16 + k * 11, y - 24)]), fill=255, width=3 * S)
x, y = on_spine(.82); person(x, y, 22); dfg.line(P([(x + 6, y - 20), (x + 12, y)]), fill=255, width=2 * S)
fgm = arr(fg)
lay(fgm, "N")
rimfg = np.clip(fgm - np.roll(np.roll(fgm, 3, 0), 3, 1), 0, 1)
lay(rimfg, "B", .9)

# ---------- 黑水：倒影刻线 ----------
wt, dwt = canvas()
for y in range(WATER + 4, H - 56, 4):
    x = 50
    while x < W - 50:
        L_ = rng.uniform(10, 70); t = .25 + .5 * ((y - WATER) / (H - WATER))
        if rng.random() < t * .8: dwt.line(P([(x, y), (x + L_, y)]), fill=255, width=1)
        x += L_ + rng.uniform(6, 50)
wtm = arr(wt) * (1 - np.flipud(np.zeros_like(fgm)))
# 倒影：岸上亮处的竖向拉长
refl = np.zeros((HS, WS), np.float32)
src = img.mean(2)
cut = WATER * S
n_ = HS - cut
refl[cut:, :] = gaussian_filter(np.flipud(src[max(cut - n_, 0):cut, :]), (10, 1))[:n_, :] if cut - n_ >= 0 else 0
lay(wtm * (1 - (arr(bn) > .5)), "C", .55)
lay(wtm * np.clip(refl * 3, 0, 1) * (1 - (arr(bn) > .5)), "B", .5)
mist(260, WATER - 30, WATER + 70, "C", .45)

# ---------- 前面一批灯笼 ----------
occ = np.clip(twm + hatm + bkm + hsm + (arr(bn) > .5) + tnm, 0, 1)
def avoid(x, y):
    i, j = int(np.clip(y * S, 0, HS - 1)), int(np.clip(x * S, 0, WS - 1))
    return occ[max(i - 60, 0):i + 60, max(j - 60, 0):j + 60].max() > .5 or math.hypot(x - EX, y - EY) < 160
bacilli(11, ((470, 1150), (160, 1050)), 34, 1.0, avoid)
bacilli(10, ((80, 1150), (90, 1000)), 18, .6, avoid)

# ---------- 档案边框 + 一行标签 ----------
fr, df = canvas()
df.rectangle(P([(36, 36), (W - 36, H - 36)]), outline=255, width=3)
df.rectangle(P([(48, 48), (W - 48, H - 48)]), outline=255, width=1)
lay(arr(fr), "C", .7)
try: FONT = lambda s: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", s * S)
except Exception: FONT = lambda s: ImageFont.load_default()
tx, dt = canvas()
dt.text((70 * S, (H - 46) * S - 6 * S), "No.02  ·  PESTIS NIGRA  ·  FIRENZE 1348", font=FONT(14), fill=255)
lay(arr(tx), "C", .85)

# 暗角：四周往底色收
vig = np.clip(1 - .85 * (np.hypot((xxS / WS - .5) * 1.1, (yyS / HS - .45)) / .75) ** 2.5, 0, 1)[..., None]
img = C["N"] + (img - C["N"]) * vig
out = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
out.save(f"plague_tower_{PAL}_s{SEED}.png"); print("ok")
