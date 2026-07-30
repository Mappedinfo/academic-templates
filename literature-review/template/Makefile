WORK      = main
LATEXMK   = latexmk -xelatex -interaction=nonstopmode -halt-on-error

all:
	$(LATEXMK) $(WORK).tex

watch:
	$(LATEXMK) -pvc $(WORK).tex

figures:
	python3 scripts/plot_metrics.py

clean:
	latexmk -C

.PHONY: all watch figures clean
