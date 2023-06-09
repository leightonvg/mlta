from typing import List, Optional, Tuple

import numpy as np
import pandas as pd

from metadatabase import MetaDataBase
from metalearners import BaseLearner


class BaseEvaluation:
    def __init__(self, n_configs: int = 25, max_time: int = 300, metric: str = "neg_log_loss", n_jobs: int = 1, verbosity: int = 1) -> None:
        """Initialize the Evaluation procedure, specifying its main static options
        Arguments
        ---------
        n_configs: integer,
            the number of solutions that should be evaluated for the metalearner (potentialy per dataset)
        max_time: int,
            time in seconds allowed for the metalearner's `online_phase()`
        metric: str,
            specify the metric to evaluate on
        n_jobs: int,
            the number of threads the `metalearner` is allowed to use. Default is 1.
        verbosity: int,
            if set to 1, then shows dataset_id when done with dataset
        """
        self._max_time = max_time
        self._metric = metric
        self._n_jobs = n_jobs
        self._verbosity = verbosity
        self._evaluation_results = None

    def evaluate(
        self,
        mdbase: MetaDataBase,
        metalearner: BaseLearner,
        dataset_characterizations: Optional[List[Tuple[int, List[int | float]]]],
        config_characterizations: Optional[List[Tuple[int, List[int | float]]]],
    ) -> List[Tuple[int, List[float | None]]]:
        """Evaluates the metalearner using this evaluation method, potentially using pre-computed dataset and configuration characterizations.
        Should store the evaluation results in self._evaluation_results to avoid losing any results""

        Arguments
        ---------
        mdbase: MetaDataBase,
            the metadatabase to perform the evaluation
        metalearner: Subclass of BaseStrategy,
            the meta-learning strategy that should be evaluated on the mdbase, should inherent from BaseStrategy
        dataset_characterizations: Optional[List[Tuple[int, List[int | float]]]]
            Pre-computed dataset characterizations, to avoid expensive re-computation per metalearner.
            A list of tuples, where each tuple represents a dataset characterization.
                The first element in the tuple refers to the dataset_id in mdbase,
                The second element is the purely numeric vector representing the dataset
        config_characterizations: Optional[List[Tuple[int, List[int | float | str]]]],
            Pre-computed configuration characterizations, to avoid expensive re-computation per metalearner.
            A list of tuples, where each tuple represents a configuration characterization.
                The first element in the tuple refers to the pipeline_id in `mdbase`,
                The second element is the vector representing the configuration (pipeline).

        Returns
        -------
        evaluation_results: List[Tuple[int, List[float | None]]],
            The evaluation results for each dataset in `mdbase`, each tuple in the list refers to evaluation results for one dataset.
            The first entry refers to the dataset_id as in the `mdbase`.
            The second entry is a list of floats or None, with the evaluation_results according to `metric` for all `n_configs` configurations.
                Each element is a config score, with `None` for a configuration which could not be evaluated properly on the test set.

        """
        raise NotImplementedError("This method should be implemented by a child class.")

    def store_results(self, path: str, metalearner_name: str):
        """Meant to be ran after `evaluate()`, to store its results to `path`.csv

        Arguments
        ---------
        metalearner_name: string
            the name the metalearner gets in the csv file under the "metalearner_name" header
        """
        if self._evaluation_results is None:
            raise Warning("No results to store, run `evaluate()` before running `store_results()`")

        results = []
        for dataset_results in self._evaluation_results:
            if dataset_results[1] is not None:
                if len(dataset_results[1]) != 0:
                    for score in dataset_results[1]:
                        results.append([metalearner_name, "{}".format(dataset_results[0]), score])

        if results == []:
            raise Warning("No results to store, all dataset evaluations were None.")

        evaluation_df = pd.DataFrame(np.array(results), columns=["metalearner_name", "dataset_id", "{}".format(self._metric)])
        evaluation_df.to_csv(path, index=False)
