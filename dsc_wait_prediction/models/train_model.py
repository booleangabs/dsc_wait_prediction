# -*- coding: utf-8 -*-
import click
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
import polars as pl
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.experimental import enable_iterative_imputer 
from sklearn.impute import IterativeImputer
from sklearn.metrics import classification_report, ConfusionMatrixDisplay
from catboost import CatBoostClassifier
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import pickle
sns.set_theme(style="white")

@click.command()
@click.argument('input_filepath', type=click.Path(exists=True))
@click.argument('output_filepath', type=click.Path())
def main(input_filepath, output_filepath):
    """ Runs model training
    """
    logger = logging.getLogger(__name__)
    logger.info('starting training procedure')
    
    logger.info('loading features')
    train_val_file = Path(input_filepath).joinpath("train_val_features.csv")
    assert train_val_file.is_file(), f'Dataset path "{train_val_file.absolute()}" is invalid.'
    train_val = pl.read_csv(train_val_file, null_values="NA").to_pandas()

    test_file = Path(input_filepath).joinpath("test_features.csv")
    assert test_file.is_file(), f'Dataset path "{test_file.absolute()}" is invalid.'
    test = pl.read_csv(test_file, null_values="NA").to_pandas()

    logger.info('train-val stratified split (80-20 split)')
    X = train_val.drop("espera", axis=1)
    y = train_val["espera"]
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=13, stratify=y)

    logger.info('filling null values with sklearn.impute.IterativeImputer')
    cols = list(X_train.columns)[3:]
    imp_train = IterativeImputer(max_iter=15, random_state=42)
    imp_val = IterativeImputer(max_iter=15, random_state=42)
    imp_test = IterativeImputer(max_iter=15, random_state=42, keep_empty_features=True)
    X_train[cols] = imp_train.fit_transform(X_train[cols])
    X_val[cols] = imp_val.fit_transform(X_val[cols])
    test[cols] = imp_test.fit_transform(test[cols])

    class_weight = 0.35 * ((y_train == 0).sum() / y_train.sum())
    logger.info(f'positive class weight for imbalanced model training set to {class_weight}')

    cat_features = ["origem", "destino", "rota"]
    logger.info(f'marking {cat_features} as "category" type')
    for c in cat_features:
        train_val[c] = train_val[c].astype("category")
        test[c] = test[c].astype("category")

    logger.info('initializing model')
    model = CatBoostClassifier(iterations=1000, depth=6, learning_rate=0.1,
                           verbose=False, cat_features=cat_features, 
                           random_state=1234, scale_pos_weight=class_weight)

    logger.info(model.get_params())

    logger.info('executing training')
    model.fit(X_train, y_train)

    logger.info('evaluating on validation data')
    y_pred_val = model.predict(X_val)

    logger.info('evaluation results:')
    print(classification_report(y_val, y_pred_val))
    ConfusionMatrixDisplay.from_predictions(y_val, y_pred_val, normalize="true", values_format=".3f")
    plt.show()
    importances = model.feature_importances_
    cols = np.array(list(X.columns))
    idx = np.argsort(importances)[::-1]
    plt.title("Feature importances")
    sns.barplot(x=importances[idx], y=cols[idx])
    plt.show()

    y_pred = model.predict(test.drop("espera", axis=1))
    submission_file_base = Path(input_filepath).parent / "interm" / "test.csv"
    assert submission_file_base.is_file(), "Cannot find submission file base (original test data with flight ids). " \
         + f"Should be in {submission_file_base}!"
    submission = pl.read_csv(submission_file_base, null_values="NA")[["flightid"]]
    submission = submission.with_columns(pl.Series(name="espera", values=y_pred))

    output_filepath = Path(output_filepath)
    output_filepath.mkdir(parents=True, exist_ok=True)
    submission.write_csv(output_filepath / "submission.csv")
    pickle.dump(model, open(output_filepath / "catboost.pkl", "wb"))


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(module)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
