"script for assessing the performance of sklearns SVC on connectivity data"

import argparse

import os
import glob
import json
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from format_data import load_data

def get_model_input(path, task = 'rest', subjects = [], phenotypes = []):
    """
    Prepare input data for model fitting

    Parameters
    ----------
    path (str): Path to derivatives directory or equivalent
    task (str): Functional task to use connectivity data of
    subjects (list): Subjects to get data for
    phenotypes (list): Phenotypic values to classify

    Returns
    ----------
    features (np.array): Array of subject connectivity matrices
    labels (np.array): Array of phenotypic labels
    """
    data = load_data(path, subjects)
    labels = data.phenotypic.T[1]
    
    if not(subjects):
        subjects = [sub.split('-')[1] for sub in data.order]
    features = np.asarray([np.load(os.path.join(path, 'connectomes', f'sub-{sub}_{task}_connectome.npy'), allow_pickle=True) for sub in subjects])
    
    if phenotypes:
        keep = [bool(lab in phenotypes) for lab in labels]
        features = features[keep]
        labels = labels[keep]

    return features, labels



if __name__ == '__main__':

    # parse arguments

    parser = argparse.ArgumentParser()
    parser.add_argument('path', type=str, help='Path to derivatives directory or equivalent')
    parser.add_argument('--file_suffix', type=str, help='Suffix of saved output files', default="")
    parser.add_argument('--subjects', help='Path to file or Python list of subjects to get data for', default=[])
    parser.add_argument('--task', type=str, help='Functional task to use connectivity data of', default='rest')
    parser.add_argument('--phenotypes', help='Path to file or Python list phenotypic values to classify', default=[])
    parser.add_argument('--verbosity', type=int, default=1)
    args = parser.parse_args()

    save_to = os.path.join('/'.join(os.path.abspath(args.path).split('/')[:-2]), 'results', 'ml_metrics')
    if not(glob.glob(save_to)):
        os.mkdir(save_to)

    if args.subjects:
        if type(args.subjects) is str:
            with open(args.subjects) as subs:
                subjects = [s.strip('\n') for s in subs.readlines()]
        else:
            subjects = args.subjects
    else:
        subjects = []

    if args.phenotypes:
        if type(args.phenotypes) is str:
            with open(args.phenotypes) as phen:
                phenotypes = [p.strip('\n') for p in phen.readlines()]
        else:
            phenotypes = args.phenotypes
    else:
        phenotypes = []

    if args.verbosity:
        print('Preparing subject data...')

    features, labels = get_model_input(args.path, args.task, subjects, phenotypes)
    label_set = np.unique(labels)
    lab_names = {'CONTROL' : 'Control', 'BIPOLAR' : 'Bipolar', 'ADHD' : 'ADHD', 'SCHZ' : 'Schizophrenia'}

    # split data

    if args.verbosity:
        print('Getting independent test data...')

    X, X_test, y, y_test = train_test_split(
                                                        features,
                                                        labels,
                                                        test_size = 0.3,
                                                        shuffle = True,
                                                        stratify = labels
    )

    if args.verbosity:
        train_count = [np.count_nonzero((y == lab)) for lab in label_set]
        test_count = [np.count_nonzero((y_test == lab)) for lab in label_set]
        print('Train : Test set composition...')
        print('\n'.join([f'{label_set[i]} = {train_count[i]}:{test_count[i]}' for i in range(len(label_set))]))

    if args.verbosity:
        print('Generating K fold splits...')

    idcs = np.asarray(range(len(X)))
    np.random.shuffle(idcs)
    X = X[idcs]
    y = y[idcs]
    skf = StratifiedKFold(n_splits=5)
    splits = skf.split(X, y)



    # model 1: sklearn SVC

    if args.verbosity:
        print('Initializing support vector classifier...')

    pipe = Pipeline(steps = [('scaler', StandardScaler()), ('svc', SVC())])

    param_grid = {
                'svc__kernel':['linear'],
                'svc__C': [i for i in 10. ** np.arange(-5,8, step = 0.5)],
                }

    if args.verbosity:
        print('Performing grid search...')

    search = GridSearchCV(estimator = pipe,
                        param_grid = param_grid,
                        cv = splits,
                        return_train_score = True,
                        verbose = args.verbosity)

    search.fit(X,y)

    if args.verbosity:
        print('Predicting test data using best estimator')

    y_pred = search.predict(X_test)

    if args.verbosity:
        print('Getting coefficients...')
    
    coefficients = search.best_estimator_.named_steps['svc'].coef_
    coef_order = search.best_estimator_.named_steps['svc'].classes_
    coefficients = np.asarray([coefficients, coef_order], dtype=object)
    np.save(os.path.join('/'.join(save_to.split('/')[:-1]), f'svc_{args.task}_weights{args.file_suffix}'), coefficients, allow_pickle=True)
    
    if args.verbosity:
        print('Getting metrics...')

    cm = confusion_matrix(y_test, y_pred, labels = label_set)
    cm = np.array(cm)
    cm = pd.DataFrame(cm, index = label_set, columns = label_set)

    scores = classification_report(y_test, y_pred, labels = label_set, target_names = [lab_names[lab] for lab in label_set], output_dict = True)
    scores['accuracy'] = accuracy_score(y_test, y_pred)

    history = pd.DataFrame(search.cv_results_)

    with open(os.path.join(save_to, f'svc_{args.task}_classification_report{args.file_suffix}.json'), 'w') as savefile:
        json.dump(scores, savefile)
    cm.to_csv(os.path.join(save_to, f'svc_{args.task}_confusion_matrix{args.file_suffix}.tsv'), sep='\t')
    history.to_csv(os.path.join(save_to, f'svc_{args.task}_search_history{args.file_suffix}.tsv'), sep='\t')
    
    
    if args.verbosity:
        print('Done.')
