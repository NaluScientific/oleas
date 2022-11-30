import os
import setuptools
from setuptools import setup

setup(
    name="oleas",
    description="OLEAS readout",
    python_requires=">=3.9",
    install_requires=[],
    entry_points = {
        'console_scripts': [
            'read_sensors=oleas.scripts.read_sensors:main',
            'sweep=oleas.scripts.sweep:main',
        ],
    },
    packages=setuptools.find_packages(),
)
