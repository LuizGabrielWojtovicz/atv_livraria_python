import sqlite3
import csv
import os
from pathlib import Path
from datetime import datetime

# -------------------------------------------------------------------------------------------- #

BASE_DIR = Path("meu_sistema_livraria")
DATA_DIR = BASE_DIR / "data"
BACKUP_DIR = BASE_DIR / "backups"
EXPORT_DIR = BASE_DIR / "exports"

# -------------------------------------------------------------------------------------------- #

DATA_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR.mkdir(parents=True, exist_ok=True)
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------------------------------------- #

DB_PATH = DATA_DIR / "livraria.db"

# -------------------------------------------------------------------------------------------- #

def conectar_banco():

    return sqlite3.connect(DB_PATH)

# -------------------------------------------------------------------------------------------- #

# Função para criar a tabela de livros
def criar_tabela_livros():

    db = conectar_banco()
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS livros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL,
            ano_publicacao INTEGER NOT NULL,
            preco REAL NOT NULL
        )
    ''')
    db.commit()
    db.close()

# -------------------------------------------------------------------------------------------- #

def adicionar_livro(nome_livro, nome_autor, ano_lancamento, valor):

    db = conectar_banco()
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO livros (titulo, autor, ano_publicacao, preco)
        VALUES (?, ?, ?, ?)
    ''', (nome_livro, nome_autor, ano_lancamento, valor))
    db.commit()
    db.close()
    fazer_backup()

# -------------------------------------------------------------------------------------------- #

def exibir_livros():

    db = conectar_banco()
    cursor = db.cursor()
    cursor.execute('''SELECT * 
                        FROM livros''')
    lista_livros = cursor.fetchall()
    for item in lista_livros:
        print(f"Id -> {item[0]} | Título -> {item[1]} | Autor -> {item[2]} | Ano -> {item[3]} | Preço: {item[4]}")
    db.close()

# -------------------------------------------------------------------------------------------- #

def atualizar_valor_livro(nome_livro, novo_valor):

    db = conectar_banco()
    cursor = db.cursor()
    cursor.execute('''
        UPDATE livros 
          SET preco = ? 
        WHERE titulo = ?
    ''', (novo_valor, nome_livro))
    db.commit()
    db.close()
    fazer_backup()

# -------------------------------------------------------------------------------------------- #

def remover_livro_por_titulo(nome_livro):

    db = conectar_banco()
    cursor = db.cursor()
    cursor.execute('''
        DELETE FROM livros 
         WHERE titulo = ?
    ''', (nome_livro,))
    db.commit()
    db.close()
    fazer_backup()

# -------------------------------------------------------------------------------------------- #

def buscar_livros_por_autor(nome_autor):

    db = conectar_banco()
    cursor = db.cursor()
    cursor.execute('''
        SELECT titulo 
          FROM livros 
         WHERE autor = ?
    ''', (nome_autor,))
    livros_encontrados = cursor.fetchall()
    if livros_encontrados:
        print(f"Livros do autor {nome_autor}:")
        for livro in livros_encontrados:
            print(f"- {livro[0]}")
    else:
        print(f"Nenhum livro encontrado para o autor {nome_autor}.")
    db.close()

# -------------------------------------------------------------------------------------------- #

def exportar_para_csv():

    db = conectar_banco()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM livros')
    livros = cursor.fetchall()
    csv_path = EXPORT_DIR / "livros_exportados.csv"
    with open(csv_path, mode='w', newline='', encoding='utf-8') as arquivo_csv:
        escritor_csv = csv.writer(arquivo_csv)
        escritor_csv.writerow(['ID', 'Título', 'Autor', 'Ano de Publicação', 'Preço'])
        escritor_csv.writerows(livros)
    print(f"Dados exportados para: {csv_path}")
    db.close()

# -------------------------------------------------------------------------------------------- #

def importar_de_csv():

    csv_path = EXPORT_DIR / "livros_importados.csv"
    if not csv_path.exists():
        print(f"Arquivo {csv_path} não encontrado.")
        return
    db = conectar_banco()
    cursor = db.cursor()
    with open(csv_path, mode='r', encoding='utf-8') as arquivo_csv:
        leitor_csv = csv.reader(arquivo_csv)
        next(leitor_csv)  # Pular o cabeçalho
        for linha in leitor_csv:
            cursor.execute('''
                INSERT INTO livros (titulo, autor, ano_publicacao, preco)
                VALUES (?, ?, ?, ?)
            ''', (linha[1], linha[2], int(linha[3]), float(linha[4])))
    db.commit()
    print("Dados importados do CSV.")
    db.close()
    fazer_backup()

# -------------------------------------------------------------------------------------------- #

def fazer_backup():

    backup_path = BACKUP_DIR / f"backup_livraria_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.db"
    with open(DB_PATH, 'rb') as db_original:
        with open(backup_path, 'wb') as db_backup:
            db_backup.write(db_original.read())
    print(f"Backup realizado: {backup_path}")
    limpar_backups_antigos()

# -------------------------------------------------------------------------------------------- #

def limpar_backups_antigos():

    backups = sorted(BACKUP_DIR.glob("*.db"), key=os.path.getmtime, reverse=True)
    if len(backups) > 5:
        for backup in backups[5:]:
            backup.unlink()
            print(f"Backup antigo removido: {backup}")

# -------------------------------------------------------------------------------------------- #

criar_tabela_livros()

while True:
    opcao_escolhida = input('''\n1. Adicionar novo livro
                               \n2. Exibir todos os livros
                               \n3. Atualizar preço de um livro
                               \n4. Remover um livro
                               \n5. Buscar livros por autor
                               \n6. Exportar dados para CSV
                               \n7. Importar dados de CSV
                               \n8. Fazer backup do banco de dados
                               \n9. Sair
                               \n\nEscolha uma opção:\n''')

    if opcao_escolhida == '1':
        titulo_livro = input("Título: ")
        autor_livro = input("Autor: ")
        ano_publicacao = int(input("Ano de publicação: "))
        preco_livro = float(input("Preço: "))
        adicionar_livro(titulo_livro, autor_livro, ano_publicacao, preco_livro)

    elif opcao_escolhida == '2':
        exibir_livros()

    elif opcao_escolhida == '3':
        titulo_livro = input("Título do livro para atualizar o preço: ")
        novo_preco_livro = float(input("Novo preço: "))
        atualizar_valor_livro(titulo_livro, novo_preco_livro)

    elif opcao_escolhida == '4':
        titulo_livro = input("Título do livro para remover: ")
        remover_livro_por_titulo(titulo_livro)

    elif opcao_escolhida == '5':
        nome_autor = input("Digite o nome do autor: ")
        buscar_livros_por_autor(nome_autor)

    elif opcao_escolhida == '6':
        exportar_para_csv()

    elif opcao_escolhida == '7':
        importar_de_csv()

    elif opcao_escolhida == '8':
        fazer_backup()

    elif opcao_escolhida == '9':
        print("Sistema encerrado.")
        break

    else:
        print("Opção inválida. Tente novamente.")
