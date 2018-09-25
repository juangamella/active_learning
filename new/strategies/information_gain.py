from strategies.collect_dags import collect_dags
from utils import graph_utils
import xarray as xr
import numpy as np
import itertools as itr
from collections import defaultdict
from scipy.misc import logsumexp
from scipy import special
import random
from tqdm import tqdm


def binary_entropy(probs):
    probs = probs.copy()
    probs[probs < 0] = 0
    probs[probs > 1] = 1
    return special.entr(probs) - special.xlog1py(1 - probs, -probs)


def create_info_gain_strategy(n_boot, graph_functionals):
    def info_gain_strategy(iteration_data):
        # === CALCULATE NUMBER OF SAMPLES IN EACH INTERVENTION
        if iteration_data.max_interventions is None:
            nsamples = iteration_data.n_samples / iteration_data.n_batches
            if int(nsamples) != nsamples:
                raise ValueError('n_samples / n_batches must be an integer')
            nsamples = int(nsamples)
        # else:
        #     nsamples = iteration_data.n_samples / (iteration_data.n_batches * iteration_data.max_interventions)
        #     if int(nsamples) != nsamples:
        #         raise ValueError('n_samples / (n_batches * max interventions) must be an integer')
        #     nsamples = int(nsamples)

        sampled_dags = collect_dags(iteration_data.batch_folder, iteration_data.current_data, n_boot)
        gauss_dags = [graph_utils.prec2dag(iteration_data.precision_matrix, dag.topological_sort()) for dag in sampled_dags]

        # == CREATE MATRIX MAPPING EACH GRAPH TO 0 or 1 FOR THE SPECIFIED FUNCTIONALS
        functional_matrix = np.zeros([n_boot, len(graph_functionals)])
        for (dag_ix, dag), (functional_ix, functional) in itr.product(enumerate(gauss_dags), enumerate(graph_functionals)):
            functional_matrix[dag_ix, functional_ix] = functional(dag)

        # === FOR EACH GRAPH, OBTAIN SAMPLES FOR EACH INTERVENTION THAT'LL BE USED TO BUILD UP THE HYPOTHETICAL DATASET
        print('COLLECTING DATA POINTS')
        datapoints = [
            [
                dag.sample_interventional({intervened_node: intervention}, nsamples=nsamples)
                for intervened_node, intervention in zip(iteration_data.intervention_set, iteration_data.interventions)
            ]
            for dag in gauss_dags
        ]

        print('CALCULATING LOG PDFS')
        logpdfs = xr.DataArray(
            np.zeros([n_boot, len(iteration_data.intervention_set), n_boot, nsamples]),
            dims=['outer_dag', 'intervention_ix', 'inner_dag', 'datapoint'],
            coords={
                'outer_dag': list(range(n_boot)),
                'intervention_ix': list(range(len(iteration_data.interventions))),
                'inner_dag': list(range(n_boot)),
                'datapoint': list(range(nsamples))
            }
        )
        for outer_dag_ix in tqdm(range(n_boot), total=n_boot):
            for intv_ix, intervention in tqdm(enumerate(iteration_data.interventions), total=len(iteration_data.interventions)):
                for inner_dag_ix, inner_dag in enumerate(gauss_dags):
                    loc = dict(outer_dag=outer_dag_ix, intervention_ix=intv_ix, inner_dag=inner_dag_ix)
                    logpdfs.loc[loc] = inner_dag.logpdf(
                        datapoints[outer_dag_ix][intv_ix],
                        interventions={iteration_data.intervention_set[intv_ix]: intervention}
                    )

        print('COLLECTING SAMPLES')
        current_logpdfs = np.zeros([n_boot, n_boot])
        selected_interventions = defaultdict(int)
        for sample_num in range(nsamples):
            intervention_scores = np.zeros(len(iteration_data.interventions))
            intervention_logpdfs = np.zeros([len(iteration_data.interventions), n_boot, n_boot])
            for intv_ix in range(len(iteration_data.interventions)):
                for outer_dag_ix in range(n_boot):
                    # current number of times this intervention has already been selected
                    datapoint_ix = selected_interventions[intv_ix]

                    intervention_logpdfs[intv_ix, outer_dag_ix] = logpdfs.sel(
                        outer_dag=outer_dag_ix,
                        intervention_ix=intv_ix,
                        datapoint=datapoint_ix
                    )
                    new_logpdfs = current_logpdfs[outer_dag_ix] + intervention_logpdfs[intv_ix, outer_dag_ix]

                    importance_weights = np.exp(new_logpdfs - logsumexp(new_logpdfs))
                    functional_probabilities = (importance_weights[:, np.newaxis] * functional_matrix).sum(axis=0)

                    functional_entropies = binary_entropy(functional_probabilities)
                    intervention_scores[intv_ix] += functional_entropies.sum()
            # print(intervention_scores)

            if iteration_data.max_interventions is None or len(selected_interventions.keys()) < iteration_data.max_interventions:
                best_intervention_score = intervention_scores.min()
            else:
                best_intervention_score = intervention_scores[list(selected_interventions.keys())].min()
            best_scoring_interventions = np.nonzero(intervention_scores == best_intervention_score)[0]
            selected_intv_ix = random.choice(best_scoring_interventions)
            current_logpdfs = current_logpdfs + intervention_logpdfs[selected_intv_ix]
            selected_interventions[selected_intv_ix] += 1

        return selected_interventions

    return info_gain_strategy

