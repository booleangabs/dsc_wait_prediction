# -*- coding: utf-8 -*-
import click
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv

import polars as pl


def parse_airport_info(file_lines):
    airport_data = []
    for line in file_lines:
        curr_data = []

        # ICAO
        ICAO = line[:4]
        curr_data.append(ICAO)
        line = line[5:]
        
        # latitude
        k = 9
        lat = ""
        while line[k].isalnum() or (line[k] in ["-", ",", ""]):
            lat += line[k]
            k += 1
        curr_data.append(float(lat.replace(",", ".")))
        line = line[k + 3:]

        # longitude
        k = 10
        lon = ""
        while line[k].isalnum() or (line[k] in ["-", ",", ""]):
            lon += line[k]
            k += 1
        curr_data.append(float(lon.replace(",", ".")))
        line = line[k + 2:]
        
        # number of runways
        k = 0
        n_runways = 1
        while line[k] != ":":
            if line[k].isdigit():
                n_runways = 2
            k += 1
        curr_data.append(n_runways)
        line = line[k+2:]

        # runway designators
        if n_runways == 1:
            runway_desig = line[:5]
            curr_data.append(runway_desig)
            curr_data.append("NA")
        else:
            runway_desig1 = ""
            k = 0
            while line[k].isalnum() or line[k] == "/":
                runway_desig1 += line[k]
                k += 1
            curr_data.append(runway_desig1)

            runway_desig2 = ""
            k += 3
            while line[k].isalnum() or line[k] == "/":
                runway_desig2 += line[k]
                k += 1
            curr_data.append(runway_desig2)
        airport_data.append(curr_data)
    return airport_data


@click.command()
@click.argument('input_filepath', type=click.Path(exists=True))
@click.argument('output_filepath', type=click.Path())
def main(input_filepath, output_filepath):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../interim).
    """
    logger = logging.getLogger(__name__)
    logger.info('making final data set from raw data')

    logger.info('splitting train+validation and test sets')
    data_file = Path(input_filepath).joinpath("public.csv")
    assert data_file.is_file(), f'Dataset path "{data_file.absolute()}" is invalid.'

    train_path = Path(output_filepath).joinpath("train_val.csv")
    test_path = Path(output_filepath).joinpath("test.csv")
    if train_path.is_file() or test_path.is_file():
        logger.info('splits already exists (skipping process)')
    else:
        df = pl.read_csv(data_file, null_values="NA")
        train_ds = df.filter(pl.col("espera").is_not_null())
        test_ds = df.filter(pl.col("espera").is_null())
        train_ds.write_csv(train_path, null_value="NA")
        test_ds.write_csv(test_path, null_value="NA")

    logger.info('transforming airport information')
    ap_data_file = Path(input_filepath).joinpath("airports.txt")
    assert ap_data_file.is_file(), f'Dataset path "{ap_data_file.absolute()}" is invalid.'
    airports_ds = Path(output_filepath).joinpath("airports.csv")
    if airports_ds.is_file():
        logger.info('transformed aiport data table already exists (skipping process)')
    else:    
        ap_info = open(ap_data_file, "rt").readlines()
        ap_info = parse_airport_info(ap_info)
        columns = ["ICAO", "lat", "lon", "n_pistas", "desig_pista1", "desig_pista2"]
        df = pl.DataFrame(ap_info, schema=columns, orient="row")
        df.write_csv(airports_ds)


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(module)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
