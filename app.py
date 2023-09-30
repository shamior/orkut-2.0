import os
from platform import system
from flask import *
from models import db
from models import Usuario



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
    if request.method == "GET":
        sucesso = False
        if 'sucesso_cadastro' in session:
            sucesso = session['sucesso_cadastro']
        return render_template("index.html", sucesso_cadastro=sucesso)
    else:
        return ""



@app.route('/cadastrar', methods=["POST", "GET"])
def cadastrar():
    if request.method == "GET":
        session['sucesso_cadastro'] = False
        return render_template("cadastrar.html")
    else:
        session['sucesso_cadastro'] = True
        return redirect(url_for("index"))


with app.app_context():
    db.create_all()