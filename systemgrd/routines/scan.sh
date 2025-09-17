#/bin/bash

# ---------------------------- INFO ----------------------------
#
# Script que captura los datos de tráfico del día anterior,
# de todas las interfaces declaradas dentro de la carpeta
# `sources/SCAN/` del sistema. Obtiendo la información de 
# todas estas interfaces para almacenarlas de forma temporal 
# para su procesamiento y, posteriormente, almacenamiento 
# permanente en la base de datos del sistema.
#
# Para más información del sistema, léase `README.md`.
#
# --------------------------------------------------------------

fecha=$(date --date="yesterday" +%Y-%m-%d) 
ruta="$HOMEPROJECT/systemgrd"

if [ -d "$ruta/routines/tmp" ]; then
  if [ -n "$(ls -A "$ruta/routines/tmp" 2>/dev/null)" ]; then
    rm $ruta/routines/tmp/*
  fi
else
  mkdir $ruta/routines/tmp
fi
echo "$(date +"%Y-%m-%d %H:%M:%S") INFO Captura de datos iniciada..."
echo "$(date +"%Y-%m-%d %H:%M:%S") INFO Captura de datos iniciada..." >> $HOMEPROJECT/data/logs/SysGRD.log

cd $ruta/routines
echo $fecha > $ruta/routines/tmp/fechaayer
ls $HOMEPROJECT/sources/SCAN > $ruta/routines/tmp/lista

cat $ruta/routines/tmp/lista | while read line1
do
  capa=`echo $line1 | sed 's/.txt//g'`
  cat $HOMEPROJECT/sources/SCAN/$capa.txt | while read line2
  do
    url=`echo $line2 | awk '{print $1}' `
    interfaz=`echo $line2 | awk '{print $2}' `
    terminal=`echo $line2 | awk '{print $1}' | sed 's/\// /g' | awk -F " " '{print $NF}'`
    capacidad=`echo $line2 | awk '{print $3}' `
    tipo=`echo $line2 | awk '{print $4}' `

    wget -q --user=$USERSCAN --password=$PASSWORDSCAN --no-check-certificate $url -O $ruta/routines/tmp/$terminal > /dev/null 2>&1

    sed -i '1d' $ruta/routines/tmp/$terminal
    cat $ruta/routines/tmp/$terminal | head -500 | while read line3
    do
      # Fecha y hora en formato UNIX
      fechaunix=`echo $line3 | awk '{print $1}'` 
      # Valor de trafico de entrada promedio en bytes por segunda
      inpro=`echo $line3 | awk '{print $2}'` 
      # Valor de trafico de salida promedio en byte por segunda
      outpro=`echo $line3 | awk '{print $3}'`
      # Valor de trafico de entrada maximo en byte por segunda
      inmax=`echo $line3 | awk '{print $4}'` 
      # Valor de trafico de salida maximo en byte por segunda
      outmax=`echo $line3 | awk '{print $5}'`

      fechanormal=$(date -d @"$fechaunix" "+%Y-%m-%d %H:%M:%S")
      if [ "$capa" = "IPBras" ]; then
        echo $fechanormal $inpro $inmax | grep -f $ruta/routines/tmp/fechaayer >> $HOMEPROJECT/data/SCAN/$capa/$capacidad\%$interfaz  
      else
        echo $fechanormal $inpro $outpro $inmax $outmax | grep -f $ruta/routines/tmp/fechaayer >> $HOMEPROJECT/data/SCAN/$capa/$tipo\%$interfaz\%$capacidad
      fi         
    done
      
    lineas=`cat $HOMEPROJECT/data/SCAN/$capa/$tipo\%$interfaz\%$capacidad | grep -f $ruta/routines/tmp/fechaayer | wc -l`
    hora=$(date +"%y-%m-%d %T")
    echo $hora $capa $interfaz $lineas >> $HOMEPROJECT/data/logs/Alertas-SCAN.txt 
    rm $ruta/routines/tmp/$terminal
  done  
done

rm $ruta/routines/tmp/*
echo "$(date +"%Y-%m-%d %H:%M:%S") INFO Captura de datos finalizada"
echo "$(date +"%Y-%m-%d %H:%M:%S") INFO Captura de datos finalizada" >> $HOMEPROJECT/data/logs/SysGRD.log