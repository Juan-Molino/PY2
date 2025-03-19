from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import time

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///arquivos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Arquivo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    conteudo = db.Column(db.LargeBinary, nullable=False)

class Tarefa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(200), nullable=True)
    duracao = db.Column(db.Integer, nullable=False)
    data_criacao = db.Column(db.Integer, nullable=False)
    data_limite = db.Column(db.Integer, nullable=False)
    progresso = db.Column(db.Float, nullable=False, default=0)
    expirada = db.Column(db.Boolean, nullable=False, default=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tarefas', methods=['POST'])
def adicionar_tarefa():
    data = request.get_json()
    nome = data.get('nome')
    descricao = data.get('descricao')
    duracao = data.get('duracao')
    
    if not nome or not duracao:
        return jsonify({'status': 'error', 'message': 'Campos obrigatórios não preenchidos'}), 400
    
    nova_tarefa = Tarefa(
        nome=nome,
        descricao=descricao,
        duracao=duracao,
        data_criacao=int(time.time()),
        data_limite=int(time.time()) + duracao * 60
    )
    db.session.add(nova_tarefa)
    db.session.commit()
    
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)