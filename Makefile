.PHONY: clean data lint 

#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROFILE = default
PROJECT_NAME = dsc_wait_prediction
PYTHON_INTERPRETER = python

#################################################################################
# COMMANDS                                                                      #
#################################################################################

## Make Dataset
data: 
	$(PYTHON_INTERPRETER) $(PROJECT_NAME)/data/make_dataset.py data/raw data/interm

## Make Features
features: data
	$(PYTHON_INTERPRETER) $(PROJECT_NAME)/features/build_features.py data/interm data/processed

train: features
	$(PYTHON_INTERPRETER) $(PROJECT_NAME)/models/train_model.py data/processed models

## Delete all compiled Python files
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

## Lint using flake8
lint:
	flake8 src
