# -*- coding: utf-8 -*-
import click
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
import requests

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


def download_csv(url, file_path):
    response = requests.get(url)
    with open(file_path, 'wb') as f:
        f.write(response.content)


@click.command()
@click.argument('input_filepath', type=click.Path(exists=True))
@click.argument('output_filepath', type=click.Path())
def main(input_filepath, output_filepath):
    """ Runs data processing scripts to turn raw data from ($(PROJECT_ROOT)/data/raw) into
        cleaned data ready to be analyzed (saved in $(PROJECT_ROOT)/data/interm).
    """
    logger = logging.getLogger(__name__)
    logger.info('making intermediate datasets from raw data')

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

    logger.info('Downloading parsed metar data')
    train_val_url = "https://www.dropbox.com/scl/fi/ga74carg8xb0b2nx4s0tu/metar_data.csv?rlkey=9ifv5gw7rrx8cm6z5up7umsql&st=p5rryx7j&dl=1"
    train_val_metar_file = Path(output_filepath).joinpath("metar_data.csv")
    download_csv(train_val_url, train_val_metar_file)

    test_url = "https://www.dropbox.com/scl/fi/9e4p0jm4j5kohh5monkp4/test_metar_data.csv?rlkey=hqn3vp32m8n4dwbxs6y0zmked&st=sycsewtr&dl=1"
    test_metar_file = Path(output_filepath).joinpath("test_metar_data.csv")
    download_csv(test_url, test_metar_file)

    logger.info('Downloading processed image data')
    train_val_url = "https://www.dropbox.com/scl/fi/0jixzvlpuvbb20tvnhpb4/image_color_data.csv?rlkey=4plryz14zqf4cb3k7unqocj9p&st=sigq0g6c&dl=1"
    train_val_img_file = Path(output_filepath).joinpath("image_color_data.csv")
    download_csv(train_val_url, train_val_img_file)

    test_url = "https://www.dropbox.com/scl/fi/bt1a4uqhl5rgfgmd0ym8w/test_image_color_data.csv?rlkey=hoqu5rxdda3s6j97t7dzm6msf&st=zhok3ozu&dl=1"
    test_img_file = Path(output_filepath).joinpath("test_image_color_data.csv")
    download_csv(test_url, test_img_file)


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(module)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
