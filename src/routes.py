from flask import render_template, request, jsonify,flash,Response,redirect, url_for, send_file
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
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, UserMixin, LoginManager, current_user
from sqlalchemy.orm import joinedload
import pandas as pd
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

app.data_comp = None

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

class Candidato(db.Model):
    __tablename__ = 'candidatos'
    candidate_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    party = db.Column(db.String(255), nullable=False)

class Testigos(UserMixin, db.Model):
    __tablename__ = 'testigos'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    candidate = db.Column(db.String(255), nullable=False)
    voting_tables = db.Column(db.String(255), nullable=False)
    
class Escrutinio(db.Model):
    __tablename__ = 'escrutinio'
    id = db.Column(db.Integer, primary_key=True)
    lugar = db.Column(db.String(255), nullable=False)
    mesa = db.Column(db.Integer, nullable=False)
    id_testigo = db.Column(db.Integer, db.ForeignKey('testigos.id'), nullable=False) 
    edison = db.Column(db.Integer, nullable=True)
    juan = db.Column(db.Integer, nullable=True)
    genaldo = db.Column(db.Integer, nullable=True)
    mikan = db.Column(db.Integer, nullable=True)
    blanca = db.Column(db.Integer, nullable=True)
    voto_blanco = db.Column(db.Integer, nullable=True)
    nulo = db.Column(db.Integer, nullable=True)
    testigo =db.relationship('Testigos', backref=db.backref('escrutinio', lazy=True))

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


#*************************  LOGIN  ********************/
@login_manager.user_loader
def load_user(user_id):
    try:
        testigo = Testigos.query.get(int(user_id))
        if testigo is not None:
            print('='*50) 
            print(f'===   {testigo.email}  ===')
            print('='*50) 
            return testigo
    except Exception as e:
        # Manejar la excepción de la manera que desees (p. ej., registrarla)
        print(f"Error al cargar el usuario: {str(e)}")

    # Devolver un valor predeterminado o None en caso de error
    return None

    
    
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
    

@app.route('/ads.txt')
def serve_ads_txt():
    return send_file('ads.txt')

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/loginPost', methods=['POST'])
def loginPost():

    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    print(f'loginPost: {email}, {password}, {remember}')
    
    testigo = Testigos.query.filter_by(email=email).first()
    print(f'existe:{ testigo}')    
    
        
    if not testigo:       
        flash('Por favor verifique su correo de inicio de sesión.')
        return redirect(url_for('login'))
    else:
        if not testigo.password == password:
            flash('Por favor verifique sus datos de inicio de sesión.')             
            return redirect(url_for('login'))
        else:
            login_user(testigo, remember=remember)
            return redirect(url_for('registerVote'))
            return redirect(url_for('appPage.home'))
        
#/*************************  CERRAR SESION  ********************/
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
        
        

@app.route('/save_row', methods=['POST'])
@login_required
def saveRow():
    data = request.get_json()
    print(f'data: {data}')
    #data: {'mesaId': 1, 'edison': '5', 'juan': '6', 'genaldo': '4', 'mikan': '5', 'blanca': '8', 'voto_blanco': '3', 'nulos': '5'}
    
    id = data['mesaId']
    edison = data['edison']
    juan = data['juan']
    genaldo = data['genaldo']
    mikan = data['mikan']
    blanca = data['blanca']
    voto_blanco = data['voto_blanco']
    nulo = data['nulos']
    # si alguno es vacio, se pone en null
    if edison == '':
        edison = None
    if juan == '':
        juan = None
    if genaldo == '':
        genaldo = None
    if mikan == '':
        mikan = None
    if blanca == '':
        blanca = None
    if voto_blanco == '':
        voto_blanco = None
    if nulo == '':
        nulo = None
        
    
    escrutinio = Escrutinio.query.filter_by(id=id).first()
    escrutinio.edison = edison
    escrutinio.juan = juan
    escrutinio.genaldo = genaldo
    escrutinio.mikan = mikan
    escrutinio.blanca = blanca
    escrutinio.voto_blanco = voto_blanco
    escrutinio.nulo = nulo
    db.session.commit()
    return jsonify({'success':True})
    

        
@app.route('/check_change_votes')
@login_required
def checkChangeVotes():
    data = Escrutinio.query.options(joinedload(Escrutinio.testigo)).all()
    data = sorted(data, key=lambda x: x.id) 
    data_act=[]
    for mesa in data:        
        testigo = mesa.testigo
        campana = testigo.candidate
        total = sum(filter(None, [mesa.edison, mesa.juan, mesa.genaldo, mesa.mikan, mesa.blanca, mesa.voto_blanco, mesa.nulo]))
        row = {'lugar':mesa.lugar, 'numero': mesa.mesa, 'campana': campana, 'edison': mesa.edison, 'juan': mesa.juan, 'genaldo': mesa.genaldo, 'mikan': mesa.mikan, 'blanca': mesa.blanca, 'voto_blanco': mesa.voto_blanco, 'nulos': mesa.nulo, 'total': total}
        data_act.append(row)        

    
    if data_act == app.data_comp:
        return jsonify({'success':False})
    else:
        return jsonify({'success':True})
    
        
@app.route('/register_vote')
@login_required
def registerVote():
    #Parte1
    time_1 = datetime.now()
    data = Escrutinio.query.options(joinedload(Escrutinio.testigo)).all()   
    data = sorted(data, key=lambda x: x.id)
    
    
    lugares=[
        'coliseo',
        'campo_alegre',
        'mega_colegio',
    ]
    mesas_edit = []
    mesas_view_coliseo=[]
    mesas_view_campo_alegre=[]
    mesas_view_mega_colegio=[]
    mesas_view_rodeo=[]
    
    #Parte2
    time_2 = datetime.now()
    current_email= current_user.email
    table_register = False
    app.data_comp=[]
    for mesa in data:        
        testigo = mesa.testigo
        email = testigo.email
        campana = testigo.candidate
        if email == current_email:
            table_register = True
            mesas_edit.append({'id':mesa.id,'numero': mesa.mesa, 'email': email, 'edison': mesa.edison, 'juan': mesa.juan, 'genaldo': mesa.genaldo, 'mikan': mesa.mikan, 'blanca': mesa.blanca, 'voto_blanco': mesa.voto_blanco, 'nulos': mesa.nulo})
        
        total = sum(filter(None, [mesa.edison, mesa.juan, mesa.genaldo, mesa.mikan, mesa.blanca, mesa.voto_blanco, mesa.nulo]))
        row = {'lugar':mesa.lugar, 'numero': mesa.mesa, 'campana': campana, 'edison': mesa.edison, 'juan': mesa.juan, 'genaldo': mesa.genaldo, 'mikan': mesa.mikan, 'blanca': mesa.blanca, 'voto_blanco': mesa.voto_blanco, 'nulos': mesa.nulo, 'total': total}
        app.data_comp.append(row)
        if mesa.lugar == 'coliseo':
            mesas_view_coliseo.append(row)
        elif mesa.lugar == 'campo_alegre':
            mesas_view_campo_alegre.append(row)
        elif mesa.lugar == 'mega_colegio':
            mesas_view_mega_colegio.append(row)
        elif mesa.lugar == 'rodeo':
            mesas_view_rodeo.append(row)
    
        time_3 = datetime.now()

    
    # COLISEO
    df = pd.DataFrame(mesas_view_coliseo)    
    df = df.groupby(['lugar', 'numero', 'campana']).sum().reset_index()
    df_edison = df[df['campana']=='edison']
    df_edison_sum = df_edison.sum(axis = 0, skipna = True)
    df_blanca = df[df['campana']=='blanca']
    df_blanca_sum = df_blanca.sum(axis = 0, skipna = True)
    df_mikan = df[df['campana']=='mikan']
    df_mikan_sum = df_mikan.sum(axis = 0, skipna = True)
    df_genaldo = df[df['campana']=='genaldo']
    df_genaldo_sum = df_genaldo.sum(axis = 0, skipna = True)
    mesas_view_coliseo_suma = [
        {'lugar': 'coliseo', 'numero': 'Total', 'campana': 'edison', 'edison': df_edison_sum['edison'], 'juan':df_edison_sum['juan'], 'genaldo':df_edison_sum['genaldo'], 'mikan':df_edison_sum['mikan'], 'blanca':df_edison_sum['blanca'], 'voto_blanco':df_edison_sum['voto_blanco'], 'nulos':df_edison_sum['nulos'], 'total':df_edison_sum['total']},
        {'lugar': 'coliseo', 'numero': 'Total', 'campana': 'blanca', 'edison': df_blanca_sum['edison'], 'juan':df_blanca_sum['juan'], 'genaldo':df_blanca_sum['genaldo'], 'mikan':df_blanca_sum['mikan'], 'blanca':df_blanca_sum['blanca'], 'voto_blanco':df_blanca_sum['voto_blanco'], 'nulos':df_blanca_sum['nulos'], 'total':df_blanca_sum['total']},
        {'lugar': 'coliseo', 'numero': 'Total', 'campana': 'mikan', 'edison': df_mikan_sum['edison'], 'juan':df_mikan_sum['juan'], 'genaldo':df_mikan_sum['genaldo'], 'mikan':df_mikan_sum['mikan'], 'blanca':df_mikan_sum['blanca'], 'voto_blanco':df_mikan_sum['voto_blanco'], 'nulos':df_mikan_sum['nulos'], 'total':df_mikan_sum['total']},
        {'lugar': 'coliseo', 'numero': 'Total', 'campana': 'genaldo', 'edison': df_genaldo_sum['edison'], 'juan':df_genaldo_sum['juan'], 'genaldo':df_genaldo_sum['genaldo'], 'mikan':df_genaldo_sum['mikan'], 'blanca':df_genaldo_sum['blanca'], 'voto_blanco':df_genaldo_sum['voto_blanco'], 'nulos':df_genaldo_sum['nulos'], 'total':df_genaldo_sum['total']}
    ]
    
    # CAMPO ALEGRE
    df = pd.DataFrame(mesas_view_campo_alegre)
    df = df.groupby(['lugar', 'numero', 'campana']).sum().reset_index()
    df_edison = df[df['campana']=='edison']
    df_edison_sum = df_edison.sum(axis = 0, skipna = True)
    df_blanca = df[df['campana']=='blanca']
    df_blanca_sum = df_blanca.sum(axis = 0, skipna = True)
    df_mikan = df[df['campana']=='mikan']
    df_mikan_sum = df_mikan.sum(axis = 0, skipna = True)
    df_genaldo = df[df['campana']=='genaldo']
    df_genaldo_sum = df_genaldo.sum(axis = 0, skipna = True)
    mesas_view_campo_alegre_suma = [
        {'lugar': 'campo_alegre', 'numero': 'Total', 'campana': 'edison', 'edison': df_edison_sum['edison'], 'juan':df_edison_sum['juan'], 'genaldo':df_edison_sum['genaldo'], 'mikan':df_edison_sum['mikan'], 'blanca':df_edison_sum['blanca'], 'voto_blanco':df_edison_sum['voto_blanco'], 'nulos':df_edison_sum['nulos'], 'total':df_edison_sum['total']},
        {'lugar': 'campo_alegre', 'numero': 'Total', 'campana': 'blanca', 'edison': df_blanca_sum['edison'], 'juan':df_blanca_sum['juan'], 'genaldo':df_blanca_sum['genaldo'], 'mikan':df_blanca_sum['mikan'], 'blanca':df_blanca_sum['blanca'], 'voto_blanco':df_blanca_sum['voto_blanco'], 'nulos':df_blanca_sum['nulos'], 'total':df_blanca_sum['total']},
        {'lugar': 'campo_alegre', 'numero': 'Total', 'campana': 'mikan', 'edison': df_mikan_sum['edison'], 'juan':df_mikan_sum['juan'], 'genaldo':df_mikan_sum['genaldo'], 'mikan':df_mikan_sum['mikan'], 'blanca':df_mikan_sum['blanca'], 'voto_blanco':df_mikan_sum['voto_blanco'], 'nulos':df_mikan_sum['nulos'], 'total':df_mikan_sum['total']},
        {'lugar': 'campo_alegre', 'numero': 'Total', 'campana': 'genaldo', 'edison': df_genaldo_sum['edison'], 'juan':df_genaldo_sum['juan'], 'genaldo':df_genaldo_sum['genaldo'], 'mikan':df_genaldo_sum['mikan'], 'blanca':df_genaldo_sum['blanca'], 'voto_blanco':df_genaldo_sum['voto_blanco'], 'nulos':df_genaldo_sum['nulos'], 'total':df_genaldo_sum['total']}
    ]
    
    # MEGA COLEGIO
    df = pd.DataFrame(mesas_view_mega_colegio)
    df = df.groupby(['lugar', 'numero', 'campana']).sum().reset_index()
    df_edison = df[df['campana']=='edison']
    df_edison_sum = df_edison.sum(axis = 0, skipna = True)
    df_blanca = df[df['campana']=='blanca']
    df_blanca_sum = df_blanca.sum(axis = 0, skipna = True)
    df_mikan = df[df['campana']=='mikan']
    df_mikan_sum = df_mikan.sum(axis = 0, skipna = True)
    df_genaldo = df[df['campana']=='genaldo']
    df_genaldo_sum = df_genaldo.sum(axis = 0, skipna = True)
    mesas_view_mega_colegio_suma = [
        {'lugar': 'mega_colegio', 'numero': 'Total', 'campana': 'edison', 'edison': df_edison_sum['edison'], 'juan':df_edison_sum['juan'], 'genaldo':df_edison_sum['genaldo'], 'mikan':df_edison_sum['mikan'], 'blanca':df_edison_sum['blanca'], 'voto_blanco':df_edison_sum['voto_blanco'], 'nulos':df_edison_sum['nulos'], 'total':df_edison_sum['total']},
        {'lugar': 'mega_colegio', 'numero': 'Total', 'campana': 'blanca', 'edison': df_blanca_sum['edison'], 'juan':df_blanca_sum['juan'], 'genaldo':df_blanca_sum['genaldo'], 'mikan':df_blanca_sum['mikan'], 'blanca':df_blanca_sum['blanca'], 'voto_blanco':df_blanca_sum['voto_blanco'], 'nulos':df_blanca_sum['nulos'], 'total':df_blanca_sum['total']},
        {'lugar': 'mega_colegio', 'numero': 'Total', 'campana': 'mikan', 'edison': df_mikan_sum['edison'], 'juan':df_mikan_sum['juan'], 'genaldo':df_mikan_sum['genaldo'], 'mikan':df_mikan_sum['mikan'], 'blanca':df_mikan_sum['blanca'], 'voto_blanco':df_mikan_sum['voto_blanco'], 'nulos':df_mikan_sum['nulos'], 'total':df_mikan_sum['total']},
        {'lugar': 'mega_colegio', 'numero': 'Total', 'campana': 'genaldo', 'edison': df_genaldo_sum['edison'], 'juan':df_genaldo_sum['juan'], 'genaldo':df_genaldo_sum['genaldo'], 'mikan':df_genaldo_sum['mikan'], 'blanca':df_genaldo_sum['blanca'], 'voto_blanco':df_genaldo_sum['voto_blanco'], 'nulos':df_genaldo_sum['nulos'], 'total':df_genaldo_sum['total']}
    ]
    
    # RODEO
    df = pd.DataFrame(mesas_view_rodeo)
    df = df.groupby(['lugar', 'numero', 'campana']).sum().reset_index()
    df_edison = df[df['campana']=='edison']
    df_edison_sum = df_edison.sum(axis = 0, skipna = True)
    df_blanca = df[df['campana']=='blanca']
    df_blanca_sum = df_blanca.sum(axis = 0, skipna = True)
    df_mikan = df[df['campana']=='mikan']
    df_mikan_sum = df_mikan.sum(axis = 0, skipna = True)
    df_genaldo = df[df['campana']=='genaldo']
    df_genaldo_sum = df_genaldo.sum(axis = 0, skipna = True)
    mesas_view_rodeo_suma = [
        {'lugar': 'rodeo', 'numero': 'Total', 'campana': 'edison', 'edison': df_edison_sum['edison'], 'juan':df_edison_sum['juan'], 'genaldo':df_edison_sum['genaldo'], 'mikan':df_edison_sum['mikan'], 'blanca':df_edison_sum['blanca'], 'voto_blanco':df_edison_sum['voto_blanco'], 'nulos':df_edison_sum['nulos'], 'total':df_edison_sum['total']},
        {'lugar': 'rodeo', 'numero': 'Total', 'campana': 'blanca', 'edison': df_blanca_sum['edison'], 'juan':df_blanca_sum['juan'], 'genaldo':df_blanca_sum['genaldo'], 'mikan':df_blanca_sum['mikan'], 'blanca':df_blanca_sum['blanca'], 'voto_blanco':df_blanca_sum['voto_blanco'], 'nulos':df_blanca_sum['nulos'], 'total':df_blanca_sum['total']},
        {'lugar': 'rodeo', 'numero': 'Total', 'campana': 'mikan', 'edison': df_mikan_sum['edison'], 'juan':df_mikan_sum['juan'], 'genaldo':df_mikan_sum['genaldo'], 'mikan':df_mikan_sum['mikan'], 'blanca':df_mikan_sum['blanca'], 'voto_blanco':df_mikan_sum['voto_blanco'], 'nulos':df_mikan_sum['nulos'], 'total':df_mikan_sum['total']},
        {'lugar': 'rodeo', 'numero': 'Total', 'campana': 'genaldo', 'edison': df_genaldo_sum['edison'], 'juan':df_genaldo_sum['juan'], 'genaldo':df_genaldo_sum['genaldo'], 'mikan':df_genaldo_sum['mikan'], 'blanca':df_genaldo_sum['blanca'], 'voto_blanco':df_genaldo_sum['voto_blanco'], 'nulos':df_genaldo_sum['nulos'], 'total':df_genaldo_sum['total']}
    ]

    
    # CONSOLIDADO
    mesas_view_all = mesas_view_coliseo + mesas_view_campo_alegre + mesas_view_mega_colegio + mesas_view_rodeo
    df = pd.DataFrame(mesas_view_all)
    df = df.groupby(['lugar', 'numero', 'campana']).sum().reset_index()
    df_edison = df[df['campana']=='edison']
    df_edison_sum = df_edison.sum(axis = 0, skipna = True)
    df_blanca = df[df['campana']=='blanca']
    df_blanca_sum = df_blanca.sum(axis = 0, skipna = True)
    df_mikan = df[df['campana']=='mikan']
    df_mikan_sum = df_mikan.sum(axis = 0, skipna = True)
    df_genaldo = df[df['campana']=='genaldo']
    df_genaldo_sum = df_genaldo.sum(axis = 0, skipna = True)
    mesas_view_consolidado = [
        {'lugar': 'consolidado', 'numero': 'Total', 'campana': 'edison', 'edison': df_edison_sum['edison'], 'juan':df_edison_sum['juan'], 'genaldo':df_edison_sum['genaldo'], 'mikan':df_edison_sum['mikan'], 'blanca':df_edison_sum['blanca'], 'voto_blanco':df_edison_sum['voto_blanco'], 'nulos':df_edison_sum['nulos'], 'total':df_edison_sum['total']},
        {'lugar': 'consolidado', 'numero': 'Total', 'campana': 'blanca', 'edison': df_blanca_sum['edison'], 'juan':df_blanca_sum['juan'], 'genaldo':df_blanca_sum['genaldo'], 'mikan':df_blanca_sum['mikan'], 'blanca':df_blanca_sum['blanca'], 'voto_blanco':df_blanca_sum['voto_blanco'], 'nulos':df_blanca_sum['nulos'], 'total':df_blanca_sum['total']},
        {'lugar': 'consolidado', 'numero': 'Total', 'campana': 'mikan', 'edison': df_mikan_sum['edison'], 'juan':df_mikan_sum['juan'], 'genaldo':df_mikan_sum['genaldo'], 'mikan':df_mikan_sum['mikan'], 'blanca':df_mikan_sum['blanca'], 'voto_blanco':df_mikan_sum['voto_blanco'], 'nulos':df_mikan_sum['nulos'], 'total':df_mikan_sum['total']},
        {'lugar': 'consolidado', 'numero': 'Total', 'campana': 'genaldo', 'edison': df_genaldo_sum['edison'], 'juan':df_genaldo_sum['juan'], 'genaldo':df_genaldo_sum['genaldo'], 'mikan':df_genaldo_sum['mikan'], 'blanca':df_genaldo_sum['blanca'], 'voto_blanco':df_genaldo_sum['voto_blanco'], 'nulos':df_genaldo_sum['nulos'], 'total':df_genaldo_sum['total']}
    ]
    
    

    time_4 = datetime.now()
    
    print(f'time_2: {time_2-time_1}')
    print(f'time_3: {time_3-time_2}')
    print(f'time_4: {time_4-time_3}')
    
    return render_template("register_vote.html",
                    current_user = current_user.email,
                    mesas_edit=mesas_edit, 
                    
                    mesas_view_coliseo=mesas_view_coliseo,
                    mesas_view_campo_alegre=mesas_view_campo_alegre,
                    mesas_view_mega_colegio=mesas_view_mega_colegio,
                    mesas_view_rodeo=mesas_view_rodeo,
                    
                    mesas_view_coliseo_suma=mesas_view_coliseo_suma,
                    mesas_view_campo_alegre_suma=mesas_view_campo_alegre_suma,
                    mesas_view_mega_colegio_suma=mesas_view_mega_colegio_suma,
                    mesas_view_rodeo_suma=mesas_view_rodeo_suma,
                    
                    mesas_view_consolidado=mesas_view_consolidado,
                    
                    table_register = table_register)





def inscribir_testigos():
    testigos=[
        {'email': 'micandidato.org@gmail.com', 'password': '123', 'candidate': 'edison', 'voting_tables': 'ADMINISTRADOR'},
        {'email': 'edison@gmail.com','password': '123', 'candidate': 'edison', 'voting_tables': 'CANDIDATO'},
        {'email': 'edison_1@gmail.com','password': '123', 'candidate': 'edison', 'voting_tables': '1, 2, 3'},
        {'email': 'edison_2@gmail.com', 'password': '123', 'candidate': 'edison', 'voting_tables': '4, 5, 6'},
        {'email': 'edison_3@gmail.com', 'password': '123', 'candidate': 'edison', 'voting_tables': '7, 8, 9'},
        {'email': 'edison_4@gmail.com', 'password': '123', 'candidate': 'edison', 'voting_tables': '10, 11, 12'},
        {'email': 'edison_5@gmail.com', 'password': '123', 'candidate': 'edison', 'voting_tables': '13, 14, 15'},
        {'email': 'edison_6@gmail.com', 'password': '123', 'candidate': 'edison', 'voting_tables': '16, 17, 18'},
        {'email': 'edison_7@gmail.com', 'password': '123', 'candidate': 'edison', 'voting_tables': '19, 20, 21'},
        {'email': 'edison_8@gmail.com', 'password': '123', 'candidate': 'edison', 'voting_tables': '22, 23, 24'},
        {'email': 'edison_9@gmail.com', 'password': '123', 'candidate': 'edison', 'voting_tables': '25, 26, 27'},
        {'email': 'edison_10@gmail.com', 'password': '123', 'candidate': 'edison', 'voting_tables': '28, 29, 30'},
        {'email': 'edison_11@gmail.com', 'password': '123', 'candidate': 'edison', 'voting_tables': '31, 32, 33'},
        {'email': 'edison_12@gmail.com', 'password': '123', 'candidate': 'edison', 'voting_tables': '34, 35, 36'},
        {'email': 'edison_13@gmail.com', 'password': '123', 'candidate': 'edison', 'voting_tables': '37, 38, 39'},
        {'email': 'edison_14@gmail.com', 'password': '123', 'candidate': 'edison', 'voting_tables': '40, 41, 42'},
        {'email': 'edison_15@gmail.com', 'password': '123', 'candidate': 'edison', 'voting_tables': '43, 44, 45'},    
        {'email': 'edison_16@gmail.com', 'password': '123', 'candidate': 'edison', 'voting_tables': '46'}    
    ]
    
    for testigo in testigos:
        new_testigo = Testigos(email=testigo['email'], password=testigo['password'], candidate=testigo['candidate'], voting_tables=testigo['voting_tables'])
        db.session.add(new_testigo)
        db.session.commit()
     
def inscribir_mesas():
    '''
    Coliseo              mesa 1 a la 30
    campo alegre        mesa 1 y 2
    mega colegio        mesa 1 a la 27
    rodeo              mesa 1 
    '''
    lugares = [['coliseo',30],
                ['campo_alegre',2],
                ['mega_colegio',27],
                ['rodeo',1]]
    
    Candidatos = ['edison',
                'blanca',
                'mikan',
                'genaldo'
                ]
        

    for lugar in lugares:
        print(f'lugar: {lugar[0]}')
        for mesa in range(1,lugar[1]+1):            
            for candidato in Candidatos:
                email_testigo = f'{candidato}_{lugar[0]}@gmail.com'
                testigo = Testigos.query.filter_by(email=email_testigo).first()
                new_mesa = Escrutinio(lugar=lugar[0], mesa=mesa, id_testigo=testigo.id)
                db.session.add(new_mesa)
                db.session.commit()
                print(f'mesa: {mesa}, candidato: {candidato} email_testigo: {email_testigo}')
    
    return
    for mesa in mesas:
        # ejemplo existing_user = Usuario.query.filter_by(token=token, has_voted=False).first()
        testigo = Testigos.query.filter_by(email=mesa['email_testigo']).first()
        if testigo:
            new_mesa = Escrutinio(mesa=mesa['mesa'], id_testigo=testigo.id)
            db.session.add(new_mesa)
            db.session.commit()
     

     

@app.route("/results")
def results(): 
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
        vote_for_candidate = Voto.query.filter_by(user_id=existing_user.user_id).first().candidate_id
        candidate_name = Candidato.query.filter_by(candidate_id=vote_for_candidate).first().name
        candidate_name = candidate_name.title()
        return render_template('coprobant.html', user_id=existing_user.user_id, candidate_name=candidate_name, votefor=vote_for_candidate)   
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
'''
def readVotes():

    # leer votos
    read_votes = Voto.query.all()
    # ordenar por id
    read_votes.sort(key=lambda x: x.vote_id, reverse=False) 
    edison = 0 #candidato 1
    juan_andres = 0 #candidato 2
    genaldo = 0 #candidato 3
    mikan = 0 #candidato 4
    blanca_lilia = 0 #candidato 5
    voto_blanco = 0 #candidato 6
    
    for vote in read_votes:
        with open('src/static/json/votes.txt', 'a') as f: 
            db_timestamp = vote.vote_timestamp    
            ''' ejemplo ote.data_loc
            {'status': 'success', 'country': 'Colombia', 'countryCode': 'CO', 'region': 'DC', 'regionName': 'Bogota D.C.', 'city': 'Bogot\u00e1', 'zip': '111411', 'lat': 4.6115, 'lon': -74.0833, 'timezone': 'America/Bogota', 'isp': 'Level 3 Colombia S.A', 'org': 'M@STV PRODUCCIONES', 'as': 'AS3549 Level 3 Parent, LLC', 'query': '190.217.106.4'}
            {'status': 'success', 'country': 'Peru', 'countryCode': 'PE', 'region': 'LMA', 'regionName': 'Lima', 'city': 'Lima', 'zip': '', 'lat': -12.0432, 'lon': -77.0282, 'timezone': 'America/Lima', 'isp': 'Telefonica del Peru S.A.A.', 'org': 'Telefonica del Peru S.A.A', 'as': 'AS6147 Telefonica del Peru S.A.A.', 'query': '181.66.164.173'}
            {'status': 'success', 'country': 'Colombia', 'countryCode': 'CO', 'region': 'DC', 'regionName': 'Bogota D.C.', 'city': 'Bogot\u00e1', 'zip': '111411', 'lat': 4.6115, 'lon': -74.0833, 'timezone': 'America/Bogota', 'isp': 'Level 3 Colombia S.A', 'org': 'M@STV PRODUCCIONES', 'as': 'AS3549 Level 3 Parent, LLC', 'query': '190.217.106.4'}
            
            
            {'status': 'success',
            'country': 'Colombia',
            'countryCode': 'CO',
            'region': 'DC',
            'regionName': 'Bogota D.C.',
            'city': 'Bogot\u00e1',
            'zip': '110111',
            'lat': 4.6913,
            'lon': -74.032,
            'timezone': 'America/Bogota',
            'isp': 'Comcel S.A.',
            'org': 'COMUNICACI\u00d3N CELULAR S.A. COMCEL S.A',
            'as': 'AS26611 COMUNICACI\u00d3N CELULAR S.A. COMCEL S.A.',
            'query': '191.156.57.63'}
            
            
            json_data_loc = json.loads(vote.data_loc)
            print(type(json_data_loc))
            country = json_data_loc['country']
            countryCode = json_data_loc['countryCode']
            region = json_data_loc['region']
            regionName = json_data_loc['regionName']
            city = json_data_loc['city']
            zip_code = json_data_loc['zip']
            lat = json_data_loc['lat']
            lon = json_data_loc['lon']
            timezone = json_data_loc['timezone']
            isp = json_data_loc['isp']
            org = json_data_loc['org']
            as_ = json_data_loc['as']
            query = json_data_loc['query']
            f.write(f"{vote.vote_id};  {vote.user_id}; {vote.candidate_id};{db_timestamp};{vote.ip_address}; {country}; {countryCode}; {region};{regionName};{city};{zip_code}; {lat};{lon}; {timezone};{isp};{org};{as_};{query}\n")
            '''

                
            
            f.write(f"{vote.vote_id};  {vote.user_id}; {vote.candidate_id};{db_timestamp};{vote.ip_address};{vote.data_loc}\n")





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
     
    #leer usuarios y ordenarlos por id
    read_users = Usuario.query.all()
    # ordenar por id
    read_users.sort(key=lambda x: x.user_id, reverse=False)
    
     
    #read_users = Usuario.query.all()
    total_user_registed = len(read_users)
    print(f"total_user_registed {total_user_registed}")
    for user in read_users:
        with open('src/static/json/users.txt', 'a') as f:      
            #dividir con @ el email user.email
            email_extract = user.email.split('@')[1]   
            f.write(f"{user.user_id};{user.email};{user.has_voted};{user.token};{email_extract}\n")
