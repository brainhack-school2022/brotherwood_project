"script for generation of connectome correlation matrices"

import argparse

import os
import glob
import numpy as np
import nibabel as nib
from nilearn.maskers import NiftiLabelsMasker
from nilearn.connectome import ConnectivityMeasure
from nilearn.interfaces.fmriprep import load_confounds
from format_data import load_data

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('path_to_data', type=str, help='Path to derivatives directory or equivalent')
    parser.add_argument('path_to_atlas', type=str, help='Path to atlas file for masking')
    parser.add_argument('--subjects', help='Path to file or Python list of subjects to get connectivity data for')
    parser.add_argument('--task', type =str, help='Functional task to get connectivity data for', default='rest')
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

    if args.verbosity:
        print('Loading subject data...')

    data = load_data(args.path_to_data, subjects)

    if args.verbosity:
        print('Initializing mask...')

    masker = NiftiLabelsMasker(labels_img=args.path_to_atlas, standardize=True)

    if args.verbosity:
        print('Initialising connectivity measure...')

    correlation_measure = ConnectivityMeasure(kind=args.connectivity_measure, vectorize=True)

    if args.verbosity:
        print(f'Data for {len(data.func)} subjects loaded, generating correlation matrices...')

    for sub in range(len(data.func)):

        subname = data.order[sub]

        if args.verbosity-1:
            print('\n')
            print(f'Subject {subname.split("-")[1]} ({sub+1}/{len(data.func)}):')

        func_path = data.func[sub][np.where(np.char.count(data.func[sub], f'task-{args.task}'))[0][0]]

        if args.verbosity-1:
            print('Loading nibabel image...')

        img = nib.load(func_path)

        if args.verbosity-1:
            print('Loading confounds...')

        conf = load_confounds(func_path)[0]

        if args.verbosity-1:
            print('Fitting mask...')

        time_series = masker.fit_transform(img, confounds=conf)

        if args.verbosity-1:
            print('Getting correlation matrix...')

        correlation_matrix = correlation_measure.fit_transform([time_series])[0]
        np.save(os.path.join(save_to, f'{subname}_{args.task}_connectome'), correlation_matrix, allow_pickle=True)

        if args.verbosity-1:
            print('Done.')

    if args.verbosity:
        print('\n')
        print(f'{len(data.func)} correlation matrices saved to {save_to}.')