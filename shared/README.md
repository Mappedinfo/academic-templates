# 共享实验工具（Shared Assets）

`shared/` 是**跨模板共享、与字体无关**的工具与配置的权威来源。字体基线的权威来源
仍是 [`fonts/`](../fonts/README.md)；两者遵循同一条规则：

> **先改权威源，再同步副本。** 直接改某个模板里的副本会造成漂移。

## 为什么需要它

生成的项目必须自包含（不能依赖这个仓库），所以每个用到的模板里都留一份**逐字节相同**的
副本。手工同步会失败——事实上有一次就失败了：`paper-replication` 的
`matplotlib-style.mplstyle` 曾漏掉 `Noto Sans SC` 双名回退。因此同步是可执行的：

```bash
./scripts/sync-shared.sh          # 权威源 -> 各模板副本
./scripts/sync-shared.sh --check  # 只检查漂移，有漂移退出码 1
```

新增共享资产后，把它登记到 `scripts/sync-shared.sh` 的 `ASSETS` 数组；同步脚本只会更新
**该模板已经存在**的副本，因此新模板需要先手工放一份，再纳入同步。对于 `.gitignore`
这类通用文件名，条目必须用第三个字段显式列出模板（例如
`shared/gitignore:.gitignore:paper,paper-with-code`）——否则会把别的模板自己手写的同名
文件当成副本覆盖掉。

## 目录内容

| 路径 | 用途 |
|---|---|
| `scripts/fetch_and_plot.py` | 批量 HTTP/API 取数：有界并发 + 磁盘缓存 + 断点续跑 + 立即出图 |
| `config/urls.example.txt` | URL 清单格式示例（复制为 `config/urls.txt` 后使用） |
| `data-exploration/` | 本地 Notebook、绘图数据目录和图目录，远端计算按需经 SSH 取回 |

## fetch_and_plot.py 的纪律

生成的项目里对应 `scripts/fetch_and_plot.py`，约定如下：

1. **有界并发**：一个工作池保持 `--concurrency` 个请求在途。对一批 API 写串行 `for`
   循环是 bug，不是简化。
2. **原始响应落盘**：每个响应缓存在 `data/cache/`，按 URL 哈希命名；重跑不重复请求，
   重画不重新取数。缓存内容保持原始口径，派生值由代码现算。
3. **断点续跑**：中断后重跑同一条命令——已缓存的跳过，失败的按指数退避重试。
4. **先看图**：数据到手立刻出 `figures/fetch-preview.pdf`（覆盖面板 + 自动识别经纬度时的
   地图面板），再写文字结论。图里标题明写 `raw fetch preview - not a result figure`，
   避免预览图被当成结果图。
5. **长任务不阻塞**：整批取数放到后台跑，日志与图事后取用，不要在对话里同步等。

```bash
python3 scripts/fetch_and_plot.py --urls config/urls.txt
python3 scripts/fetch_and_plot.py --urls config/urls.txt --concurrency 16
python3 scripts/fetch_and_plot.py --urls config/urls.txt --refresh
python3 scripts/fetch_and_plot.py --selftest     # 离线：只画合成数据，用于验证字体与样式
```

输出：`data/cache/*.json`（原始响应）、`data/fetch_manifest.csv`（url/状态/字节数/时间，
可追溯清单）、`figures/fetch-preview.pdf`（预览图）。

`--selftest` 不联网，是新机器上验证字体基线是否装好的最快方式（与
[`fonts/README.md`](../fonts/README.md) 的「CI/新机器渲染前先跑安装脚本」配套）。
