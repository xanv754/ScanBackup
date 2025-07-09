#/bin/bash

# ---------------------------- INFO ----------------------------
# 
# Script que captura los datos de todas las interfacez de BBIP
# obtenidas desde el aplicativo SCAN
#
# --------------------------------------------------------------

# Captura la fecha del dia anterior
fecha=$(date --date="yesterday" +%Y-%m-%d) 
ruta="$HOMEPROJECT/systemgrd"

cd $ruta/routines
rm $ruta/routines/tmp/*
echo $fecha > $ruta/routines/tmp/fechaayer
# Lista las capas a capturar data 
ls $ruta/sources/SCAN > $ruta/routines/tmp/lista #TODO: MEJORAR

echo "$(date +"%Y-%m-%d %H:%M:%S") INFO Captura de datos iniciada..."
echo "$(date +"%Y-%m-%d %H:%M:%S") INFO Captura de datos iniciada..." >> $ruta/data/logs/SysGRD.log

cat $ruta/routines/tmp/lista | while read line1
do
  capa=`echo $line1 | sed 's/.txt//g'`
  cat $ruta/sources/SCAN/$capa.txt | while read line2
  do
    url=`echo $line2 | awk '{print $1}' `
    interfaz=`echo $line2 | awk '{print $2}' `
    terminal=`echo $line2 | awk '{print $1}' | sed 's/\// /g' | awk -F " " '{print $NF}'`
    capacidad=`echo $line2 | awk '{print $3}' `
    tipo=`echo $line2 | awk '{print $4}' `

    wget --user=$USERSCAN --password=$PASSWORDSCAN --no-check-certificate $url -O $ruta/routines/tmp/$terminal

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
        echo $fechanormal $inpro $inmax | grep -f $ruta/routines/tmp/fechaayer >> $ruta/data/SCAN/$capa/$capacidad\%$interfaz  
      else
        echo $fechanormal $inpro $outpro $inmax $outmax | grep -f $ruta/routines/tmp/fechaayer >> $ruta/data/SCAN/$capa/$tipo\%$interfaz\%$capacidad
      fi         
    done
      
    lineas=`cat $ruta/data/SCAN/$capa/$tipo\%$interfaz\%$capacidad | grep -f $ruta/routines/tmp/fechaayer | wc -l`
    hora=$(date +"%y-%m-%d %T")
    echo $hora $capa $interfaz $lineas >> $ruta/data/logs/Alertas-SCAN.txt 
    rm $ruta/routines/tmp/$terminal
  done  
done

rm $ruta/routines/tmp/*
echo "$(date +"%Y-%m-%d %H:%M:%S") INFO Captura de datos finalizada"
echo "$(date +"%Y-%m-%d %H:%M:%S") INFO Captura de datos finalizada" >> $ruta/data/logs/SysGRD.log