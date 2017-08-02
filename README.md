# PIN-Inference
### A project by Tristan Gurtler, Charissa Miller, Kendall Molas, and Lynn Wu during the NYIT REU 2017 session.

This project analyzes keystroke timings collected from a simulated ATM, in order to determine if side-channel attacks are viable on ATMs. Specifically, we seek to test whether or not, by determining the timing between keystrokes, we can extract information about what PINs could possibly fit these interkey timings, and reduce the possible space of PINs to try. This tool, then, analyzes the interkey timings and performs inference on them to discover PINs.

## Usage

Two python scripts in this project can be run to perform particular tasks.

### timing_stats.py

This tool takes timings collected into a SQLite database and visualizes keystroke timings, while performing basic statistical analysis on them. It features several modes:

* All users mode: (**-a**) analyzes the population data of all users collected
* Individual users mode: (**-i**) analyzes each user separately
* Raw data mode: (**-r**) makes visualizations based on the raw data, rather than any models attempted to be fit into them
* Modeled data mode: (**-m**) makes visualizations based on models fit to the data, rather than raw data

Any and all of these modes can be used simultaneously.

Use this tool as follows:

**python timing_stats.py [-a] [-i] [-m] [-r] <superlist> <output_plot> [--plot_title "title of the plot"] [--text_output <text_output_file>]**

Where **<superlist>** is the list of sets you want to compare (specified in common.py), **<output_plot>** is the filename of the plot that will be output, **--plot_title** specifies an alternate title for the plot (there is a default), and **--text_output** is the filename of the output of statistical functions to be carried out (which have only text output; default action is to not save this output).

### inference.py

This tool takes timings collected into a SQLite database and attempts to perform inference on the PINs found. It outputs a list of how many guesses it required to find every PIN it tests.

Use this tool as follows:

**python inference.py**
