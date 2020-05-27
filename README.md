# ABCD vs A-ICP comparison

This repo is forked from [agrawalraj/active_learning](https://github.com/agrawalraj/active_learning). It contains minor changes to the code to get it to run and retrieve results for the experiments comparing ABCD to [A-ICP](https://github.com/agrawalraj/juangamella/aicp).

## Dependencies

You will need at least

Python 3.6

R 3.6

The installation procedure they provide didn't work for me, and some python dependencies were missing from the venv. This is what I did to get the code to run.

### Installing the R dependencies:

In an R terminal (also in `install.R`)

```
if (!requireNamespace("BiocManager", quietly = TRUE))
    install.packages("BiocManager")
BiocManager::install()
BiocManager::install("Rgraphviz, RBGL")
install.packages('pcalg', repos='http://cran.us.r-project.org')
install.packages('gRbase', repos='http://cran.us.r-project.org')
```

### Installing the Python dependencies

```
cd new/
bash make_venv.sh
source venv/bin/activate
pip install pyaml tqdm xarray causaldag
```

## Executing experiments

The dataset used to run the experiments is in data/dataset_3. Unfortunately, running the code renders the dataset unusable for other runs, so we have to copy it (I like to keep `dataset_3` as the "master copy"). For the experiments (a total of 12), we copy it 12 times, plus one to check everything works:

```
cd data/
cp -r dataset_3 dataset_3_0
cp -r dataset_3 dataset_3_1
cp -r dataset_3 dataset_3_2
cp -r dataset_3 dataset_3_3
cp -r dataset_3 dataset_3_4
cp -r dataset_3 dataset_3_5
cp -r dataset_3 dataset_3_6
cp -r dataset_3 dataset_3_7
cp -r dataset_3 dataset_3_8
cp -r dataset_3 dataset_3_9
cp -r dataset_3 dataset_3_10
cp -r dataset_3 dataset_3_11
cp -r dataset_3 dataset_3_test
```

I would then run a small experiment once to see if everything works:

```
python run_experiments.py -n 10 -b 2 -k 1 --boot 20 -s 7 --folder dataset_3_test --strategy entropy --starting-samples 100
```

If it doesn't crash after 1 minute I would then kill it and run the rest. To run the ABCD algorithm at 50, 100 and 1000 observational sample sizes, each for four rounds:

```
cd new/

python run_experiments.py -n 500 -b 50 -k 1 --boot 100 -s 7 --folder dataset_3_0 --strategy entropy --starting-samples 50
python run_experiments.py -n 500 -b 50 -k 1 --boot 100 -s 7 --folder dataset_3_1 --strategy entropy --starting-samples 50
python run_experiments.py -n 500 -b 50 -k 1 --boot 100 -s 7 --folder dataset_3_2 --strategy entropy --starting-samples 50
python run_experiments.py -n 500 -b 50 -k 1 --boot 100 -s 7 --folder dataset_3_3 --strategy entropy --starting-samples 50

python run_experiments.py -n 500 -b 50 -k 1 --boot 100 -s 7 --folder dataset_3_4 --strategy entropy --starting-samples 100
python run_experiments.py -n 500 -b 50 -k 1 --boot 100 -s 7 --folder dataset_3_5 --strategy entropy --starting-samples 100
python run_experiments.py -n 500 -b 50 -k 1 --boot 100 -s 7 --folder dataset_3_6 --strategy entropy --starting-samples 100
python run_experiments.py -n 500 -b 50 -k 1 --boot 100 -s 7 --folder dataset_3_7 --strategy entropy --starting-samples 100

python run_experiments.py -n 500 -b 50 -k 1 --boot 100 -s 7 --folder dataset_3_8 --strategy entropy --starting-samples 1000
python run_experiments.py -n 500 -b 50 -k 1 --boot 100 -s 7 --folder dataset_3_9 --strategy entropy --starting-samples 1000
python run_experiments.py -n 500 -b 50 -k 1 --boot 100 -s 7 --folder dataset_3_10 --strategy entropy --starting-samples 1000
python run_experiments.py -n 500 -b 50 -k 1 --boot 100 -s 7 --folder dataset_3_11 --strategy entropy --starting-samples 1000
```

**Parallelization**

The code automatically runs on as many cores as are made available to it. In Euler I would run each job with 48 cores. Perhaps this is not possible in the SfS machines.

**Results**

The results are pickled into the `new` directory. The filenames contain a timestamp and the parameters used, eg.

```
pp_1589260274_n_samples:500_n_batches:50_max_interventions:1_strategy:entropy_intervention_strength:5.0_starting_samples:100_target:0_intervention_type:gauss_target_allowed:True.pickle
```
