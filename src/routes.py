from flask import render_template, request, jsonify,flash
from flask_mail import Mail, Message
from flask import make_response
from datetime import datetime
from src import app, db
import secrets
import json
from decouple import config
import geoip2.database


app.config['SECRET_KEY'] = config('SECRET_KEY')
app.config['MAIL_SERVER'] = config('MAIL_SERVER')
app.config['MAIL_PORT'] = int(config('MAIL_PORT'))
app.config['MAIL_USERNAME'] = config('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = config('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = config('MAIL_USE_TLS', default=True, cast=bool)
app.config['MAIL_USE_SSL'] = config('MAIL_USE_SSL', default=False, cast=bool)
mail = Mail(app)




class Usuario(db.Model):
    __tablename__ = 'usuarios'
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    has_voted = db.Column(db.Boolean, default=False)
    token = db.Column(db.String(128))

class Voto(db.Model):
    __tablename__ = 'votos'
    vote_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.user_id'), nullable=False) 
    candidate_id = db.Column(db.Integer, nullable=False)
    vote_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(100), nullable=False)
    data_loc = db.Column(db.TEXT, nullable=False)
    usuario = db.relationship('Usuario', backref=db.backref('votos', lazy=True))



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/government_plan_genaldo')
def government_plan_1():
    return render_template('government_plan_genaldo.html')

@app.route('/government_plan_edison')
def government_plan_2():
    return render_template('government_plan_edison.html')


@app.route('/government_plan_blanca_lilia')
def government_plan_3():
    return render_template('government_plan_blanca_lilia.html')



@app.route('/government_plan_mikan')
def government_plan_4():
    return render_template('government_plan_mikan.html')

@app.route('/government_plan_juan_andres')
def government_plan_5():
    return render_template('government_plan_juan_andres.html')



@app.route('/enviar_correo', methods=['POST'])
def enviar_correo():
    if request.method == 'POST':
        email = request.form.get('correo')
        email_correct = validateEmail(email=email)
        if email_correct:
            existing_user = Usuario.query.filter_by(email=email).first()
            if existing_user:          
                if existing_user.has_voted:
                    return jsonify({"message": "El correo electrónico proporcionado ya ha sido utilizado para emitir un voto"}), 400
                else:
                    # Si el usuario ya está registrado pero no ha votado
                    # reenviar el token existente
                    existing_token = existing_user.token
                    sendEmail(email, existing_token)
                    return jsonify({"message": "Correo ya está registrado, se reenviará el link de votación"}), 200
            else:
                # Si el usuario no está registrado
                # Generar un nuevo token y enviar correo
                # almacenarlo en el nuevo usuario
                token = secrets.token_hex(16)
                sent = sendEmail(email, token) 
                if sent:
                    # Crear un nuevo usuario en la base de datos
                    new_user = Usuario(email=email, token=token)
                    db.session.add(new_user)
                    db.session.commit()
                    # Devolver una respuesta JSON para indicar que el correo se recibió correctamente.
                    return jsonify({"message": "Correo enviado con éxito. ¡Revisa tu bandeja de entrada para el enlace de votación!"}), 200
                else:
                    return jsonify({"message": "Error al enviar el correo con el link de votación, inténtalo de nuevo"}), 500
        else:
            return jsonify({"message": "Correo electrónico inválido."}), 400

               
    
@app.route('/votacion', methods=['GET'])
def votacion():
    token = request.args.get('token')
    print("El token es {}".format(token))
    if tokenValid(token):
        # El token es válido, el usuario puede votar
        # Configurar las cabeceras de la respuesta para evitar el almacenamiento en caché
        response = make_response(render_template('voting.html'))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        return response
    else:
        # El token no es válido, redirige al error 404
        return render_template('404.html'), 404

@app.route('/votar', methods=['POST'])
def votar():
    try:
        # Obtener el ID del candidato, el nombre y el token desde la solicitud
        candidate_id = request.form.get('candidateId')
        candidate_name = request.form.get('candidateName')
        token = request.form.get('token')

        # Realizar las validaciones necesarias, como verificar el token y registrar el voto
        # Primero, verifica si el token es válido y si el usuario aún no ha votado
        existing_user = Usuario.query.filter_by(token=token, has_voted=False).first()
        
        if existing_user:
            # Actualiza el estado del usuario para indicar que ha votado
            existing_user.has_voted = True
            
            ip_address = request.remote_addr
            ip_address = "181.78.15.119"
            data_loc= obtener_info_geolocalizacion(ip_address)


            # Convierte el diccionario en una cadena JSON
            #data_loc_json = "{}".format(data_loc)
            data_loc_json = json.dumps(data_loc)

            # Crea una instancia de Voto y regístrala en la base de datos
            new_vote = Voto(user_id=existing_user.user_id, candidate_id=candidate_id, ip_address=ip_address, data_loc=data_loc_json)
            db.session.add(new_vote)
            db.session.commit()

            # Devolver una respuesta de éxito
            return jsonify({'success': True, 'message': 'Voto registrado exitosamente.'})
        else:
            # El token no es válido o el usuario ya ha votado
            return jsonify({'success': False, 'message': 'Link inválido o usuario ya ha votado.'})
    except Exception as e:
        # Manejar cualquier error que pueda ocurrir
        return jsonify({'success': False, 'error': str(e)})



# Manejador de error 404
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.route('/politica-de-privacidad', methods=['GET'])
def politica_de_privacidad():
    return render_template('privacy.html')






def tokenValid(token):
    # Realiza una consulta en la base de datos para verificar si el token existe en la tabla Usuario
    existing_user = Usuario.query.filter_by(token=token).first()

    # Si usuario_existente es None, el token no existe en la base de datos
    if existing_user is None:
        return False

    # Si has_voted es True, el usuario ya ha votado
    if existing_user.has_voted:
        return False

    # Si llegamos aquí, el token existe y el usuario no ha votado, por lo que es válido
    return True


import re
def validateEmail(email):
    # Patrón de expresión regular para validar correos electrónicos
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'    
    if re.match(patron, email):
        return True
    else:
        return False

def sendEmail(email_destination, token):
    # Crear el mensaje de correo  
    msg = Message('🤵MI CANDIDATO: Link de votación, encuesta alcaldía de El Rosal ',
                  sender='edwinarevalo88@gmail.com',
                  recipients=[email_destination])
    
    
    enlace_votacion = f'http://127.0.0.1:5000/votacion?token={token}'
    correo_contenido = (
        f'¡Hola!\n\n'
        f'Gracias por participar en nuestra encuesta de votación electrónica. '
        f'Estamos emocionados por conocer tu opinión sobre el tema.\n\n'
        f'Este es un proceso seguro y anónimo. Por favor, sigue estas instrucciones:\n'
        f'➡ No compartas este enlace de votación con otros.\n'
        f'➡ Solo puedes votar una vez.\n'
        f'➡ Asegúrate de que tu voto refleje tu opinión honesta.\n\n'
        f'Haz clic en el siguiente enlace para votar:\n'
        f'🗳️ {enlace_votacion}\n\n'
        f'Tu privacidad es importante para nosotros. Queremos asegurarte que solo publicaremos la intención de voto de los candidatos, y no revelaremos tu información personal ni a quién votaste.\n\n'
        f'¡Gracias por tu participación y contribución!\n\n'
        f'Atentamente,\n'
        f'MiCandidato.org '
    )

    msg.body = correo_contenido
    
    try:
        mail.send(msg)
        flash('Correo enviado exitosamente', 'success')
        return True
    except Exception as e:
        flash('Error al enviar el correo: ' + str(e), 'error')
        return False


import requests




def obtener_info_geolocalizacion(ip):
    # Ruta a tu base de datos de MaxMind
    db_path = 'src/static/db/GeoLite2-City_20230919/GeoLite2-City.mmdb'


    try:
        # Crear un objeto lector
        with geoip2.database.Reader(db_path) as reader:
            # Realizar una búsqueda de ciudad para la IP proporcionada
            response = reader.city(ip)
            continent = response.continent.names.get('es')
            continent_id = response.continent.geoname_id
            country = response.country.names.get('es')
            country_id = response.country.geoname_id
            location = {
                "accuracy_radius": response.location.accuracy_radius,
                "latitude": response.location.latitude,
                "longitude": response.location.longitude,
                "time_zone": response.location.time_zone
            }
            subdivisions = response.subdivisions[0].names.get('es')
            subdivisions_id = response.subdivisions[0].geoname_id

            
            info_geolocalizacion = {
                    'continent': continent,
                    'continent_id': continent_id,
                    'country': country,
                    'country_id': country_id,
                    'subdivisions': subdivisions,
                    'subdivisions_id': subdivisions_id,
                    'location': location
                }

            return info_geolocalizacion
    except Exception as e:
        # Manejar cualquier error que pueda ocurrir
        print(f"Error al obtener información de geolocalización para la IP {ip}: {str(e)}")
        return None





'''

# Supongamos que tienes la dirección IP en la variable 'ip_address'
ip_address = "181.78.15.119"  # Reemplaza con la dirección IP real


# Llamada a la API para obtener coordenadas
response = requests.get(f"https://ipinfo.io/{ip_address}/json")
data = response.json()
location = data.get("loc")
latitude, longitude = location.split(",")
print("*"*30)
print(data)
print(latitude, longitude)
print("*"*30)
'''


'''
# Llamada a la API de GeoNames
response = requests.get(f"http://api.geonames.org/findNearbyPlaceNameJSON?lat=latitude&lng=longitude&username=tu_usuario")
data = response.json()
municipality = data.get("geonames")[0].get("name")
print(data)
print(municipality)
print("+"*30)
'''


"""
lo que sigue
4) desplegar a produccion
5) ajustar lo de consejales
6) ajustar ip para que funcione con api web en los caso que no se encueuntre en la db
"""