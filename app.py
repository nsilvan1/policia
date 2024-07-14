from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from bson.objectid import ObjectId
import datetime

app = Flask(__name__)
app.config.from_object(Config)

mongo = PyMongo(app)

# Função para criar banco de dados e coleções no primeiro acesso
def create_database():
    db = mongo.db
    collections = ['policial', 'curso', 'armamento', 'aviso']
    for collection in collections:
        if collection not in db.list_collection_names():
            db.create_collection(collection)

# Função para criar usuário administrador padrão
def create_admin_user():
    admin_user = mongo.db.policial.find_one({'username': 'admin'})
    if not admin_user:
        admin_user = {
            'passport': '000000000',
            'name': 'Admin',
            'cargo': 'Delegado Geral',
            'unidade': 'POLÍCIA CIVIL',
            'transgressao': '',
            'ultima_promocao': 'N/A',
            'username': 'admin',
            'password': generate_password_hash('admin123'),
            'active': True
        }
        mongo.db.policial.insert_one(admin_user)

# Chama as funções para criar o banco de dados e coleções, se não existirem, e o usuário admin
create_database()
create_admin_user()

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = mongo.db.policial.find_one({'username': username})
        
        if user:
            if check_password_hash(user['password'], password):
                if user['active']:
                    session['username'] = username
                    return redirect(url_for('dashboard'))
                else:
                    flash('Usuário inativo.', 'error')
            else:
                flash('Senha incorreta.', 'error')
        else:
            flash('Usuário não encontrado.', 'error')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        user = mongo.db.policial.find_one({'username': session['username']})
        if user:
            policiais = list(mongo.db.policial.find())
            avisos = list(mongo.db.aviso.find().sort('data', -1).limit(3))
            
            # Quantitativo por cargo
            cargos = [
                "Delegado Geral", "Delegado Geral Adjunto", "Delegado", "Delegado Adjunto",
                "Supervisor", "Investigador Chefe", "Investigador", "Escrivão",
                "Agente Classe Especial", "Agente 1ª Classe", "Agente 2ª Classe", "Agente 3ª Classe",
                "Estagiário", "Acadêmico (Acadepol)"
            ]
            quantitativo_cargo = {cargo: 0 for cargo in cargos}
            for policial in policiais:
                if policial['cargo'] in quantitativo_cargo:
                    quantitativo_cargo[policial['cargo']] += 1
            
            # Quantitativo por guarnição
            guarnicoes = [
                "DEIC", "GARRA", "SAT", "GARRA MOTOS", "G.E.R", "POLÍCIA CIVIL", "DIPOL", "G.O.E"
            ]
            quantitativo_guarnicao = {guarnicao: 0 for guarnicao in guarnicoes}
            for policial in policiais:
                if policial['unidade'] in quantitativo_guarnicao:
                    quantitativo_guarnicao[policial['unidade']] += 1

            total_policiais = mongo.db.policial.count_documents({})
            total_cursos = mongo.db.curso.count_documents({})
            total_armamentos = mongo.db.armamento.count_documents({})
            total_avisos = mongo.db.aviso.count_documents({})
            
            return render_template(
                'dashboard.html', user=user, policiais=policiais, avisos=avisos, 
                quantitativo_cargo=quantitativo_cargo, quantitativo_guarnicao=quantitativo_guarnicao,
                total_policiais=total_policiais, total_cursos=total_cursos,
                total_armamentos=total_armamentos, total_avisos=total_avisos
            )
    return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form.to_dict()
        if mongo.db.policial.find_one({'username': data['username']}):
            flash('Username already exists')
            return redirect(url_for('register'))
        data['password'] = generate_password_hash(data['password'])
        data['aprovado'] = False
        mongo.db.policial.insert_one(data)
        flash('Registration successful, waiting for approval.')
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/cadastro_policial', methods=['GET', 'POST'])
def cadastro_policial():
    if 'username' in session:
        user = mongo.db.policial.find_one({'username': session['username']})
        if user and user['cargo'] in ['Delegado Geral', 'Delegado Geral Adjunto']:
            if request.method == 'POST':
                data = request.form.to_dict()
                data['password'] = generate_password_hash(data['password'])
                data['aprovado'] = False
                mongo.db.policial.insert_one(data)
                flash('Policial cadastrado com sucesso, aguardando aprovação.')
                return redirect(url_for('dashboard'))
            return render_template('cadastro_policial.html')
    return redirect(url_for('login'))

@app.route('/aprovar_policial/<policial_id>')
def aprovar_policial(policial_id):
    if 'username' in session:
        user = mongo.db.policial.find_one({'username': session['username']})
        if user and user['cargo'] in ['Delegado Geral', 'Delegado Geral Adjunto']:
            mongo.db.policial.update_one({'_id': ObjectId(policial_id)}, {'$set': {'aprovado': True}})
            flash('Policial aprovado com sucesso.')
            return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/curso', methods=['GET', 'POST'])
def curso():
    if 'username' in session:
        user = mongo.db.policial.find_one({'username': session['username']})
        if request.method == 'POST':
            curso_data = request.form.to_dict()
            mongo.db.curso.insert_one(curso_data)
            flash('Curso cadastrado com sucesso.')
            return redirect(url_for('dashboard'))
        cursos = list(mongo.db.curso.find())
        return render_template('curso.html', user=user, cursos=cursos)
    return redirect(url_for('login'))

@app.route('/armamento', methods=['GET', 'POST'])
def armamento():
    if 'username' in session:
        user = mongo.db.policial.find_one({'username': session['username']})
        if user and user['cargo'] in ['Delegado Geral', 'Delegado Geral Adjunto', 'Supervisor']:
            if request.method == 'POST':
                armamento_data = request.form.to_dict()
                mongo.db.armamento.insert_one(armamento_data)
                flash('Armamento cadastrado com sucesso.')
                return redirect(url_for('dashboard'))
        armamentos = list(mongo.db.armamento.find())
        return render_template('armamento.html', user=user, armamentos=armamentos)
    return redirect(url_for('login'))

@app.route('/avisos', methods=['GET', 'POST'])
def avisos():
    if 'username' in session:
        user = mongo.db.policial.find_one({'username': session['username']})
        if user and user['cargo'] in ['Delegado Geral', 'Delegado Geral Adjunto', 'Instrutor']:
            if request.method == 'POST':
                aviso_data = request.form.to_dict()
                aviso_data['data'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                aviso_data['autor'] = f"{user['cargo']} - {user['name']}"
                mongo.db.aviso.insert_one(aviso_data)
                flash('Aviso publicado com sucesso.')
                return redirect(url_for('avisos'))
        
        page = int(request.args.get('page', 1))
        per_page = 3
        total_avisos = mongo.db.aviso.count_documents({})
        avisos = list(mongo.db.aviso.find().sort('data', -1).skip((page - 1) * per_page).limit(per_page))
        
        next_page = page + 1 if total_avisos > page * per_page else None
        prev_page = page - 1 if page > 1 else None

        return render_template('avisos.html', user=user, avisos=avisos, next_page=next_page, prev_page=prev_page)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)