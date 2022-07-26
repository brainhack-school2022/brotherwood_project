"script for generation of connectome correlation matrices"

import argparse

import os
import glob
import numpy as np
import pandas as pd
from scipy.spatial.distance import squareform
import nibabel as nib
from nilearn.maskers import NiftiLabelsMasker
from nilearn.connectome import ConnectivityMeasure
from format_data import load_data

__all__ = [
'check_confounds'
]

def check_confounds(confounds, img, verbose = True):
    """
    Check confounds tsv for and remove nan values

    Parameters
    ----------
    confounds (pd.DataFrame): Confounds file loaded into a DataFrame
    img (nibabel.niftil.NiftiImage): fMRI data to which confounds correspond

    Returns
    ----------
    confounds (pd.DataFrame): Confounds DataFrame with timepoints containing missing values removed
    new_img (nibabel.niftil.NiftiImage): fMRI data with corresponding timepoints removed
    """
    start_idx = 0
    while True:
        if not(True in [confounds[col][start_idx:].isnull().values.any() for col in confounds.columns]):
            break
        start_idx += 1

    if verbose and start_idx:
        print(f'NaN values found up to timepoint {start_idx}: dropping prior timepoints...')

    confounds = confounds.iloc[start_idx:]
    new_img = img.slicer[:,:,:,start_idx:]

    return confounds, new_img



if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('path_to_data', type=str, help='Path to derivatives directory or equivalent')
    parser.add_argument('path_to_atlas', type=str, help='Path to atlas file for masking')
    parser.add_argument('--subjects', help='Path to file or Python list of subjects to get connectivity data for')
    parser.add_argument('--task', type =str, help='Functional task to get connectivity data for', default='rest')
    parser.add_argument('--selected_confounds', help='Path to file or Python list of confounds to regress during masking')
    parser.add_argument('--connectivity_measure', type=str, help='Metric to use in quantifying connectivity measure', default='correlation')
    parser.add_argument('--verbosity', type=int, default=1)
    args = parser.parse_args()

    save_to = os.path.join(os.path.abspath(args.path_to_data), 'connectomes')
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

    if args.selected_confounds:
        if type(args.selected_confounds) is str:
            with open(args.selected_confounds) as confs:
                confounds = [c.strip('\n') for c in confs.readlines()]
        else:
            confounds = args.selected_confounds
    else:
        confounds = []

    if args.verbosity:
        print('Loading subject data...')

    data = load_data(args.path_to_data, subjects)

    if args.verbosity:
        print('Initializing mask...')

    masker = NiftiLabelsMasker(labels_img=args.path_to_atlas, standardize=True)

    if args.verbosity:
        print('Initialising connectivity measure...')

    correlation_measure = ConnectivityMeasure(kind=args.connectivity_measure)

    if args.verbosity:
        print(f'Data for {len(data.func)} subjects loaded, generating correlation matrices...')

    for sub in range(len(data.func)):

        subname = data.order[sub]

        if args.verbosity-1:
            print('\n')
            print(f'Subject {subname.split("-")[1]} ({sub+1}/{len(data.func)}):')

        func_path = data.func[sub][np.where(np.char.count(data.func[sub], f'task-{args.task}'))[0][0]]
        conf_path = data.confounds[sub][np.where(np.char.count(data.confounds[sub], f'task-{args.task}'))[0][0]]

        if args.verbosity-1:
            print('Loading nibabel image...')

        img = nib.load(func_path)

        if args.verbosity-1:
            print('Loading confounds...')

        conf = pd.read_csv(conf_path, sep = '\t')

        if confounds:
            conf = conf[confounds]
        
        conf, img = check_confounds(conf, img, verbose = args.verbosity-1)

        if args.verbosity-1:
            print('Fitting mask...')

        time_series = masker.fit_transform(img, confounds=conf)

        if args.verbosity-1:
            print('Getting correlation matrix...')

        correlation_matrix = correlation_measure.fit_transform([time_series])[0]
        np.fill_diagonal(correlation_matrix,0)
        utv = squareform(correlation_matrix)
        np.save(os.path.join(save_to, f'{subname}_{args.task}_connectome'), utv, allow_pickle=True)

        if args.verbosity-1:
            print('Done.')

    if args.verbosity:
        print('\n')
        print(f'{len(data.func)} correlation matrices saved to {save_to}.')