# Brainhack 2022 Project of Peter Brotherwood

## About Me

<a href="https://github.com/PeteBro">
   <img src="https://avatars.githubusercontent.com/u/64285401?v=4?s=100" width="100px;" alt=""/>
   <br /><sub><b>Peter Brotherwood</b></sub>
</a>

I am a first year PhD student at the University of Montreal studying in computational neuroscience. I come from a fairly different background, with a BSc in Genetics and an MSci in Bioinformatics from the University of Birmingham. Much of my current work is in perception, using machine learning based approaches to model representational spaces in individual subjects. My hope is that BHS will introduce me to tools and best prectices I need to learn in order to fully integrate into the field of computational cognitive neuroscience.

## Project Summary



### Main Objectives
- Provide a full neuroimaging workflow from preprocessing of raw data to visualisation of results.
- Emphasize reproducibility, making all elements of the project as reproducible as possible.
- Investigate ability of machine learning algorithms in predicting phenotypic information of psychiatric disorders based on fMRI data recorded at rest and over a series of attentional tasks.

### Personal Objectives
- Learn more about open data and project reproducibility.
- Gain an understanding of fMRI and neuroimaging database structures and best practices.
- Develop skills in proprocessing and analysis of fMRI data.
- Apply knowledge of machine learning to neuroscientfic studies.

### Tools
- Compute Canada for Job Submission
- Git and Github for Version Control
- DataLad for Reproducibility
- Docker for Reproducibility
- fMRIPrep for data preprocessing
- Python Packages: `matplotlib`, `seaborn`, `scikit-learn`, `nilearn`

### Data
The dataset used in this study comes from the UCLA Consortium for Neuropsychiatric Phenomics LA5c Study (Poldrack *et al*., 2016). The dataset is comprised of fMRI data for 130 healthy individuals, and 142 individuals with neuropsychiatric disorders. Of these 148 individuals, 50 suffer from schizophrenia, 49 from bipolar disorder, and 43 from ADHD. The dataset contains fMRI data collected at rest and over a series of attentional tasks. The fMRI data is in nifti format and the dataset is provided in BIDS format. More information on this dataset can be found at https://openneuro.org/datasets/ds000030/versions/1.0.0.

### Project Deliverables
- Reproducible project workflow, detailed in git repo and via datalad logs, reproducible via containers.
- Istallable python module containing all build in functions for reproducibility with alternative datasets
- Executable Python scripts for data preparation and machine learning
- Markdown file introducing the project and detailing project results
