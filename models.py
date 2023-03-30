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
#TABELA: PROJETOS
#ORIGEM: BANCO DE DADOS
#---------------------------------------------------------------------------------------------------------------------------------
class tb_projetos(db.Model):
    cod_projeto = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome_projeto = db.Column(db.String(50), nullable=False)
    datainicio_projeto = db.Column(db.Date, nullable=False)
    datafim_projeto = db.Column(db.Date, nullable=False)
    desc_projeto = db.Column(db.String(50), nullable=False)
    cod_usuario = db.Column(db.Integer, nullable=False)
    status_projeto = db.Column(db.Integer, nullable=False)
    def __repr__(self):
        return '<Name %r>' % self.name
    

#---------------------------------------------------------------------------------------------------------------------------------
#TABELA: PROJETOS
#ORIGEM: BANCO DE DADOS
#---------------------------------------------------------------------------------------------------------------------------------
class tb_backlogs(db.Model):
    cod_backlog = db.Column(db.Integer, primary_key=True, autoincrement=True)
    desc_backlog = db.Column(db.String(500), nullable=False)
    prioridade_backlog = db.Column(db.Integer, nullable=False)
    estimativa_backlog = db.Column(db.Integer, nullable=False)
    dependencias_backlog = db.Column(db.String(50), nullable=False)
    criterios_backlog = db.Column(db.String(500), nullable=False)
    datacriacao_backlog = db.Column(db.Date, nullable=False)
    dataconclusao_backlog = db.Column(db.Date, nullable=False)
    obs_backlog = db.Column(db.String(500), nullable=False)    
    status_backlog = db.Column(db.Integer, nullable=False)
    esforco_backlog = db.Column(db.Integer, nullable=False)
    cod_projeto = db.Column(db.Integer, nullable=False)
    titulo_backlog = db.Column(db.String(45), nullable=False)
    def __repr__(self):
        return '<Name %r>' % self.name
    
#---------------------------------------------------------------------------------------------------------------------------------
#TABELA: PROJETOS
#ORIGEM: BANCO DE DADOS
#---------------------------------------------------------------------------------------------------------------------------------
class tb_tarefas(db.Model):
    cod_tarefas = db.Column(db.Integer, primary_key=True, autoincrement=True)
    titulo_tarefa = db.Column(db.String(45), nullable=False)
    descricao_tarefa = db.Column(db.String(500), nullable=False)
    prioridade_tarefa = db.Column(db.Integer, nullable=False)
    estimativa_tarefa = db.Column(db.Integer, nullable=False)
    datacriacao_tarefa = db.Column(db.Date, nullable=False)
    dataconclusao_tarefa = db.Column(db.Date, nullable=False)
    obs_tarefa = db.Column(db.String(500), nullable=False)    
    status_tarefa = db.Column(db.Integer, nullable=False)
    cod_usuario = db.Column(db.Integer, nullable=False)
    cod_backlog = db.Column(db.Integer, nullable=False)    
    def __repr__(self):
        return '<Name %r>' % self.name
