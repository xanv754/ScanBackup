#/bin/bash
# ---------------------------- INFO Rutina Scan. ----------------------------
# Script que captura los datos de tráfico del día anterior,
# de todas las interfaces declaradas dentro de la carpeta
# `sources/SCAN/` del sistema. Obtiendo la información de 
# todas estas interfaces para almacenarlas de forma temporal 
# para su procesamiento y, posteriormente, almacenamiento 
# permanente en la base de datos del sistema.
#
# Para más información del sistema, léase `README.md`.
# --------------------------------------------------------------

systemDate="${1:-$(date --date="yesterday" +%Y-%m-%d)}"
specifyLayer="${2:-}"
specifyLayer="$(echo "$specifyLayer" | awk '{print toupper($0)}')"
home="$HOMEPROJECT/scanbackup"
layerIPBras="IPBRAS"
separator=";"

if [ -d "$home/routines/tmp" ]; then
  if [ -n "$(ls -A "$home/routines/tmp" 2>/dev/null)" ]; then
    rm $home/routines/tmp/*
  fi
else
  mkdir $home/routines/tmp
fi
echo "$(date +"%Y-%m-%d %H:%M:%S") INFO Rutina Scan. Captura de datos del $systemDate iniciada..."
echo "$(date +"%Y-%m-%d %H:%M:%S") INFO Rutina Scan. Captura de datos del $systemDate iniciada..." >> $HOMEPROJECT/data/logs/SysGRD.log

cd $home/routines
echo $systemDate > $home/routines/tmp/fechaayer
if [ -z "$specifyLayer" ]; then
  ls $HOMEPROJECT/sources/SCAN > $home/routines/tmp/lista
else
  echo "$specifyLayer" > $home/routines/tmp/lista
fi

cat $home/routines/tmp/lista | while read line1
do
  layer=`echo $line1 | sed 's/ //g'`
  cat $HOMEPROJECT/sources/SCAN/$layer | while read line2
  do
    cols2=$(echo "$line2" | awk -F "$separator" '{print NF}')
    if [ "$cols2" -lt 4 ]; then
        echo "$(date +"%Y-%m-%d %H:%M:%S") ERROR Rutina Scan. Línea corrupta en sources ($layer): '$line2' ($cols2 columnas) - No se obtuvo la información esperada"
        echo "$(date +"%Y-%m-%d %H:%M:%S") ERROR Rutina Scan. Línea corrupta en sources ($layer): '$line2' ($cols2 columnas) - No se obtuvo la información esperada" >> $HOMEPROJECT/data/logs/SysGRD.log
        continue
    fi

    url=`echo $line2 | awk -F "$separator" '{print $1}' `
    interfaceName=`echo $line2 | awk -F "$separator" '{print $2}' | sed 's/\//\&/g' `
    terminal=`echo $line2 | awk -F "$separator" '{print $1}' | sed 's/\// /g' | awk -F " " '{print $NF}'`
    capacity=`echo $line2 | awk -F "$separator" '{print $3}' `
    type=`echo $line2 | awk -F "$separator" '{print $4}'`

    wget -q --timeout=180 --tries=2 --user=$USERSCAN --password=$PASSWORDSCAN --no-check-certificate $url -O $home/routines/tmp/$terminal > /dev/null 2>&1
    if [ $? -ne 0 ]; then
      echo "$(date +"%Y-%m-%d %H:%M:%S") ERROR Rutina Scan. Falló wget de la URL: $url"
      echo "$(date +"%Y-%m-%d %H:%M:%S") ERROR Rutina Scan. Falló wget de la URL: $url" >> $HOMEPROJECT/data/logs/SysGRD.log
      continue
    fi

    sed -i '1d' $home/routines/tmp/$terminal
    if [ $? -ne 0 ]; then
      echo "$(date +"%Y-%m-%d %H:%M:%S") ERROR Rutina Scan. 'sed' falló en el archivo $terminal"
      echo "$(date +"%Y-%m-%d %H:%M:%S") ERROR Rutina Scan. 'sed' falló en el archivo $terminal" >> $HOMEPROJECT/data/logs/SysGRD.log
    fi

    cat $home/routines/tmp/$terminal | head -500 | while read line3
    do
      cols=$(echo "$line3" | awk '{print NF}')
      if [ "$cols" -lt 1 ]; then
        echo "$(date +"%Y-%m-%d %H:%M:%S") ERROR Rutina Scan. Línea corrupta en $terminal: '$line3' ($cols columnas)"
        echo "$(date +"%Y-%m-%d %H:%M:%S") ERROR Rutina Scan. Línea corrupta en $terminal: '$line3' ($cols columnas)" >> $HOMEPROJECT/data/logs/SysGRD.log
        continue
      fi

      UNIXtime=`echo $line3 | awk '{print $1}'` 
      inProm=`echo $line3 | awk '{print $2}'` 
      outProm=`echo $line3 | awk '{print $3}'`
      inPromMax=`echo $line3 | awk '{print $4}'` 
      outPromMax=`echo $line3 | awk '{print $5}'`

      time=$(date -d @"$UNIXtime" "+%Y-%m-%d;%H:%M:%S")
      if [ "$layer" = "$layerIPBras" ]; then
        echo $time$separator$inProm$separator$inPromMax | grep -f $home/routines/tmp/fechaayer >> "$HOMEPROJECT/data/SCAN/${layer}/${capacity}${separator}${interfaceName}"
      else
        echo $time$separator$inProm$separator$outProm$separator$inPromMax$separator$outPromMax | grep -f $home/routines/tmp/fechaayer >> "$HOMEPROJECT/data/SCAN/${layer}/${type}${separator}${interfaceName}${separator}${capacity}"
      fi
    done
      
    if [ "$layer" = "$layerIPBras" ]; then
      lineas=`cat "$HOMEPROJECT/data/SCAN/${layer}/${capacity}${separator}${interfaceName}" | grep -f $home/routines/tmp/fechaayer | wc -l`
    else
      lineas=`cat "$HOMEPROJECT/data/SCAN/${layer}/${type}${separator}${interfaceName}${separator}${capacity}" | grep -f $home/routines/tmp/fechaayer | wc -l`
    fi

    hour=$(date +"%y-%m-%d %T")
    echo $hour $layer $interfaceName $lineas >> $HOMEPROJECT/data/logs/Alertas-SCAN.log
    rm $home/routines/tmp/$terminal
  done  
done

rm $home/routines/tmp/*
echo "$(date +"%Y-%m-%d %H:%M:%S") INFO Rutina Scan. Captura de datos del $systemDate finalizada"
echo "$(date +"%Y-%m-%d %H:%M:%S") INFO Rutina Scan. Captura de datos del $systemDate finalizada" >> $HOMEPROJECT/data/logs/SysGRD.log