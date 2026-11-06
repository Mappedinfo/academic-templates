# 数据探索与本地重绘

`analysis.ipynb` 在本机查看和编辑；默认不连接远程。项目可以改用 `.qmd`、`.Rmd` 或 `.md`，沿用现有报告，不必同时维护多份主稿。首次探索须实际记录来源与版本、观察单位、分布、适用的时间/空间覆盖与分辨率、缺失和零值及限制。

- 保留原始数据的现有本机或远程位置，不覆盖或删除；写明实际路径、数据版本、访问方式及保留策略。远程文件的长期可用性须实际核验。
- `plot-data/` 存本机重画所需的分组、统计值、频数、分箱、分母和空间数据，写明口径与源版本；此目录中的数据默认不进 Git，按数据许可和项目规则决定是否分享。
- `figures/` 存本机输出图；Notebook 代码读取本机绘图数据重新绘图。样例只说明接口，不制造结果或下载数据。
- 对远程大数据，先在该 Notebook 显式配置 `RUN_REMOTE`、SSH 别名、远端计算命令及产物路径；程序通过 SSH 运行获准的计算，读取远端结果并新建本地文件，不启动远程 Notebook、不覆盖已有本地数据。远端计算逻辑写在项目脚本中，原数据不参与搬迁。
- 汇总表无法支持新的粒度或分箱时，按现有权限重新访问原始数据、生成新版本；不把旧均值当成原始观测。记录参数、代码/数据版本、实际结果位置和未完成项。

安装项目使用的 Jupyter、pandas、matplotlib（或按实际工作切换 R/Quarto）。在本机打开 `analysis.ipynb`，选择本机内核，按 Notebook 的说明配置输入与列名，检查真实输出图。没有数据时保留未完成状态。

## 可选示例脚本

`python scripts/summarize.py --input <真实原始.csv> --group <分组列> --value <数值列> --output plot-data/summary.csv` 对 CSV 分块计算行数、有效数、零、缺失、总和和均值；默认只有空字符串为缺失，其他缺失符号用 `--missing-token` 明确声明。它只做一个分组列与一个数值列的汇总，时间/空间粒度、覆盖分母和复杂输入须按实际数据扩展。

`Rscript scripts/plot.R plot-data/summary.csv <x列> <y列> figures/summary.pdf` 在本机用保存的汇总表画图（需要 SVG 时可指定 `.svg`；优先使用 R 包 `svglite`，否则使用 R 自带的 Cairo SVG 设备）；输出已存在时需要新文件名。Notebook 可按实际项目将 `REMOTE_COMMAND` 指向远端项目中的汇总脚本。

本机需要 SVG 且 `svglite` 不可用时，可在有网络的 R 环境安装 `svglite`；保持项目依赖及实际 R 库路径可复查。

## 初始化绘图环境检查

运行 `python scripts/check_dependencies.py`（从本目录）或 `python analysis/data-exploration/scripts/check_dependencies.py`（从项目根目录）。检查器在临时目录实际绘制并检查 R 自带 SVG、`svglite` SVG、R PDF 与当前 Python 环境的 Matplotlib；macOS 额外查看 XQuartz 安装记录。可使用 `--json` 供工具读取。检查不会安装软件或修改项目，缺少可选依赖时仍正常退出。

R SVG 或 XQuartz 不是强制依赖：可用 PDF、Python 图件、已有图件或文字报告，按项目需求选择。没有任何可用绘图路径时，报告未完成的图件并按检查输出选择安装；不要把安装提示当作科研运行已完成。Notebook 的内核可能与终端使用不同的 Python 环境，应在实际本地内核环境中重新检查。
