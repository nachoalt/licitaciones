from flask import Flask, jsonify
import pandas as pd
from datetime import datetime, timedelta
import io
import requests

app = Flask(__name__)

@app.route("/listar_licitaciones", methods=["GET"])
def listar_licitaciones():
    try:
        # Descargar el Excel desde COMPR.AR
        url = "https://comprar.gob.ar/descargarReporteExcel.aspx?qs=W1HXHGHtH10="
        response = requests.get(url)
        if response.status_code != 200:
            return jsonify({"error": "No se pudo descargar el Excel"}), 500

        # Leer archivo en memoria
        excel_file = io.BytesIO(response.content)
        df = pd.read_excel(excel_file)

        # Normalizar columnas
        df.columns = [col.strip().lower() for col in df.columns]

        # Filtrar por apertura > hoy + 7 días
        fecha_corte = datetime.now() + timedelta(days=7)
        df = df[df['fecha de apertura'] > fecha_corte]

        # Filtrar por objeto
        df = df[df['objeto'].str.contains("mantenimiento|limpieza|obra", case=False, na=False)]
        df = df[~df['objeto'].str.contains("seguridad|informática|vigilancia|sistemas", case=False, na=False)]

        # Seleccionar columnas clave
        columnas = {
            'nro proceso': 'codigo',
            'unidad operativa de contrataciones': 'entidad',
            'objeto': 'objeto',
            'fecha de apertura': 'fecha_apertura',
            'presupuesto oficial': 'presupuesto'
        }

        df = df[[*columnas.keys()]].rename(columns=columnas)
        data = df.to_dict(orient='records')

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
