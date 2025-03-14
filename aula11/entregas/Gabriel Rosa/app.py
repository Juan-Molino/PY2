# Importações necessárias
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import re  # Para manipulação de strings

# Configuração do aplicativo Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contatos.db'  # Banco de dados SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --------------------------------------------
# Modelo do Banco de Dados
# --------------------------------------------

class Contato(db.Model):
    """Modelo para representar um contato na agenda"""
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100))
    observacoes = db.Column(db.String(200))  # 🔹 Corrigido para "observacoes"

    def __repr__(self):
        return f'<Contato {self.nome}>'

# --------------------------------------------
# Rotas do Flask
# --------------------------------------------

@app.route('/')
def index():
    """Página principal - lista todos os contatos"""
    termo_busca = request.args.get('busca', '')  # Pega o termo de busca da URL
    
    if termo_busca:
        # Filtra contatos que contenham o termo no nome
        contatos = Contato.query.filter(Contato.nome.ilike(f'%{termo_busca}%')).all()
    else:
        contatos = Contato.query.all()
    
    return render_template('index.html', contatos=contatos, termo_busca=termo_busca)

@app.route('/adicionar', methods=['GET', 'POST'])
def adicionar_contato():
    """Adiciona um novo contato à agenda"""
    if request.method == 'POST':
        telefone_limpo = re.sub(r'\D', '', request.form['telefone'])

        if len(telefone_limpo) != 11:
            return render_template('formulario.html', error="Telefone deve ter 11 dígitos!")

        novo_contato = Contato(
            nome=request.form['nome'],
            telefone=telefone_limpo,
            email=request.form['email'],
            observacoes=request.form['observacoes']  # 🔹 Captura as observações
        )
        db.session.add(novo_contato)
        db.session.commit()
        return redirect(url_for('index'))
    
    return render_template('formulario.html')

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_contato(id):
    """Edita um contato existente"""
    contato = Contato.query.get_or_404(id)
    
    if request.method == 'POST':
        telefone_limpo = re.sub(r'\D', '', request.form['telefone'])

        if len(telefone_limpo) != 11:
            return render_template('formulario.html', contato=contato, error="Telefone inválido!")

        contato.nome = request.form['nome']
        contato.telefone = telefone_limpo
        contato.email = request.form['email']
        contato.observacoes = request.form['observacoes']  # 🔹 Atualiza as observações
        db.session.commit()
        return redirect(url_for('index'))
    
    return render_template('formulario.html', contato=contato)

@app.route('/excluir/<int:id>', methods=['GET', 'POST'])
def excluir_contato(id):
    """Exclui um contato da agenda"""
    contato = Contato.query.get(id)
    if contato:
        db.session.delete(contato)
        db.session.commit()
    return redirect(url_for('index'))

# Filtro para formatar o telefone nos templates
@app.template_filter('format_telefone')
def format_telefone(numero):
    """Formata o telefone no formato (xx) xxxxx-xxxx"""
    if len(numero) != 11:
        return numero
    return f'({numero[:2]}) {numero[2:7]}-{numero[7:]}'

# --------------------------------------------
# Execução do Aplicativo
# --------------------------------------------

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Cria tabelas se não existirem
        
        # Adiciona contatos iniciais para teste
        if not Contato.query.first():
            contatos_iniciais = [
                Contato(nome='Prof. Daniel Mesquita', telefone='45984318261', email='danielme17@gmail.com', observacoes="Exemplo de observação")
            ]
            db.session.add_all(contatos_iniciais)
            db.session.commit()
    
    app.run(debug=True)