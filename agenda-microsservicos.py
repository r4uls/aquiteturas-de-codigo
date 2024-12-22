
import sqlite3
from flask import Flask, request, jsonify

app_contatos = Flask(__name__)

def get_db():
    db = sqlite3.connect('contatos.db')
    db.execute('CREATE TABLE IF NOT EXISTS contatos (id INTEGER PRIMARY KEY, nome TEXT NOT NULL, telefone TEXT NOT NULL, email TEXT NOT NULL)')
    return db

@app_contatos.route('/contatos', methods=['POST'])
def adicionar_contato():
    data = request.json
    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO contatos (nome, telefone, email) VALUES (?, ?, ?)', (data['nome'], data['telefone'], data['email']))
    db.commit()
    return jsonify({'id': cursor.lastrowid}), 201

@app_contatos.route('/contatos', methods=['GET'])
def listar_contatos():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM contatos')
    contatos = [{'id': row[0], 'nome': row[1], 'telefone': row[2], 'email' : row[3]} for row in cursor.fetchall()]
    return jsonify(contatos)

if __name__ == '__main__':
    app_contatos.run(port=5000)


import sqlite3
from flask import Flask, request, jsonify
import requests

app_compromissos = Flask(__name__)

def get_db():
    db = sqlite3.connect('compromissos.db')
    db.execute('CREATE TABLE IF NOT EXISTS compromissos (id INTEGER PRIMARY KEY, descricao TEXT NOT NULL, data TEXT NOT NULL, contato_id INTEGER)')
    return db

@app_compromissos.route('/compromissos/pesquisar', methods=['GET'])
def pesquisar_compromissos():
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    
    if not data_inicio or not data_fim:
        return jsonify('Erro')

    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'select * from compromissos where data between ? and ?', 
            (data_inicio, data_fim)
        )
        compromissos = [{'id': row[0], 'descricao': row[1], 'data': row[2], 'contato_id': row[3]} for row in cursor.fetchall()]
        for compromisso in compromissos:
            if compromisso['contato_id']:
                response = requests.get(f'http://localhost:5000/contatos/{compromisso["contato_id"]}')
                if response.status_code == 200:
                    compromisso['contato'] = response.json()

        return jsonify(compromissos)

    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@app_compromissos.route('/compromissos', methods=['POST'])
def adicionar_compromisso():
    data = request.json
    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO compromissos (descricao, data, contato_id) VALUES (?, ?, ?)',
                   (data['descricao'], data['data'], data.get('contato_id')))
    db.commit()
    return jsonify({'id': cursor.lastrowid}), 201

@app_compromissos.route('/compromissos', methods=['GET'])
def listar_compromissos():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM compromissos')
    compromissos = [{'id': row[0], 'descricao': row[1], 'data': row[2], 'contato_id': row[3]} for row in cursor.fetchall()]
    
    for compromisso in compromissos:
        if compromisso['contato_id']:
            response = requests.get(f'http://localhost:5000/contatos/{compromisso["contato_id"]}')
            if response.status_code == 200:
                compromisso['contato'] = response.json()
    
    return jsonify(compromissos)

if __name__ == '__main__':
    app_compromissos.run(port=5001)


import requests

def adicionar_contato():
    nome = input("Nome do contato: ")
    telefone = input("Telefone do contato: ")
    email = input("Email do contato: ")
    response = requests.post('http://localhost:5000/contatos', json={'nome': nome, 'telefone': telefone, 'email': email})
    print(f"Contato adicionado com ID: {response.json()['id']}")

def adicionar_compromisso():
    descricao = input("Descrição do compromisso: ")
    data = input("Data do compromisso (YYYY-MM-DD HH:MM): ")
    contato_id = input("ID do contato (opcional): ")
    data = {'descricao': descricao, 'data': data}
    if contato_id:
        data['contato_id'] = int(contato_id)
    response = requests.post('http://localhost:5001/compromissos', json=data)
    print(f"Compromisso adicionado com ID: {response.json()['id']}")

def listar_contatos():
    response = requests.get('http://localhost:5000/contatos')
    contatos = response.json()
    for contato in contatos:
        print(f"ID: {contato['id']}, Nome: {contato['nome']}, Telefone: {contato['telefone']}, Email: {contato}")

def listar_compromissos():
    response = requests.get('http://localhost:5001/compromissos')
    compromissos = response.json()
    for compromisso in compromissos:
        contato = compromisso.get('contato', {})
        print(f"ID: {compromisso['id']}, Descrição: {compromisso['descricao']}, Data: {compromisso['data']}, Contato: {contato.get('nome', 'N/A')}")

def pesquisar_compromissos():
    data_inicio = input("Data de início (aaaa-mm-dd): ")
    data_fim = input("Data do fim (aaaa-mm-dd): ")
    response = requests.get(
        'http://localhost:5000/compromissos/pesquisar', 
        params={'data_inicio': data_inicio, 'data_fim': data_fim}
    )
    if response.status_code == 200:
        compromissos = response.json()
        if compromissos:
            print("Compromissos encontrados:")
            for compromisso in compromissos:
                contato = compromisso.get('contato', {})
                print(f"ID: {compromisso['id']}, Descrição: {compromisso['descricao']}, Data: {compromisso['data']}, Contato: {contato.get('nome', 'N/A')}")
        else:
            print("Nenhum compromisso.")
    else:
        print("Erro")



def main():
    while True:
        print("\n1. Adicionar Contato")
        print("2. Adicionar Compromisso")
        print("3. Listar Contatos")
        print("4. Listar Compromissos")
        print("5. Pesquisar Compromissos")
        print("6. Sair")

        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            adicionar_contato()
        elif opcao == '2':
            adicionar_compromisso()
        elif opcao == '3':
            listar_contatos()
        elif opcao == '4':
            listar_compromissos()
        elif opcao == '5':
            pesquisar_compromissos()
        elif opcao == '6':
         break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()
