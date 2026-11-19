# Academic Templates

一套标准化的科研工作模板库，统一解决**中文字体、英文字体、图片字体**问题，
覆盖科研项目的常见形态。每个子目录是一个独立的 [copier](https://copier.readthedocs.io/) 模板。

## ATS：从 Git 安装

ATS（Academic Template Starter）是这套模板的小型 Python CLI，需要 Python 3.11+、
[uv](https://docs.astral.sh/uv/) 和 Git。本轮仅通过现有 Git 仓库分发，不上传 PyPI。
以下安装命令固定使用 `v0.1.0`，不会随默认分支变化。

```bash
uv tool install 'mappedinfo-ats @ git+https://github.com/Mappedinfo/academic-templates.git@v0.1.0'
ats --version
ats list
ats init paper-with-code my-paper

# 可选：覆盖问卷变量，其余使用原 Copier 默认值
ats init paper-with-code another-paper --data 'title=My Paper' --data author=Alice --data language=en

# 卸载 CLI（已生成的项目仍保留）
uv tool uninstall mappedinfo-ats
```

`init` 的目标必须是不存在的新目录；已有目录（包括空目录）、文件或符号链接均会被拒绝。
项目名默认取目标目录名。初始化只渲染模板，不运行模板任务、不自动信任模板、不训练、
不安装字体或项目依赖，也不初始化 Git。`paper-with-code` 的实验脚本目前写入占位数据，
真实训练、数据、指标与实验协议需要在新项目内实现；本版不迁移已有实验。

安装包自带全部 7 个模板，初始化无需再下载仓库，离开源码目录也能使用。
模板仍只在现有 `<template>/copier.yml` 和 `<template>/template/` 中维护：构建钩子
将同一份文件打入 wheel，sdist 保留原路径，仓库中不维护第二套副本。

ATS 与 `academic-project-init` 使用同一套 Copier 来源。需要固定已发布版本时用上述 ATS
命令；该 skill 已有的本地仓库具体提交哈希与直接 Copier 调用路径继续适用。ATS 不代替
skill 的字体、编译、依赖检查等后续工作。`paper-with-code`、`paper-replication` 已生成的
`.copier-answers.yml` 由 ATS 记录为本仓库的对应版本 tag；其他模板沿用原有行为。
使用 `copier update` 前先提交项目修改并检查 answers 文件与来源版本。

仓库目前未声明许可证；本版不添加许可证或授权声明。

维护者可在干净 checkout 中构建和验证同一份标准 Python 包（无需发布到 PyPI）：

```bash
uv build
uv tool install ./dist/mappedinfo_ats-0.1.0-py3-none-any.whl
python3 scripts/smoke_ats.py "$(command -v ats)"
```

GitHub Actions 构建 wheel/sdist 并验证已安装 CLI，构建产物保存在工作流 artifacts 中。
本次 `v0.1.0` 的发布分支在验证通过后创建新 tag，再从远端 tag 使用隔离环境安装并运行
同一 smoke 脚本，成功后创建 GitHub Release 并附上 wheel/sdist。
已有 tag 保持不变；当前仓库不自动发布到包注册表。

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

# 方式一：直接从 GitHub 初始化（交互式选择模板）
copier copy gh:mappedinfo/academic-templates ~/Coding/my-project

# 非交互指定模板与变量
copier copy --defaults --data template=paper --data project_name=my-paper \
  gh:mappedinfo/academic-templates ~/Coding/my-paper

# 方式二：本地克隆后按模板使用
copier copy ./academic-templates/literature-review ~/Coding/my-review
```

Copier 会逐个询问 `template`、`project_name`、`title`、`author` 等变量，
`--defaults` 使用默认值。需要升级时先确认生成了 `.copier-answers.yml`；
`paper-with-code` 和 `paper-replication` 已包含该文件，其他模板不能假定支持 `copier update`。

## 格式宪法

模板遵循三档产出规范（与 `shiqi-assistant-router` 的 research-output-rules 一致）：

1. 思考/调研中间产物 → **Obsidian Markdown**（`brainstorm/`）
2. 需要复现的内容 → **Quarto `.qmd` + Python/R 代码绘图**（`report/`、`paper-replication/`）
3. 文献综述及正式文稿 → **LaTeX `.tex`**（`literature-review/`、`paper/`、`paper-with-code/`）

图的纪律：科研数据图**必须代码根据真实数据绘制**；流程图/框架图可模型生成
（TikZ / draw.io），但同样要求可版本化、与正文一致。禁止手绘数据图、禁止截图。

## 数据获取与立即出图

`paper/`、`paper-replication/`、`paper-with-code/`、`report/` 四个模板自带
`scripts/fetch_and_plot.py`：批量 HTTP/API 取数的默认实现，**有界并发 + 磁盘缓存 +
断点续跑 + 立即出图**。

```bash
cp config/urls.example.txt config/urls.txt          # 一个 URL 一行
python3 scripts/fetch_and_plot.py --urls config/urls.txt   # 或 make fetch
python3 scripts/fetch_and_plot.py --selftest               # 离线：只画合成数据
```

纪律（详见 [`shared/README.md`](shared/README.md)）：

- 对一批 API 写串行 `for` 循环是 bug，不是简化；默认 `--concurrency 8`。
- 原始响应落盘 `data/cache/`，重跑只补失败项，重画不重新取数。
- 数据到手先出 `figures/fetch-preview.pdf` 看图，再写文字结论；预览图标题明写
  `not a result figure`，避免被当成结果图。
- 整批取数放后台跑，不阻塞对话；`data/fetch_manifest.csv` 是 url/状态/字节数/时间的
  可追溯清单。

## 实验数据探索

`paper-replication` 和 `paper-with-code` 初始化后自带 `analysis/data-exploration/`：
本地 `analysis.ipynb` 查看和重绘，`plot-data/` 保存本机汇总，`figures/` 保存本地图。
原始数据可留在远程原位置；按需由本地 Notebook 经 SSH 执行获准汇总并取回数据。
操作、数据保护与 Notebook 参数见生成项目中的该目录 README；项目可按需要改用
Quarto、R Markdown 或其他报告格式。模板不会在初始化时连接远程或生成虚构结果。

## 仓库结构

```text
fonts/                 字体基线的唯一权威来源（策略、安装脚本、各工具链接入文件）
shared/                跨模板共享的实验工具权威来源（取数脚本、URL 清单示例）
scripts/sync-shared.sh 权威源 -> 各模板副本；--check 只查漂移并以退出码报错
<template>/
  copier.yml           变量定义
  template/            模板文件（*.jinja 会被变量渲染，其余原样拷贝）
```

## 添加新模板

1. 新建 `<name>/copier.yml` + `<name>/template/`；
2. 涉及字体的文件复用 `fonts/` 下的接入文件（LaTeX `latex-fonts.tex`、
   matplotlib `matplotlib-style.mplstyle`、R `ggplot-theme.R`）；
3. 需要共享实验工具就放一份 `shared/scripts/fetch_and_plot.py` 与
   `shared/config/urls.example.txt` 的副本，然后跑 `./scripts/sync-shared.sh`；
4. 在本 README 的模板清单中登记。
