#!/usr/bin/env python

import json

DICT_FN = 'MUL-PanSharpen-ORG-remap.json'
CSV_FN = 'AOI_5_Khartoum_Train_Building_Solutions.csv'
OUT_FN = 'remapsummary.csv'

dd = json.load(open(DICT_FN))
# print(dd)

out_fn = open(OUT_FN, mode='w')

# read csv file
with open(CSV_FN) as f:
  out_fn.write(f.readline())

  for line in f:
    if 'AOI' in line:
      imageId = line.split(',')[0]
      line = line.replace(imageId, dd[imageId])

    out_fn.write(line)

out_fn.close()
