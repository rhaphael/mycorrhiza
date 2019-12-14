from ..dataset.dataset import Dataset
from ..dataset.helpers import _partition
import numpy as np

class Model:
	'''
	Generic model for a sklearn classifier (sklearn.ensemble)
		adapted to mycorrhiza dataset types

	Note:
		RandomForestClassifier was used as a structure template (comments and names were taken from there):
			https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier
	'''
	def __init__(self, classifier, service_path, **args):
		"""
		Inits the mycorrhiza model with supplementary classifier from sklearn system.
		Args:
			classifier: sklearn classifier (sklearn.ensemble).
			service_path (str): Path to service folder that will be used as a temp storage for temp files.
			**args: all the other arguments to initialize classifier
		"""
		self.clf = classifier(**args)
		self.service_path = service_path

	@property
	def base_estimator_(self):
		'''
		The child estimator template used to create the collection of fitted sub-estimators.
		'''
		return self.clf.base_estimator_

	@property
	def estimators_(self):
		'''
		The collection of fitted sub-estimators.
		'''
		return self.clf.estimators_
	
	@property
	def classes_(self):
		'''
		The classes labels (single output problem), or a list of arrays of class labels (multi-output problem).
		'''
		return self.clf.classes_

	@property
	def n_classes_(self):
		'''
		The number of classes (single output problem), or a list containing the number of classes for each output (multi-output problem).
		'''
		return self.clf.n_classes_

	@property
	def n_features_(self):
		'''
		The number of features when fit is performed.
		'''
		return self.clf.n_features_

	@property
	def n_outputs_(self):
		'''
		The number of outputs when fit is performed.
		'''
		return self.clf.n_outputs_
	
	@property
	def feature_importances_(self):
		'''
		Return the feature importances (the higher, the more important the feature).
		'''
		return self.clf.feature_importances_

	@property
	def oob_score_(self):
		return self.clf.oob_score_

	@property
	def oob_decision_function_(self):
		return self.clf.oob_decision_function_

	
	def fit(self, dataset: Dataset=None, populations: np.ndarray=None, partitions=None,
			n_cores: int=1, include_indices: list=None, exclude_indices: list=None):
		"""
		Trains the classifier using the mycorrhiza templated dataset
		Args:
			dataset (Dataset): dataset to train
			populations (np.ndarray): populations
			partitions: list of partitions or partition generated by from mycorrhiza.dataset.helpers import _partition
				In case of list first element will be used
			n_cores (int): number of cores to use for tree splitting

		Note:
			If dataset is given, partitions will be ignored.
			If partitions is given, dataset and populations arguments will be ignored.
			Populations is required in case partitions scenario

		Advice:
			Try to utilize model._get_partition(dataset, n_cores) to obtain partition and then use it in the method.
			Regeneration of the partition can be computationally expensive.
		"""
		if dataset:
			if not dataset.num_samples:
				dataset.load()
			if not isinstance(populations, np.ndarray):
				populations = np.array(dataset.populations)

			partition = self._get_partition(dataset=dataset, n_cores=n_cores)

		elif isinstance(partitions, list):
			partition = partitions[0]
		elif isinstance(partitions, np.ndarray):
			partition = partitions
		else:
			raise ValueError("Either dataset of partitions must be provided")

		if isinstance(populations, list):
			populations = np.array(populations)
		elif not isinstance(populations, np.ndarray):
			raise ValueError("Populations must be provided")

		if isinstance(include_indices, (np.ndarray,list)):
			partition = partition[include_indices]
			populations = populations[include_indices]
		elif isinstance(exclude_indices, (np.ndarray,list)):
			include_indices = np.full(partition.shape[0], True, dtype=bool)
			include_indices[exclude_indices] = False
			partition = partition[include_indices]
			populations = populations[include_indices]

		self.clf.fit(partition, populations)

		return self

	def predict_proba(self, dataset: Dataset=None, partitions=None, n_cores: int=1,
			include_indices: list=None, exclude_indices: list=None):
		"""
		Predicts probability for the mycorrhiza templated dataset
		Args:
			dataset (Dataset): dataset to predict
			partitions: list of partitions or partition generated by from mycorrhiza.dataset.helpers import _partition
				In case of list first element will be used
			n_cores (int): number of cores to use for tree splitting

		Note:
			If dataset is given, partitions will be ignored.
			If partitions is given, dataset argument will be ignored.

		Advice:
			Try to utilize model._get_partition(dataset, n_cores) to obtain partition and then use it in the method.
			Regeneration of the partition can be computationally expensive.
		"""
		if dataset:
			if not dataset.num_samples:
				dataset.load()

			partition = self._get_partition(dataset=dataset, n_cores=n_cores)
		elif isinstance(partitions, list):
			partition = partitions[0]
		elif isinstance(partitions, np.ndarray):
			partition = partitions
		else:
			raise ValueError("Either dataset of partitions must be provided")

		if isinstance(include_indices, (np.ndarray,list)):
			partition = partition[include_indices]
		elif isinstance(exclude_indices, (np.ndarray,list)):
			include_indices = np.full(partition.shape[0], True, dtype=bool)
			include_indices[exclude_indices] = False
			partition = partition[include_indices]

		return self.clf.predict_proba(partition)

	def predict(self, dataset: Dataset=None, partitions=None, n_cores: int=1,
			include_indices: list=None, exclude_indices: list=None):
		"""
		Predicts classes for the mycorrhiza templated dataset
		Args:
			dataset (Dataset): dataset to predict
			partitions: list of partitions or partition generated by from mycorrhiza.dataset.helpers import _partition
				In case of list first element will be used
			n_cores (int): number of cores to use for tree splitting

		Note:
			If dataset is given, partitions will be ignored.
			If partitions is given, dataset argument will be ignored.

		Advice:
			Try to utilize model._get_partition(dataset, n_cores) to obtain partition and then use it in the method.
			Regeneration of the partition can be computationally expensive.
		"""
		if dataset:
			if not dataset.num_samples:
				dataset.load()

			partition = self._get_partition(dataset=dataset, n_cores=n_cores)
		elif isinstance(partitions, list):
			partition = partitions[0]
		elif isinstance(partitions, np.ndarray):
			partition = partitions
		else:
			raise ValueError("Either dataset of partitions must be provided")

		if isinstance(include_indices, (np.ndarray,list)):
			partition = partition[include_indices]
		elif isinstance(exclude_indices, (np.ndarray,list)):
			include_indices = np.full(partition.shape[0], True, dtype=bool)
			include_indices[exclude_indices] = False
			partition = partition[include_indices]

		return self.clf.predict(partition)

	def _get_partition(self, dataset: Dataset=None, n_cores: int=1):
		"""
		Obtain partition used for the class' methods.
		Args:
			dataset (Dataset): dataset to obtain partition
			n_cores (int): number of cores to use for tree splitting
		Note:
			The method generates single partition (1) with all the loci (0).
			For other configurations use mycorrhiza.dataset.helpers._partition 
		"""
		return _partition(dataset, self.service_path, 1, 0, n_cores)[0]