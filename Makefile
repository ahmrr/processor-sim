PY:=python3.11
INFILE:=sample-complete.dat
FLAGS:=--step --memory 4096
MAIN:=src/controller.py

all: run

run:
	$(PY) $(MAIN) $(FLAGS) $(INFILE)