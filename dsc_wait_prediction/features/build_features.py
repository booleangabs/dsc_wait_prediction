# -*- coding: utf-8 -*-
import click
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
import polars as pl
import numpy as np


def sin_col(col, period):
    return np.sin(col / period * 2 * np.pi)

def cos_col(col, period):
    return np.cos(col / period * 2 * np.pi)


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
    train_val_out = Path(output_filepath).joinpath("train_val_features.csv")
    test_out = Path(output_filepath).joinpath("test_features.csv")
    if train_val_out.is_file() and test_out.is_file():
        logger.info('feature files already exist (skipping process)')
        return

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

    logger.info('loading airport data')
    airport_file = Path(input_filepath).joinpath("airports.csv")
    assert airport_file.is_file(), f'Dataset path "{airport_file.absolute()}" is invalid.'
    airport_data = pl.read_csv(airport_file, null_values="NA")

    logger.info('trigonometric encodings of "hora_ref" month, day and hour')
    avg_days_per_month = 30.437
    train_val = train_val.with_columns(
        sin_col(pl.col("hora_ref").dt.month(), 12).alias("month_sin"),
        sin_col(pl.col("hora_ref").dt.day(), avg_days_per_month).alias("day_sin"),
        sin_col(pl.col("hora_ref").dt.hour(), 24).alias("hour_sin"),
        cos_col(pl.col("hora_ref").dt.month(), 12).alias("month_cos"),
        cos_col(pl.col("hora_ref").dt.day(), avg_days_per_month).alias("day_cos"),
        cos_col(pl.col("hora_ref").dt.hour(), 24).alias("hour_cos"),
    )
    train_val = train_val.select([pl.all().exclude("hora_ref")])

    test = test.with_columns(
        sin_col(pl.col("hora_ref").dt.month(), 12).alias("month_sin"),
        sin_col(pl.col("hora_ref").dt.day(), avg_days_per_month).alias("day_sin"),
        sin_col(pl.col("hora_ref").dt.hour(), 24).alias("hour_sin"),
        cos_col(pl.col("hora_ref").dt.month(), 12).alias("month_cos"),
        cos_col(pl.col("hora_ref").dt.day(), avg_days_per_month).alias("day_cos"),
        cos_col(pl.col("hora_ref").dt.hour(), 24).alias("hour_cos"),
    )
    test = test.select([pl.all().exclude("hora_ref")])

    logger.info('trigonometric encodings of "wind_direction_rad"')
    train_val = train_val.with_columns(
        sin_col(pl.col("wind_direction_rad"), 2 * np.pi).alias("wind_direction_rad_sin"),
        sin_col(pl.col("wind_direction_rad"), 2 * np.pi).alias("wind_direction_rad_cos")
    )
    train_val = train_val.select([pl.all().exclude("wind_direction_rad")])

    test = test.with_columns(
        sin_col(pl.col("wind_direction_rad"), 2 * np.pi).alias("wind_direction_rad_sin"),
        sin_col(pl.col("wind_direction_rad"), 2 * np.pi).alias("wind_direction_rad_cos")
    )
    test = test.select([pl.all().exclude("wind_direction_rad")])

    logger.info('creation of "rota" (flight route) feature')
    train_val = train_val.with_columns(
        (pl.col("origem") + "_" + pl.col("destino")).alias("rota")
    ).to_pandas()

    test = test.with_columns(
        (pl.col("origem") + "_" + pl.col("destino")).alias("rota")
    ).to_pandas()

    logger.info('creation of "n_pistas" (number of runways) feature')
    train_val["n_pistas"] = train_val["destino"].map(
        lambda x: airport_data.filter(pl.col("ICAO") == x)["n_pistas"][0]
    )

    test["n_pistas"] = test["destino"].map(
        lambda x: airport_data.filter(pl.col("ICAO") == x)["n_pistas"][0]
    )

    logger.info('discarding/reordering features')
    ord = [
        'origem', 'destino', 'rota', 'prev_troca_cabeceira',
        'troca_cabeceira_hora_anterior', 'elevation', 'air_temperature',
        'dew_point_temp', 'visibility', 'wind_speed', 'cloud_coverage_oktas',
        'altimeter', 'pressure_station_level_atm', 'sat_yellow_green',
        'sat_purple_red', 'sat_blue', 'month_sin', 'day_sin', 'hour_sin',
        'month_cos', 'day_cos', 'hour_cos', 'wind_direction_rad_sin',
        'wind_direction_rad_cos', 'n_pistas',  'espera'
    ]
    train_val = train_val[ord]
    test = test[ord]

    logger.info('saving data')
    train_val.to_csv(
        train_val_out, 
        index=False, na_rep="NA"
    )
    test.to_csv(
        test_out,
        index=False, na_rep="NA"
    )


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(module)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
