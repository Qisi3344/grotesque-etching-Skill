---
name: grotesque-etching
description: 怪诞蚀刻风 Midjourney 提示词 Skill。暗黑童话 × 旧蚀刻版画质感，基于 --sref 6819387。收到"怪诞/暗黑童话/蚀刻版画风"需求时，按本文结构写 prompt。
---

# Grotesque Etching 怪诞蚀刻 · Skill

> 暗黑童话气质的 Midjourney 风格：**旧蚀刻版画 × 怪诞舞台布景**。
> 核心只有一行：`--sref 6819387`。风格交给 sref，prompt 只管把"画什么"写清楚。

风格来源：小红书「尤安Yoann」《怪诞风格探索分享》对 `--sref 6819387` 的实测。

---

## 1. 视觉特征（sref 会搞定的部分，不用在 prompt 里堆画风词）

- **质感**：旧蚀刻版画式的细密线条，细节极繁复
- **底色**：深黑夜空打底，画面压抑宏大
- **烟雾**：青白色/淡青蓝色烟雾在建筑间缭绕翻涌
- **点光**：暖黄 / 暖橙的窗光、零星暖色光斑，冷底上的暖点缀
- **点睛**：一小块红色（红衣人影、红色光斑），只做点缀
- **人物**：永远渺小——黑色剪影、桥上行人、远处小人，衬托建筑尺度
- **氛围**：神秘诡谲、压抑又华丽，暗黑童话感

## 2. Prompt 结构

```
建筑主体 ＋ 空间关系 ＋ 环境细节 ＋ 少量点景元素 ＋ 参数
```

- **建筑主体**：选一个（怪诞古堡 / 废弃剧院 / 迷宫街道 / 枯树环绕的小镇…）
- **空间关系**：加一种**不合常理**的关系——桥通向半空、树枝穿过房屋、几栋建筑嵌套在一起。这是"故事感"的来源。
- **环境细节**：夜空、烟雾、窗光，写具体颜色（pale blue smoke、warm orange windows、vast black sky）
- **点景元素**：少量、要小（tiny figures in red、pale deer spirit）——人物一律写小
- **参数**：`--ar 21:9 --sref 6819387 --v 8.2`（宽幅最出效果）

## 3. 示例

**怪诞剧院**
```
A labyrinthine old theater with ornate domes, arched bridges connecting its wings,
pale blue smoke drifting through the buildings, tiny figures in red crossing the bridges,
vast black sky --ar 21:9 --sref 6819387 --v 8.2
```

**枯树老宅**
```
A towering crooked manor with spired attics, enormous bare trees flanking it with
claw-like branches, dozens of windows glowing warm yellow, pale mist coiling on the
ground, deep black night --ar 21:9 --sref 6819387 --v 8.2
```

**幽林小镇**
```
A crooked wooden village at night, massive dead trunks growing through the rooftops,
a translucent pale deer spirit with giant antlers floating above a winding street,
a few warm orange windows, deep black sky --ar 21:9 --sref 6819387 --v 8.2
```

## 4. 避坑

- **人物别写大**：这个 sref 做人物效果一般。人物只配做剪影和点景，越小越好。
- **风格词别堆**：什么 "dark fairy tale, grotesque, etching" 不用写，sref 全包了，堆词反而打架。
- **浓度用 `--sw` 调**：默认 100。先按默认出一轮，太浓就调低，太淡就调高。
- **题材别跑偏**：现代建筑、明亮白天、写实人像都不对味。认准"夜晚＋老建筑＋怪诞空间关系"。
