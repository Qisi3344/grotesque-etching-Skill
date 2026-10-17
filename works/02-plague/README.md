# No.02《黑死病》Pestis Nigra · Firenze 1348

鸟嘴医生的面具长成一座钟塔，长喙伸进夜空，正对着屋顶上蹲着的一只巨蚤；黑家鼠的骨架横跨黑水当桥，运尸车和提灯的小人走在它的脊椎上；鼠疫杆菌像一盏盏两头发亮的灯笼，从城里飘起来。全画唯一的焦点：面具的镜片。

- 配色：13 寄生生物（底 `#1E191C`，由 `#51434B` 压深）
  - `#D7B66D` 主刻线：喙、鼠骨、窗光、杆菌两极
  - `#9BAA87` 面具头罩与塔身、巨蚤
  - `#7A91A0` 夜空、薄雾、帽子、远处的房子
  - `#C98C9A` 焦点：镜片
- 技法：`engrave()` 按形状的距离场和受光方向自动排线，越亮线越粗；夜空横向断续刻线；薄雾走 curl noise 流线；最后四周暗角往底色收。

```bash
pip install numpy pillow scipy
python plague_tower.py 1 parasite    # 种子 配色（parasite | fossil）
```

![No.02 黑死病](../../examples/02_plague_s1.png)
