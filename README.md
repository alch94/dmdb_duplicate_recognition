# DMDB Duplicate recognition script
This code was written for a class at OTH Regensburg
#Description
The goal of the class was to remove as many duplicates as possible from the restaurants dataset, which can be found at https://hpi.de/naumann/projects/repeatability/datasets/restaurants-dataset.html.
## Setup before running
Before running the scripts, you need to specify necessary properties in Scripts/Properties.py so thhe scripts can access your data files and mongodb server
## How to run the whole script
- create a python venv and install requirements.txt with
`pip install requirements.txt`
- Enter the necessary properties in scripts/Properties.py
- Run the remove_duplicates.py file to store the data in your mongodb cluster and print several metrics
- Additionally if you want to run the jupyter notebook, you need to start a jupyter server and navigate to the remove_duplicates.ipynp directory


