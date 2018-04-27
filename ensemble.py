#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ensemble.py: ensemble multiple prediction results

The processes are:
- load each result file (stored as a numpy array file, each pixel represents 'confidence')
- average all results
- write to csv
"""

# from logging import getLogger, Formatter, StreamHandler, INFO, FileHandler
import subprocess
import importlib
import math
from pathlib import Path
import json
import re
import warnings
import os

import tqdm
import click
import tables as tb
import pandas as pd
import shapely.wkt
import shapely.ops
import shapely.geometry
import skimage.transform
import rasterio.features

import sys
import numpy as np

INPUT_NUMPY_LIST    = ['./khartoum-03-17.npy', './khartoum-10-17.npy']
TEST_IMAGE_LIST     = './AOI_5_Khartoum_test_ImageId.csv'
OUTPUT_CSV          = 'out.csv'
MIN_POLYGON_AREA_TH = 150

def _remove_interiors(line):
    if "), (" in line:
        line_prefix = line.split('), (')[0]
        line_terminate = line.split('))",')[-1]
        line = (
            line_prefix +
            '))",' +
            line_terminate
        )
    return line

def mask_to_poly(mask, min_polygon_area_th=MIN_POLYGON_AREA_TH):
    mask = (mask > 0.5).astype(np.uint8)
    shapes = rasterio.features.shapes(mask.astype(np.int16), mask > 0)
    poly_list = []
    mp = shapely.ops.cascaded_union(
        shapely.geometry.MultiPolygon([
            shapely.geometry.shape(shape)
            for shape, value in shapes
        ]))

    if isinstance(mp, shapely.geometry.Polygon):
        df = pd.DataFrame({
            'area_size': [mp.area],
            'poly': [mp],
        })
    else:
        df = pd.DataFrame({
            'area_size': [p.area for p in mp],
            'poly': [p for p in mp],
        })

    df = df[df.area_size > min_polygon_area_th].sort_values(
        by='area_size', ascending=False)
    df.loc[:, 'wkt'] = df.poly.apply(lambda x: shapely.wkt.dumps(
        x, rounding_precision=0))
    df.loc[:, 'bid'] = list(range(1, len(df) + 1))
    df.loc[:, 'area_ratio'] = df.area_size / df.area_size.max()
    return df

def ensemble():

  print('loading {}'.format(INPUT_NUMPY_LIST[0]))
  pred_value = np.load(INPUT_NUMPY_LIST[0])
  pred_count = 1

  print('pred_value.shape: ', pred_value.shape)
  print('pred_value.dtype: ', pred_value.dtype)
  # read and sum
  for fn in INPUT_NUMPY_LIST[1:]:
    print('loading {}'.format(fn))
    val = np.load(fn)
    print('{}.shape: '.format(fn), val.shape)
    print('{}.dtype: '.format(fn), val.dtype)
    assert pred_value.shape == val.shape
    assert pred_value.dtype == val.dtype

    pred_value = np.add(pred_value, val)
    pred_count += 1

  # average
  pred_value /= pred_count

  # Postprocessing phase
  print("\nPostprocessing phase")
  df_test = pd.read_csv(TEST_IMAGE_LIST, index_col='ImageId')

  with open(OUTPUT_CSV, 'w') as f:
    f.write("ImageId,BuildingId,PolygonWKT_Pix,Confidence\n")

    test_image_list = df_test.index.tolist()
    for idx, image_id in tqdm.tqdm(enumerate(test_image_list),
                                    total=len(test_image_list)):
        df_poly = mask_to_poly(pred_value[idx], min_polygon_area_th=MIN_POLYGON_AREA_TH)
        if len(df_poly) > 0:
            for i, row in df_poly.iterrows():
                line = "{},{},\"{}\",{:.6f}\n".format(
                    image_id,
                    row.bid,
                    row.wkt,
                    row.area_ratio)
                line = _remove_interiors(line)
                f.write(line)
        else:
            f.write("{},{},{},0\n".format(
                image_id,
                -1,
                "POLYGON EMPTY"))

  print('finished writing result to {}'.format(OUTPUT_CSV))

if __name__ == '__main__':
  ensemble()
