# MIPS Processor Simulator by Ahmer Raza and Matthew Everette

**CPSC 3300 - Project 3**

Simulates a MIPS 5-stage pipelined processor, with only a limited set of instructions:
`lw`, `sw`, `beq`, `add`, `sub`, `and`, `or`, `slt`, `j`

The simulator has automatic data and control hazard detection and handling.

Dependencies:

- Python >3.11
- The Python `curses` module

## Running

Run the `controller.py` file in the `src` directory (with Python v3.11 or greater), specifying a valid MIPS binary as the input:

```console
user@computer:~$ python3.11 src/controller.py
usage: controller.py [-h] [-s] [-m size] [-d data] infile

Simulate a MIPS-ISA 5-stage pipelined processor

positional arguments:
  infile                the input file (instruction memory)

options:
  -h, --help            show this help message and exit
  -s, --step            enable stepping mode; wait for user input before beginning next clock cycle
  -m size, --memory size, --mem size
                        specify custom size of data memory; default is 1024
  -d data, --data data  specify custom data memory input; default is empty. If a memory size is also specified, any remaining space not included in
                        the input data file will be filled.
error: the following arguments are required: infile
user@computer:~$ python3.11 src/controller.py --step --memory 4096 --data test/sample-data.dat test/fib.dat
user@computer:~$
```

There are a number of sample inputs, given in the `test` directory. The given Makefile's default target (`make run`, `make`) runs the program with step mode enabled, a data memory size of 4096, a sample data memory of `sample-data.dat`, and the Fibonacci sample assembly program (`fib.dat`, assembled from `fib.s`).

Fibonacci program:

```c
lw $1, 0($0)
lw $2, 4($0)
add $3, $0, $0
lw $4, 4($0)
add $5, $3, $4
add $3, $4, $0
add $4, $5, $0
sub $1, $1, $2
beq $1, $0, 1
j 4
sw $3, 0($0)
```

Pseudocode equivalent:

```c
$1 = *(0x0)
$2 = *(0x4)
$3 = $0 + $0
$4 = *(0x4)
$5 = $3 + $4
$3 = $4 + $0
$4 = $5 + $0
$1 = $1 - $2
if ($1 == $0)
    branch_to_line(1)
jump_to_pc(4)
*(0x0) = $3
```

## Controls

If stepping mode is enabled, use the `S` key to step through each instruction and the `Q` key to quit. Use the left and right arrow keys to cycle through pipeline registers, and up and down arrow keys to browse data memory. If stepping mode is not enabled, you may only use the quit function and may only view memory and pipeline registers after the entire program's execution has finished.

## Notes

The recommended terminal size is 30 lines by 120 cols. The program gives an error message if your terminal is too small; in that case, either zoom out, lower the font size, or resize the window, then rerun the program:

```console
user@computer:~$ echo "`tput lines` `tput cols`"
25 80
user@computer:~$ python3.11 src/controller.py --step --memory 4096 --data test/sample-data.dat test/fib.dat
error: terminal is too small
user@computer:~$ echo "`tput lines` `tput cols`"
30 120
user@computer:~$ python3.11 src/controller.py --step --memory 4096 --data test/sample-data.dat test/fib.dat
user@computer:~$
```

Python 3.11 was used simply because of its extensive typing features. The Python curses library was used to provide the terminal GUI. The MVC architectural pattern was used to organize the program, and the Observer design pattern was used to rerender the View whenever the Model is updated.

The hazard detection unit inserts `nop`s whenever a control or data hazard occurs. `nop`s are also inserted at the end of the program to "flush" the remaining pipeline stages that need to be executed.
