# ggplot-theme.R — Academic Templates figure font baseline for R/ggplot2.
# Usage: source("ggplot-theme.R") then + theme_shiqi()
# Requires: install.packages(c("showtext", "ggplot2")) and the font baseline
# installed (fonts/setup-fonts.sh).

library(showtext)
library(ggplot2)

font_add("libertinus-sans", regular = "Libertinus Sans")
font_add("noto-cjk-sans", regular = "Noto Sans CJK SC")
showtext_auto()

theme_shiqi <- function(base_size = 11) {
  theme_minimal(base_size = base_size, base_family = "libertinus-sans") +
    theme(
      plot.title = element_text(face = "bold"),
      panel.grid.minor = element_blank()
    )
}
