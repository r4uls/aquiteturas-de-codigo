
import sqlite3

class CamadaDados:
    def __init__(self):
        self.conn = sqlite3.connect('agenda.db')
        self.criar_tabelas()

    def criar_tabelas(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contatos (
                id INTEGER PRIMARY KEY,
                nome TEXT NOT NULL,
                telefone TEXT NOT NULL
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
            SELECT c.id, c.descricao, c.data, co.id, co.nome
            FROM compromissos c
            LEFT JOIN contatos co ON c.contato_id = co.id
        ''')
        return cursor.fetchall()
    
    def buscar_compromissos_por_intervalo(self, data_inicio, data_fim):
        cursor = self.conn.cursor()
        cursor.execute('''
            select c.id, c.descricao, c.data, co.id, co.nome
            from compromissos c
            left join contatos co ON c.contato_id = co.id
            where c.data between ? and ?
        ''', (data_inicio, data_fim))
        return cursor.fetchall()



class CamadaNegocios:
    def __init__(self):
        self.dados = CamadaDados()

    def adicionar_contato(self, nome, telefone, email):
        if not nome or not telefone or not email:
            raise ValueError("Nome, telefone e email são obrigatórios")
        return self.dados.adicionar_contato(nome, telefone, email)

    def adicionar_compromisso(self, descricao, data, contato_id=None):
        if not descricao or not data:
            raise ValueError("Descrição e data são obrigatórios")
        return self.dados.adicionar_compromisso(descricao, data, contato_id)

    def listar_contatos(self):
        return self.dados.listar_contatos()

    def listar_compromissos(self):
        compromissos = self.dados.listar_compromissos()
        return [
            {
                'id': c[0],
                'descricao': c[1],
                'data': c[2],
                'contato': {'id': c[3], 'nome': c[4]} if c[3] else None
            }
            for c in compromissos
        ]

    def pesquisar_compromissos(self, data_inicio, data_fim):
        if not data_inicio or not data_fim:
            raise ValueError("Erro!")
        if data_inicio > data_fim:
            raise ValueError("Erro!")
        
        compromissos = self.dados.buscar_compromissos_por_intervalo(data_inicio, data_fim)
        return [
            {
                'id': c[0],
                'descricao': c[1],
                'data': c[2],
                'contato': {'id': c[3], 'nome': c[4]} if c[3] else None
            }
            for c in compromissos
        ]



class CamadaApresentacao:
    def __init__(self):
        self.negocios = CamadaNegocios()

    def exibir_menu(self):
        print("\n1. Adicionar Contato")
        print("2. Adicionar Compromisso")
        print("3. Listar Contatos")
        print("4. Listar Compromissos")
        print("5. Pesquisar Compromissos")
        print("6. Sair")

    def adicionar_contato(self):
        nome = input("Nome do contato: ")
        telefone = input("Telefone do contato: ")
        email = input("Email do contato: ")
        try:
            id_contato = self.negocios.adicionar_contato(nome, telefone, email)
            print(f"Contato adicionado com ID: {id_contato}")
        except ValueError as e:
            print(f"Erro: {str(e)}")

    def adicionar_compromisso(self):
        descricao = input("Descrição do compromisso: ")
        data = input("Data do compromisso (YYYY-MM-DD HH:MM): ")
        contato_id = input("ID do contato (opcional): ")
        try:
            id_compromisso = self.negocios.adicionar_compromisso(descricao, data, int(contato_id) if contato_id else None)
            print(f"Compromisso adicionado com ID: {id_compromisso}")
        except ValueError as e:
            print(f"Erro: {str(e)}")

    def listar_contatos(self):
        contatos = self.negocios.listar_contatos()
        for contato in contatos:
            print(f"ID: {contato[0]}, Nome: {contato[1]}, Telefone: {contato[2]}, Email: {contato[3]}")

    def listar_compromissos(self):
        compromissos = self.negocios.listar_compromissos()
        for compromisso in compromissos:
            contato = compromisso['contato']
            print(f"ID: {compromisso['id']}, Descrição: {compromisso['descricao']}, Data: {compromisso['data']}, "
                  f"Contato: {contato['nome'] if contato else 'N/A'}")
            
    def pesquisar_compromissos(self):
        data_inicio = input("Data inicial (aaaa-mm-dd): ")
        data_fim = input("Data final (aaaa-mm-dd): ")
        try:
            compromissos = self.negocios.pesquisar_compromissos(data_inicio, data_fim)
            if compromissos:
                print("Compromissos encontrados:")
                for compromisso in compromissos:
                    contato = compromisso['contato']
                    print(f"ID: {compromisso['id']}, Descrição: {compromisso['descricao']}, Data: {compromisso['data']}, "
                          f"Contato: {contato['nome'] if contato else 'N/A'}")
            else:
                print("Nenhum compromisso.")
        except ValueError as e:
            print(f"Erro: {str(e)}")

    def executar(self):
        while True:
            self.exibir_menu()
            opcao = input("Escolha uma opção: ")

            if opcao == '1':
                self.adicionar_contato()
            elif opcao == '2':
                self.adicionar_compromisso()
            elif opcao == '3':
                self.listar_contatos()
            elif opcao == '4':
                self.listar_compromissos()
            elif opcao == '5':
                self.pesquisar_compromissos()
            elif opcao == 6:
                print("Encerrando o programa...")
                break
            else:
                print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    app = CamadaApresentacao()
    app.executar()