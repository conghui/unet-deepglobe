#!/bin/bash

MODEL="AOI_5_Khartoum"
PREFIX="RGB-PanSharpen_AOI_5_Khartoum_img"
SUFFIX="tif"
INDIR="RGB-PanSharpen"
OUTDIR="${INDIR}-remap"
REMAP_FN=${OUTDIR}.json

if ! [[ -d ${INDIR} ]]; then
  echo "$INDIR not exist"
  exit 1
fi

mkdir -p $OUTDIR
rm -f ${REMAP_FN}

echo -n '{' > ${REMAP_FN}

COUNT=1
for f in ${INDIR}/*.${SUFFIX}; do
  newfn=${OUTDIR}/${PREFIX}${COUNT}.${SUFFIX}
  orgfn=$(readlink -f $f) # original file name

  key=$(echo $f | sed 's/.*_AOI_/AOI_/' | sed "s/\.${SUFFIX}//")
  value=${MODEL}_img${COUNT}

  if ! [[ $COUNT -eq 1 ]]; then
    echo -n "," >> $REMAP_FN
  fi

  echo -n "\"$key\":\"$value\"" >> $REMAP_FN

  echo "ln -fs ${newfn} ${orgfn}"
  ln -fs  ${orgfn} ${newfn}

  COUNT=$((COUNT + 1))

  # if [[ $COUNT -eq 5 ]]; then
  #   break
  # fi
done

echo '}' >> ${REMAP_FN}
