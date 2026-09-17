VENV = env
PRES = pres.ipynb
NOTES = notes.pdf
SRC = $(shell find src -name "*.md" | sort -n)

GEN = $(PRES) $(NOTES)

$(PRES):	$(VENV) $(SRC)
		$(VENV)/bin/lucina -o $@ $(SRC) --no-autolaunch

$(NOTES):	notes.md
		pandoc -V geometry:margin=0.3in $^ -o $@

$(VENV):
		python -m venv $@
		$(VENV)/bin/pip install -r requirements.txt

pres:		$(PRES)

notes:		$(NOTES)

clean:
		rm -f $(GEN)

re:		clean $(GEN)

serve:		$(PRES)
		$(VENV)/bin/jupyter-notebook --no-browser

run:		$(PRES)
		$(VENV)/bin/jupyter-notebook $<

.PHONY:		pres notes clean re serve run
