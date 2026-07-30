# Academic Templates

一套标准化的科研工作模板库，统一解决**中文字体、英文字体、图片字体**问题，
覆盖科研项目的常见形态。每个子目录是一个独立的 [copier](https://copier.readthedocs.io/) 模板。

## 字体基线（所有模板共享）

**Libertinus（英文）+ Noto CJK SC（中文）**——开源、跨平台可复现、Times 兼容。

```bash
./fonts/setup-fonts.sh        # 首次使用：安装字体基线（macOS/Homebrew）
./fonts/setup-fonts-direct.sh # 备选：brew 下载失败时，从 GitHub 直接安装
```

权威说明见 [`fonts/README.md`](fonts/README.md)；LaTeX / matplotlib / ggplot / Quarto
的接入点均已内置在各模板中。

## 模板清单

| 模板 | 场景 | 产出形态 |
|---|---|---|
| `report/` | 汇报（组会、进展、口头报告） | Quarto `.qmd` → revealjs 幻灯片 |
| `literature-review/` | 文献综述 | LaTeX `.tex`（xelatex） |
| `paper/` | 论文项目 | LaTeX `.tex` 手稿 |
| `paper-replication/` | 论文复现 | `.qmd` 报告 + Python 代码 + claim 追踪 |
| `dev-project/` | 开发项目 | Python 包（uv + pytest，src layout） |
| `paper-with-code/` | 论文+代码开发 | LaTeX 论文 + Python 代码 + 实验管线 |
| `brainstorm/` | 头脑风暴 | Obsidian `.md`（想法卡 / 问题卡 / inbox） |

## 用法

```bash
# 安装 copier（任一）
uv tool install copier        # 或：pipx install copier

# 初始化一个项目
copier copy gh:mappedinfo/academic-templates/report ~/Coding/my-report
copier copy gh:mappedinfo/academic-templates/paper ~/Coding/my-paper

# 本地克隆后使用
copier copy ./academic-templates/literature-review ~/Coding/my-review
```

copier 会逐个询问 `project_name`、`title`、`author` 等变量（均有默认值，
`--defaults` 可全部跳过）。已生成的项目日后可用 `copier update` 跟随模板升级。

## 格式宪法

模板遵循三档产出规范（与 `shiqi-assistant-router` 的 research-output-rules 一致）：

1. 思考/调研中间产物 → **Obsidian Markdown**（`brainstorm/`）
2. 需要复现的内容 → **Quarto `.qmd` + Python/R 代码绘图**（`report/`、`paper-replication/`）
3. 文献综述及正式文稿 → **LaTeX `.tex`**（`literature-review/`、`paper/`、`paper-with-code/`）

图的纪律：科研数据图**必须代码根据真实数据绘制**；流程图/框架图可模型生成
（TikZ / draw.io），但同样要求可版本化、与正文一致。禁止手绘数据图、禁止截图。

## 仓库结构

```text
fonts/                 字体基线的唯一权威来源（策略、安装脚本、各工具链接入文件）
<template>/
  copier.yml           变量定义
  template/            模板文件（*.jinja 会被变量渲染，其余原样拷贝）
```

## 添加新模板

1. 新建 `<name>/copier.yml` + `<name>/template/`；
2. 涉及字体的文件复用 `fonts/` 下的接入文件（LaTeX `latex-fonts.tex`、
   matplotlib `matplotlib-style.mplstyle`、R `ggplot-theme.R`）；
3. 在本 README 的模板清单中登记。
