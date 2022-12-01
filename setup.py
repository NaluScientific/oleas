import setuptools


setuptools.setup(
    name="oleas",
    description="OLEAS readout",
    python_requires=">=3.9",
    install_requires=[],
    packages=setuptools.find_packages(),
    entry_points = {
        'console_scripts': [
            'show_boards=oleas.scripts.show_boards:main',
        ],
    },

)
