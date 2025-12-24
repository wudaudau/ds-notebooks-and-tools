# Environments

This project uses multiple Conda environments depending on analysis type:

- ds-core: general Python data analysis
- ds-r-core: general R data analysis, including R notebooks and Olink analyses (TODO: add later)
- df-genomics: genomics-focused analyses with specialized bioinformatics tools (TODO: add later)

Notebooks indicate the required environment via their Jupyter kernel.


## Installing Conda
If you don’t have Conda installed, download and install Miniconda from https://docs.conda.io/en/latest/miniconda.html.

## Creating Environments
To create the required Conda environments, run at workspace root:
```bash
conda env create -f envs/ds-core.yml
conda env create -f envs/ds-r-core.yml
```

## Activating Environments
To activate an environment, use:
```bash
conda activate ds-core
# or
conda activate ds-r-core
```

## Jupyter Kernels
Each environment includes a Jupyter kernel. To use the kernels in Jupyter notebooks, ensure you have `ipykernel` installed in each environment:
```bashconda activate ds-core
pip install ipykernel
conda activate ds-ml
pip install ipykernel
```
When you open a notebook, select the appropriate kernel from the Jupyter interface to match the environment specified in the notebook metadata.

## Updating Environments
To update an environment after modifying its YAML file, run:
```bash
conda env update -f environment-ds-core.yml --prune
conda env update -f environment-ds-ml.yml --prune
```

This will install any new dependencies and remove any that are no longer needed.

## Listing Environments
To see a list of all your Conda environments, use:
```bash
conda env list
```

## Removing Environments
To remove an environment, use:
```bash
conda env remove -n ds-core
# or
conda env remove -n ds-ml
```