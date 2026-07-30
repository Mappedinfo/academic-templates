# 字体基线（Font Baseline）

本仓库所有模板的字体策略的**唯一权威来源**。解决三类长期痛点：中文字体、英文字体、图片字体。

## 基线组合（全平台可复现、无版权风险）

| 角色 | 字体 | 用途 |
|---|---|---|
| 中文正文 | **Noto Serif CJK SC**（思源宋体） | 正式文稿、论文、综述 |
| 中文黑体 | **Noto Sans CJK SC**（思源黑体） | 幻灯片、标题、图片 |
| 中文等宽 | **Noto Sans Mono CJK SC** | 代码 |
| 英文衬线 | **Libertinus Serif**（Times 兼容） | 正文 |
| 英文无衬线 | **Libertinus Sans** | 幻灯片、图片、标题 |
| 英文等宽 | **Libertinus Mono** | 代码 |
| 数学 | **Libertinus Math**（unicode-math） | 公式 |

设计理由：Noto CJK 与 Libertinus 都是开源字体，macOS/Linux/Windows/CI 均可安装，
渲染结果跨机器一致；Libertinus Serif 与 Times New Roman 度量兼容，投稿时替换零成本。

## 安装

```bash
./fonts/setup-fonts.sh        # macOS (Homebrew)
```

Homebrew 的 Noto CJK 包体积大、网络不佳时易失败；备选方案（同一 release zip，支持断点续传，可反复运行直至完成）：

```bash
./fonts/setup-fonts-direct.sh # 从 GitHub 直接下载 Noto CJK OTF + Libertinus
```

两套命名等价（同一设计的不同打包），所有模板已内置双名回退：优先 `Noto * CJK SC`，
自动回退 `Noto * SC`。其他平台见脚本内注释（Debian/Ubuntu: `fonts-noto-cjk` + `fonts-libertinus`）。

## 各工具链接入点

| 工具链 | 接入文件 | 用法 |
|---|---|---|
| XeLaTeX / LuaLaTeX | `fonts/latex-fonts.tex` | `\input{latex-fonts.tex}`（模板已含） |
| Quarto | 模板 `_quarto.yml` 的 `mainfont/sansfont/monofont` | 已预置，无需操作 |
| matplotlib | `fonts/matplotlib-style.mplstyle` | `plt.style.use(...)`（模板脚本已含） |
| R / ggplot2 | `fonts/ggplot-theme.R` | `source(...)` + `theme_shiqi()` |

## 铁律

1. **不新增第四种字体家族**。模板外的临时需求也从上表选。
2. **图片字体与正文字体同源**：matplotlib/ggplot 输出的图嵌入文档后不产生字体突兀。
3. **不提交字体二进制**到任何项目仓库；字体由 `setup-fonts.sh` 安装到系统。
4. CI/新机器渲染前必须先跑字体安装脚本，否则回退字体导致版面漂移。
