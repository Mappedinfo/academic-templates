LATEXMK = latexmk -xelatex -interaction=nonstopmode -halt-on-error

all: experiments figures paper

fetch:
	@test -f config/urls.txt || { echo "create config/urls.txt from config/urls.example.txt"; exit 1; }
	python3 scripts/fetch_and_plot.py --urls config/urls.txt

experiments:
	python3 scripts/run_experiments.py

figures:
	python3 scripts/plot_results.py

paper:
	cd paper && $(LATEXMK) main.tex

test:
	cd code && uv run pytest

clean:
	cd paper && latexmk -C

.PHONY: all fetch experiments figures paper test clean
