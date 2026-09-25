WORK      = main
LATEXMK   = latexmk -xelatex -interaction=nonstopmode -halt-on-error

all:
	$(LATEXMK) $(WORK).tex

watch:
	$(LATEXMK) -pvc $(WORK).tex

fetch:
	@test -f config/urls.txt || { echo "create config/urls.txt from config/urls.example.txt"; exit 1; }
	python3 scripts/fetch_and_plot.py --urls config/urls.txt

figures:
	python3 scripts/plot_main_result.py

clean:
	latexmk -C

.PHONY: all watch fetch figures clean
