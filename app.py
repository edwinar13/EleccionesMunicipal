from src import app
from decouple import config

if __name__ == '__main__':
    app.debug = config('DEBUG', default=False, cast=bool)
    port = config('PORT', default=5000, cast=int)  # Cargar el valor de PORT como entero
    app.run(host='0.0.0.0', port=port)  # Usar el valor de port como el puerto de la aplicación
