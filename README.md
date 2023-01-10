# OLEAS Readout Scripts


### Setup
First, ensure that NaluDaq and NaluConfigs are installed and up to date, and you are using an environment with Python 3.9+.

Next, clone this repository if you don't have it locally already:
```
$ git clone http://gitlab.naluscientific.com/nalusoft/prototypes/oleas-readout.git
```

Next, install the package as editable. You MUST include the `-e` flag to edit the sweep parameters!
```
(my-env) $ pip install -e oleas-readout
```

## Gated PMT Sweep (For Calibration)
The `scripts/sweep.py` script runs a 2D sweep over the PMT gain and gate delay and captures events at each point.

The sweep is run using the following command:
```
(my-env) $ python scripts/sweep.py -s BOARD_SERIAL_NUMBER -o OUTPUT_FILE
```

- `BOARD_SERIAL_NUMBER` is the FTDI serial number of the board. If you are unsure of the serial number, you can use the `scripts/show_boards.py` script to fetch the serial numbers of boards currently connected to your computer.
- `OUTPUT_FILE` is the location where the output pickle file should be saved.

To adjust the sweep settings please edit the `scripts/sweep.py` script.

## Capture Script
The `scripts/capture.py` script is run using the same arguments as the `sweep.py` (calibration) script, with the
addition of a `-i`/`--interval` argument (see below).

This script will run indefinitely, capturing at a set interval. To stop the script, press `Control`+`C` in the terminal window.
For each iteration, the gate delay and PMT gain are moved together, with the PMT gain as an arbitrary function of the gate delay.

Each iteration happens at a fixed interval. After completing one iteration, the script will pause until it is
time for the next iteration. This duration must be set using the `-i`/`--interval` argument. If the duration
is too short, iterations will occur back-to-back.

To adjust the capture settings please edit the `scripts/capture.py` script.


### Calibration Data Format
The sweep (calibration) output file is a Python pickle, and is loaded like so:

```py
>>> import pickle
>>> with open('the/pickle/file.pkl', 'rb') as f:
...     sweep_data = pickle.load(f)
```

The sweep data itself is a dictionary with the following entries:
- `'dac'` (`list[int]`): a list of the dac values used to control the PMT gain.
- `'delay'` (`list[int]`): a list of the gate delay values.
- `'data'` (`list[list[list[dict]]]`): the events gathered at each point. Events are accessed in the following manner: `[gain_index][delay_index][capture_number]`. The indices correspond with the `'dac'` and `'delay'` lists.


### Capture Data Format
The capture output file is a also Python pickle, and is loaded like so:

```py
>>> import pickle
>>> with open('the/pickle/file.pkl', 'rb') as f:
        capture_data = pickle.load(f)
```

The capture data is formatted similarly to the calibration data, and has the following keys:
- `'dac'` (`list[int]`): a list of the dac values used to control the PMT gain.
- `'delay'` (`list[int]`): a list of the gate delay values.
- `'data'` (`list[list[list[dict]]]`): the events gathered at each iteration. Events are accessed in the following manner: `[iteration][dac_delay_index][capture_number]`. `dac_delay_index` corresponds with the `'dac'` and `'delay'` lists.
- `'times'` (`list[datetime]`): the ordered starting times for each iteration.

The `'dac'` and `'delay'` lists are the PMT DAC and gate delay values used when capturing a gated portion of the reflections for a single laser pulse.
