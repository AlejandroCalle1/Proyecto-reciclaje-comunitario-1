# importar bibliotecas
from flask import Flask, render_template

# inicializar la aplicación
app = Flask(__name__)

# rutas
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/informacion1')
def informacion1():
    return render_template('informacion1.html')

@app.route('/informacion2')
def informacion2():
    return render_template('informacion2.html')

# ejecutar la app
if __name__ == "__main__":
    app.run(debug=True)  # facilidad para modificar el programa
