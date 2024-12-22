import sqlite3
from datetime import datetime

class Agenda:
    def __init__(self):
        self.conn = sqlite3.connect('agenda.db')
        self.criar_tabelas()

    def criar_tabelas(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contatos (
                id INTEGER PRIMARY KEY,
                nome TEXT NOT NULL,
                telefone TEXT NOT NULL,
                email TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS compromissos (
                id INTEGER PRIMARY KEY,
                descricao TEXT NOT NULL,
                data TEXT NOT NULL,
                contato_id INTEGER,
                FOREIGN KEY (contato_id) REFERENCES contatos (id)
            )
        ''')
        self.conn.commit()

    def adicionar_contato(self, nome, telefone, email):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO contatos (nome, telefone, email) VALUES (?, ?, ?)', (nome, telefone, email))
        self.conn.commit()
        return cursor.lastrowid

    def adicionar_compromisso(self, descricao, data, contato_id=None):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO compromissos (descricao, data, contato_id) VALUES (?, ?, ?)',
                       (descricao, data, contato_id))
        self.conn.commit()
        return cursor.lastrowid

    def listar_contatos(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM contatos')
        return cursor.fetchall()

    def listar_compromissos(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT c.descricao, c.data, co.nome
            FROM compromissos c
            LEFT JOIN contatos co ON c.contato_id = co.id
        ''')
        return cursor.fetchall()

    def pesquisar_compromissos(self, data_inicio, data_fim):
        cursor = self.conn.cursor()
        cursor.execute('''
        select c.descricao, c.data, co.nome
        from compromissos.c
        left join contatos co on c.contato_id = co.id
        where c.data between ? and ?
        order by c.data
        ''', (data_inicio, data_fim))
        return cursor.fetchall()

def main():
    agenda = Agenda()

    while True:
        print("\n1. Adicionar Contato")
        print("2. Adicionar Compromisso")
        print("3. Listar Contatos")
        print("4. Listar Compromissos")
        print("5. Pesquisar Comprimissos")
        print("6. Sair")

        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            nome = input("Nome do contato: ")
            telefone = input("Telefone do contato: ")
            email = input("Email do contato:")
            agenda.adicionar_contato(nome, telefone, email)
        elif opcao == '2':
            descricao = input("Descrição do compromisso: ")
            data = input("Data do compromisso (YYYY-MM-DD HH:MM): ")
            contato_id = input("ID do contato (opcional): ")
            agenda.adicionar_compromisso(descricao, data, contato_id if contato_id else None)
        elif opcao == '3':
            contatos = agenda.listar_contatos()
            for contato in contatos:
                print(f"ID: {contato[0]}, Nome: {contato[1]}, Telefone: {contato[2]}")
        elif opcao == '4':
            compromissos = agenda.listar_compromissos()
            for compromisso in compromissos:
                print(f"Descrição: {compromisso[0]}, Data: {compromisso[1]}, Contato: {compromisso[2] or 'N/A'}")
        elif opcao == '5':
            data_inicio = input("Data inicial(aaaa-mm-dd): ")
            data_fim =  input("Data final(aaaa-mm-dd): ")
            compromisso = agenda.pesquisar_compromissos(data_inicio, data_fim)
            
            print("Compromissos encontrados:")
            for compromisso in compromissos:
                print(f"Descriçao: {compromisso[0]}, Data: {compromisso[1]}, Contato {compromisso[2] or 'N/A'}")
        elif opcao == '6':
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()
