from flask import Flask, render_template, request, redirect, url_for
import csv
from collections import defaultdict
from datetime import datetime

app = Flask(__name__)

# Lista en memoria para registros recientes
materiales = []

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para registrar material reciclado
@app.route('/impacto', methods=['GET', 'POST'])
def impacto():
    if request.method == 'POST':
        tipo = request.form['tipo']
        cantidad = float(request.form['cantidad'])
        fecha = request.form['fecha']
        ubicacion = request.form['ubicacion']

        # Factores de CO₂ por kg reciclado
        factores_co2 = {
            'Plástico': 1.5,
            'Vidrio': 0.3,
            'Papel': 1.0,
            'Cartón': 0.8,
            'Metal': 2.0
        }

        co2 = round(cantidad * factores_co2.get(tipo, 0), 2)

        registro = {
            'tipo': tipo,
            'cantidad': cantidad,
            'fecha': fecha,
            'ubicacion': ubicacion,
            'co2': co2
        }

        materiales.append(registro)

        # Guardar en CSV
        with open('materiales_reciclados.csv', 'a', newline='', encoding='utf-8') as archivo:
            writer = csv.writer(archivo)
            writer.writerow([tipo, cantidad, fecha, ubicacion, co2])

        return redirect(url_for('impacto'))

    return render_template('impacto.html', materiales=materiales)

# Ruta para funciones
@app.route('/funciones')
def funciones():
    return render_template('funciones.html')

# Ruta para reportes
@app.route('/reportes')
def reportes():
    return render_template('reportes.html')

# Función para calcular estadísticas (versión simplificada)
def calcular_estadisticas():
    estadisticas = defaultdict(lambda: defaultdict(float))
    arboles_salvados = 0

    try:
        with open('materiales_reciclados.csv', 'r', encoding='utf-8') as archivo:
            reader = csv.reader(archivo)
            for linea in reader:
                if len(linea) >= 5:  # Asegura que tenga todos los campos
                    tipo = linea[0]
                    cantidad = float(linea[1])
                    fecha = linea[2]
                    
                    # Procesar fecha y agrupar por mes-año
                    fecha_obj = datetime.strptime(fecha, "%Y-%m-%d")
                    mes_anio = fecha_obj.strftime("%Y-%m")
                    
                    # Sumar cantidades por material y mes
                    estadisticas[mes_anio][tipo] += cantidad
                    
                    # Calcular árboles salvados (solo para papel)
                    if tipo == 'Papel':
                        arboles_salvados += cantidad / 100  # 100kg de papel = 1 árbol
    except FileNotFoundError:
        pass

    return estadisticas, round(arboles_salvados, 2)

# Ruta para estadísticas (versión tabla HTML)
@app.route('/estadisticas')
def estadisticas():
    estadisticas_data, arboles = calcular_estadisticas()
    
    # Obtener todos los tipos de materiales únicos y ordenados
    tipos_material = sorted({tipo for mes in estadisticas_data.values() for tipo in mes.keys()})

    return render_template(
        'estadisticas.html',
        estadisticas=estadisticas_data,
        tipos_material=tipos_material,
        arboles=arboles
    )

if __name__ == '__main__':
    app.run(debug=True)