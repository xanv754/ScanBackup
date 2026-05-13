#/bin/bash
# ---------------------------- INFO ----------------------------
# Script que captura los datos de tráfico del día anterior,
# de todas las interfaces declaradas dentro de la carpeta
# `sources/SCAN/` del sistema. Obtiendo la información de 
# todas estas interfaces para almacenarlas de forma temporal 
# para su procesamiento y, posteriormente, almacenamiento 
# permanente en la base de datos del sistema.
#
# Para más información del sistema, léase `README.md`.
# --------------------------------------------------------------

TARGET_DATE="$1"
SPECIFIC_LAYER="$2"
HOME_PROJECT_PATH="$3"
SEPARATOR="$4"

cat $HOME_PROJECT_PATH/sources/SCAN/$layer | while read line2
  do
    cols2=$(echo "$line2" | awk -F "$SEPARATOR" '{print NF}')
    if [ "$cols2" -lt 4 ]; then
        echo "$(date +"%Y-%m-%d %H:%M:%S") ERROR Rutina Scan. Línea corrupta en sources ($layer): '$line2' ($cols2 columnas) - No se obtuvo la información esperada"
        continue
    fi

    url=`echo $line2 | awk -F "$SEPARATOR" '{print $1}' `
    interfaceName=`echo $line2 | awk -F "$SEPARATOR" '{print $2}' | sed 's/\//\&/g' `
    terminal=`echo $line2 | awk -F "$SEPARATOR" '{print $1}' | sed 's/\// /g' | awk -F " " '{print $NF}'`
    capacity=`echo $line2 | awk -F "$SEPARATOR" '{print $3}' `
    type=`echo $line2 | awk -F "$SEPARATOR" '{print $4}'`

    wget -q --timeout=180 --tries=2 --user=$USERSCAN --password=$PASSWORDSCAN --no-check-certificate $url -O $HOME_PROJECT_PATH/routines/tmp/$terminal > /dev/null 2>&1
    if [ $? -ne 0 ]; then
      echo "$(date +"%Y-%m-%d %H:%M:%S") ERROR Rutina Scan. Falló wget de la URL: $url"
      echo "$(date +"%Y-%m-%d %H:%M:%S") ERROR Rutina Scan. Falló wget de la URL: $url" >> $PWDSCANBACKUP/data/logs/$FILE_LOG_PATH
      continue
    fi

    sed -i '1d' $HOME_PROJECT_PATH/routines/tmp/$terminal
    if [ $? -ne 0 ]; then
      echo "$(date +"%Y-%m-%d %H:%M:%S") ERROR Rutina Scan. 'sed' falló en el archivo $terminal"
      echo "$(date +"%Y-%m-%d %H:%M:%S") ERROR Rutina Scan. 'sed' falló en el archivo $terminal" >> $PWDSCANBACKUP/data/logs/$FILE_LOG_PATH
    fi

    cat $HOME_PROJECT_PATH/routines/tmp/$terminal | head -500 | while read line3
    do
      cols=$(echo "$line3" | awk '{print NF}')
      if [ "$cols" -lt 1 ]; then
        echo "$(date +"%Y-%m-%d %H:%M:%S") ERROR Rutina Scan. Línea corrupta en $terminal: '$line3' ($cols columnas)"
        echo "$(date +"%Y-%m-%d %H:%M:%S") ERROR Rutina Scan. Línea corrupta en $terminal: '$line3' ($cols columnas)" >> $PWDSCANBACKUP/data/logs/$FILE_LOG_PATH
        continue
      fi

      UNIXtime=`echo $line3 | awk '{print $1}'` 
      inProm=`echo $line3 | awk '{print $2}'` 
      outProm=`echo $line3 | awk '{print $3}'`
      inPromMax=`echo $line3 | awk '{print $4}'` 
      outPromMax=`echo $line3 | awk '{print $5}'`
      time=$(date -d @"$UNIXtime" "+%Y-%m-%d;%H:%M:%S")

      if [ "$layer" = "$IP_BRAS_LAYER" ]; then
        echo $time$SEPARATOR$inProm$SEPARATOR$inPromMax | grep -f $HOME_PROJECT_PATH/routines/tmp/fechaayer >> "$PWDSCANBACKUP/data/SCAN/${layer}/${type}${SEPARATOR}${interfaceName}${SEPARATOR}${capacity}"
      else
        echo $time$SEPARATOR$inProm$SEPARATOR$outProm$SEPARATOR$inPromMax$SEPARATOR$outPromMax | grep -f $HOME_PROJECT_PATH/routines/tmp/fechaayer >> "$PWDSCANBACKUP/data/SCAN/${layer}/${type}${SEPARATOR}${interfaceName}${SEPARATOR}${capacity}"
      fi
    done
      
    lineas=`cat "$PWDSCANBACKUP/data/SCAN/${layer}/${type}${SEPARATOR}${interfaceName}${SEPARATOR}${capacity}" | grep -f $HOME_PROJECT_PATH/routines/tmp/fechaayer | wc -l`

    hour=$(date +"%y-%m-%d %T")
    echo $hour $layer $interfaceName $lineas >> $PWDSCANBACKUP/data/logs/Alertas-SCAN.log
    rm $HOME_PROJECT_PATH/routines/tmp/$terminal
  done  
done

echo "$(date +"%Y-%m-%d %H:%M:%S") INFO Scan Collector: Captura de datos del $TARGET_DATE finalizada"
