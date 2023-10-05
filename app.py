import os
from platform import system
from flask import *
from models import db
from models import Usuario
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




@app.route('/', methods=["POST", "GET"])
def index():
    global sucesso_cadastro
    if request.method == "GET":
        sucesso = sucesso_cadastro
        sucesso_cadastro = False
        return render_template("index.html", sucesso_cadastro=sucesso)
    else:
        #consulta no banco o usuario
        user = Usuario.query.filter_by(usuario="usuario vindo do formulario").first()
        if user == None:
            return "usuario nao cadastrado"
        else:
            if check_password_hash("senha do banco de dados", "senha do formulario"):
                return "senha correta"
            else:
                return "senha incorreta"



@app.route('/cadastrar', methods=["POST", "GET"])
def cadastrar():
    global sucesso_cadastro
    if request.method == "GET":
        sucesso_cadastro = False
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
        sucesso_cadastro = True
        return redirect(url_for("index"))



@app.route("/listar/usuarios")
def listar_usuarios():
    users = Usuario.query.all()
    return render_template(
        "listar_usuarios.html",
        usuarios=users
    )

@app.route("/existe/<usuario>")
def existe(usuario):
    user = Usuario.query.filter_by(usuario=usuario).first()
    return jsonify({"existe": bool(user)})


with app.app_context():
    db.create_all()