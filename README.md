dsc_wait_prediction
==============================

Submission to Data Science Challenge @ EEF promoted by ITA - Brazil.
The objective is predicting the need for maneuvering aircrafts around the destination, waiting for ATC clearance.
The data provided contains weather, airport and satellite information. I've combined this with manually acquired external data.
The jupyter notebooks contain my exploration process and are not very nicely organized and can be seem as a more raw version of my actual code. I've seeded my code and saved all my environment information to try and make this code as reproducible as I could. This code was tested on a Windows machine using conda for package and environment management. I plan on iterating this source to improve the project (specially the documentation). 


To run training:
- Create an environment using environment.yml and activate it
- Use pip to install requirements.txt
- Run `make train`


TODO:
- Inference code with online data acquistion, transformation and processing

Project Organization
------------

    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make data` or `make train`
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interm         <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── docs               <- A default Sphinx project; see sphinx-doc.org for details
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jgpt-data-exploration`.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment
    ├── environmet.ynl     <- The conda environment configuration file
    │
    ├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
    ├── dsc_wait_predic... <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data
    │   │   └── make_dataset.py
    │   │
    │   ├── features       <- Scripts to turn intermediate data into features for modeling
    │   │   └── build_features.py
    │   │
    │   ├── models         <- Scripts to train models and then use trained models to make
    │   │   │                 predictions
    │   │   ├── predict_model.py
    │   │   └── train_model.py
    │   │
    │   └── visualization  <- Scripts to create exploratory and results oriented visualizations
    │       └── visualize.py
    │
    └── tox.ini            <- tox file with settings for running tox; see tox.readthedocs.io


--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
