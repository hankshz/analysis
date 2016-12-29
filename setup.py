from setuptools import setup, find_packages
import os

setup(
    name = "poll",
    version = '0.1',
    description = "Poll based on twitter",
    long_description = "Poll based on twitter",

    packages=find_packages(),

    scripts=['bin/{}'.format(filename) for filename in os.listdir('bin')],

    # build dependencies
    setup_requires = [],

    # run-time package dependencies
    install_requires = [],

    # data files installed in packages
    package_data = {},

    # data files outside package
    data_files = [],
)
