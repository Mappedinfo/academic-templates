#!/usr/bin/env Rscript
# 从已保存的真实汇总表重画，不覆盖已有图。
args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 4) stop('用法: Rscript plot.R summary.csv x_column y_column output.pdf|output.svg')
input <- args[[1]]
x_column <- args[[2]]
y_column <- args[[3]]
output <- args[[4]]
if (!file.exists(input)) stop('输入汇总表不存在')
if (file.exists(output)) stop('输出已存在；请使用新文件名')
data <- read.csv(input, check.names = FALSE, stringsAsFactors = FALSE)
if (!all(c(x_column, y_column) %in% names(data))) stop('列名不在输入表中')
if (!is.numeric(data[[y_column]])) stop('y 列必须为数值')
dir.create(dirname(output), recursive = TRUE, showWarnings = FALSE)
extension <- tolower(tools::file_ext(output))
if (extension == "pdf") {
  pdf(output, width = 7, height = 4)
} else if (extension == "svg") {
  svg(output, width = 7, height = 4)
} else {
  stop("输出格式必须是 .pdf 或 .svg")
}
if (dev.cur() == 1L) stop("绘图设备未启动；请检查 SVG/Cairo 依赖或改用 PDF")
x <- data[[x_column]]
if (is.character(x)) x <- factor(x)
plot(x, data[[y_column]], xlab = x_column, ylab = y_column)
dev.off()
if (!file.exists(output) || file.info(output)$size == 0) stop('绘图失败：输出不存在或为空')
cat('已保存本地图:', output, '\n')
