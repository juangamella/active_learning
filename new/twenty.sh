#!/usr/bin/env bash

python3 make_dataset.py -p 20 -s .5 -d 50 --folder twenty
python3 run_experiments.py -n 60 -b 2 -k 2 --folder twenty --strategy random
python3 run_experiments.py -n 60 -b 2 -k 2 --folder twenty --strategy edge-prob
python3 run_experiments.py -n 60 -b 2 -k 2 --folder twenty --strategy learn-parents
python3 run_experiments.py -n 120 -b 2 -k 2 --folder twenty --strategy random
python3 run_experiments.py -n 120 -b 2 -k 2 --folder twenty --strategy edge-prob
python3 run_experiments.py -n 120 -b 2 -k 2 --folder twenty --strategy learn-parents