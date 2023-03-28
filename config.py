import os

SECRET_KEY = 'cidadepartificpativa2023'


# conexão com o banco de dados mysql
SQLALCHEMY_DATABASE_URI = \
    '{SGBD}://{usuario}:{senha}@{servidor}/{database}'.format(
        SGBD ='mysql+mysqlconnector',
        usuario ='root',
        senha = '12345',
        servidor ='localhost',
        database ='db_gerenciadorcontratos')

#CAMINHO DO UPLOAD (SE DISPONIVEL)
UPLOAD_PATH = os.path.dirname(os.path.abspath(__file__)) + '/static/upload/'

#QUANTIDADE DE REGISTROS POR PÁGINA
ROWS_PER_PAGE = 10

#CHAVE DE CRIPTOGRAFIA
CHAVE = "GERENCIADOR2023"