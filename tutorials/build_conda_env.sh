#!/bin/bash
​
conda create -n ookla-open-data -y
conda activate ookla-open-data
​
conda config --env --add channels conda-forge \
    && conda config --env --set channel_priority strict
​
conda install pip python=3 geopandas -y
conda install jupyter matplotlib descartes -y
pip install adjustText
