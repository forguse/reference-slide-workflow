# Reference Slide Workflow

从参考图或 PPT 中提取视觉规则，根据新内容重新组织页面，制作风格一致、可以继续编辑的演示文稿。

An agent skill for reference-based presentation design: understand the visual language, adapt the composition, preview in HTML, export editable PPTX and verify the actual result.

![Two optional styles](docs/examples/style-comparison.png)

## 它解决什么问题

参考很精致，生成的页面却只剩相似配色；同一个布局反复套用；标题和正文各有一条边；HTML 正常，PPT 导出后跑位。这套工作流把这些问题分成可处理的步骤：

1. 读参考的画布、字体层级、图文比例、信息密度、渐变和对齐关系。
2. 区分需要保持的视觉锚点、可以变化的构图、需要单独授权的身份素材。
3. 按新内容选择比较、流程、证据等页面结构，先做代表页验证。
4. HTML 和 PPT 使用同一份页面源，检查文字容量、关系对齐和实际导出效果。
5. 后续修改只调整必要页面，保留原稿，复用验证过的未变化页面。

它适用于不同主题和风格，不限定科研答辩，也不把字体、蓝色或 16:9 当作全局规则。PNG/JPG、PDF 和 PPTX 都可以作为参考。复杂动画、视频和已有原生对象的保留应进入相应的原生编辑流程，不用静态页面替代它们。

## 安装

在 Codex 中可以让技能安装器安装此仓库的 `skills/reference-slide-workflow` 目录：

```text
请使用 skill-installer，从 https://github.com/forguse/reference-slide-workflow 安装 skills/reference-slide-workflow。
```

也可以下载仓库，在本地运行：

```sh
python install.py
```

脚本安装到个人 Codex skills 目录，保留整个技能和资源。遇到同名已安装目录会停止，不覆盖旧版本。安装后下一轮即可使用 `$reference-slide-workflow`。

## 怎么用

给一张参考图或一份参考 PPT，再给真实内容：

```text
请使用 $reference-slide-workflow，参考附件的视觉风格，按我的材料制作 8 页 PPT。
保留它的字体层级、图文比例和信息密度，根据内容安排布局。
先做 HTML，再导出可编辑 PPT；请自行检查对齐、间距和实际导出效果。
```

没有参考时，可以明确选择内置样式：

```text
请使用 $reference-slide-workflow 的 editorial-light 样式，制作 6 页教学介绍。
```

后续修改时保留完整项目目录：

```text
继续修改这个项目，第 3 页换成这张图并精简说明。
保留其他页面，更新预览，复核变化页和全稿总览后重新导出。
```

如果在 PowerPoint/WPS 中手动改过文件，请提供最新 PPT 并说明“以这份为准”。流程会保留这些修改，不从旧源覆盖。

## 两套可选样式

| 样式 | 视觉特征 | 示例 |
|---|---|---|
| `academic-blue` | 蓝色层级、克制渐变、浅色底、紧凑证据页 | [可编辑示例](docs/examples/academic-blue.pptx) |
| `editorial-light` | 暖白纸感、深色文字、陶红强调、开放构图 | [可编辑示例](docs/examples/editorial-light.pptx) |

两套各含封面、过渡、证据、比较、流程和结束页。内容与评分为演示数据；没有真实人物、机构标志或私有研究图片。模板是可选起点，用户提供的参考始终优先。示例的六页不会强制新任务也做六页。

示例图表和表格由可编辑的形状与文字组成。需要 Excel 数据驱动的原生图表时，使用转换器对应的图表能力。

还做了一个换主题测试：只给一张参考图，制作“图书资料检索”的比较页与流程页。新内容采用了新的构图，保留参考的字重、颜色和留白关系。[下载风格迁移示例](docs/examples/reference-transfer.pptx)。

![从参考风格迁移到新主题](docs/examples/reference-transfer.png)

## 修改为什么更快

默认流程是“修改当前页面源 → 刷新 HTML → 检查变化 → 重新导出”。不会为了改一句话重新设计整套页面。自动检查每次覆盖全稿，视觉检查聚焦变化页并查看总览。未变页面只有在源文件、字体环境、渲染器和截图证据都匹配时才复用。

PPT 文件仍由正式转换器完整封装，保证对象关系完整。已有 PPT 被手动修改时，进入原生编辑路线。排版检查由代理完成，不让用户反复逐页找错。

## 写作偏好

优先具体标题和自然短句。默认不反复使用前置中点、连续标签或空泛口号；确实需要列举时才用列表。重要限定保留在相关结论处，其余支撑信息进入备注。

## 运行依赖

技能说明可由代理直接使用。附带的检查与导出脚本需要 Python 3.12+、Node 20+、Playwright/Chromium 和目标字体。图片/PDF 检查用 Pillow/PyMuPDF。PPTX 转换使用单独获取的 [PPT Master](https://github.com/hugohe3/ppt-master)，保留其许可证、署名和完整性检查。实际 PPT 渲染可用宿主提供的 Artifact Tool，或 PowerPoint 等工具导出的逐页 PNG。

不打包字体、第三方转换器或私有运行时。脚本不依赖作者电脑的固定路径。详细命令见 [运行说明](skills/reference-slide-workflow/references/runtime.md)。

## 文档

- [参考风格如何提取](skills/reference-slide-workflow/references/reference-analysis.md)
- [样式与页面关系规范](skills/reference-slide-workflow/references/style-schema.md)
- [构图、排版与文案](skills/reference-slide-workflow/references/composition-and-writing.md)
- [局部修改与检查机制](skills/reference-slide-workflow/references/revision-and-review.md)
- [公开发布与素材归属](skills/reference-slide-workflow/references/privacy-and-attribution.md)
- [验证范围](docs/validation.md)

本仓库不上传用户参考材料。生成工作区和发布文件应分开存放；公开分享前检查文字、备注、元数据、媒体和图片像素。原始参考与第三方素材不因套用样式而获得本仓库许可证。

## License

Original code, documentation and neutral presets: [MIT](LICENSE). Third-party dependencies and user-provided assets retain their own terms; see [notices](THIRD_PARTY_NOTICES.md).
