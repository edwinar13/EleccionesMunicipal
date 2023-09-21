from src import app
from decouple import config

if __name__ == '__main__':
    app.debug = config('DEBUG', default=False, cast=bool)
    app.run(host='0.0.0.0', port=5000)
