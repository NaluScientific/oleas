import os
import setuptools
from setuptools import setup

setup(
    name="oleas",
    description="OLEAS readout",
    python_requires=">=3.9",
    install_requires=[
        'dynaconf==3.1.11'
    ],
    entry_points = {
        'console_scripts': [
            'oleas_sensors=oleas.scripts.read_sensors:main',
            'oleas_sweep=oleas.scripts.sweep:main',
        ],
    },
    packages=setuptools.find_packages(),
)
