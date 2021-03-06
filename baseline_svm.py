#!/usr/bin/env python3

"""Adapted from https://github.com/mdeff/fma/blob/master/baselines.ipynb"""

import numpy as np
import pandas as pd
from sklearn.utils import shuffle
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

import fma


y_train = pd.read_csv('data/train_labels.csv', index_col=0, squeeze=True)
features = fma.load('data/features.csv')
X_train = features[:25000]
X_test = features[25000:]


# Data cleaning


X_train = X_train.drop(fma.FAULTY_FILES)
y_train = y_train.drop(fma.FAULTY_FILES)

# The track IDs are integers for the training set.
X_train.index = pd.Index((int(i) for i in X_train.index), name='track_id')

# Should be done already, but better be sure.
X_train.sort_index(inplace=True)
X_test.sort_index(inplace=True)
y_train.sort_index(inplace=True)

assert (X_train.index == y_train.index).all()


# Pre-processing


X_train, y_train = shuffle(X_train, y_train, random_state=42)

# Should not be needed.
# enc = LabelEncoder()
# y_train = enc.fit_transform(y_train)

# Standardize features by removing the mean and scaling to unit variance.
scaler = StandardScaler(copy=False)
scaler.fit_transform(X_train)
scaler.transform(X_test)


# Train the classifier and make predictions.


clf = SVC(kernel='rbf', probability=True)
clf.fit(X_train, y_train)
y_test = clf.predict_proba(X_test)


# Create the submission file.


submission = pd.DataFrame(y_test, X_test.index, clf.classes_)
submission.index.name = 'file_id'

# Be sure that we predicted one and only one genre per track.
np.testing.assert_allclose(submission.sum(axis=1), 1)

print('Predicted tracks per genre:')
print(submission.idxmax(axis=1).value_counts())

submission.to_csv('data/submission_svm.csv', header=True)
