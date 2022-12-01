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

## Gated PMT Sweep
The `scripts/sweep.py` script runs a 2D sweep over the PMT gain and gate delay and captures events at each point.

The sweep is run using the following command:
```
(my-env) $ python scripts/sweep.py -s BOARD_SERIAL_NUMBER -o OUTPUT_FILE
```

- `BOARD_SERIAL_NUMBER` is the FTDI serial number of the board. If you are unsure of the serial number, you can use the `scripts/show_boards.py` script to fetch the serial numbers of boards currently connected to your computer.
- `OUTPUT_FILE` is the location where the output pickle file should be saved.

To adjust the sweep settings please edit the `scripts/sweep.py` script.


### Sweep Data Format
The sweep output file is a Python pickle, and is loaded like so:

```py
>>> import pickle
>>> with open('the/pickle/file.pkl', 'rb') as f:
...     sweep_data = pickle.load(f)
```

The sweep data itself is a dictionary with the following entries:
- `'pmt_gains'` (`list[int]`): a list of the dac values used to control the PMT gain.
- `'gate_delays'` (`list[int]`): a list of the gate delay values.
- `'data'` (`list[list[list[dict]]]`): the events gathered at each point. Events are accessed in the following manner: `[gain_index][delay_index][capture_number]`. The indices correspond with the `'pmt_gains'` and `'gate_delays'` lists.
- ~~`'sensors'` (`list[list[dict]]`): a list of the sensor readings at each iteration.~~ Not implemented.
