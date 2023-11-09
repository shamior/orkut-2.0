import os
from platform import system
from flask import *
from models import db
from models import Usuario, Post
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash

sucesso_cadastro = False

#A URI tem diferenca do linux para o windows
#Como estou usando linux e vocês windows
#então resolvi colocar esse if para compatibilidade
if system() == "Windows":
    sqlite_prefixo = "sqlite:///"
else:
    sqlite_prefixo = "sqlite:////"

pasta_atual = os.path.abspath(os.path.dirname(__file__))
uri_db = sqlite_prefixo + pasta_atual + '/database/banco.sqlite'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sgrdo'
app.config['SQLALCHEMY_DATABASE_URI'] = uri_db
db.init_app(app)



def login_required(funcao):
    @wraps(funcao)
    def inner(*args, **kwargs):
        if 'logado' in session:
            return funcao(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return inner






@app.route("/", methods=['GET', 'POST'])
def index():
    if not 'logado' in session:
        return render_template("index.html")
    

    user = session['logado']
    if request.method == 'POST':
        new_post = Post(
            conteudo=request.form['post'],
            para=session['logado']['usuario'],
            de=session['logado']['usuario']
        )
        db.session.add(new_post)
        db.session.commit()
        print(request.form['post'])
        return redirect(url_for('index'))
    
    posts = \
    Post.query.filter_by(
        de=user['usuario'],
        para=user['usuario']
    ).order_by(
        Post.criado_em.desc(),
    ).all()
    return render_template('welcome.html', user=user, posts=posts)


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "GET":
        if 'logado' in session:
            return redirect(url_for('index'))
        sucesso = False
        if 'sucesso_cadastro' in session:
            sucesso = session['sucesso_cadastro']
        session['sucesso_cadastro'] = False
        return render_template("login.html", sucesso_cadastro=sucesso)
    else:
        #consulta no banco o usuario
        user = Usuario.query.filter_by(usuario=request.form['usuario']).first()
        if user == None:
            return "usuario nao cadastrado"
        else:
            if check_password_hash(user.senha, request.form['senha']):
                session['logado'] = {
                    "nome": user.nome,
                    "usuario": user.usuario,
                    "sobrenome": user.sobrenome
                }
                return redirect(url_for('index'))
            else:
                return "senha incorreta"



@app.route('/cadastrar', methods=["POST", "GET"])
def cadastrar():
    if request.method == "GET":
        session['sucesso_cadastro'] = False
        return render_template("cadastrar.html")
    else:
        dados = request.form
        senha_hash = generate_password_hash(dados['senha'])
        user = Usuario(
            usuario=dados['usuario'],
            nome=dados['nome'],
            sobrenome=dados['sobrenome'],
            senha=senha_hash
        )
        db.session.add(user)
        db.session.commit()
        session['sucesso_cadastro'] = True
        return redirect(url_for("login"))


@app.route("/listar/usuarios")
@login_required
def listar_usuarios():
    users = Usuario.query.all()
    return render_template(
        "usuarios.html",
        usuarios=users
    )

@app.route("/logout")
@login_required
def logout():
    del session['logado']
    return redirect(url_for('login'))


@app.route("/posts/<id>", methods=['GET', 'DELETE'])
@login_required
def posts(id):
    query = Post.query.filter_by(id=id)
    if request.method == 'GET':
        post = query.first()
        if post:
            return f"<h1>{post.de}</h1><pre>{post.conteudo}</pre>"
        return 'post nao encontrado'
    
    deletions = query.delete()
    db.session.commit()
    return jsonify({"deletions": deletions})

@app.route("/existe/<user>")
def existe(user):
    user = Usuario.query.filter_by(usuario=user).first()
    return jsonify({"existe": bool(user)})


with app.app_context():
    db.create_all()