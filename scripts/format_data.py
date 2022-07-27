#!/usr/bin/env python3

"functions for organization derivatives from fmriprep"

import argparse
import pathlib

import os
import glob
import numpy as np
import json
import pandas as pd
from sklearn.utils import Bunch

__all__ = [
'get_directories',
'get_format_file'
]

def get_directories(path = '.'):
    """
    Retrieve a list of paths to subject files containing individual data

    Parameters
    ----------
    path (str): path to top level data directory

    Returns
    ----------
    paths (list): list of paths to all subject folders
    """
    abspath = os.path.abspath(path)
    paths = [path for path in glob.glob(f'{abspath}/*sub-*')]
    order = [int(path.split('-')[-1]) for path in paths]
    index = np.argsort(order)
    paths = [paths[i] for i in index]
    
    return paths



def get_format_file(path, bold_suffix):
    """
    Create and save a JSON file containing relvant subject information

    Parameters
    ----------
    path (str): path to top level data directory
    bold_suffix (str): suffix of bold files following identifier
    confound_suffix (str): suffix of confound (tsv) files following identifier
    """

    dirs = get_directories(path)
    
    participants = pd.read_csv(os.path.join(path, 'participants.tsv'), sep='\t')
    participant_list = participants['participant_id'].tolist()
    available_subjects = [path.split('/')[-1] for path in dirs]
    keep = [bool(sub in available_subjects) for sub in participant_list]
    participants = participants.loc[keep]

    assert available_subjects == participants['participant_id'].tolist(), 'Inconsistent subject order in participants.tsv'

    phenotypes = [pheno.tolist() for index, pheno in participants[['participant_id','diagnosis','age','gender']].iterrows()]
    
    func_paths = []

    for dir in dirs:
        path_to_data = os.path.join(dir, 'func')
        func_paths.append(glob.glob(f'{path_to_data}/*{bold_suffix}*'))

    database = {
        'func' : func_paths,
        'phenotypic' : phenotypes,
        'subject_order' : available_subjects
    }

    with open(f'{path}/format_file.json', 'w') as savefile:
        json.dump(database, savefile)

    return

def load_data(path, subjects = []):
    """
    Load subject information into memory

    Parameters
    ----------
    path (str): path to directory
    subjects (list): list of subject identfiers to load

    Returns
    ----------
    data (dict): data for specified subjects
    """
    with open(os.path.join(path,'format_file.json'), 'r') as o:
        data = json.load(o)

    if subjects:
        idcs = [data['subject_order'].index(f'sub-{sub}') for sub in subjects]
    else:
        idcs = list(range(len(data['subject_order'])))

    data = Bunch(
        order = [data['subject_order'][sub] for sub in idcs],
        func = [data['func'][sub] for sub in idcs],
        phenotypic = np.asarray([data['phenotypic'][sub] for sub in idcs]),
        )
    
    return data

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('path_to_data', type=pathlib.Path, help='Path to derivatives directory or equivalent')
    parser.add_argument('bold_suffix', type=str, help='Suffix of preprocessed BOLD files')
    args = parser.parse_args()
    
    get_format_file(args.path_to_data, args.bold_suffix)