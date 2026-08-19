# 鼠标指针主题制作器 (Mouse Pointer Theme Maker)

[简体中文](README.md) · [English](README.en.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Português (Brasil)](README.pt-BR.md)

**喜欢的角色不该只留在图片里，把它带到你的指尖。**

把吉祥物、原创 IP、二次元角色甚至一个灵感草图，做成可用于 macOS 或 Windows 的完整鼠标指针主题——逐个状态精心设计、超清画质预览，只有你满意后才打包交付。

**选一个角色，挑一种风格，拥有属于你的专属鼠标世界。**

✦ **3 种独特画风 · 8 个常用功能状态 · 完美适配 macOS & Windows**
✦ 上传参考图——或者直接说出你想要的角色名字
✦ 在收到任何安装文件之前，先查看完整的高清预览大图

从慵懒可爱的像素吉祥物、萌系 Q 版角色，到极具张力的趣味表情包，每一个指针都为角色量身打造，真正融入光标功能——绝不是简单把图片生硬贴在箭头上。

## 精选主题

### 烤仔 · 复古像素风 (Retro Pixel)

真正的 16/32 位复古像素重构，清晰利落的功能轮廓，完美还原烤仔标志性的慵懒困倦神态。

![烤仔复古像素风八状态鼠标指针主题](examples/kaozai-retro-pixel/preview.png)

### 烤妹儿 · Q 版二次元风 (Chibi Anime)

精致的 Q 版二次元角色体系，围绕蓝色熊帽、灵动表情与清晰易辨的鼠标符号精心设计。

![烤妹儿Q版二次元风八状态鼠标指针主题](examples/kaomeier-chibi-anime/preview.png)

### 宫斗表情包 · 抽象表达风 (Abstract Expression)

夸张的动作姿势、视觉隐喻和表情包节奏，生动展现抽象风格的趣味性与表现力（绝不仅限于恶搞）。

![宫斗抽象表达风八状态鼠标指针主题](examples/zhenhuan-abstract-expression/preview.png)

> 红色十字仅用于确认真实点击热点（Hotspot），安装后的实际鼠标图案中绝不会出现。

## 从想法到可安装主题

1. 先选择电脑系统：**macOS** 或 **Windows 10/11**。
2. 提供角色名称、原创吉祥物或参考图片，并选择心仪画风。
3. 审查一张包含全部 8 个状态的高清 PNG 预览大图。
4. 满意并明确确认后，生成对应系统的专属安装包。

固定流程：“先预览，满意后再打包”。在用户确认之前，绝不提前生成 `.cape`、`.cur` 或安装压缩包。

## 三种画风

| 画风 | 说明 |
| --- | --- |
| `retro-pixel` | 专为光标定制的 16/32 位像素艺术，轮廓清晰锐利，色块层次分明 |
| `chibi-anime` | 萌系 Q 版角色，大表情、干净利落的线条与统一的角色配饰 |
| `abstract-expression` | 夸张形变、视觉隐喻、超现实幽默、民俗插画感或表情包张力 |

## 八个常用状态

| 状态 | 功能说明 |
| --- | --- |
| `normal` | 普通选择光标（默认箭头） |
| `text` | 文本输入工字光标（I-beam） |
| `action` | 链接/按钮点击小手 |
| `forbidden` | 不可用/禁止操作标识 |
| `busy` | 后台处理中/等待沙漏 |
| `open_hand` | 拖拽/移动画布抓手 |
| `resize_horizontal` | 左右水平缩放调整箭头 |
| `resize_vertical` | 上下垂直缩放调整箭头 |

这 8 个原创核心设计会自动智能扩展为 51 个 macOS 精确光标标识和 15 个 Windows 鼠标角色。具体光标类型由操作系统和各应用程序自行调用，低频状态会在对应支持的场景中出现。

## 安装与使用 Codex Skill

```bash
git clone https://github.com/kaomei/mouse-pointer-theme-maker.git
mkdir -p ~/.codex/skills
cp -R mouse-pointer-theme-maker ~/.codex/skills/mouse-pointer-theme-maker
```

重启 Codex，然后可以这样说：

```text
使用 $mouse-pointer-theme-maker。
电脑：macOS
画风：retro-pixel
主题：把我上传的蓝色原创吉祥物参考图做成一套完整鼠标皮肤。
```

Skill 会首先确认你的操作系统平台，介绍三种画风并确认角色主题；随后先生成高清 PNG 预览卡片供你确认，确认满意后再指导安装。

## 平台交付规格

### macOS

确认后的图案会打包为 `.cape` 主题包。导入和一键应用需要第三方开源工具 [Mousecape SwiftUI 最新版本](https://github.com/sdmj76/Mousecape-swiftUI/releases)。本仓库不内置或二次分发 Mousecape 应用程序；使用前请查阅其开源许可协议（尤其在商业场景下）。

### Windows

确认后的图案会打包为 15 个标准 `.cur` 光标文件，并附带当前用户一键安装 PowerShell 脚本与一键恢复默认脚本。安装脚本仅写入 `HKCU\Control Panel\Cursors`，无需管理员权限，安全干净。

## 质量保证

- 呈现给用户的预览图为 2440×1388 或更高超清分辨率 PNG。
- 预览卡片均基于 320×320 原始高分辨率素材渲染，绝不使用 32×32 小图放大拉伸。
- 热点（Hotspot）精确对齐箭头尖端、I 型光标中心、食指尖、掌心或缩放箭头交叉点。
- 严格的安全边距与透明通道质检，杜绝边缘裁切残留或多余杂线。
- macOS 与 Windows 产物严格独立打包交付。
- 用户提供的参考图、下载的外部工具和生成的最终安装包均不会进入公开代码仓库。

## 已知限制

- 部分第三方软件（如某些游戏或特殊绘图工具）使用自绘光标或始终固定普通箭头。
- 忙碌、不可用、拖拽与拉伸等状态的具体触发频率取决于当前运行的应用程序。
- 用户指定的角色名和参考图仅作为创作需求与视觉参考，不代表官方授权或合作背书。
- 请仅提交或公开你拥有合法使用权的素材与图片。

## 仓库结构

```text
agents/       Codex UI 交互元数据
assets/       可复用的 Manifest 主题清单模板
examples/     精选高分辨率主题预览示例库
references/   画风、状态映射、平台规则与安装教程参考文档
scripts/      预览生成、主题打包、热点校验与格式转换工具集
tests/        契约与功能单元测试用例
SKILL.md      Codex Skill 核心工作流规范
```

## 参与贡献

欢迎提交 Issue 和 Pull Request！请保持功能符号清楚、热点准确，请勿引入第三方二进制应用安装包，并在提交前运行测试：

```bash
python3 -m unittest discover -s tests -v
```

## 开源许可证

本项目 Skill 源代码遵循 [MIT License](LICENSE)。示例中的角色图案与设计版权归原作者所有，仅用于功能与效果展示，不构成官方产品或授权背书。
