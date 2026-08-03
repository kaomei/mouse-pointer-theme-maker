# 鼠标指针主题制作器

[English](README.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Português (Brasil)](README.pt-BR.md)

把角色、原创 IP 或一个视觉想法，做成可用于 macOS 或 Windows 的完整鼠标指针主题；安装之前，先给你看清晰的完整预览。

**三种画风 · 八个常用状态 · 按电脑平台单独交付**

## 精选主题

### 烤仔 · 复古像素风

不是给原图套像素滤镜，而是按 16/32 位游戏素材重新设计，同时保留烤仔标志性的困倦表情。

![烤仔复古像素风八状态鼠标指针主题](examples/kaozai-retro-pixel/preview.png)

### 烤妹儿 · Q 版二次元风

围绕蓝色熊帽、浅蓝双辫与学生服，重新设计八种清楚、可爱又有功能性的鼠标状态。

![烤妹儿Q版二次元风八状态鼠标指针主题](examples/kaomeier-chibi-anime/preview.png)

### 宫斗表情包 · 抽象表达风

用夸张动作、视觉隐喻和表情包节奏表现抽象风；它可以幽默，但不局限于恶搞。

![宫斗抽象表达风八状态鼠标指针主题](examples/zhenhuan-abstract-expression/preview.png)

> 红色十字只用来确认真实点击热点，安装后的鼠标图案里不会出现。

## 从想法到可安装主题

1. 先选择 **macOS** 或 **Windows 10/11**。
2. 提供角色名、原创 IP 或参考图，并选择画风。
3. 先查看一张包含八种状态的高清 PNG 预览。
4. 明确确认后，只生成所选电脑平台的安装包。

固定顺序是“先预览、后安装”。用户确认之前，不生成 `.cape`、`.cur` 或安装压缩包。

## 三种画风

| 画风 | 含义 |
| --- | --- |
| `retro-pixel` | 专门绘制的 16/32 位像素画，轮廓锐利、色块清楚 |
| `chibi-anime` | 可爱的 Q 版角色、大表情、干净线稿与统一配件 |
| `abstract-expression` | 夸张、视觉隐喻、超现实幽默、民俗插画感或表情包反应 |

## 八个常用状态

`normal` 正常选择、`text` 文字输入、`action` 链接/点击、`forbidden` 不可用、`busy` 忙碌、`open_hand` 移动画布、`resize_horizontal` 左右调整、`resize_vertical` 上下调整。

八张原创图会自动扩展为 51 个 macOS 精确标识和 15 个 Windows 鼠标角色。软件仍然自己决定调用哪一种鼠标，所以低频状态不会在所有应用中出现。

## 安装 Codex Skill

```bash
git clone https://github.com/kaomei/mouse-pointer-theme-maker.git
mkdir -p ~/.codex/skills
cp -R mouse-pointer-theme-maker ~/.codex/skills/mouse-pointer-theme-maker
```

重新启动 Codex，然后可以这样说：

```text
使用 $mouse-pointer-theme-maker。
电脑：macOS
画风：retro-pixel 复古像素风
主题：把我上传的蓝色原创角色做成完整鼠标皮肤。
```

Skill 会先问电脑平台，介绍三种画风，再确认角色和主题；之后先生成 PNG 预览，不会一上来就让用户处理安装文件。

## 平台交付

### macOS

确认后的图案会打包为 `.cape`。导入和应用需要第三方 [Mousecape SwiftUI 最新版本](https://github.com/sdmj76/Mousecape-swiftUI/releases)。本仓库不会打包或再分发 Mousecape；使用前请查看它自己的许可证，商业场景尤其需要注意。

### Windows

确认后的图案会打包为 15 个 `.cur` 文件，并提供当前用户安装脚本和恢复脚本。安装脚本只写入 `HKCU\Control Panel\Cursors`，不需要管理员权限。

## 质量保证

- 用户预览图为 2440×1388 或更高分辨率 PNG。
- 卡片来自 320×320 源图，不放大模糊的 32×32 图标。
- 热点落在箭头尖端、I 形中心、手指尖、掌心或调整箭头上。
- 安全边距检查会拒绝裁切、残线和相邻格混入。
- macOS 与 Windows 始终分开打包。
- 用户参考图、下载的应用程序和生成的安装包不会进入公开仓库。

## 已知限制

- 有些软件会绘制自己的鼠标，或始终调用普通箭头。
- 忙碌、不可用、移动和拉伸状态出现频率取决于应用。
- 角色名和参考图只是创作需求，不代表官方授权或合作。
- 只能提交或公开自己有权使用的图片。

## 参与贡献与许可证

欢迎提交 Issue 和 Pull Request。请保持功能符号清楚、热点准确，不加入第三方应用安装包，并运行：

```bash
python3 -m unittest discover -s tests -v
```

Skill 源码使用 [MIT License](LICENSE)。示例角色图的权利仍属于各自创作者，仅用于功能展示，不代表官方产品或授权。
