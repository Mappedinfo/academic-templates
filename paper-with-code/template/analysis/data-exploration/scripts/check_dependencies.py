#!/usr/bin/env python3
"""检查本机可用的绘图路径；缺少可选依赖不阻止项目初始化。"""
import json
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def probe(command, cwd):
    try:
        result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def check():
    rscript = shutil.which("Rscript")
    with tempfile.TemporaryDirectory(prefix="research-graphics-check-") as tmp:
        root = Path(tmp)
        results = {}
        for key, device, suffix in (
            ("r_svg", "grDevices::svg(f)", "svg"),
            ("r_svglite", 'if (!requireNamespace("svglite", quietly=TRUE)) quit(status=2); svglite::svglite(f)', "svg"),
            ("r_pdf", "grDevices::pdf(f)", "pdf"),
        ):
            output = root / (key + "." + suffix)
            code = ('f <- commandArgs(TRUE)[1]; ' + device + '; '
                    'if (dev.cur() == 1L) quit(status=3); plot(1:3); dev.off(); '
                    'if (!file.exists(f) || file.info(f)$size == 0) quit(status=4)')
            results[key] = bool(rscript and probe([rscript, "--vanilla", "-e", code, str(output)], tmp)
                                and output.is_file() and output.stat().st_size > 0)
        python_output = root / "python.png"
        code = ('import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as p; '
                'import sys; p.plot([1,2,3]); p.savefig(sys.argv[1])')
        results["python_matplotlib"] = bool(probe([sys.executable, "-c", code, str(python_output)], tmp)
                                              and python_output.is_file() and python_output.stat().st_size > 0)
    results["r_installed"] = bool(rscript)
    results["xquartz_installed"] = None
    if platform.system() == "Darwin":
        results["xquartz_installed"] = probe(["pkgutil", "--pkg-info", "org.xquartz.X11"], None)
    results["plot_available"] = any(results[k] for k in ("r_svg", "r_svglite", "r_pdf", "python_matplotlib"))
    return results


def display(result):
    def status(value):
        return "可用" if value else "不可用"
    print("绘图环境检查（可选依赖不会阻止初始化）")
    for label, key in (("R 自带 SVG", "r_svg"), ("R svglite SVG", "r_svglite"),
                       ("R PDF", "r_pdf"), ("当前 Python 的 Matplotlib", "python_matplotlib")):
        print(f"  {label}: {status(result[key])}")
    if result["xquartz_installed"] is not None:
        print(f"  XQuartz 安装记录: {'存在' if result['xquartz_installed'] else '未发现'}（仅供诊断，并非必需）")
    if not result["r_installed"]:
        print("  如需 R：从 https://cran.r-project.org/ 安装 R。")
    elif not result["r_svg"] and result["xquartz_installed"] is not None:
        print("  如需修复 macOS 的 R 自带 SVG：检查 Cairo/X11 依赖；可安装 XQuartz：brew install --cask xquartz（https://www.xquartz.org/）。安装后重启 R 再检查；仍失败时查看具体 R 错误。")
    if result["r_installed"] and not result["r_svglite"]:
        print('  如需 svglite：Rscript -e \'install.packages("svglite", repos="https://cloud.r-project.org")\'')
    if not result["python_matplotlib"]:
        print("  如需 Python 绘图：在本地 Notebook 所用环境中安装 matplotlib，例如 python -m pip install matplotlib。")
    if result["plot_available"]:
        print("  至少一种绘图路径可用；按报告需要选择。Notebook 内核的环境可能不同，需在该环境重新运行检查。")
    else:
        print("  当前检查未发现可用绘图路径；仍可初始化并撰写文字报告，图件待配置或使用已有图件。")


if __name__ == "__main__":
    result = check()
    if sys.argv[1:] == ["--json"]:
        print(json.dumps(result, ensure_ascii=False))
    elif sys.argv[1:]:
        print("用法: python check_dependencies.py [--json]", file=sys.stderr)
        sys.exit(2)
    else:
        display(result)
