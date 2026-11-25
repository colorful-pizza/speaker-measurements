# Contributing

Adding a speaker is the point of this repository, so contributions are welcome.
The bar is documentation, not perfection — a measurement with honest caveats is
more useful than a pretty one with none.

## What a new measurement needs

1. A folder `measurements/<brand>-<model>/` containing:
   - `raw/*.mdat` — the REW file(s), unedited
   - `data/` — export with `python scripts/export_data.py` (adjust the paths) or
     by hand from REW: *File → Export → Export measurement as text*
   - `img/` — figures produced by `scripts/plot.py`, plus a photo of the setup
   - `README.md` — copy `measurements/jbl-go-2/README.md` and fill it in
2. Conditions written down, even when they are imperfect: room, distance, angle,
   microphone, interface, input type, volume setting, temperature/humidity.
3. The same caveats as everybody else: say whether the microphone and the SPL scale
   were calibrated. "Not calibrated" is a fine answer.

## Conventions

- At least two input levels if you are claiming anything about output limits.
- Keep the raw `.mdat`. It is the only artefact that cannot be regenerated.
- Do not smooth data before exporting it; smoothing belongs in the plotting step.
- One folder per speaker; keep files out of the repository root.

## Adding to the table

The table in `README.md` and `README.zh-CN.md` is updated by hand — add one row per
device with the date, the input levels used and a link to the folder.

---

# 参与贡献（中文版）

添加音箱正是这个仓库存在的意义，所以欢迎提交。门槛是**记录清楚**，不是测得完美——
一份带着诚实说明的粗糙测量，比一份好看但什么都没交代的测量有用得多。

## 一份新测量需要包含什么

1. 一个目录 `measurements/<品牌>-<型号>/`，里面放：
   - `raw/*.mdat` —— REW 原始文件，不要改动
   - `data/` —— 用 `python scripts/export_data.py` 导出（自行调整路径），或者在 REW 里
     手动导出：*File → Export → Export measurement as text*
   - `img/` —— `scripts/plot.py` 生成的图，外加一张测量摆位的照片
   - `README.md` —— 复制 `measurements/jbl-go-2/README.md` 的结构，填上自己的内容
2. 把条件写下来，哪怕不完美：房间、距离、角度、麦克风、声卡、输入方式、音量档位、温湿度。
3. 和其他人一样交代清楚：麦克风有没有校准、声压刻度有没有校准。写“没校准”是完全合格的答案。

## 约定

- 只要你想谈论输出上限，至少测两个输入电平。
- **保留原始 `.mdat`**。它是唯一无法重新生成的东西。
- 导出前不要做平滑，平滑属于出图环节。
- 每只音箱一个目录，不要把文件堆在仓库根目录。

## 加入表格

`README.md` 和 `README.zh-CN.md` 里的表格是手工维护的 —— 每加一只设备就补一行，
写上日期、用到的输入电平和目录链接。
