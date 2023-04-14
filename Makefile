PY:=python3.11
INFILE:=test/fib.dat
FLAGS:=--step --data test/sample-data.dat --memory 4096
MAIN:=src/controller.py

run:
	$(PY) $(MAIN) $(FLAGS) $(INFILE)

zip:
	zip -x .git/\* .vscode/\* __pycache__/\* src/__pycache__/\* .gitignore LICENSE -r ../project3.zip .