# -*- coding: utf-8 -*-
"""
Created on Fri Jun 19 14:27:02 2020

@author: biomet
"""

import numbers
import warnings
from abc import ABCMeta
from abc import abstractmethod
from math import ceil
import numpy as np
from scipy.sparse import issparse
import pandas as pd

from sklearn.base import BaseEstimator
from sklearn.base import ClassifierMixin
from sklearn.base import clone
from sklearn.base import RegressorMixin
from sklearn.base import is_classifier
from sklearn.base import MultiOutputMixin
from sklearn.utils import Bunch
from sklearn.utils import check_array
from sklearn.utils import check_random_state
from sklearn.utils.validation import _check_sample_weight
from sklearn.utils import compute_class_weight
from sklearn.utils.multiclass import check_classification_targets
from sklearn.utils.validation import check_is_fitted
from sklearn.utils.validation import _deprecate_positional_args
from sklearn import metrics
from sklearn.model_selection import train_test_split

from sklearn.tree._criterion import Criterion
from sklearn.tree._splitter import Splitter
from sklearn.tree._tree import DepthFirstTreeBuilder
from sklearn.tree._tree import BestFirstTreeBuilder
from sklearn.tree._tree import Tree
from sklearn.tree._tree import _build_pruned_tree_ccp
from sklearn.tree._tree import ccp_pruning_path
from sklearn.tree import _tree, _splitter, _criterion


DTYPE = _tree.DTYPE
DOUBLE = _tree.DOUBLE

CRITERIA_CLF = {"gini": _criterion.Gini, "entropy": _criterion.Entropy}

DENSE_SPLITTERS = {"best": _splitter.BestSplitter,
                   "random": _splitter.RandomSplitter}

# =============================================================================
# Read data set
# =============================================================================
        
cdi_meta = pd.read_csv("cdi_meta.csv").set_index("sample_id")
cdi_microbiome = pd.read_csv("cdi_OTUs.csv").set_index("index")

microbiome = cdi_microbiome
y = cdi_meta["DiseaseState"]
y = cdi_meta["DiseaseState"].apply(lambda x: 0 
                                          if x == "CDI" else 1
                                          if x == "ignore-nonCDI" else 2)
class_name = ["CDI", "ignore-nonCDI", "Health"]
X_train, X_test, y_train, y_test = train_test_split(microbiome, y, test_size=0.3, random_state=42)

# =============================================================================
# Main function
# =============================================================================



# =============================================================================
# Decision Tree Algorithm
# =============================================================================            
        
max_depth = 10
min_samples_leaf = 4
min_samples_split = 4
max_leaf_nodes = None
max_features = "auto"
criterion = "gini"
splitter = "best"
expanded_class_weight = None
sample_weight = expanded_class_weight
min_weight_leaf = 0.0
min_impurity_split = 0
min_impurity_decrease = 0
random_state = 42

random_state = check_random_state(random_state)

check_X_params = dict(dtype=DTYPE, accept_sparse="csc")
check_y_params = dict(ensure_2d=False, dtype=None)

X_train = check_array(X_train, **check_X_params)
y_train = check_array(y_train, **check_y_params)

n_samples, n_features_ = X_train.shape
y_train = np.atleast_1d(y_train)
y_train = np.reshape(y_train, (-1,1))

n_outputs_ = y_train.shape[1]

check_classification_targets(y_train)
y_train = np.copy(y_train)

classes_ = []
n_classes_ = []

y_original = np.copy(y)

y_encoded = np.zeros(y_train.shape, dtype=np.int)

for k in range(n_outputs_):
    class_k, y_encoded[:, k] = np.unique(y_train[:, k], return_inverse=True)
    classes_.append(class_k)
    n_classes_.append(class_k.shape[0])
    
y_train = y_encoded

n_classes_ = np.array(n_classes_, dtype=np.intp)

if getattr(y_train, "dtype", None) != DOUBLE or not y_train.flags.contigous:
    y_train = np.ascontiguousarray(y_train, dtype=DOUBLE)

max_depth = (np.iinfo(np.int32).max if max_depth is None 
             else max_depth)
max_leaf_nodes = (-1 if max_leaf_nodes is None 
                  else max_leaf_nodes)

max_features = max(1, int(np.sqrt(n_features_)))

criterion = CRITERIA_CLF[criterion](n_outputs_, n_classes_)

SPLITTERS = DENSE_SPLITTERS

splitter = SPLITTERS[splitter](criterion,
                               max_features,
                               min_samples_leaf,
                               min_weight_leaf,
                               random_state)

tree_ = Tree(n_features_, n_classes_, n_outputs_)

builder = DepthFirstTreeBuilder(splitter, min_samples_split,
                                min_samples_leaf, min_weight_leaf,
                                max_depth, min_impurity_decrease,
                                min_impurity_split)

builder.build(tree_, X_train, y_train)

classes_ = classes_[0]

n_classes_ = np.atleast_1d(n_classes_)
pruned_tree = Tree(n_features_, n_classes_, n_outputs_)
_build_pruned_tree_ccp(pruned_tree, tree_, 0)
tree_ = pruned_tree

X_test = check_array(X_test, dtype=DTYPE, accept_sparse="csr")
proba = tree_.predict(X_test)
n_samples = X_test.shape[0]
predictions = classes_.take(np.argmax(proba, axis=1), axis=0)
metrics.accuracy_score(y_test, predictions)























