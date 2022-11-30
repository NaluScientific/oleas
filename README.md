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

After installing the package you will have access to two new commands:
- `oleas_sweep`
- `oleas_sensors`

### Gated PMT Sweep
The `oleas_sweep` script sweeps the gate delay and captures events at each point. On each iteration the PMT gain is adjusted as well.

The sweep is run using the following command:
```
(my-env) $ oleas_sweep -s BOARD_SERIAL_NUMBER -o OUTPUT_FILE
```

- `BOARD_SERIAL_NUMBER` is the FTDI serial number of the board.
- `OUTPUT_FILE` is the location where the output pickle file should be saved.


To adjust the sweep settings, you may edit the `settings.toml` file located in this package.


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
- `'data'` (`list[list[dict]]`): a list of the events gathered at each iteration.
- `'sensors'` (`list[dict]`): a list of the sensor readings at each iteration.
