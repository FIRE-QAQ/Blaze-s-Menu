# 烈火家今天的饭 — 项目交接说明

单文件静态网页，一份个人菜谱收藏，日式菜单版式。线上地址
<https://fire-qaq.github.io/Blaze-s-Menu/>（GitHub Pages，仓库
`FIRE-QAQ/Blaze-s-Menu`，`main` 分支根目录发布）。

本文件是给接手的 agent 看的。下面的「不要碰」一节是几十次失败换来的，
改之前先读完。

---

## 1. 用户是谁，他要什么

用户做饭**基本不看文字步骤，只看视频**。这句话是整个项目的设计前提：

- 每道菜的封面图本身就是链接，点图直达原帖视频。这是网站唯一的核心功能。
- 材料和步骤是「顺便记下来的」，折叠在 `<details>` 里，不是主角。
- 所以封面图缺失 > 步骤写得不全。补封面的优先级永远高于补文字。

菜谱来源绝大多数是 X（Twitter）上的日本家常菜账号。

---

## 2. 文件结构

```
Blaze-s-Menu/
├── index.html      ← 全部东西都在这里：CSS + 数据 + JS，70KB
├── img/            ← 43 张封面，1.jpg … 43.jpg（缺 12.jpg），外加 43_card.jpg
├── README.md       ← 给人看的，面向用户不是 agent
├── .nojekyll       ← 必须存在，否则 Pages 会吃掉某些文件
├── .gitignore
├── push.command    ← 用户双击用的推送脚本（macOS）
└── tools/
    └── make_invite.py  ← 生成带房号的二维码邀请函
```

`index.html` 是唯一的真实来源。没有构建步骤，没有 npm，没有打包器。
改网站 = 直接改 `index.html`。

`img/12.jpg` 不存在是故意的 —— 第 12 道「虾仁滑蛋」至今没有原帖链接也没有封面，
`HAS_IMG` 这个 Set 里也没有 12。它在页面上显示为无图卡片。

---

## 3. 数据结构

菜谱数组在 `index.html` 里，`const D = [` 开始，43 条。每条长这样：

```js
{i:1, zh:"不用卷的卷心菜肉卷", orig:"巻かないロールキャベツ ／ @TaberuYaseru",
 url:"https://x.com/taberuyaseru/status/2101921943918432687",
 st:"full", main:["鸡肉"], form:["炖菜"], scene:["备餐"],
 goal:["高蛋白","减脂"], cuisine:"日式",
 note:"不用一个个卷，切法就是全部重点。",
 ing:["卷心菜 1/2 个", "鸡肉末 200g", ...],
 steps:["卷心菜整个底面朝侧放，对半切开", ...],
 tip:"2 人份。"}
```

| 字段 | 说明 |
|---|---|
| `i` | 序号，同时决定封面文件名 `img/{i}.jpg`。新增时取当前最大值 +1 |
| `zh` | 中文菜名。**这是显示的主标题，务必准确** |
| `orig` | 原文菜名 ／ 作者 handle，小字副标题 |
| `url` | 原帖链接，点封面跳这里 |
| `url2` / `url2label` | 可选的第二链接（图文版、原博客等），5 条有 |
| `urlLabel` | 可选，覆盖主链接的按钮文字，2 条有 |
| `card` | 可选，额外的菜谱卡片图（目前只有 43 用了 `img/43_card.jpg`） |
| `st` | `"full"` 完整配方 / `"part"` 部分信息 / `"link"` 只有视频 |
| `main` | 主料，取值：鸡肉 猪肉 牛肉 海鲜 鸡蛋 豆腐 素菜 |
| `form` | **决定分区，必须命中 `SECTIONS` 的 key**：盖饭 米饭 面条 意面 炒菜 炖菜 炸物 汤 配菜 甜点 |
| `scene` | 场景，取值：快手 一锅 备餐 周末 微波炉 电饭煲 高压锅 烤箱 |
| `goal` | 高蛋白 / 减脂，可空数组 |
| `cuisine` | 日式 中式 西式 韩式 越南 |
| `note` | 一两句话的推荐语，卡片上直接显示 |
| `ing` `steps` `tip` | 折叠区内容，可缺省 |

注意 `form` 里写的是 `"炒菜"` 和 `"配菜"`，但界面上显示成「小炒」「小菜」——
`SECTIONS` 里 `key` 和 `name` 是分开的，别把它们改成一样的。

---

## 4. 加一道新菜的完整流程

1. 读原帖（见第 6 节，X 的读取方式有坑）
2. 下载封面图 → `img/{新序号}.jpg`，长边压到 ~800px，JPEG q80 左右。
   整个 `img/` 目录现在约 1MB，别让单张超过 60KB
3. 在 `const D = [` 数组末尾加一条对象，字段照上表填
4. 把新序号加进 `HAS_IMG` 这个 Set
5. 如果新增了分类，同步改 `SECTIONS`；新增主料/场景，同步改 `FACETS` 的 `order`
6. 更新 `README.md` 和 `tools/make_invite.py` 里的「43 道」计数
7. 本地开个 `python3 -m http.server` 在手机和桌面各看一眼
8. `git add -A && git commit && git push`

**当前待办队列**（用户已发链接但还没收录，因为当时浏览器工具断线）：

| 序号 | 链接 |
|---|---|
| 44 | https://x.com/yoyo138168/status/2103141436208341224 |
| 45 | https://x.com/beauty_mamemame/status/2102992069463838798 |
| 46 | https://x.com/hourui86742553/status/2103121136695529601 |

44 疑似是「微波炉鸡蛋沙拉」，但没确认过，以原帖为准。

---

## 5. 不要碰 — 硬换来的教训

### 手机上不要再加任何吸顶/固定元素

`@media (max-width:760px)` 里把 `header.board`、`.sec-band` 全部设成
`position:static`，`.bookbar`、`.hint`、`.pgdots` 全部 `display:none`。
**这是最终方案，不是半成品。**

iOS Safari 上试过 6 种做法让顶栏贴住屏幕顶端——`viewport-fit=cover` 加
`env(safe-area-inset-top)`、把 `<html>` 背景刷成栏的颜色、
`translateZ(0)` 提升合成层、`backdrop-filter` 毛玻璃、sticky 换 fixed……
全部失败，内容照样从栏上面漏出去。最后截图显示那条栏本身就被顶到了
屏幕顶端下面约 55px 的位置，上方还露出清晰的页面内容，
说明遮挡/涂色/模糊这条路根本走不通。

用户的原话是「宁可遮住也别漏」，最后的决定是手机端干脆什么都不固定。
代价是滚动时看不到招牌和当前分区名。**如果要改善，做右下角那个 FAB，
把当前分区名显示进去，不要把顶栏放回来。**

### 不要用「按范围替换」的方式改 CSS

有一次用起止行号替换 CSS 块，一次性删掉了约 5300 字节的基础样式
（`.photo` `.play` `.marks` `.btn` `footer` `.dishes` `.dish` `h3.zh`
`.empty` `.filler` 全没了，播放按钮掉到图片外面）。
**改 CSS 一律用唯一字符串精确替换，一次改一个选择器。**

### 竖排中文不能用 `writing-mode: vertical-rl`

CJK 字形在这个模式下垂直步进为 0，整列糊成一团黑（拉丁字母正常，
所以不容易第一眼发现）。`text-orientation:upright` 也救不回来。
现在用的是窄列 hack：`width:1.2em; word-break:break-all`。

### 菜名不要用 `max-height` + `overflow:hidden` 截断

用 `nameSize(t)` 按字数返回字号：≤5 字 21px，≤7 字 19px，
≤8 字 17px，≤10 字 15.5px，再长 14px。加新菜时如果菜名特别长，
调这个函数，不要加省略号。

### 排列方向是从左到右

曾经为了「日式感」做成从右往左换行，用户明确说「好奇怪」。
翻页按钮、方向键、侧边导航栏全部按 LTR 摆放，别再翻回去。

### 图片上的手势

封面 `<img>` 必须带 `draggable="false"` 且在 `dragstart` 上
`preventDefault()`。浏览器原生拖图会触发 `pointercancel`，
让 `swallowClick` 卡在 true，之后所有点击都被吃掉。
`swallowClick` 还有个 350ms 的超时兜底，别删。

---

## 6. 读 X 帖子的正确姿势

- `WebFetch` 对 `x.com` 一律返回 `ROBOTS_DISALLOWED`，不用试
- 云端容器的出口代理封了 `pbs.twimg.com`（403）。如果你在本地跑、
  网络不受限，直接下载即可；如果受限，就在浏览器页面内用 JS
  `fetch` + canvas 缩图，把 base64 带出来
- 取封面时**优先用帖子里的 media 图片，不要用视频 poster**。
  第 42 道「蒙古牛肉」就是因为脚本优先取 poster，结果抓了回复里一张
  写着 "YUM" 的 GIF 当封面，用户一眼看出来了
- 帖子正文里如果本来就有完整材料和步骤，`st` 填 `"full"`，
  卡片上会出现红色「推」章

---

## 7. 部署

```bash
git add -A
git commit -m "..."
git -c http.postBuffer=524288000 -c http.version=HTTP/1.1 push origin main
```

`http.postBuffer` 和 `HTTP/1.1` 不是装饰。仓库接近 1MB，默认设置下
推送会在 993KiB 左右报 `RPC failed; HTTP 400`。`push.command` 里已经
写好了先 HTTP/1.1 再退回 HTTP/2 的重试逻辑，用户双击就能推。

其它两条：

- **GitHub Pages 只有在收到 push 时才会构建。** 在设置页把 Source 改成
  `main / (root)` 之后如果不推一次，Actions 里是 0 个 workflow run，
  访问就是 404。曾经在这里卡了很久
- **不要用 `raw.githubusercontent.com` 验证线上文件**，它有缓存，
  会给你看旧版本，害我两次基于过时内容做诊断。要看真实的线上文件，
  用 contents API 带上 `?ref=main`

---

## 8. 二维码邀请函

`tools/make_invite.py` 生成带房号的邀请卡，和菜单同一套视觉
（米色和纸底、深色招牌带红线、右上角红色「邀」印、朱红房号）。

```bash
python3 tools/make_invite.py --room "2-338" --line "烈火请您用餐啦"
```

依赖 `segno` `pillow`，验证解码用 `opencv-python`。
需要 Noto Serif/Sans CJK 字体，脚本里写的是 Debian 的路径
(`/usr/share/fonts/opentype/noto/...`)，macOS 上要改成本机字体路径，
或者装 `brew install font-noto-serif-cjk-sc`。

二维码固定用纠错等级 **H**，生成后务必在 1080/600/400/260/160 五个
宽度下用 `cv2.QRCodeDetector` 解一遍再交付——微信会压缩图片，
打印也可能很小，H 级别加上验证才能保证扫得出来。

已经生成过的卡片在用户的 `Documents/菜谱/二维码/`（不在仓库里）：
`B326邀请函.png`、`2-338邀请函.png`，各自还有一份 `-打印用` 的
2160×3120 @300dpi 版本。

---

## 9. 还没做完的事

- **第 12 道「虾仁滑蛋」缺原帖链接和封面**，一直是个空位
- **44–46 三条待收录**（见第 4 节）
- **手机端分区提示**：用户滚动时不知道自己在哪个分区，
  方案是把分区名放进右下角 FAB，提过但没做
- **原始 Google Doc 从来没回写过**。整个项目的起点是用户的一份
  Google Doc 菜谱收藏，内容被整理进了 `index.html`，但那份文档
  至今还是最初的样子。如果要同步回去，需要先连 Google Drive 连接器
- 另有一个 Claude Artifact 版本（内嵌 base64 图片的单文件），
  和一份 `烈火家今天的饭.html` 独立文件（1.29MB，断网可看）。
  它们和仓库里的 `index.html` 是**分叉的副本**，改了仓库不会自动同步

---

## 10. 和用户沟通

用中文。用户会直接说「不行」「还是漏」「呃」，这种时候不要
重复解释原理，直接换方案。他不太关心实现细节，关心的是
手机上能不能好好用、菜名对不对、封面好不好看。

如果同一个问题改了三次还没好，说明思路错了，换一个方向，
或者直接问他能不能接受一个不同的取舍——第 5 节那个「手机端
什么都不固定」的结论，就是这么来的。
