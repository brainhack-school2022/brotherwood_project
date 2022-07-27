# Classifying Neuropsychiatric Disorder Diagnoses Using Resting State BOLD fMRI Connectovoty Data

## About Me

<a href="https://github.com/PeteBro">
   <img src="https://avatars.githubusercontent.com/u/64285401?v=4?s=100" width="100px;" alt=""/>
   <br /><sub><b>Peter Brotherwood</b></sub>
</a>

I am a first year PhD student at the University of Montreal studying in computational neuroscience. I come from a fairly different background, with a BSc in Genetics and an MSci in Bioinformatics from the University of Birmingham. Much of my current work is in perception, using machine learning based approaches to model representational spaces in individual subjects. My hope is that BHS will introduce me to tools and best prectices I need to learn in order to fully integrate into the field of computational cognitive neuroscience.

## Project Summary

### Introduction
Brain regions with correlated temporal activity are seen to form functional networks of varying scale and distribution. Regions correlated at rest form resting state networks. Aberrant functional connectivity of resting state networks has been observed in multiple populations sufering from neuropsychiatric disorders; including ADHD (Sudre *et al*., 2017), Bipolar Disorder (Syan *et al*., 2018), and Schizophrenia (Sheffield & Barch, 2016). Given these observed differences in resting state network connectivity, this project aims to apply machine learning methods to investigate if aberrations in resting state functional connectvitiy can be used to identify neurophychiatric diagnoses.

### Main Objectives
- Provide a full neuroimaging workflow from preprocessing of raw data to visualisation of results.
- Emphasize reproducibility, making all elements of the project as reproducible as possible.
- Investigate ability of machine learning algorithms in predicting phenotype based on connectivity data.

### Personal Objectives
- Learn more about open data and project reproducibility.
- Gain an understanding of fMRI and neuroimaging database structures and best practices.
- Develop skills in proprocessing and analysis of fMRI data.
- Apply knowledge of machine learning to neuroscientfic studies.

### Tools
- Compute Canada for Job Submission
- Git and Github for Version Control
- DataLad for Reproducibility
- Singularity for Reproducibility
- fMRIPrep for data preprocessing
- Python Packages: `matplotlib`, `seaborn`, `scikit-learn`, `nilearn`

### Data
The dataset used in this study comes from the UCLA Consortium for Neuropsychiatric Phenomics LA5c Study (Poldrack *et al*., 2016). The dataset is comprised of fMRI data for 130 healthy individuals, and 142 individuals with neuropsychiatric disorders. Of these 148 individuals, 50 suffer from schizophrenia, 49 from bipolar disorder, and 43 from ADHD. The dataset contains fMRI data collected at rest and over a series of attentional tasks. The fMRI data is in nifti format and the dataset is provided in BIDS format. More information on this dataset can be found at https://openneuro.org/datasets/ds000030/versions/1.0.0.

A summary of the dataset is as follows:

### Project Deliverables
- Reproducible project workflow, detailed in git repo and via datalad logs, reproducible via containers.
- Executable Python scripts for data preparation and machine learning
- Markdown file introducing the project and detailing project results

## Guide to Reproducibility
All scripts used in the analyses are located in the `scripts` directory and are executable in the Linux command line. Each script is written such that it can be executed using fMRI data from alternative functional tasks from the same dataset, or with similar datasets conforming to BIDS formatting standards. The `requirements.txt` file provides all neccesary dependencies for execution of scripts following preprocessing using fMRIprep. To run `preprocessing.sh` it is highly recommended to use a HPC cluster, more instructions on preprocessing requirements and how to properly format `preprocessing.sh` can be found at https://www.nipreps.org/apps/singularity/.

A basic example of running the contents of the `scripts` directory is as follows:
```
```

##References
Poldrack, R., Congdon, E., Triplett, W., Gorgolewski, K., Karlsgodt, K., Mumford, J., Sabb, F., Freimer, N., London, E., Cannon, T. and Bilder, R., 2016. A phenome-wide examination of neural and cognitive function. *Scientific Data*, 3(1).

Sheffield, J. and Barch, D., 2016. Cognition and resting-state functional connectivity in schizophrenia. *Neuroscience; Biobehavioral Reviews*, 61, pp.108-120.

Sudre, G., Szekely, E., Sharp, W., Kasparek, S. and Shaw, P., 2017. Multimodal mapping of the brain’s functional connectivity and the adult outcome of attention deficit hyperactivity disorder. *Proceedings of the National Academy of Sciences*, 114(44), pp.11787-11792.

Syan, S., Smith, M., Frey, B., Remtulla, R., Kapczinski, F., Hall, G. and Minuzzi, L., 2018. Resting-state functional connectivity in individuals with bipolar disorder during clinical remission: a systematic review. *Journal of Psychiatry and Neuroscience*, 43(5), pp.298-316.
