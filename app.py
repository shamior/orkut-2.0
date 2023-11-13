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


# funcao que serve como uma magica para nos
# basta colocar @login_required em cima das funções
# que você queira que o usuário esteja logado
# essa funcao verifica se o usuario esta logado
# se ele estiver, ela deixa ele passar
# se não estiver, ele redireciona para a pagina de login
def login_required(funcao):
    @wraps(funcao)
    def inner(*args, **kwargs):
        if 'logado' in session:
            return funcao(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return inner





#rota padrão
#se o usuario nao estiver logado, renderiza o /templates/auth/index.html
#se estiver logado, renderiza a rota que é definida pela funçao posts
#nesse caso vai ser a rota /posts
@app.route("/")
def index():
    if not 'logado' in session:
        return render_template("auth/index.html")
    return redirect(url_for('posts'))


#rota /postar
@app.route('/postar', methods=['GET', 'POST'])
# é necessário estar logado
@login_required
def postar():
    #Agora se o metodo for post então quer dizer que o usuário usou o
    #formulário para escrever um post
    if request.method == 'POST':
        #nesse caso, criamos um post, cuja o conteudo é o conteudo vindo do formulario
        #como o usuário está postando em seu proprio mural, podemos dizer que ele está mandando
        #o post dele para ele mesmo
        #então os campos 'para' e 'de' desse novo post equivalem ao nome de usuario de quem está logado
        new_post = Post(
            conteudo=request.form['post'],
            para=session['logado']['usuario'],
            de=session['logado']['usuario']
        )
        #adiciona o post na sessão
        db.session.add(new_post)
        #e finalmente adiciona no banco de dados
        db.session.commit()
        #no final redireciona ele para a pagina de posts
        return redirect(url_for('posts'))
    else:
        #Se o método for GET, ele renderiza o formulario definido em
        # /templates/profile/postar.html
        return render_template('profile/postar.html')



#rota /posts
@app.route('/posts')
# é necessário estar logado
@login_required
def posts():
    #recupera informacoes do usuario logado
    user = session['logado']

    #recupera posts do banco de dados
    #como o posts do usuário são dele para ele mesmo
    #eu posso filtrar todos os posts com esse detalhe
    posts = Post.query.filter_by(
        de=user['usuario'],  #de usuario logado
        para=user['usuario'] #para usuario logado
    ).order_by(
        Post.criado_em.desc(), #ordenando em ordem decrescente 
    ).all() #recupera todos os posts, sendo assim, uma lista de posts
    
    # manda renderizar o template em /templates/profile/posts.html
    # pasando como parametro user e posts
    return render_template('profile/posts.html', user=user, posts=posts)



#rota /login
#Essa rota já vimos detalhes dela
@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "GET":
        if 'logado' in session:
            return redirect(url_for('index'))
        sucesso = False
        if 'sucesso_cadastro' in session:
            sucesso = session['sucesso_cadastro']
        session['sucesso_cadastro'] = False
        return render_template("auth/login.html", sucesso_cadastro=sucesso)
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


#rota /cadastrar
#Essa rota ja vimos detalhes dela
@app.route('/cadastrar', methods=["POST", "GET"])
def cadastrar():
    if request.method == "GET":
        session['sucesso_cadastro'] = False
        return render_template("auth/cadastrar.html")
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


# rota /listar/usuarios
@app.route("/listar/usuarios")
#é necessário estar logado
@login_required
def listar_usuarios():
    #recupera todos os usuarios do banco de dados
    users = Usuario.query.all()

    #e manda renderizar o template em
    # /templates/usuarios.html
    # passando as informações dos usuarios recuperados
    return render_template(
        "usuarios.html",
        usuarios=users
    )


#rota /logout
@app.route("/logout")
# é necessário estar logado
@login_required
def logout():
    # remove o cookie de sessão "logado"
    del session['logado']
    #e redireciona o usuario para a pagina de login
    return redirect(url_for('login'))



#rota /post/<id>
@app.route("/post/<id>", methods=['GET', 'DELETE'])
#é necessário estar logado
@login_required
#recebe como parametro o id que o usuário quer ver ou deletar
def post(id):
    #recupera o usuario que está logado
    user = session['logado']
    #monta uma pesquisa filtrando os posts cuja o id é igual ao id
    #vindo como parametro
    query = Post.query.filter_by(id=id)

    #se o método for GET
    if request.method == 'GET':
        #então recupera o post
        post = query.first()
        #e se existe esse post
        if post:
            #então mostra para o usuario informações dele
            return f"<h3>De: {post.de}</h3><h3>Para: {post.para}</h3><pre>{post.conteudo}</pre>"
        else:
            #se não, mostra que voce não conseguiu encontrar o post
            return 'post nao encontrado'
    #se o método for outro
    #nesse caso DELETE
    # pois essa rota so aceita GET e DELETE
    else:
        #então faz uma requisição para deletar o post
        #mas essa requisição so pode ser feita se o usuario logado
        #pertence ao post
        #tanto no campo 'para' ou no campo 'de'
        #ou seja, so deleta se o usuario logado estiver alguma relação com o post
        deletions = query.where((Post.para==user['usuario']) | (Post.de==user['usuario'])).delete()
        db.session.commit()
        return jsonify({"deletions": deletions})


#rota /existe/<user>
#essa rota serve para quando o usuário for cadastrar
#ele poder ser informado se pode cadastrar com aquele usuario
# ou nao
@app.route("/existe/<user>")
def existe(user):
    user = Usuario.query.filter_by(usuario=user).first()
    return jsonify({"existe": bool(user)})


#Exercicio da ultima aula
#Listar os posts de um usuario
@app.route('/<username>/posts')
#para isso é necessário estar logado
@login_required
def usuario(username):
    #recupera dados do usuario para ver se o mesmo existe
    user = Usuario.query.filter_by(usuario=username).first() #dados de um usuario
    # se o usuario nao existe
    if user == None:
        # entao retorna que o usuario nao existe
        return 'Usuario não existe'
    
    #agora se o usuario existe
    #entao o codigo continua
    #recuperando todos os posts cuja tenha sido enviado do usuario para ele mesmo
    posts = Post.query.filter_by(de=username, para=username).order_by(
        Post.criado_em.desc(),# ordenando em ordem descrescente
    ).all()

    #entao renderiza o html presente em
    #/templates/usuario/posts.html
    #passando os parametros necessários
    return render_template(
        'usuario/posts.html',
        nome=user.nome,
        sobrenome=user.sobrenome,
        usuario=user.usuario,
        posts=posts
    )


############################################################################################
############################################################################################
######################## VOCE DEVE MODIFICAR O CODIGO ABAIXO ###############################
############################################################################################
############################################################################################


#Aqui é os seus depoimentos
#Ou seja, depoimentos enviados para você
@app.route('/depoimentos')
def depoimentos():
    # você consegue receber somente GET nessa rota
    # entao tudo que é necessário é adicionar uma logica para recuperar os posts
    # cuja seja destinado para você, mas que a origem não venha de você
    # A logica é usar um where
    #posts = Post.query.where(Post.de!=nomedousuariologado).filter_by(para=nomedousuariologado).all()
    return render_template('/profile/depoimentos.html')


#Esse que complica um pouco
#Essa rota permite postar depoimentos
#A logica é parecida com 'postar' da linha 62
@app.route('/<username>/postar', methods=['GET', 'POST'])
# é necessário estar logado
@login_required
def postar_depoimento(username):
    #recupera dados do usuario que voce esta querendo ver os depoimentos
    para = Usuario.query.filter_by(usuario=username).first()
    #se ele não existe, então retorna que não existe
    if para == None:
        return 'Usuario não existe'
    else:
        #Aqui que você deve implementar maioria da logica
        #Voce deve ver se o método é GET ou POST
        #Se for GET, você deve renderizar o html como está abaixo
        return render_template('usuario/postar.html', nome=para.nome, usuario=para.usuario)
        #Se for POST, você deve pegar os dados que estão chegando do formulario
        #E criar um novo post
        #cujo
        #'de' é o usuario logado
        #para é o usuario recuperado na linha 298 entao seria para.usuario
        #e conteudo é o conteudo vindo do formulário
        



#Esses são os depoimentos de algum usuario
#Vai ser praticamente a mesma logica dos seus depoimentos
#Unica coisa diferente é que no lugar de nomedousuariologado
#Voce deve usar o username vindo como parametro
@app.route('/<username>/depoimentos')
@login_required
def usuario_depoimentos(username):
    return render_template('/usuario/depoimentos.html')






############################################################################################
############################################################################################
######################## VOCE DEVE MODIFICAR O CODIGO ACIMA ################################
############################################################################################
############################################################################################



# caso as tabelas ou colunas de uma tabela do banco de dados 
# tenham sido modificadas, essas duas linhas fazem essa alteração
with app.app_context():
    db.create_all()