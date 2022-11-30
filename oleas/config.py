from pathlib import Path

from dynaconf import Dynaconf

FILE = Path(__file__).resolve().parent.parent / 'settings.toml'

settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=[str(FILE)],
)

# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load these files in the order.
