# discharge-normalizer

[screenshot]: ./.github/screenshot.png

![screenshot][screenshot]

`normalizer.py` -- selectively normalizes discharge capacity data

## description

`normalizer.py` is a command line interface (CLI) written in Python 2.7 that
reads an input directory containing .csv files of battery cycle data. It then
selects data to process and normalizes the discharge capacities of each selected
cycle from 0 to 1. This processed data is then output to a nested directory
within the original directory, named `Normalized_Discharge_Capacities`.

Data is selected on the following criteria:

* If the percent difference between the global maximum current (over all cycles)
  and any current measurement within a cycle is greater than 10%, then only the
  first cycle and all other cycles with >10% current difference are selected. A
  significant change in current indicates a change within the cycling parameters
  (e.g.  power consumption), and hence the data should be kept and analyzed
  during these cycles.

* Otherwise (when no anomalous cycles are detected), then only the first, last, and
  every 100th trial in between are kept.

## options

```
[-v]	Generate verbose output for debugging. All other options are ignored
	entirely.
```

## usage

### On UNIX-like distributions:

Clone/download this `git` repository and run `./normalizer.py` in your terminal once
inside the directory.

### On Windows:

Clone/download this `git` repository. Open `normalizer.py` by double-clicking on
the file, and this should automatically spawn a Windows terminal executing this
script in `python2.7`. Alternatively, if Windows does not recognize
`normalizer.py` or if you just hate the Windows terminal like me, you may
install the `IDLE` Python IDE instead and run this module by pressing `<F5>`.
This will allow you to run the script as if you were using a terminal.

## future directions

As this is my first professional application of Python, I'm quite proud of it.
However, there are many design flaws that can be improved, and I hope to fix
them as an exercise to improve my scripting ability in Python.

* __Doesn't take full advantage of Python's features.__ I'm not a big fan of
  Python thus far.  There are a lot of artificial OOP constructs required by the
  average programmer to memorize, and are completely embedded within the
  language. However, in exchange, you get a language that makes programming
  about as easy as building with Legos, as long as you don't need to care about
  the speed or bloat of your software. I was completely bored out of my mind
  studying Python, and I only read the first few chapters on data structures and
  their objects and methods. I'll try to finish my textbook, and apply some of
  what I've learned to perhaps shorten this script.

* __Poor input/exception handling.__ I didn't do a lot of testing with this, and
  there are possibly many hidden nuances of user-side implementation I didn't
  account for. In addition, as errors in Python throw exceptions that completely
  shut down the program if not caught in a `try...except` block (rather than
  having sane exit codes like functions in `C`), tiny mistakes in the input will
  break the script and bewilder users.  In addition, the input handling could be
  optimized, I'd like to implement tab-completion and arrow keys if possible.

```
hydrocodone@t420 ~ % time ./normalizer.py
...
./normalizer.py 29.31s user 0.29s system 78% cpu 37.585 total
```

* __It's slow.__ While Python inherently is a slow, interpreted language, it
  shouldn't be this slow. There are a lot of reasons for this. This script
  creates two temporary files and parses each one before generating the next,
  and thus a total of three files are parsed for every file generated. Not an
  intelligent or optimized implementation, but it made the most sense and was
  easy to implement. Ideally, no temporary files should be generated at all.
  Reducing the number of `for` loops used would also improve performance
  slightly. For 226MB (only 10 batteries) of data, it takes my Thinkpad T420
  (Quad-core Intel i5-2520M @3.200GHz) nearly half a minute to process. On the
  old Windows 7 systems I tested it on, the same 226MB of data took more than a
  minute. For servers potentially storing gigabytes of unprocessed data, this is
  unacceptable.

* __It's kind of ugly.__ The lines often exceed 80 characters.  Sometimes, this
  is because of long strings for the CLI, and must be changed manually until I
  write a script that helps me format them automatically.  However, most of the
  time, there are too many indentations, nested `for` loops, etc. The
  readability should be improved.

## about

This script was written during my internship at Amprius Corporation, a company
specializing in the manufacture of lithium-ion batteries. Hence, it has a rather
specific use-case.
