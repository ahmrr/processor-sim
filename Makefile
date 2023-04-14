PY:=python3.11
INFILE:=test/fib.dat
FLAGS:=--step --data test/sample-data.dat --memory 4096
MAIN:=src/controller.py

run:
	$(PY) $(MAIN) $(FLAGS) $(INFILE)