# -*- coding: utf-8 -*-
import click
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
import polars as pl


@click.command()
@click.argument('input_filepath', type=click.Path(exists=True))
@click.argument('output_filepath', type=click.Path())
def main(input_filepath, output_filepath):
    """ Runs feature engineering and preprocessing scripts to turn 
        intermediate data from ($(PROJECT_ROOT)/data/interm) into 
        features for modelling (saved in $(PROJECT_ROOT)/data/features).
    """
    logger = logging.getLogger(__name__)
    logger.info('making final dataset from intermediate data')

    logger.info('loading splits')
    train_val_file = Path(input_filepath).joinpath("train_val.csv")
    assert train_val_file.is_file(), f'Dataset path "{train_val_file.absolute()}" is invalid.'
    train_val = pl.read_csv(train_val_file, null_values="NA")

    test_path = Path(input_filepath).joinpath("test.csv")
    assert test_path.is_file(), f'Dataset path "{test_path.absolute()}" is invalid.'
    test = pl.read_csv(test_path, null_values="NA")

    logger.info('casting "hora_ref" to datetime')
    train_val = train_val.with_columns(
        pl.col("hora_ref").cast(pl.Datetime)
    )
    test = test.with_columns(
        pl.col("hora_ref").cast(pl.Datetime)
    )

    logger.info('loading metar data')
    train_val_metar_file = Path(input_filepath).joinpath("metar_data.csv")
    assert train_val_metar_file.is_file(), f'Dataset path "{train_val_metar_file.absolute()}" is invalid.'
    train_val_metar = pl.read_csv(train_val_metar_file, null_values="NA")

    test_metar_file = Path(input_filepath).joinpath("test_metar_data.csv")
    assert test_metar_file.is_file(), f'Dataset path "{test_metar_file.absolute()}" is invalid.'
    test_metar = pl.read_csv(test_metar_file, null_values="NA")

    logger.info('merging main data with metar data')
    train_val = pl.concat([train_val.drop("metar", "metaf"), train_val_metar], how="horizontal")
    test = pl.concat([test.drop("metar", "metaf"), test_metar], how="horizontal")

    logger.info('loading image color data')
    train_val_img_file = Path(input_filepath).joinpath("image_color_data.csv")
    assert train_val_img_file.is_file(), f'Dataset path "{train_val_img_file.absolute()}" is invalid.'
    train_val_img = pl.read_csv(train_val_img_file, null_values="NA")

    test_img_file = Path(input_filepath).joinpath("test_image_color_data.csv")
    assert test_img_file.is_file(), f'Dataset path "{test_img_file.absolute()}" is invalid.'
    test_img = pl.read_csv(test_img_file, null_values="NA")

    logger.info('merging main data with image color data')
    train_val = pl.concat([train_val.drop("url_img_satelite", "url_img_satelite"), train_val_img], how="horizontal")
    test = pl.concat([test.drop("url_img_satelite", "url_img_satelite"), test_img], how="horizontal")

    print(train_val.to_pandas().info())
    print(test.to_pandas().info())


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(module)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
