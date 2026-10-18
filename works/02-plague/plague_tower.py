"""怪诞蚀刻 · No.02《黑死病》Pestis Nigra · Firenze 1348
和 No.01 同一套刻法：背景刻线 → 剪影整块盖掉 → 只在边上刻亮线。
左边鸟嘴医生的面具长成一座钟塔，长喙伸进夜空；它的镜片是全画唯一的光源和焦点。
城里升起黄绿的瘴气，鼠疫杆菌像灯笼一样在里面飘；右岸屋顶上蹲着一只巨蚤；
黑家鼠的骨架横跨黑水当桥，运尸车和提灯的小人走在脊椎上。
配色 13「寄生生物」：#1E191C 底（#51434B 压深）/ #7A91A0 夜空 / #9BAA87 瘴气
/ #D7B66D 窗光与杆菌两极 / #C98C9A 镜片
用法：python plague_tower.py [种子]
"""
import numpy as np, math, sys
from PIL import Image, ImageDraw

SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 1
rng = np.random.default_rng(SEED)
S = 2; W, H = 1200, 1500; WS, HS = W * S, H * S
def hx(h): return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.float32) / 255
C = {"N": hx("#1E191C"), "B": hx("#7A91A0"), "G": hx("#9BAA87"), "Y": hx("#D7B66D"), "R": hx("#C98C9A")}
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
def fbm(scale, oct=4):
    out = np.zeros((H, W), np.float32); a = 1; t = 0
    for o in range(oct):
        s = max(2, int(scale / 2 ** o))
        g = rng.random((H // s + 3, W // s + 3)).astype(np.float32)
        im = np.asarray(Image.fromarray((g * 255).astype(np.uint8)).resize((W + 3 * s, H + 3 * s), Image.BICUBIC), np.float32)[:H, :W] / 255
        out += a * im; t += a; a *= .5
    return out / t
def curve(p0, p1, p2, n=40):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in np.linspace(0, 1, n)]
L = {k: Image.new("L", (WS, HS), 0) for k in "BGYR"}; D = {k: ImageDraw.Draw(L[k]) for k in L}      # 前景刻线
LB = {k: Image.new("L", (WS, HS), 0) for k in "BGYR"}; DB = {k: ImageDraw.Draw(LB[k]) for k in LB}  # 背景刻线
SIL = Image.new("L", (WS, HS), 0); DS = ImageDraw.Draw(SIL)
def P(pts): return [(x * S, y * S) for x, y in pts]

HORIZON = 1185
HX, HY = 300, 560
EX, EY, ER = 392, 548, 54                          # 镜片
glow = np.exp(-np.hypot(xx - EX, (yy - EY) * 1.1) / 300).astype(np.float32)

# ---------- 夜空：横向断续刻线；顶上留黑，越靠近镜片、越往下越密 ----------
nz = fbm(120)
sky_t = np.clip(.03 + .62 * (yy / HORIZON) ** 1.6 + .4 * glow + .18 * (nz - .5), 0, 1)
for y in range(0, HORIZON + 30, 3):
    x = 0
    while x < W:
        sg = rng.uniform(20, 140); t = sky_t[min(y, H - 1), min(int(x), W - 1)]
        if rng.random() < t * 1.35:
            DB["B"].line(P([(x, y + rng.uniform(-.6, .6)), (x + sg, y + rng.uniform(-.6, .6))]), fill=255, width=1)
        x += sg + rng.uniform(4, 30) * (1.2 - t)
for _ in range(80):
    x, y = rng.uniform(0, W), rng.uniform(0, 600)
    if glow[int(y), int(x)] < .2:
        r = rng.uniform(.6, 1.5); DB["G"].ellipse(P([(x - r, y - r), (x + r, y + r)]), fill=255)

# ---------- 瘴气：从城里升起，沿 curl noise 翻卷，往右上方飘 ----------
gy_, gx_ = np.gradient(fbm(140, 3))
def plume(x, y):
    t = np.clip((HORIZON - y) / 1000, 0, 1)
    cx = 640 + 420 * t ** 1.1 + 50 * math.sin(t * 5)
    w = 140 + 280 * t ** .8
    return max(0., 1 - abs(x - cx) / w) * (y < HORIZON + 10)
for _ in range(2600):
    t0 = rng.random() ** .8
    y = HORIZON - t0 * 1000; x = 640 + 420 * t0 ** 1.1 + rng.normal(0, 120 + 240 * t0)
    if plume(x, y) < rng.random() * .6: continue
    pts = [(x, y)]
    for k in range(int(rng.uniform(20, 70))):
        i, j = int(np.clip(y, 0, H - 1)), int(np.clip(x, 0, W - 1))
        vx, vy = gy_[i, j] * 900 + .3, -gx_[i, j] * 900 - 1.1
        n = math.hypot(vx, vy) + 1e-6; x += 3 * vx / n; y += 3 * vy / n
        if plume(x, y) <= 0 or y < 30: break
        pts.append((x, y))
    if len(pts) > 4:
        hi = plume(*pts[0])
        DB["G" if rng.random() < .3 + .55 * hi else "B"].line(P(pts), fill=255, width=1 if rng.random() < .7 else 2)

# 贴地的雾：城与水之间的长横线（小人和骨桥就站在这层雾前面）
for y in range(HORIZON - 120, HORIZON + 15, 3):
    dens = 4 + 34 * max(0, (y - HORIZON + 120) / 135) ** 1.6
    for _ in range(int(dens)):
        x = rng.uniform(0, W); sg = rng.uniform(40, 220)
        DB["G" if rng.random() < .3 else "B"].line(P([(x, y + rng.uniform(-1, 1)), (x + sg, y)]), fill=255, width=1)

# ---------- 左：鸟嘴面具钟塔（全是剪影） ----------
DS.ellipse(P([(HX - 190, HY - 210), (HX + 190, HY + 200)]), fill=255)                      # 头罩
cloakL = curve((HX - 170, HY + 100), (HX - 200, HY + 420), (HX - 250, HORIZON + 5), 30)
cloakR = curve((HX + 250, HORIZON + 5), (HX + 200, HY + 420), (HX + 160, HY + 120), 30)
DS.polygon(P(cloakL + cloakR), fill=255)                                                  # 斗篷长成塔身
for bx_ in (HX - 300, HX + 238):                                                           # 扶壁与小尖塔
    DS.polygon(P([(bx_, HORIZON + 5), (bx_ + 30, HORIZON - 320), (bx_ + 62, HORIZON - 320), (bx_ + 72, HORIZON + 5)]), fill=255)
    DS.polygon(P([(bx_ + 30, HORIZON - 320), (bx_ + 46, HORIZON - 470), (bx_ + 62, HORIZON - 320)]), fill=255)
brim = (HX - 300, HY - 262, HX + 285, HY - 196)
DS.ellipse(P([brim[:2], brim[2:]]), fill=255)                                              # 宽檐帽
crownL = curve((HX - 150, HY - 236), (HX - 165, HY - 360), (HX - 120, HY - 402), 16)
crownR = curve((HX + 110, HY - 406), (HX + 155, HY - 360), (HX + 140, HY - 236), 16)
DS.polygon(P(crownL + crownR), fill=255)
DS.ellipse(P([(HX - 125, HY - 426), (HX + 115, HY - 384)]), fill=255)
DS.polygon(P([(HX - 13, HY - 410), (HX - 3, HY - 580), (HX + 7, HY - 410)]), fill=255)     # 帽顶的尖塔
TIP = (900, 770)
top_e = curve((HX + 150, HY - 95), (HX + 430, HY - 60), TIP, 44)
bot_e = curve((TIP[0] - 8, TIP[1] + 10), (HX + 420, HY + 120), (HX + 140, HY + 120), 44)
DS.polygon(P(top_e + bot_e), fill=255)                                                    # 长喙，往下弯

# 被光勾出来的轮廓（只刻边，像 No.01 的厂房）
D["B"].line(P(top_e), fill=255, width=2)
D["B"].arc(P([brim[:2], brim[2:]]), 180, 360, fill=255, width=2)
D["B"].arc(P([brim[:2], brim[2:]]), 0, 180, fill=255, width=1)
D["B"].line(P(crownL + [(HX - 120, HY - 402)]), fill=255, width=1); D["B"].line(P(crownR), fill=255, width=2)
D["B"].line(P([(HX - 13, HY - 410), (HX - 3, HY - 580), (HX + 7, HY - 410)]), fill=255, width=1)
D["B"].arc(P([(HX - 190, HY - 210), (HX + 190, HY + 200)]), 270, 340, fill=255, width=2)
D["B"].line(P(cloakR), fill=255, width=2); D["B"].line(P(cloakL), fill=255, width=1)
D["B"].arc(P([(HX - 190, HY - 210), (HX + 190, HY + 200)]), 150, 270, fill=255, width=1)
D["B"].line(P(bot_e), fill=255, width=1)
for bx_ in (HX - 300, HX + 238):
    D["B"].line(P([(bx_ + 62, HORIZON - 320), (bx_ + 46, HORIZON - 470), (bx_ + 30, HORIZON - 320)]), fill=255, width=1)
    D["B"].line(P([(bx_ + 62, HORIZON - 320), (bx_ + 72, HORIZON)]), fill=255, width=1)
# 喙上的缝线：只是几道细细的弧，和喙的上沿一样被光勾出来
for t in (.22, .46, .7):
    i = int(t * 43); (ax, ay), (bx2, by2) = top_e[i], bot_e[43 - i]
    D["B"].line(P(curve((ax, ay), ((ax + bx2) / 2 + 14, (ay + by2) / 2), (bx2, by2), 12)), fill=255, width=1)
    for k in range(0, 12, 2):
        u = k / 11; px = (1 - u) ** 2 * ax + 2 * (1 - u) * u * ((ax + bx2) / 2 + 14) + u * u * bx2
        py = (1 - u) ** 2 * ay + 2 * (1 - u) * u * ((ay + by2) / 2) + u * u * by2
        D["B"].line(P([(px - 4, py), (px + 4, py)]), fill=255, width=1)
# 喙上沿：一排细竖刻线，像 No.01 厂房的屋檐
for i in range(2, 42):
    if rng.random() < .55:
        x, y = top_e[i]; D["B"].line(P([(x, y + 2), (x + 1, y + rng.uniform(6, 28))]), fill=255, width=1)
# 镜片：剪影里挖一个洞，里面一圈圈的粉色反光
DS.ellipse(P([(EX - ER, EY - ER), (EX + ER, EY + ER)]), fill=0)
D["B"].ellipse(P([(EX - ER - 10, EY - ER - 10), (EX + ER + 10, EY + ER + 10)]), outline=255, width=2)
D["B"].ellipse(P([(EX - ER - 3, EY - ER - 3), (EX + ER + 3, EY + ER + 3)]), outline=255, width=1)
for r in range(4, ER, 6):
    D["R"].ellipse(P([(EX - r, EY - r), (EX + r, EY + r)]), outline=255, width=2 if r < ER * .6 else 1)
D["Y"].arc(P([(EX - ER + 10, EY - ER + 10), (EX + ER - 10, EY + ER - 10)]), 200, 255, fill=255, width=4)
for k in range(150):                                # 镜片的光溅在面具上的短刻线（像 No.01 的裂口）
    a = rng.uniform(0, 2 * math.pi); r0 = ER + rng.uniform(14, 24); r1 = r0 + rng.uniform(8, 80) * rng.random()
    D["R" if rng.random() < .45 else "Y"].line(P([(EX + r0 * math.cos(a), EY + r0 * math.sin(a)),
                                                   (EX + r1 * math.cos(a), EY + r1 * math.sin(a))]), fill=255, width=1)
# 塔身的窗：稀稀拉拉几扇暖黄的拱窗
for row, yw in enumerate(range(HY + 270, HORIZON - 70, 100)):
    half = 70 + row * 22
    for xw in np.arange(HX - half, HX + half + 1, 40):
        if rng.random() < .16:
            D["Y"].rectangle(P([(xw - 4, yw), (xw + 4, yw + 16)]), fill=255); D["Y"].ellipse(P([(xw - 4, yw - 4), (xw + 4, yw + 4)]), fill=255)
# 塔脚的小城
x = 20
while x < 660:
    w_ = rng.uniform(30, 58); h_ = rng.uniform(40, 100); top = HORIZON - h_
    DS.rectangle(P([(x, top), (x + w_, HORIZON + 5)]), fill=255)
    DS.polygon(P([(x - 3, top + 1), (x + w_ / 2, top - w_ * .85), (x + w_ + 3, top + 1)]), fill=255)
    D["B"].line(P([(x + w_ / 2, top - w_ * .85), (x + w_ + 3, top + 1)]), fill=255, width=1)
    if rng.random() < .35: D["Y"].rectangle(P([(x + w_ / 2 - 3, top + 14), (x + w_ / 2 + 3, top + 24)]), fill=255)
    x += w_ + rng.uniform(-6, 8)

# ---------- 右岸：窄高的山墙房，屋顶上蹲着巨蚤 ----------
roofs = []; x = 930
for w_, h_ in ((70, 200), (96, 320), (60, 240), (92, 280)):
    top = HORIZON - h_
    DS.rectangle(P([(x, top), (x + w_, HORIZON + 5)]), fill=255)
    pk = top - w_ * .9; DS.polygon(P([(x - 6, top + 2), (x + w_ / 2, pk), (x + w_ + 6, top + 2)]), fill=255)
    D["B"].line(P([(x - 6, top + 2), (x + w_ / 2, pk)]), fill=255, width=1)
    D["B"].line(P([(x, top), (x, HORIZON)]), fill=255, width=1)
    for k in range(int(h_ // 7)):
        D["B"].line(P([(x, top + k * 7), (x + rng.uniform(3, 10), top + k * 7)]), fill=255, width=1)
    roofs.append((x + w_ / 2, pk))
    for wy in range(int(top + 18), HORIZON - 30, 26):
        for wx in range(int(x + 10), int(x + w_ - 14), 18):
            if rng.random() < .13: D["Y"].rectangle(P([(wx, wy), (wx + 5, wy + 8)]), fill=255)
    x += w_ - 4
FX, FY, FS = TIP[0] + 30, TIP[1] - 150, .62                       # 巨蚤爬在喙尖上，头朝着镜片
def F_(x, y): return (FX + x * FS, FY + y * FS)
back = curve(F_(-165, 20), F_(-110, -175), F_(120, -130), 30) + curve(F_(120, -130), F_(215, -70), F_(175, 60), 20)[1:]
belly = curve(F_(175, 60), F_(60, 140), F_(-80, 95), 20)[1:] + curve(F_(-80, 95), F_(-150, 80), F_(-200, 60), 12)[1:]
DS.polygon(P(back + belly + [F_(-205, 40)]), fill=255)
def limb(pts, w0, w1):
    for i in range(len(pts) - 1):
        w = w0 + (w1 - w0) * i / max(1, len(pts) - 2)
        DS.line(P([pts[i], pts[i + 1]]), fill=255, width=int(w * S)); x, y = pts[i + 1]
        DS.ellipse(P([(x - w / 2, y - w / 2), (x + w / 2, y + w / 2)]), fill=255)
LEGS = [[F_(-140, 70), F_(-175, 125), F_(-150, 175), F_(-190, 205), F_(-205, 212)],
        [F_(-40, 105), F_(-70, 165), F_(-40, 205), F_(-75, 230), F_(-90, 235)],
        [F_(70, 95), F_(165, 150), F_(75, 175), F_(190, 235), F_(250, 248)]]
for k, Lg in enumerate(LEGS): limb(Lg, (14, 16, 26)[k] * FS, (5, 5, 7)[k] * FS)
D["B"].line(P(back), fill=255, width=2)                                    # 只有拱起的背被勾亮
for k in range(1, 9):                                                      # 背板的分节：几道短刻线
    i = int(k / 9 * (len(back) - 1)); x, y = back[i]
    D["B"].line(P([(x, y + 2), (x - 3, y + rng.uniform(10, 22))]), fill=255, width=1)
for k in range(90):                                                        # 往后梳的刚毛
    i = rng.integers(2, len(back) - 2); bx, by = back[i]
    Lh = rng.uniform(5, 14); a = math.radians(rng.uniform(20, 50))
    D["B"].line(P([(bx, by), (bx + Lh * math.cos(a), by - Lh * math.sin(a) * .6)]), fill=255, width=1)
D["B"].line(P(curve(F_(-160, -20), F_(-150, -55), F_(-120, -60), 10)), fill=255, width=1)   # 触角
for Lg in LEGS: D["B"].line(P(Lg[1:]), fill=255, width=1)

# ---------- 黑水 ----------
DS.rectangle(P([(0, HORIZON + 5), (W, H)]), fill=0)                        # 水面本身不是剪影
for y in range(HORIZON + 8, H, 3):
    for _ in range(int(rng.uniform(16, 28))):
        x = rng.uniform(-40, W) if rng.random() < .55 else rng.normal(700, 200); sg = rng.uniform(8, 70)
        near = abs(x - EX) < 70; pl = abs(x - 720) < 330
        ink = "R" if near and rng.random() < .35 else ("G" if rng.random() < (.45 if pl else .12) else "B")
        DB[ink].line(P([(x, y), (x + sg * (1 - .5 * (y - HORIZON) / (H - HORIZON)), y)]), fill=255, width=1)
for y in range(HORIZON + 8, H - 20, 3):                                    # 骨桥背后：瘴气在水里的倒影，最亮的一片
    f = 1 - (y - HORIZON) / (H - HORIZON)
    for _ in range(int(30 * f + 8)):
        x = rng.normal(740, 190); sg = rng.uniform(10, 80)
        DB["G" if rng.random() < .55 else "B"].line(P([(x, y), (x + sg, y)]), fill=255, width=1)
for wx in range(0, W, 9):                                                  # 窗光的倒影：竖向碎点
    if rng.random() < .05:
        for y in range(HORIZON + 10, HORIZON + int(rng.uniform(40, 160)), 6):
            DB["Y"].line(P([(wx, y), (wx + rng.uniform(3, 9), y)]), fill=255, width=1)

# ---------- 鼠骨桥：剪影，水面的刻线从肋骨之间透出来 ----------
def bone(a, b, w, knob=1.5):
    DS.line(P([a, b]), fill=255, width=int(w * S))
    for (x, y) in (a, b): DS.ellipse(P([(x - w * knob / 2, y - w * knob / 2), (x + w * knob / 2, y + w * knob / 2)]), fill=255)
spine = curve((470, 1330), (720, 1050), (1000, 1250), 44)
for i, (x, y) in enumerate(spine):
    s_ = 18 - 6 * abs(i / 43 - .5)
    DS.ellipse(P([(x - s_ * .55, y - s_ * .42), (x + s_ * .55, y + s_ * .42)]), fill=255)
    if i % 2 == 0: DS.line(P([(x, y), (x - 3, y - s_ * .95)]), fill=255, width=3 * S)
for i in range(20, 37, 2):                                                 # 肋骨垂进水里，像一排桥拱
    x, y = spine[i]; Lr = 120 + 60 * math.sin((i - 20) / 16 * math.pi)
    DS.line(P(curve((x, y + 5), (x - 8 - Lr * .1, y + Lr * .6), (x - 30 - (i - 20) * 1.4, y + Lr), 16)), fill=255, width=4 * S)
SK = (990, 1238); kk = 1.2
def K(x, y): return (SK[0] + x * kk, SK[1] + y * kk)
DS.polygon(P([K(-20, -26), K(30, -44), K(95, -36), K(150, -16), K(170, 0), K(160, 12), K(90, 22), K(20, 30), K(-20, 18)]), fill=255)
DS.polygon(P([K(20, 32), K(120, 22), K(132, 32), K(40, 54), K(8, 48)]), fill=255)       # 下颌
DS.line(P(curve(K(165, 6), K(176, 26), K(160, 44), 10)), fill=255, width=7 * S)         # 门齿
DS.ellipse(P([K(48, -24), K(84, 4)]), fill=0)                                              # 眼眶
bone((920, 1225), (895, 1290), 16); bone((895, 1290), (910, 1400), 12)                  # 前肢＝桥墩
bone((560, 1250), (600, 1330), 15); bone((600, 1330), (570, 1420), 11)                  # 后肢
tail = curve((470, 1330), (380, 1380), (300, 1440), 24) + curve((300, 1440), (250, 1480), (320, 1490), 12)[1:]
for i, (x, y) in enumerate(tail):
    s_ = 14 * (1 - i / len(tail)) + 3
    DS.ellipse(P([(x - s_ * .6, y - s_ * .38), (x + s_ * .6, y + s_ * .38)]), fill=255)
D["B"].line(P([(x, y - 9) for x, y in spine]), fill=255, width=1)          # 脊背上一道亮边
D["B"].line(P([K(30, -44), K(95, -36), K(150, -16), K(170, 0)]), fill=255, width=1)

# ---------- 脊背上的小人：推运尸车、提灯、拄杖 ----------
def at(t):
    i = int(t * 43); x, y = spine[i]; return x, y - 18
def person(x, y, h, lean=0):
    hw = h * .17
    DS.ellipse(P([(x - hw * .55 + lean, y - h), (x + hw * .55 + lean, y - h + hw * 1.15)]), fill=255)
    DS.polygon(P([(x - hw + lean, y - h + hw * 1.1), (x + hw + lean, y - h + hw * 1.1), (x + hw * 1.4, y), (x - hw * 1.4, y)]), fill=255)
    D["B"].line(P([(x + hw * .5 + lean, y - h + 2), (x + hw * .55 + lean, y - h + hw)]), fill=255, width=1)
for t, h, ln_ in ((.26, 46, 3), (.47, 44, -2), (.6, 45, 4)):
    person(*at(t), h, ln_)
cx_, cy_ = at(.37)                                                          # 运尸车
DS.rectangle(P([(cx_ - 30, cy_ - 22), (cx_ + 28, cy_ - 8)]), fill=255)
for wx in (cx_ - 18, cx_ + 16): DS.ellipse(P([(wx - 8, cy_ - 12), (wx + 8, cy_ + 4)]), fill=255)
for k in range(4): DS.line(P([(cx_ - 24 + k * 14, cy_ - 22), (cx_ - 20 + k * 14, cy_ - 32)]), fill=255, width=4 * S)
lx, ly = at(.72); person(lx, ly, 40)
DS.line(P([(lx + 7, ly - 30), (lx + 18, ly - 18)]), fill=255, width=2 * S)
D["Y"].ellipse(P([(lx + 15, ly - 18), (lx + 22, ly - 9)]), fill=255)       # 提灯：一点暖光

# ---------- 合成：背景刻线 → 剪影盖掉 → 前景刻线 ----------
sil = np.asarray(SIL, np.float32) / 255
img = np.ones((HS, WS, 3), np.float32) * C["N"]
for k in "BGYR":
    a = np.asarray(LB[k], np.float32) / 255 * (1 - sil)
    if k == "B": a = a * .75
    img = img * (1 - a[..., None]) + C[k] * a[..., None]
img = img * (1 - sil[..., None]) + C["N"] * sil[..., None]

# 鼠疫杆菌灯笼：浮在剪影前面，只用线勾（像 No.01 的摩天轮）
lan = Image.new("L", (WS, HS), 0); dl = ImageDraw.Draw(lan)
placed = []
for _ in range(800):
    if len(placed) >= 13: break
    t0 = rng.uniform(.08, .95); y = HORIZON - 60 - t0 * 900; x = 640 + 420 * t0 ** 1.1 + rng.normal(0, 100 + 170 * t0)
    if not (60 < x < W - 60) or any(math.hypot(x - px, y - py) < 90 for px, py in placed): continue
    if math.hypot(x - EX, y - EY) < 160: continue
    a = rng.uniform(0, math.pi); Lb = rng.uniform(44, 78) * (1.15 - .45 * t0); w = Lb * .42
    ux, uy = math.cos(a) * Lb / 2, math.sin(a) * Lb / 2; nx, ny = -math.sin(a) * w / 2, math.cos(a) * w / 2
    side1 = [(x - ux + nx, y - uy + ny), (x + ux + nx, y + uy + ny)]; side2 = [(x - ux - nx, y - uy - ny), (x + ux - nx, y + uy - ny)]
    D["G"].line(P(side1), fill=255, width=2); D["G"].line(P(side2), fill=255, width=2)
    for s_ in (-1, 1):
        ex, ey = x + s_ * ux, y + s_ * uy; ang = math.degrees(a) + (90 if s_ < 0 else -90)
        D["G"].arc(P([(ex - w / 2, ey - w / 2), (ex + w / 2, ey + w / 2)]), ang, ang + 180, fill=255, width=2)
        e2x, e2y = x + s_ * ux * .55, y + s_ * uy * .55; r = w * .22
        D["Y"].ellipse(P([(e2x - r, e2y - r), (e2x + r, e2y + r)]), fill=255)
    D["G"].line(P(curve((x, y + w / 2), (x + rng.normal(0, 6), y + 30), (x + rng.normal(0, 12), y + rng.uniform(45, 90)), 10)), fill=255, width=1)
    placed.append((x, y))

for k in "BGYR":
    a = np.asarray(L[k], np.float32) / 255
    if k == "B": a = a * .8
    img = img * (1 - a[..., None]) + C[k] * a[..., None]
out = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
o = np.asarray(out, np.float32) / 255
vig = np.clip(1 - ((xx - W / 2) / W) ** 2 * 1.2 - ((yy - H * .5) / H) ** 2 * 1.4, 0, 1)[..., None]
o = C["N"] + (o - C["N"]) * (0.45 + 0.55 * vig)
Image.fromarray((np.clip(o, 0, 1) * 255).astype(np.uint8)).save(f"plague_tower_s{SEED}.png")
print("ok")
