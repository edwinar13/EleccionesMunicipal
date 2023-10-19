from flask import render_template, request, jsonify,flash,Response,redirect, url_for
from flask_mail import Mail, Message
from flask import make_response
from datetime import datetime
from sqlalchemy.exc import OperationalError
from src import app, db
import secrets
import json
from decouple import config
import geoip2.database
import jinja2

'''
#from read import read_votes
<!--
<a href="https://www.linkedin.com/in/edwin-j-arevalo" target="_blank"><i class="fab fa-linkedin"></i></a>
<a href="https://api.whatsapp.com/send?phone=573118994279&amp;text=Hola%20Edwin, " target="_blank"><i class="fab fa-whatsapp"></i></a>
-->
'''

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



@app.route("/")
def index():   
    with open('src/static/json/council_candidates_v1.json', 'r', encoding='utf-8') as f:
        data = json.load(f)    

    for candidato in data['candidatos']:            
        candidato['nombre'] = candidato['nombre'].title()
        candidato['apellido'] = candidato['apellido'].title()
            
    councils= data['candidatos']
    publish = config('PUBLISH', default=False, cast=bool)
    return render_template("index.html", 
                           councils=councils, publish=publish)
    

@app.route("/results")
def results(): 
    
    '''
    # json con los candiatas y porcentajes de votos
    date_votes = {'genaldo': {'votes': 0, 'percentage': 0.00},
                'edison': {'votes': 0, 'percentage': 0.00},
                'blanca_lilia': {'votes': 0, 'percentage': 0.00},
                'mikan': {'votes': 0, 'percentage': 0.00},
                'juan_andres': {'votes': 0, 'percentage': 0.00},
                'voto_blanco': {'votes': 0, 'percentage': 0.00}}
    #json con los votos por dias y por candidato
    date_votes_day = {'genaldo': [(0,'10/01'), (1,'10/02'),(5,'10/03')],
                        'edison': [(0,'10/01'), (5,'10/02'),(20,'10/03')],
                        'blanca_lilia': [(0,'10/01'), (1,'10/02'),(5,'10/03')],
                        'mikan': [(0,'10/01'), (4,'10/02'),(5,'10/03')],
                        'juan_andres': [(0,'10/01'), (0,'10/02'),(2,'10/03')] }    
    date_info = {'total_user_registed': 400,
                'total_votes': 250,                 
                 'votes_from_cundinamarca': 100
                 }    
    '''
    publish = config('PUBLISH', default=False, cast=bool)
    if publish:
        return render_template("results.html")
    else:
        return render_template('404.html'), 404

        
        
    


@app.route('/government_plan_genaldo')
def government_plan_1():
    plan = 1
    return render_template('government_plan.html', plan = plan)

@app.route('/government_plan_edison')
def government_plan_2():
    plan = 2
    return render_template('government_plan.html', plan = plan)

@app.route('/government_plan_blanca_lilia')
def government_plan_3():
    plan = 3
    return render_template('government_plan.html', plan = plan)

@app.route('/government_plan_mikan')
def government_plan_4():
    plan = 4
    return render_template('government_plan.html', plan = plan)

@app.route('/government_plan_juan_andres')
def government_plan_5():
    plan = 5
    return render_template('government_plan.html', plan = plan)



@app.route('/enviar_correo', methods=['POST'])
def enviar_correo():
    try:
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
                        return jsonify({"message": "Correo enviado con éxito. ¡Revisa tu bandeja de entrada para ver el enlace de votación!"}), 200
                    else:
                        return jsonify({"message": "Error al enviar el correo con el link de votación, inténtalo de nuevo"}), 500
            else:
                return jsonify({"message": "Correo electrónico inválido."}), 400
    
    except OperationalError as e:
        # Manejar el error de conexión a la base de datos
        #imprimir mesaje
        return jsonify({'message': 'Error de conexión a la base de datos, vuelve a intentarlo '}), 500
               
    

    
@app.route('/votacion', methods=['GET'])
def votacion():
    token = request.args.get('token')
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
    #try:
    # Obtener los datos enviados por el formulario de votación
    candidate_id = request.form.get('candidateId')
    token = request.form.get('token')


    existing_user = Usuario.query.filter_by(token=token, has_voted=False).first()
    
    if existing_user:
         
        
        x_forwarded_for = request.headers.get('X-Forwarded-For')
        app.logger.info("→→→ X-Forwarded-For: {}".format(x_forwarded_for))
        if x_forwarded_for:
            ip_with_port = x_forwarded_for.split(',')[0]
            ip_address = ip_with_port.split(':')[0]
        else:
            ip_address = request.remote_addr
                
        data_loc= obtener_info_geolocalizacion(ip_address)
        
        app.logger.info("→→→ IP: {}".format(ip_address))    
        if data_loc["status"]:
            data_loc_json = json.dumps(data_loc["message"])
        else:           
            data_loc_json = str("{}-{}".format(x_forwarded_for, data_loc["message"]))
            ip_address = ""


        
        existing_user.has_voted = True       
        new_vote = Voto(user_id=existing_user.user_id, candidate_id=candidate_id, ip_address=ip_address, data_loc=data_loc_json)
        db.session.add(new_vote)
        db.session.commit()
        
        sent = sendEmailVoucher(existing_user.email, token) 
        return jsonify({'success': True, 'message': 'Voto registrado exitosamente.'})
    else:
        # El token no es válido o el usuario ya ha votado
        return jsonify({'success': False, 'message': 'Link inválido o usuario ya ha votado.'})
    '''
    except Exception as e:
        # Manejar cualquier error que pueda ocurrir
        return jsonify({'success': False, 'error': str(e)})
    '''
    


@app.route('/comprobante', methods=['GET'])
def comprobante():
    token = request.args.get('token')
    if tokenHasVoted(token=token):       
        existing_user = Usuario.query.filter_by(token=token).first()       
        return render_template('coprobant.html', user_id=existing_user.user_id)    
    else:        
        return render_template('404.html'), 404


# Manejador de error 404
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.route('/politica-de-privacidad', methods=['GET'])
def politica_de_privacidad():
    return render_template('privacy.html')






def tokenHasVoted(token):
    existing_user = Usuario.query.filter_by(token=token).first()
    if existing_user:
        if existing_user.has_voted:
            return True
    return False


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
    msg = Message('🤵MI CANDIDATO: Link de votación, encuesta a la alcaldía de El Rosal ',
                  sender='micandidato.org@gmail.com',
                  recipients=[email_destination])
    
    
    enlace_votacion = f'https://www.micandidato.org//votacion?token={token}'
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

def sendEmailVoucher(email_destination, token):
    # Crear el mensaje de correo  
    msg = Message('🤵MI CANDIDATO: Link de comprobante, encuesta a la alcaldía de El Rosal ',
                  sender='micandidato.org@gmail.com',
                  recipients=[email_destination])
    
    
    enlace_comprobante = f'https://www.micandidato.org/comprobante?token={token}'
    correo_contenido = (
        f'¡Estimado votante!,\n\n'
        f'En nombre de MiCandidato.org, queremos agradecerte sinceramente por tu participación en nuestra encuesta de votación electrónica. Tu voz es importante y tu voto cuenta.\n\n'
        f'Esperamos que tu experiencia de votación haya sido satisfactoria. Tu comprobante de votación se encuentra disponible para tu referencia. Puedes verlo haciendo clic en el siguiente enlace:\n\n'
        f'📄 {enlace_comprobante}\n\n'
        f'Gracias por ser parte de nuestro proceso democrático y ayudarnos a tomar decisiones informadas. Tu privacidad es esencial para nosotros, y queremos asegurarte que tus datos y elecciones son confidenciales.\n\n'
        f'Si tienes alguna pregunta o comentario sobre el proceso de votación o cualquier otro asunto relacionado, no dudes en ponerte en contacto con nosotros.\n\n'
        f'Una vez más, gracias por tu participación y tu contribución a nuestra comunidad.\n\n'
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


def obtener_info_geolocalizacion(ip_address):
    try:
        # Llama a la API de ip-api.com con la dirección IP
        api_url = f"http://ip-api.com/json/{ip_address}"
        response = requests.get(api_url)

        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                return {"status": True, "message": "{}".format(data)}
            else:
                return {"status": False, "message": "Error en la respuesta de la API de geolocalización: {}".format(data.get('message', 'Sin mensaje de error disponible.'))}
        else:
            return {"status": False, "message": "Error al conectarse a la API de geolocalización. Código de estado HTTP: {}".format(response.status_code)}

    except requests.exceptions.RequestException as e:
        return {"status": False, "message": "Error al realizar la solicitud a la API de geolocalización: {}".format(str(e))}
    except Exception as e:
        return {"status": False, "message": "Error inesperado: {}".format(str(e))}


def obtener_info_geolocalizacion0(ip_address):
    try:
        # Llama a la API de ip-api.com con la dirección IP
        api_url = f"http://ip-api.com/json/{ip_address}"
        response = requests.get(api_url)
        

        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                return {"status": True, "message": "{}".format(data)}
            
            else:
                return {"status": False, "message": "No se pudo obtener información de geolocalización."}

        else:
            return {"status": False, "message": "No se pudo conectar a la API de geolocalización."}

    except Exception as e:
        return str(e)




def obtener_info_geolocalizacion1(ip):
    try:
        # Llamada a la API para obtener coordenadas
        response = requests.get(f"https://ipinfo.io/{ip}/json")
        info_geolocalizacion = response.json()
        print("ipinfo "*5)
        print(info_geolocalizacion)
        print("ipinfo "*5)
        return info_geolocalizacion
    except Exception as e:
        # Manejar cualquier error que pueda ocurrir
        print(f"Error al obtener información de geolocalización para la IP {ip}: {str(e)}")
        return None

def obtener_info_geolocalizacion2(ip):
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

import os
def createdPdf(path_template, data, path_css=""):
  
    name_template = path_template.split('/')[-1]
    path_template = path_template.replace(name_template,'')
    print(name_template)
    print(path_template)
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(path_template))
    template = env.get_template(name_template)
    html = template.render(data)
    print(html)
    
#createdPdf('../src/templates/coprobant.html', {"noComprobante":'00055'})



# funcion para sumar los votos de los candidatos



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


AJUASTA MENU EN NLOS PLANES DE GOBIERNO
"""


'''
def readVotes():

    # leer votos
    read_votes = Voto.query.all()
    edison = 0 #candidato 1
    juan_andres = 0 #candidato 2
    genaldo = 0 #candidato 3
    mikan = 0 #candidato 4
    blanca_lilia = 0 #candidato 5
    voto_blanco = 0 #candidato 6
    
    for vote in read_votes:
        with open('src/static/json/votes.txt', 'a') as f: 
            db_timestamp = vote.vote_timestamp    
            f.write(f"{vote.vote_id};{vote.user_id};{vote.candidate_id};{db_timestamp};{vote.ip_address};{vote.data_loc}\n")

        if vote.candidate_id == 1:
            edison += 1
        elif vote.candidate_id == 2:
            juan_andres += 1
        elif vote.candidate_id == 3:
            genaldo += 1
        elif vote.candidate_id == 4:
            mikan += 1
        elif vote.candidate_id == 5:
            blanca_lilia += 1
        elif vote.candidate_id == 6:
            voto_blanco += 1
        else:
            print("no se encontro candidato "*10)
    print(f"edison {edison} juan_andres {juan_andres} genaldo {genaldo} mikan {mikan} blanca_lilia {blanca_lilia} voto_blanco {voto_blanco}")
     
     #leer usuarios
    read_users = Usuario.query.all()
    total_user_registed = len(read_users)
    print(f"total_user_registed {total_user_registed}")
    for user in read_users:
        with open('src/static/json/users.txt', 'a') as f:            
            f.write(f"{user.user_id};{user.email};{user.has_voted};{user.token}\n")

           

'''