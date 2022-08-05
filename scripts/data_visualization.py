"script for producing all plots shown in README.md file"


import os
import json
import numpy as np
import pandas as pd
from scipy.spatial.distance import squareform
from itertools import combinations as cb
from nilearn import datasets, plotting
from nilearn.maskers import NiftiLabelsMasker
from nilearn.connectome import ConnectivityMeasure
from nilearn.interfaces.fmriprep import load_confounds_strategy
import matplotlib.pyplot as plt
import seaborn as sns
from format_data import load_data

if __name__ == '__main__':

    lab_names = {'CONTROL' : 'Control', 'BIPOLAR' : 'Bipolar', 'ADHD' : 'ADHD', 'SCHZ' : 'Schizophrenia'}

    data = load_data('data/derivatives')

    # get dataset summary statistics

    phen = pd.DataFrame(data.phenotypic, columns=['Subject', 'Diagnosis', 'Age', 'Sex']).set_index('Subject')
    summary = pd.DataFrame({
                'Participants' : [*phen['Diagnosis'].value_counts().tolist(), phen['Diagnosis'].count()],
                'Male' : [*phen[phen['Sex'] == 'M']['Diagnosis'].value_counts().tolist(), phen['Sex'].value_counts()['M']],
                'Female' : [*phen[phen['Sex'] == 'F']['Diagnosis'].value_counts().tolist(), phen['Sex'].value_counts()['F']],
                'Age Avg' : [*[round(np.mean([int(a) for a in phen[phen['Diagnosis'] == dis]['Age']]), 2) for dis in np.unique(phen['Diagnosis'])], round(np.mean([int(a) for a  in phen['Age']]), 2)],
                'Age Std' : [*[round(np.std([int(a) for a in phen[phen['Diagnosis'] == dis]['Age']]), 2) for dis in np.unique(phen['Diagnosis'])], round(np.std([int(a) for a  in phen['Age']]), 2)]
                }, index =[ 'Control', 'Schizophrenia', 'Bipolar', 'ADHD', 'Total'] )

    summary.to_csv('results/plots/summary_statistics.tsv', sep = '\t')

    # plot phenotype distributions

    phen['Age'] = [int(a) for a in phen['Age']]
    plot = sns.violinplot(x='Diagnosis', y='Age', hue='Sex', data=phen)
    plot.set_xticklabels(['Control', 'Schizophrenia', 'Bipolar', 'ADHD'])
    plot.get_figure().savefig('results/plots/data_distribution.svg', format='svg')
    plt.clf()

    # plot atlas used in masking

    atlas = datasets.fetch_atlas_basc_multiscale_2015()
    plotting.plot_roi(atlas['scale064'], draw_cross=False)
    plt.savefig('results/plots/atlas_rois.svg', format='svg')
    plt.clf()

    view = plotting.view_img(atlas['scale064'])
    view.save_as_html('results/plots/atlas_rois.html')
    plt.clf()


    # plot some fMRI timeseries

    img = data.func[0][0]
    conf, sample_mask = load_confounds_strategy(img, denoise_strategy = 'simple', motion = 'basic', global_signal = 'basic')
    masker = NiftiLabelsMasker(labels_img=atlas['scale064'], standardize=True)
    masked_data = masker.fit_transform(img, confounds=conf, sample_mask=sample_mask)
    plt.plot(masked_data[0])
    plt.savefig('results/plots/single_timeseries.svg', format='svg')
    plt.clf()
    plt.plot(masked_data)
    plt.savefig('results/plots/all_timeseries.svg', format='svg')
    plt.clf()

    # plot connectivity matrix

    matrix = np.load(os.path.join('data/derivatives/connectomes', os.listdir('data/derivatives/connectomes')[0]))
    plotting.plot_matrix(squareform(matrix), vmin = -1, vmax = 1, labels=masker.labels_)
    plt.savefig('results/plots/connectivity_matrix.svg', format='svg')
    plt.clf()

    # plot feature matrix

    matrices = np.asarray([np.load(os.path.join('data/derivatives/connectomes', mat)) for mat in os.listdir('data/derivatives/connectomes')])
    plt.imshow(matrices, aspect='auto')
    plt.colorbar()
    plt.title('feature matrix')
    plt.xlabel('features')
    plt.ylabel('subjects')
    plt.savefig('results/plots/feature_matrix.svg', format='svg')
    plt.clf()

    # plot model confusion matrix and metrics
    # for both stratified control sample and full control sample

    for suffix in ['', '_stratified']:

        cmat = pd.read_csv(f'results/ml_metrics/svc_rest_confusion_matrix{suffix}.tsv', sep='\t', index_col=0)
        history = pd.read_csv(f'results/ml_metrics/svc_rest_search_history{suffix}.tsv', sep='\t')
        with open(f'results/ml_metrics/svc_rest_classification_report{suffix}.json', 'r') as o:
            report = json.load(o)

        # search history

        train_score = history[history['param_svc__kernel'] == 'linear']['mean_train_score'].tolist()
        val_score = history[history['param_svc__kernel'] == 'linear']['mean_test_score'].tolist()
        C_val = val_std = history[history['param_svc__kernel'] == 'linear']['param_svc__C'].tolist()

        plt.figure(figsize=(12,8))
        plt.plot(np.log10(C_val), train_score, label = 'Average Training Score')
        plt.plot(np.log10(C_val), val_score, label = 'Average Validation Score')
        plt.ylabel('Accuracy')
        plt.xlabel('C Value (log10)')
        plt.legend()
        plt.title('Cross-Validation Accuracy as a Function of Regularizer C')
        plt.savefig(f'results/plots/grid_search_history{suffix}.svg', format='svg')
        plt.clf()

        # confusion matrix

        plt.matshow(cmat)
        plt.tick_params(bottom=False)
        plt.xticks([0,1,2,3],labels=['ADHD', 'Bipolar', 'Control', 'Schizophrenia'])
        plt.yticks([0,1,2,3],labels=['ADHD', 'Bipolar', 'Control', 'Schizophrenia'], va='center', rotation=90)
        for (x, y), value in np.ndenumerate(cmat.T):
            plt.text(x, y, f"{value:.0f}", va="center", ha="center")
        plt.savefig(f'results/plots/svc_cmatrix{suffix}.svg', format='svg')
        plt.clf()

        # metrics

        metric_table = pd.DataFrame({k : m for k, m in report.items() if not(k=='accuracy')})
        metric_table.to_csv(f'results/plots/svc_metrics{suffix}.tsv', sep = '\t')

    # plot svc weights

    weights = np.load('results/svc_rest_weights.npy', allow_pickle=True)

    correlation_measure = ConnectivityMeasure(kind = 'correlation', vectorize=True, discard_diagonal=True)
    correlation_matrix = correlation_measure.fit_transform([masked_data])[0]
    feat_exp_mat = correlation_measure.inverse_transform(weights[0])
    inv_mask = masker.inverse_transform(weights[0])

    idx = 0
    for dis1, dis2 in cb([lab_names[lab] for lab in weights[1]], 2):

        feat_vector = feat_exp_mat[idx]
        inv_mask_vector = inv_mask.slicer[:,:,:,idx]

        plotting.plot_matrix(feat_vector, labels=masker.labels_, tri='lower')
        plt.savefig(f'results/plots/{dis1}_vs{dis2}_feature_matrix.svg', format='svg')
        plt.clf()

        coords = plotting.find_parcellation_cut_coords(atlas['scale064'])
        plotting.plot_connectome(feat_vector, coords, edge_threshold= '98%')
        plt.savefig(f'results/plots/{dis1}_vs_{dis2}_feature_connectome.svg', format='svg')
        plt.clf()

        view = plotting.view_connectome(feat_vector, coords, edge_threshold = '98%')
        view.save_as_html(f'results/plots/{dis1}_vs_{dis2}_feature_connectome_interactive.html')
        plt.clf()

        view = plotting.view_img(inv_mask_vector, threshold = '90%')
        view.save_as_html(f'results/plots/{dis1}_vs_{dis2}_image_interactive.html')
        plt.clf()

        view = plotting.view_img_on_surf(inv_mask_vector, threshold = '90%')
        view.save_as_html(f'results/plots/{dis1}_vs_{dis2}_3D_interactive.html')
        plt.clf()

        idx+=1