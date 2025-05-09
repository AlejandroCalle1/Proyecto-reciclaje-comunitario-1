# importar bibliotecas
from flask import Flask, render_template,request,redirect,url_for
from datetime import datetime

# inicializar la aplicación
app = Flask(__name__)

#base de datos temporal
materiales=[]

# rutas
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/impacto')
def impacto():
    return render_template('impacto.html')

@app.route('/estadisticas')
def estadisticas():
    return render_template('estadisticas.html')

@app.route('/funciones')
def funciones():
    return render_template('funciones.html')

@app.route('/reportes')
def reportes():
    return render_template('reportes.html')


from werkzeug.utils import secure_filename
import os




# ejecutar la app
if __name__ == "__main__":
    app.run(debug=True)  # facilidad para modificar el programa



