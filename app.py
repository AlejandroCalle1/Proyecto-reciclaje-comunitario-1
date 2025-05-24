from flask import Flask, render_template, request, redirect, url_for
import csv
from collections import defaultdict
from datetime import datetime
import numpy as np

app = Flask(__name__)

# Lista en memoria para registros recientes
materiales = []

# Matrices de conversión ambiental
MATRICES_IMPACTO = {
    'ahorro_energia': np.array([
        [5.91, 0], 
        [0.35, 0], 
        [3.0, 0], 
        [2.5, 0], 
        [11.0, 0]
    ]),
    'ahorro_agua': np.array([
        [30, 0], 
        [10, 0], 
        [50, 0], 
        [40, 0], 
        [40, 0]
    ]),
    'reduccion_residuos': np.array([
        [1.0, 0], 
        [1.0, 0], 
        [1.0, 0], 
        [1.0, 0], 
        [1.0, 0]
    ]),
    'arboles_salvados': np.array([
        [0.1, 0], 
        [0, 0], 
        [1.0, 0], 
        [0.8, 0], 
        [0, 0]
    ]),
    'co2_evitado': np.array([
        [1.5, 0], 
        [0.3, 0], 
        [1.0, 0], 
        [0.8, 0], 
        [2.0, 0]
    ]),
    'petroleo_ahorrado': np.array([
        [0.8, 0], 
        [0, 0], 
        [0.1, 0], 
        [0.1, 0], 
        [0.5, 0]
    ])
}

MATERIALES = ['Plástico', 'Vidrio', 'Papel', 'Cartón', 'Metal']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/impacto', methods=['GET', 'POST'])
def impacto():
    if request.method == 'POST':
        tipo = request.form['tipo']
        cantidad = float(request.form['cantidad'])
        fecha = request.form['fecha']
        ubicacion = request.form['ubicacion']

        # Validación de fecha antes de procesarla
        try:
            fecha_obj = datetime.strptime(fecha, "%Y-%m-%d") if fecha else datetime.today()
        except ValueError:
            return "Error: La fecha ingresada no tiene el formato correcto."

        try:
            idx = MATERIALES.index(tipo)
        except ValueError:
            idx = 0

        # Calcular impactos ambientales
        co2 = round(cantidad * MATRICES_IMPACTO['co2_evitado'][idx][0], 2)
        energia = round(cantidad * MATRICES_IMPACTO['ahorro_energia'][idx][0], 2)
        agua = round(cantidad * MATRICES_IMPACTO['ahorro_agua'][idx][0], 2)
        residuos = round(cantidad * MATRICES_IMPACTO['reduccion_residuos'][idx][0], 2)
        arboles = round(cantidad * MATRICES_IMPACTO['arboles_salvados'][idx][0] / 100, 4)
        petroleo = round(cantidad * MATRICES_IMPACTO['petroleo_ahorrado'][idx][0], 3)

        registro = {
            'tipo': tipo,
            'cantidad': cantidad,
            'fecha': fecha_obj.strftime("%Y-%m-%d"),
            'ubicacion': ubicacion,
            'co2': co2,
            'energia': energia,
            'agua': agua,
            'residuos': residuos,
            'arboles': arboles,
            'petroleo': petroleo
        }

        materiales.append(registro)

        # Guardar datos en CSV con formato de fecha corregido
        with open('materiales_reciclados.csv', 'a', newline='', encoding='utf-8') as archivo:
            writer = csv.writer(archivo)
            writer.writerow([tipo, cantidad, fecha_obj.strftime("%Y-%m-%d"), ubicacion, co2, energia, agua, residuos, arboles, petroleo])

        return redirect(url_for('impacto'))

    return render_template('impacto.html', materiales=materiales)

def calcular_estadisticas():
    estadisticas = defaultdict(lambda: defaultdict(float))
    totales = {'co2': 0, 'energia': 0, 'agua': 0, 'residuos': 0, 'arboles': 0, 'petroleo': 0}

    try:
        with open('materiales_reciclados.csv', 'r', encoding='utf-8') as archivo:
            reader = csv.reader(archivo)
            for linea in reader:
                if len(linea) >= 10 and linea[2]:  # Verificación de fecha no vacía
                    tipo = linea[0]
                    cantidad = float(linea[1])

                    try:
                        fecha_obj = datetime.strptime(linea[2], "%Y-%m-%d")
                        mes_anio = fecha_obj.strftime("%Y-%m")
                        estadisticas[mes_anio][tipo] += cantidad
                    except ValueError:
                        print(f"Advertencia: Fecha inválida en línea {linea}")

                    # Sumar valores a totales
                    totales['co2'] += float(linea[4])
                    totales['energia'] += float(linea[5])
                    totales['agua'] += float(linea[6])
                    totales['residuos'] += float(linea[7])
                    totales['arboles'] += float(linea[8])
                    totales['petroleo'] += float(linea[9])
    except FileNotFoundError:
        pass

    return estadisticas, totales

@app.route('/estadisticas')
def estadisticas():
    estadisticas_data, totales = calcular_estadisticas()
    tipos_material = sorted({tipo for mes in estadisticas_data.values() for tipo in mes.keys()})

    return render_template('estadisticas.html', estadisticas=estadisticas_data, tipos_material=tipos_material, totales=totales, matrices=MATRICES_IMPACTO)

@app.route('/matrices')
def mostrar_matrices():
    return render_template('matrices.html', matrices=MATRICES_IMPACTO, materiales=MATERIALES)

@app.route('/funciones')
def funciones():
    return render_template('funciones.html')

@app.route('/reportes')
def reportes():
    return render_template('reportes.html')

if __name__ == '__main__':
    app.run(debug=True)
