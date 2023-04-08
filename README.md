# MIPS Processor Simulator by Ahmer Raza and Matthew Everette

CPSC 3300, Project 3 submission. Simulates a MIPS 5-stage pipelined processor.

## Running

Run the `controller.py` file in the `src` directory (with Python v3.11 or greater), specifying a valid MIPS binary as the input:

```console
user@computer:~$ python3.11 src/controller.py
usage: controller.py [-h] [-s] [-m size] infile

Simulate a MIPS-ISA 5-stage pipelined processor

positional arguments:
  infile                the input file (instruction memory)

options:
  -h, --help            show this help message and exit
  -s, --step            enable stepping mode; wait for user input before beginning next clock cycle
  -m size, --memory size, --mem size
                        specify custom size of data memory; default is 1024
**error**: the following arguments are required: infile
user@computer:~$ python3.11 src/controller.py --step --memory 4096 sample.dat
user@computer:~$
```

## Controls

If stepping mode is enabled, use the `S` key to step through each instruction and the `Q` key to quit. Use the left and right arrow keys to cycle through pipeline registers, and up and down arrow keys to browse data memory.

## Notes

The recommended terminal size is 30 lines by 120 cols. The program gives an error message if your terminal is too small; in that case, either zoom out, lower the font size, or resize the window, then rerun the program:

```console
user@computer:~$ echo "`tput lines` `tput cols`"
25 80
user@computer:~$ python3.11 src/controller.py --step --memory 4096 sample.dat
**error**: terminal is too small
user@computer:~$ echo "`tput lines` `tput cols`"
30 120
user@computer:~$ python3.11 src/controller.py --step --memory 4096 sample.dat
user@computer:~$
```

Python 3.11 was used simply because of its extensive typing features. The Python curses library was used to provide the terminal GUI. The MVC architectural pattern was used to organize the program, and the Observer design pattern was used to rerender the View whenever the Model is updated.
