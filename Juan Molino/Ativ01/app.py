import sqlite3
import os

# Função para criptografar um arquivo usando operação XOR com chave numérica de 8 dígitos.
def criptografar_arquivo(arquivo_entrada, arquivo_saida, chave):
    """
    Criptografa um arquivo usando operação XOR com chave numérica de 8 dígitos.
    A chave será convertida para bytes e repetida ciclicamente durante o XOR.
    """
    with open(arquivo_entrada, 'rb') as f:
        dados = f.read()
    
    # Converte a chave para string com zeros à esquerda e transforma em bytes
    chave_bytes = str(chave).zfill(8).encode()  # Agora usando 8 dígitos
    
    # Aplica operação XOR usando a chave estendida
    dados_cripto = xor_bytes(dados, chave_bytes)
    
    with open(arquivo_saida, 'wb') as f:
        f.write(dados_cripto)

def xor_bytes(dados, chave):
    """
    Aplica XOR entre cada byte dos dados e a chave repetida.
    Mesma função para criptografar e descriptografar.
    """
    return bytes([dado ^ chave[i % len(chave)] for i, dado in enumerate(dados)])

def tentar_descriptografia(dados_cripto, chave_tentativa):
    """
    Tenta descriptografar com uma chave de 8 dígitos.
    Retorna None se a decodificação UTF-8 falhar (chave inválida)
    """
    try:
        chave_bytes = str(chave_tentativa).zfill(8).encode()  # 8 dígitos
        dados_decripto = xor_bytes(dados_cripto, chave_bytes)
        return dados_decripto.decode('utf-8')
    except UnicodeDecodeError:
        return None

def criar_tabela_arquivos(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Cria a tabela arquivos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS arquivos (
                id INTEGER PRIMARY KEY,
                nome TEXT NOT NULL,
                conteudo BLOB
            )
        ''')
        
        # Insere um registro na tabela arquivos
        cursor.execute('''
            INSERT INTO arquivos (nome, conteudo) VALUES (?, ?)
        ''', ('segredo.enc', 'Conteúdo criptografado'.encode('utf-8')))
        
        conn.commit()
        conn.close()
        print("Tabela arquivos criada e dados inseridos com sucesso.")
    except sqlite3.Error as e:
        print(f"Erro ao acessar o banco de dados: {e}")

def db_to_file(db_path, output_file_path):
    try:
        # Conecta ao banco de dados
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Substitua 'arquivos' pelo nome correto da tabela e 'conteudo' pelo nome da coluna BLOB
        cursor.execute('''
            SELECT conteudo FROM arquivos WHERE nome = 'segredo.enc'
        ''')
        
        blob_data = cursor.fetchone()
        conn.close()
        
        if not blob_data:
            raise ValueError(f"Arquivo não encontrado no banco de dados")
        
        # Escreve o conteúdo BLOB no arquivo de saída
        with open(output_file_path, 'wb') as file:
            file.write(blob_data[0])
        
        print(f"Arquivo {output_file_path} extraído com sucesso.")
    except sqlite3.Error as e:
        print(f"Erro ao acessar o banco de dados: {e}")

def listar_tabelas(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tabelas = cursor.fetchall()
        conn.close()
        return tabelas
    except sqlite3.Error as e:
        print(f"Erro ao acessar o banco de dados: {e}")
        return []

def listar_colunas(db_path, tabela):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({tabela});")
        colunas = cursor.fetchall()
        conn.close()
        return colunas
    except sqlite3.Error as e:
        print(f"Erro ao acessar o banco de dados: {e}")
        return []

def main():
    print('Iniciando busca ao tesouro...')
    
    # Caminho para o banco de dados e arquivo de saída
    db_path = 'arquivos.db'
    output_file_path = 'segredo.enc'
    
    # Cria a tabela arquivos
    criar_tabela_arquivos(db_path)
    
    # Lista as tabelas no banco de dados novamente
    tabelas = listar_tabelas(db_path)
    print("Tabelas no banco de dados:", tabelas)
    
    # Verifica as colunas na tabela arquivos
    colunas = listar_colunas(db_path, 'arquivos')
    print(f"Colunas na tabela arquivos:", colunas)
    
    # Extrai o arquivo criptografado do banco de dados
    db_to_file(db_path, output_file_path)
    
    # Verifica se o arquivo foi criado
    if not os.path.exists(output_file_path):
        print(f"Erro: O arquivo {output_file_path} não foi encontrado.")
        return
    
    # Lê o arquivo criptografado
    with open(output_file_path, 'rb') as f:
        dados_cripto = f.read()
    
    # Tenta descriptografar usando força bruta
    for chave_tentativa in range(100000000):
        texto_descriptografado = tentar_descriptografia(dados_cripto, chave_tentativa)
        print(chave_tentativa)
        if texto_descriptografado and 'Parabéns' in texto_descriptografado:
            print(f'Chave encontrada: {chave_tentativa}')
            print(f'Texto descriptografado: {texto_descriptografado}')
            break
    else:
        print('Chave não encontrada.')

if __name__ == '__main__': 
    main()
"""
PRINCIPAIS ALTERAÇÕES E DESAFIOS:
1. A chave agora tem 8 dígitos (100 milhões de combinações possíveis)
2. Aumento exponencial na complexidade do brute force
3. Necessidade de otimização e trabalho em equipe eficiente

ESTRATÉGIAS SUGERIDAS:
1. Divisão de tarefas:
   - Dividir o intervalo 0-99999999 entre os membros do grupo
   - Ex: Cada membro testa 12.500.000 chaves (100M / 8 pessoas)

"""