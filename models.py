from gerenciadorprojetos import db

#---------------------------------------------------------------------------------------------------------------------------------
#TABELA: USUÁRIOS
#ORIGEM: BANCO DE DADOS
#---------------------------------------------------------------------------------------------------------------------------------
class tb_user(db.Model):
    cod_user = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name_user = db.Column(db.String(50), nullable=False)
    password_user = db.Column(db.String(50), nullable=False)
    status_user = db.Column(db.Integer, nullable=False)
    login_user = db.Column(db.String(50), nullable=False)
    cod_usertype = db.Column(db.Integer, nullable=False)
    email_user = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return '<Name %r>' % self.name

#---------------------------------------------------------------------------------------------------------------------------------
#TABELA: TIPO USUÁRIOS
#ORIGEM: BANCO DE DADOS
#---------------------------------------------------------------------------------------------------------------------------------
class tb_usertype(db.Model):
    cod_usertype = db.Column(db.Integer, primary_key=True, autoincrement=True)
    desc_usertype = db.Column(db.String(50), nullable=False)
    status_usertype = db.Column(db.Integer, nullable=False)
    def __repr__(self):
        return '<Name %r>' % self.name    
 
#---------------------------------------------------------------------------------------------------------------------------------
#TABELA: CLIENTES
#ORIGEM: BANCO DE DADOS
#---------------------------------------------------------------------------------------------------------------------------------
class tb_clientes(db.Model):
    cod_cliente = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nomerazao_cliente = db.Column(db.String(50), nullable=False)
    nomefantasia_cliente = db.Column(db.String(50), nullable=False)
    end_cliente = db.Column(db.String(50), nullable=False)
    numend_cliente = db.Column(db.String(50), nullable=False)
    bairro_cliente = db.Column(db.String(50), nullable=False)
    cidade_cliente = db.Column(db.String(50), nullable=False)
    uf_cliente = db.Column(db.String(50), nullable=False)
    complemento_cliente = db.Column(db.String(50), nullable=False)
    cnpj_cliente = db.Column(db.String(50), nullable=False)
    status_cliente = db.Column(db.Integer, nullable=False)
    def __repr__(self):
        return '<Name %r>' % self.name    


#---------------------------------------------------------------------------------------------------------------------------------
#TABELA: CONTRATOS
#ORIGEM: BANCO DE DADOS
#---------------------------------------------------------------------------------------------------------------------------------
class tb_contratos(db.Model):
    cod_contrato = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cod_cliente = db.Column(db.Integer, nullable=False)
    obj_contrato = db.Column(db.String(50), nullable=False)
    datavalidade_contrato = db.Column(db.Date, nullable=False)
    status_contrato = db.Column(db.Integer, nullable=False)
    def __repr__(self):
        return '<Name %r>' % self.name
    
#---------------------------------------------------------------------------------------------------------------------------------
#TABELA: CONTRATOS_ARQUIVOS
#ORIGEM: BANCO DE DADOS
#---------------------------------------------------------------------------------------------------------------------------------
class tb_contrato_arquivos(db.Model):
    cod_contrato_arquivo = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cod_contrato = db.Column(db.Integer, nullable=False)
    arquivo_contrato_arquivo = db.Column(db.String(50), nullable=False)
    def __repr__(self):
        return '<Name %r>' % self.name    

#---------------------------------------------------------------------------------------------------------------------------------
#TABELA: CONTRATOS_ARQUIVOS
#ORIGEM: BANCO DE DADOS
#---------------------------------------------------------------------------------------------------------------------------------
class tb_aditivos(db.Model):
    cod_aditivo = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cod_contrato = db.Column(db.Integer, nullable=False)
    desc_aditivo = db.Column(db.String(50), nullable=False)
    data_aditivo = db.Column(db.Date, nullable=False)
    status_aditivo = db.Column(db.Integer, nullable=False)
    def __repr__(self):
        return '<Name %r>' % self.name