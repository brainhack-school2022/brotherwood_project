"functions for organization of data folder"

import sys
import os
import glob
import json
import numpy as np
import pandas as pd

__all__ = [
'get_directories',
'get_database'
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
    paths = [os.path.join(abspath, sub) for sub in glob.glob(f'{abspath}/sub-*')]
    
    return paths.sort()



def get_database(path, task, save):
    """
    Create and save a JSON file containing relvant subject information

    Parameters
    ----------
    path (str): path to top level data directory
    task (str): task for which data is to be retrieved
    save (str): path to save the data to
    """
    with open(os.path.join(path, 'dataset_description.json')) as o:
        descriptor = json.load(o)
    descriptor = [descriptor['Description']]

    dirs = get_directories(path)
    
    participants = pd.read_csv(os.path.join(path, 'participants.tsv'))
    subjects = [path.split('/')[-1] for path in dirs]

    assert subjects == participants['participant_id'], 'Inconsistent subject order in participants.tsv'

    dtypes = participants['participant_id':'gender'].dytpes()
    phenotypes = [[pheno, dtypes] for index, pheno in participants['participant_id':'gender'].iterrows()]
    
    func_paths = []
    confound_paths = []

    for dir in dirs:
        path_to_data = os.path.join(dir, 'func')
        func_paths.append(glob.glob(os.path.join(f'{path_to_data}/*_desc-preproc_{task}.nii.gz')))
        confound_paths.append(glob.glob(os.path.join(f'{path_to_data}/*_task-{task}_desc-confounds.tsv')))

    database = {
        'func' : func_paths,
        'confounds' : confound_paths,
        'phenotype' : phenotypes,
        'description' : descriptor
    }

    with open(save, 'w') as savefile:
        json.dump(database, savefile)

    return



def load_data(path, subjects = []):
    """
    Load subject information into memory

    Parameters
    ----------
    path (str): path to JSON file describing data
    subjects (list): list of subject idnices to load

    Returns
    ----------
    data (dict): data for specified subjects
    """
    with open(path, 'r') as o:
        data = json.load(o)

    if subjects:
        data = {
            'func' : [data['func'][sub] for sub in subjects],
            'confounds' :[data['confounds'][sub] for sub in subjects],
            'phenotype' : [data['phenotype'][sub] for sub in subjects],
            'description' : data['description']
        }

    return data

if __name__ == '__main__':

    get_database(*sys.argv)