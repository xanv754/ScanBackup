"""
Este script crea los reportes diarios de los datos obtenidos
del aplicativo SCAN.

Detalles de Proceso:
- Se captura la fecha del día anterior.
- Se obtiene la capa de la interfaz a analizar.
- Se obtiene la interfaz a analizar.
- Se obtiene la capacidad de la interfaz.
- Se obtiene el tipo de la interfaz.
- Se obtiene los datos del trend de la interfaz, filtrados por el día anterior.
- Se calcula el promedio de la interfaz.
- Se calcula el uso de la interfaz.
- Se crea un diccionario donde se relacionan las variables calculadas
  con los nombres de las columnas del reporte.
- Se crea un dataframe temporal donde se escriben los resultados.
- Se concatena el dataframe temporal con el dataframe donde se guarda toda la data.
- Se exporta el dataframe en un archivo CSV.
"""

import os
import pandas as pd
from datetime import datetime, timedelta, timezone
from constants.path import layers_BBIP_SCAN
from utils.log import log


ruta_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ruta_scan_dir = os.path.join(ruta_base, "data", "SCAN")
ruta_reporte_dir = os.path.join(ruta_base, "data", "SCAN", "Reportes-Diarios")
# ayer = (datetime.now(timezone.utc) - timedelta(days=1)).strftime('%Y-%m-%d')
ayer = "2025-06-11"

log.info("Starting to generate the daily report...")
try:
    for capa in layers_BBIP_SCAN:
        ruta_data_scan = os.path.join(ruta_scan_dir, capa)
        ruta_data_reporte = os.path.join(ruta_reporte_dir, f"Resumen_{capa}.csv")

        # TODO: Eliminar encabezados magic strings
        if os.path.exists(ruta_data_reporte): 
            df_viejo_reporte = pd.read_csv(ruta_data_reporte, sep=" ", skiprows=1, names=['Interfaz', 'Tipo', 'Fecha', 'Capacidad', 'In', 'Out', 'In-Max', 'Out-Max', 'Uso-%'])
        else:
            df_viejo_reporte = pd.DataFrame(columns=['Interfaz', 'Tipo', 'Fecha', 'Capacidad', 'In', 'Out', 'In-Max', 'Out-Max', 'Uso-%'])
        df_nuevo_reporte = pd.DataFrame(columns=['Interfaz', 'Tipo', 'Fecha', 'Capacidad', 'In', 'Out', 'In-Max', 'Out-Max', 'Uso-%'])

        for archivo in os.listdir(ruta_data_scan):
            interfaz = archivo.rsplit('%')[1]  
            capacidad = float(archivo.split('%')[-1])
            tipo = archivo.rsplit('%')[0]
            df_interfaz = pd.read_csv(f'{ruta_data_scan}/{archivo}', sep=' ', names=['Fecha', 'Hora', 'IN', 'OUT', 'IN MAX', 'OUT MAX'])
            df_interfaz = df_interfaz[df_interfaz['Fecha'] == ayer]
            
            try:
                factor = 0.000000008022
                in_promedio = (df_interfaz['IN'].mean()) * factor
                out_promedio = (df_interfaz['OUT'].mean()) * factor
                inmax_promedio = (float(df_interfaz['IN MAX'].max())) * factor
                outmax_promedio = (float(df_interfaz['OUT MAX'].max())) * factor
                if inmax_promedio >= outmax_promedio:
                    uso = (inmax_promedio / capacidad) * 100
                else:
                    uso = (outmax_promedio / capacidad) * 100
            except:
                log.error(f"Failed to generate calculations for {interfaz}")
                continue

            valores = {
                'Interfaz': interfaz,
                'Tipo': tipo,
                'Fecha': ayer,
                'Capacidad': capacidad,
                'In': in_promedio,
                'Out': out_promedio,
                'In-Max': inmax_promedio,
                'Out-Max': outmax_promedio,
                'Uso-%': uso
            }

            df_interfaz = pd.DataFrame([valores])
            df_interfaz.dropna(inplace=True)
            if df_nuevo_reporte.empty: df_nuevo_reporte = df_interfaz
            else: df_nuevo_reporte = pd.concat([df_nuevo_reporte, df_interfaz], axis=0)
            df_nuevo_reporte.reset_index(drop=True, inplace=True)

        if not df_viejo_reporte.empty:
            df_nuevo_reporte = pd.concat([df_viejo_reporte, df_nuevo_reporte], axis=0)
        df_nuevo_reporte.to_csv(ruta_data_reporte, index=False, sep=" ", decimal=".")
except Exception as e:
    log.error(f"Daily report generation failed. {e}")
else:
    log.info("Daily report generation finished successfully")