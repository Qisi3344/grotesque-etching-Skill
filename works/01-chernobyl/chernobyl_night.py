"""怪诞蚀刻 · No.01《切尔诺贝利》
旧蚀刻版画的细密刻线 × 暗黑童话。深色打底，刻线是亮的（白线刻）。
配色「标本编号」：#1E1B19 压深的墨迹褐（底/剪影，#514943 压到约 37%）/ #514943 墨迹褐/ #6E8FB1 档案蓝（夜空、远景）
/ #A1AA92 记录灰绿（青白烟）/ #E4D17B 标签黄（窗光）/ #CF6B54 编号朱红（反应堆的心）
1986-04-26 夜里，普里皮亚季的人站在铁路桥上看反应堆发光。
"""
import numpy as np, math, sys
from PIL import Image, ImageDraw, ImageFilter

SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 4
rng = np.random.default_rng(SEED)
S = 2                                   # 2x 超采样画刻线
W, H = 1200, 1500
WS, HS = W * S, H * S
C = {k: np.array(v, np.float32) / 255 for k, v in {
    "K": (0x51, 0x49, 0x43), "N": (0x1E, 0x1B, 0x19), "B": (0x6E, 0x8F, 0xB1), "G": (0xA1, 0xAA, 0x92),
    "Y": (0xE4, 0xD1, 0x7B), "R": (0xCF, 0x6B, 0x54)}.items()}
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)


def fbm(scale, oct=4, h=H, w=W):
    out = np.zeros((h, w), np.float32); a = 1; t = 0
    for o in range(oct):
        s = max(2, int(scale / 2 ** o))
        g = rng.random((h // s + 3, w // s + 3)).astype(np.float32)
        im = np.asarray(Image.fromarray((g * 255).astype(np.uint8)).resize((w + 3 * s, h + 3 * s), Image.BICUBIC), np.float32)[:h, :w] / 255
        out += a * im; t += a; a *= .5
    return out / t


L = {k: Image.new("L", (WS, HS), 0) for k in "BGYR"}           # 前景刻线（剪影之后画）
D = {k: ImageDraw.Draw(L[k]) for k in L}
LB = {k: Image.new("L", (WS, HS), 0) for k in "BGYR"}          # 背景刻线（会被剪影盖住）
DB = {k: ImageDraw.Draw(LB[k]) for k in LB}
SIL = Image.new("L", (WS, HS), 0); DS = ImageDraw.Draw(SIL)     # 剪影：盖掉后面的刻线
def P(pts): return [(x * S, y * S) for x, y in pts]

CORE = (640, 905)                       # 反应堆缺口
HORIZON = 1010
glow = np.exp(-np.hypot(xx - CORE[0], (yy - CORE[1]) * 1.3) / 260).astype(np.float32)

# ---------- 夜空：横向细刻线，越靠近光越密越连 ----------
n_sky = fbm(120)
sky_t = np.clip(0.0 + 0.28 * (yy / HORIZON) ** 2 + 0.6 * glow + 0.15 * (n_sky - .5), 0, 1)
for y in range(0, HORIZON + 40, 3):
    x = 0
    while x < W:
        seg = rng.uniform(20, 140)
        t = sky_t[min(y, H - 1), min(int(x), W - 1)]
        if rng.random() < t * 1.4:
            DB["B"].line(P([(x, y + rng.uniform(-.6, .6)), (x + seg, y + rng.uniform(-.6, .6))]), fill=255, width=1)
        x += seg + rng.uniform(4, 30) * (1.2 - t)
# 几颗星，像腐蚀出的小坑
for _ in range(90):
    x, y = rng.uniform(0, W), rng.uniform(0, 520)
    if glow[int(y), int(x)] < .15:
        r = rng.uniform(.6, 1.6); DB["G"].ellipse(P([(x - r, y - r), (x + r, y + r)]), fill=255)

# ---------- 烟：沿噪声旋度场走的流线，青白色，从缺口往上翻卷 ----------
fx = fbm(160, 3); fy = fbm(160, 3)
gy_, gx_ = np.gradient(fbm(140, 3))
def smoke_density(x, y):
    t = np.clip((CORE[1] - y) / 820, 0, 1)
    cx = CORE[0] + 170 * t ** 1.5 * math.sin(t * 2.2) + 90 * t
    w = 50 + 330 * t ** .9
    return max(0., 1 - abs(x - cx) / w) * (y < CORE[1] + 10)
for _ in range(1500):
    t0 = rng.random() ** .7
    y = CORE[1] - t0 * 820; x = CORE[0] + rng.normal(0, 40 + 280 * t0) + 120 * t0
    if smoke_density(x, y) < rng.random() * .6: continue
    pts = [(x, y)]
    for k in range(int(rng.uniform(20, 70))):
        i, j = int(np.clip(y, 0, H - 1)), int(np.clip(x, 0, W - 1))
        vx, vy = gy_[i, j] * 900, -gx_[i, j] * 900          # 旋度 → 打旋
        vy -= 1.3; vx += 0.35                              # 往上升，被风推向右
        n = math.hypot(vx, vy) + 1e-6
        x += 3 * vx / n; y += 3 * vy / n
        if smoke_density(x, y) <= 0 or y < 20: break
        pts.append((x, y))
    if len(pts) > 4:
        hi = smoke_density(*pts[0]) * (1 - t0 * .5)
        ink = "G" if rng.random() < .35 + .6 * hi else "B"
        D[ink].line(P(pts), fill=255, width=1 if rng.random() < .7 else 2)

# ---------- 远处怪诞的城：苏式板楼长出穹顶、尖塔、拱桥 ----------
def building(x0, w, h, kind):
    top = HORIZON - h
    DS.rectangle(P([(x0, top), (x0 + w, HORIZON + 5)]), fill=255)
    if kind == "dome":
        DS.ellipse(P([(x0 + w * .15, top - w * .45), (x0 + w * .85, top + w * .25)]), fill=255)
        DS.polygon(P([(x0 + w / 2 - 3, top - w * .45), (x0 + w / 2, top - w * .45 - rng.uniform(40, 110)), (x0 + w / 2 + 3, top - w * .45)]), fill=255)
    elif kind == "spire":
        DS.polygon(P([(x0, top), (x0 + w / 2, top - rng.uniform(120, 260)), (x0 + w, top)]), fill=255)
        for k in range(3):
            yk = top - 20 - k * 30; DS.rectangle(P([(x0 + w * .4, yk - 12), (x0 + w * .6, yk)]), fill=255)
    elif kind == "stack":
        DS.polygon(P([(x0 + w * .3, top), (x0 + w * .38, top - 160), (x0 + w * .62, top - 160), (x0 + w * .7, top)]), fill=255)
    # 窗光：暖黄，稀稀拉拉，越靠近反应堆越少（人走了）
    for wy in range(int(top + 10), HORIZON - 8, 14):
        for wx in range(int(x0 + 6), int(x0 + w - 8), 12):
            if rng.random() < 0.07 * (1 - glow[min(wy, H - 1), min(wx, W - 1)]):
                D["Y"].rectangle(P([(wx, wy), (wx + 5, wy + 7)]), fill=255)
    # 朝光一侧的轮廓刻线
    side = x0 + w if x0 + w / 2 < CORE[0] else x0
    D["B"].line(P([(side, top), (side, HORIZON)]), fill=255, width=1)
    for k in range(int(h // 6)):
        yk = top + k * 6
        D["B"].line(P([(side - (6 if side == x0 + w else -6) * rng.uniform(.5, 2), yk), (side, yk)]), fill=255, width=1)

x = 30
while x < W - 30:
    w = rng.uniform(40, 95)
    if abs(x + w / 2 - CORE[0]) < 190: x += 20; continue
    h = rng.uniform(90, 260) * (1.3 if abs(x - CORE[0]) < 400 else 1)
    building(x, w, h, rng.choice(["flat", "dome", "spire", "flat", "stack"]))
    x += w + rng.uniform(-10, 18)

# 架在楼与楼之间的高拱桥（怪诞的城市骨架）
for (a, b, yb) in ((60, 330, 860), (860, 1150, 820), (180, 420, 930)):
    DS.rectangle(P([(a, yb), (b, yb + 10)]), fill=255)
    n = int((b - a) // 45)
    for k in range(n):
        xa = a + k * (b - a) / n; xb = xa + (b - a) / n
        DS.chord(P([(xa, yb - 2), (xb, yb + 70)]), 0, 180, fill=0)
    D["B"].line(P([(a, yb - 1), (b, yb - 1)]), fill=255, width=1)
    for k in range(0, int(b - a), 9):
        D["B"].line(P([(a + k, yb - 1), (a + k, yb - 7)]), fill=255, width=1)

# 摩天轮：普里皮亚季那座从没开过的摩天轮，只剩刻线
FW = (250, 760, 175)
cx_, cy_, R = FW
D["B"].ellipse(P([(cx_ - R, cy_ - R), (cx_ + R, cy_ + R)]), outline=255, width=3)
D["B"].ellipse(P([(cx_ - R + 14, cy_ - R + 14), (cx_ + R - 14, cy_ + R - 14)]), outline=255, width=1)
for a in np.linspace(0, 2 * math.pi, 33)[:-1]:
    D["B"].line(P([(cx_, cy_), (cx_ + R * math.cos(a), cy_ + R * math.sin(a))]), fill=255, width=1)
    gx, gy = cx_ + R * math.cos(a), cy_ + R * math.sin(a)
    D["Y" if rng.random() < .12 else "B"].rectangle(P([(gx - 8, gy + 3), (gx + 8, gy + 17)]), outline=255, width=2)
DS.polygon(P([(cx_ - 6, cy_), (cx_ + 6, cy_), (cx_ + 70, HORIZON), (cx_ + 56, HORIZON)]), fill=255)
DS.polygon(P([(cx_ - 6, cy_), (cx_ + 6, cy_), (cx_ - 56, HORIZON), (cx_ - 70, HORIZON)]), fill=255)

# ---------- 反应堆：一座长出尖塔的大教堂一样的厂房，心口裂开 ----------
RX0, RX1, RTOP = 470, 820, 830
DS.rectangle(P([(RX0, RTOP), (RX1, HORIZON + 5)]), fill=255)
DS.polygon(P([(560, RTOP), (575, 560), (600, 560), (615, RTOP)]), fill=255)      # 通风塔
DS.polygon(P([(570, 560), (587, 470), (605, 560)]), fill=255)
for k in range(5):
    yk = 590 + k * 44
    D["R" if k % 2 == 0 else "G"].line(P([(575 - k * .4, yk), (600 + k * .4, yk)]), fill=255, width=3)
for xk in (490, 790):                                                            # 两侧小尖塔
    DS.polygon(P([(xk - 18, RTOP), (xk, RTOP - 150), (xk + 18, RTOP)]), fill=255)
DS.ellipse(P([(680, RTOP - 60), (780, RTOP + 30)]), fill=255)                     # 穹顶
# 心口：参差的裂缝，里面是红黄的光
crack = [(600, RTOP + 20)]
for k in range(1, 12):
    crack.append((600 + k * 8 + rng.uniform(-6, 6), RTOP + 20 + (k % 2) * rng.uniform(20, 45) + k * 6))
crack += [(700, RTOP + 140), (690, RTOP + 175), (640, RTOP + 160), (610, RTOP + 120)]
DS.polygon(P(crack), fill=0)
cm = Image.new("L", (WS, HS), 0); ImageDraw.Draw(cm).polygon(P(crack), fill=255)
inner = [(x * .6 + 650 * .4, y * .6 + (RTOP + 100) * .4) for x, y in crack]
cr = Image.new("L", (WS, HS), 0); ImageDraw.Draw(cr).polygon(P(inner), fill=255)
hat = Image.new("L", (WS, HS), 0); dh = ImageDraw.Draw(hat)
for yk in range(0, HS, 3): dh.line([(0, yk), (WS, yk)], fill=255, width=2)
from PIL import ImageChops
L["Y"] = ImageChops.lighter(L["Y"], ImageChops.multiply(cm, hat)); D["Y"] = ImageDraw.Draw(L["Y"])
L["R"] = ImageChops.lighter(L["R"], cr); D["R"] = ImageDraw.Draw(L["R"])
for k in range(160):                                   # 光从裂口溅到墙上的短刻线
    a = rng.uniform(0, 2 * math.pi); r0 = rng.uniform(40, 70); r1 = r0 + rng.uniform(10, 90) * rng.random()
    x0, y0 = 650 + r0 * math.cos(a) * 1.2, RTOP + 95 + r0 * math.sin(a)
    if y0 < RTOP + 4: continue
    D["Y" if rng.random() < .7 else "R"].line(P([(x0, y0), (650 + r1 * math.cos(a) * 1.2, min(HORIZON, RTOP + 95 + r1 * math.sin(a)))]), fill=255, width=1)
# 光柱：从心口往上的竖向刻线（当年人们说看见一道蓝白的光柱）
for k in range(110):
    x0 = 650 + rng.normal(0, 18); y0 = RTOP + 40
    DB["G"].line(P([(x0, y0), (x0 + rng.normal(0, 6), y0 - rng.uniform(200, 560))]), fill=255, width=1)
# 被光勾出来的轮廓
for pts in ([(RX0, HORIZON), (RX0, RTOP), (600, RTOP)], [(700, RTOP), (RX1, RTOP), (RX1, HORIZON)],
            [(560, RTOP), (575, 560), (570, 560), (587, 470), (605, 560), (600, 560), (615, RTOP)],
            [(472, RTOP), (490, RTOP - 150), (508, RTOP)], [(772, RTOP), (790, RTOP - 150), (808, RTOP)]):
    D["B"].line(P(pts), fill=255, width=2)
D["B"].arc(P([(680, RTOP - 60), (780, RTOP + 30)]), 180, 360, fill=255, width=2)
# 厂房朝光的面：近乎看不清的竖刻线 + 几扇窗
for xk in range(RX0 + 4, RX1, 5):
    if rng.random() < .5:
        D["B"].line(P([(xk, RTOP + 2), (xk, RTOP + rng.uniform(10, 50))]), fill=255, width=1)
for wy in range(RTOP + 40, HORIZON - 10, 22):
    for wx in range(RX0 + 12, RX1 - 12, 20):
        if (wx < 590 or wx > 720) and rng.random() < .12:
            D["Y"].rectangle(P([(wx, wy), (wx + 6, wy + 9)]), fill=255)

# ---------- 前景：铁路桥上一排看热闹的小剪影 ----------
BY = 1190
DS.rectangle(P([(0, BY), (W, BY + 30)]), fill=255)
DS.rectangle(P([(0, BY + 30), (W, H)]), fill=255)
for k in range(6):                                         # 桥拱：拱下透出河面反光
    xa = -60 + k * 240; xb = xa + 220
    ar = [(xa, H)] + [(xa + (xb - xa) * u, BY + 75 + 110 * (1 - math.sqrt(max(0, 1 - (2 * u - 1) ** 2)))) for u in np.linspace(0, 1, 40)] + [(xb, H)]
    DS.polygon(P(ar), fill=0)
D["B"].line(P([(0, BY - 1), (W, BY - 1)]), fill=255, width=2)
for xk in range(0, W, 14):                                 # 栏杆
    DS.line(P([(xk, BY), (xk, BY - 26)]), fill=255, width=4)
DS.rectangle(P([(0, BY - 30), (W, BY - 25)]), fill=255)
D["B"].line(P([(0, BY - 31), (W, BY - 31)]), fill=255, width=1)

def person(x, h, kid=False, arm=0):
    hw = h * .17
    DS.ellipse(P([(x - hw * .55, BY - 30 - h), (x + hw * .55, BY - 30 - h + hw * 1.15)]), fill=255)
    DS.polygon(P([(x - hw, BY - 30 - h + hw * 1.1), (x + hw, BY - 30 - h + hw * 1.1),
                  (x + hw * 1.25, BY - 30 - h * .38), (x - hw * 1.25, BY - 30 - h * .38)]), fill=255)
    DS.rectangle(P([(x - hw * .8, BY - 30 - h * .4), (x - hw * .15, BY - 26)]), fill=255)
    DS.rectangle(P([(x + hw * .15, BY - 30 - h * .4), (x + hw * .8, BY - 26)]), fill=255)
    if arm:                                                # 有人抬手指着光
        DS.line(P([(x + hw, BY - 30 - h + hw * 1.4), (x + hw + 26 * arm, BY - 30 - h - 10)]), fill=255, width=6)
    # 被光勾出的一丝亮边
    D["Y"].line(P([(x + hw * .5, BY - 30 - h + 2), (x + hw * .55, BY - 30 - h + hw)]), fill=255, width=1)

xs = np.sort(rng.uniform(80, 1120, 26))
for i, x in enumerate(xs):
    kid = rng.random() < .2
    person(x, rng.uniform(34, 40) if kid else rng.uniform(52, 66), kid, arm=1 if rng.random() < .12 else 0)

# 河面：拱下的倒影，横向碎刻线，黄/红光碎在水里
for y in range(BY + 60, H, 3):
    for _ in range(int(rng.uniform(18, 34))):
        x = rng.normal(CORE[0], 380)
        seg = max(4, rng.uniform(8, 60) * (1 - abs(x - CORE[0]) / 900))
        ink = "R" if abs(x - CORE[0]) < 60 and rng.random() < .4 else ("Y" if abs(x - CORE[0]) < 200 and rng.random() < .5 else "B")
        DB[ink].line(P([(x, y), (x + seg, y)]), fill=255, width=1)

# 桥与城之间的雾：贴地的长横线
for y in range(HORIZON - 10, BY + 10, 3):
    dens = 6 + 30 * max(0, (y - HORIZON) / (BY - HORIZON)) ** 1.5
    for _ in range(int(dens)):
        x = rng.uniform(0, W); seg = rng.uniform(40, 220)
        DB["G" if rng.random() < .3 else "B"].line(P([(x, y + rng.uniform(-1, 1)), (x + seg, y)]), fill=255, width=1)

# ---------- 合成：背景刻线 → 剪影整块盖掉 → 前景刻线 ----------
sil = np.asarray(SIL, np.float32) / 255
img = np.ones((HS, WS, 3), np.float32) * C["N"]
for k in "BGYR":
    a = np.asarray(LB[k], np.float32) / 255 * (1 - sil)
    if k == "B": a = a * .75
    img = img * (1 - a[..., None]) + C[k] * a[..., None]
img = img * (1 - sil[..., None]) + C["N"] * sil[..., None]
for k in "BGYR":
    a = np.asarray(L[k], np.float32) / 255
    if k == "B": a = a * .8
    img = img * (1 - a[..., None]) + C[k] * a[..., None]
out = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
o = np.asarray(out, np.float32) / 255
vig = np.clip(1 - ((xx - W / 2) / W) ** 2 * 1.2 - ((yy - H * .55) / H) ** 2 * 1.4, 0, 1)[..., None]
o = C["N"] + (o - C["N"]) * (0.45 + 0.55 * vig)               # 暗角：往底色收
Image.fromarray((np.clip(o, 0, 1) * 255).astype(np.uint8)).save(f"chernobyl_night_s{SEED}.png")
print("ok")
