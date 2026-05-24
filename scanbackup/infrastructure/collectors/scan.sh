#!/bin/bash
# ---------------------------- INFO ----------------------------
# Script que captura los datos de consumo de tráfico del día anterior,
# obteniendo el consumo en intervalos de 5min.
#
# Esta información es obtenida de los logs del sistema de monitoreo SCAN.
#
# Para más información del sistema, léase `README.md`.
# --------------------------------------------------------------

TARGET_DATE="$1"
FILE_LAYER_SRC="$2"
SEPARATOR_DATA="$3"
USERNAME_SCAN="$4"
PASSWORD_SCAN="$5"
HEADER_DATA="$6"
DIR_SOURCES_PATH="$7"
DIR_STORAGE_PATH="$8"
DIR_TMP_PATH="$9"
FILE_LOG_PATH="${10}"
REPLACE_SYMBOL_PORTS="${11}"
REPLACE_SYMBOL_SPACE="${12}"
FORMAT_DATE="${13}"

full_format_date=$(awk \
  -v d="$FORMAT_DATE" \
  -v s="$SEPARATOR_DATA" \
  'BEGIN { print d s "%H:%M:%S" }')

while read -r line; do
  url=$(echo "${line}" | awk -F "${SEPARATOR_DATA}" '{print $1}' | xargs)
  interface_name=$(echo "${line}" | awk -F "${SEPARATOR_DATA}" '{print $2}')
  capacity=$(echo "${line}" | awk -F "${SEPARATOR_DATA}" '{print $3}')
  model=$(echo "${line}" | awk -F "${SEPARATOR_DATA}" '{print $4}')

  parser_interface_name=$(echo "${interface_name}" | xargs |
    tr '/' "${REPLACE_SYMBOL_PORTS}" |
    tr ' ' "${REPLACE_SYMBOL_SPACE}")

  file_data_tmp_path="${DIR_TMP_PATH}/${parser_interface_name}"
  file_data_final_path="${DIR_STORAGE_PATH}/${parser_interface_name}%${capacity}%${model}"

  wget -v --timeout=180 --tries=2 \
    --user="${USERNAME_SCAN}" \
    --password="${PASSWORD_SCAN}" \
    --no-check-certificate "${url}" \
    -O "${file_data_tmp_path}" </dev/null

  wget_status=$?
  if [ $wget_status -ne 0 ]; then
    if [ $wget_status -eq 6 ]; then
      echo "$(date +"%Y-%m-%d %H:%M:%S") ERROR Fallo en autentificación en SCAN. No se pudo extraer la data del día ${TARGET_DATE}. HTTP Error 401." >>"${FILE_LOG_PATH}"
      exit 6
    fi
  fi

  sed -i '1d' "${file_data_tmp_path}"

  if [ ! -s "${file_data_final_path}" ]; then
    echo "${HEADER_DATA}" >"${file_data_final_path}"
  fi

  cat "${file_data_tmp_path}" | head -500 | while read data_day_line; do
    unix_time=$(echo "${data_day_line}" | awk '{print $1}')
    in_prom=$(echo "${data_day_line}" | awk '{print $2}')
    out_prom=$(echo "${data_day_line}" | awk '{print $3}')
    in_max=$(echo "${data_day_line}" | awk '{print $4}')
    out_max=$(echo "${data_day_line}" | awk '{print $5}')
    date_time=$(date -d @"$unix_time" "+${full_format_date}")

    file_date=$(date -d @"$unix_time" "+${FORMAT_DATE}")

    if [[ "$file_date" == *"$TARGET_DATE"* ]]; then
      awk -v dt="${date_time}" \
        -v ip="${in_prom}" \
        -v op="${out_prom}" \
        -v im="${in_max}" \
        -v om="${out_max}" \
        -v sep="${SEPARATOR_DATA}" \
        'BEGIN { OFS=sep; print dt, ip, op, im, om }' >>"${file_data_final_path}"
    fi
  done

done <"${DIR_SOURCES_PATH}/${FILE_LAYER_SRC}"
