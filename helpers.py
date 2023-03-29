#importações
import os
from gerenciadorprojetos import app, db
from models import tb_user, tb_usertype, tb_projetos, tb_backlogs
from flask_wtf import FlaskForm
from wtforms import Form, StringField, validators, SubmitField,IntegerField, SelectField,PasswordField,DateField,EmailField,BooleanField,RadioField, TextAreaField, TimeField, TelField, DateTimeLocalField,FloatField, DecimalField,FileField

##################################################################################################################################
#PESQUISA
##################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: pesquisa (geral)
#TIPO: edição
#TABELA: nenhuma
#---------------------------------------------------------------------------------------------------------------------------------
class frm_pesquisa(FlaskForm):
    pesquisa = StringField('Pesquisa:', [validators.Length(min=1, max=50)],render_kw={"placeholder": "digite sua pesquisa"} )
    pesquisa_responsiva = StringField('Pesquisa:', [validators.Length(min=1, max=50)],render_kw={"placeholder": "digite sua pesquisa"} )
    salvar = SubmitField('Pesquisar')

##################################################################################################################################
#USUÁRIO
##################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: usuários
#TIPO: edição
#TABELA: tb_user
#---------------------------------------------------------------------------------------------------------------------------------
class frm_editar_usuario(FlaskForm):
    nome = StringField('Nome:', [validators.DataRequired(), validators.Length(min=1, max=50)],render_kw={"placeholder": "digite o nome do usuário"})
    status = SelectField('Situação:', coerce=int, choices=[(0,"Ativo"),(1,"Inativo")])
    login = StringField('Login:', [validators.DataRequired(), validators.Length(min=1, max=50)],render_kw={"placeholder": "digite o login do usuário"})    
    tipousuario = SelectField('Situação:', coerce=int,  choices=[(g.cod_usertype, g.desc_usertype) for g in tb_usertype.query.order_by('desc_usertype')])
    email = EmailField('Email:', [validators.DataRequired(), validators.Length(min=1, max=50)],render_kw={"placeholder": "digite o email do usuário"})
    salvar = SubmitField('Salvar')


#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: usuários
#TIPO: visualização
#TABELA: tb_user
#---------------------------------------------------------------------------------------------------------------------------------
class frm_visualizar_usuario(FlaskForm):
    nome = StringField('Nome:', [validators.DataRequired(), validators.Length(min=1, max=50)],render_kw={'readonly': True})
    status = SelectField('Situação:', coerce=int, choices=[(0,"Ativo"),(1,"Inativo")], render_kw={'readonly': True})
    login = StringField('Login:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    tipousuario = SelectField('Tipo:', coerce=int, choices=[(g.cod_usertype, g.desc_usertype) for g in tb_usertype.query.all()], render_kw={'readonly': True})
    email = EmailField('Email:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    salvar = SubmitField('Editar')    

#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: trocar senha do usuário
#TIPO: edição
#TABELA: tb_user
#---------------------------------------------------------------------------------------------------------------------------------
class frm_editar_senha(FlaskForm):
    senhaatual = PasswordField('Senha Atual:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite a senha atual"})
    novasenha1 = PasswordField('Nova Senha:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite a nova senha"})
    novasenha2 = PasswordField('Confirme Nova Senha:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite novamente a senha"})
    salvar = SubmitField('Editar')  

##################################################################################################################################
#TIPO DE USUÁRIO
##################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: tipo de usuário
#TIPO: edição
#TABELA: tb_usertype
#---------------------------------------------------------------------------------------------------------------------------------
class frm_editar_tipousuario(FlaskForm):
    descricao = StringField('Descrição:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite a descrição do tipo de usuário"})
    status = SelectField('Situação:', coerce=int, choices=[(0, 'Ativo'),(1, 'Inativo')])
    salvar = SubmitField('Salvar')    

#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: tipo de usuário
#TIPO: visualização
#TABELA: tb_usertype
#---------------------------------------------------------------------------------------------------------------------------------
class frm_visualizar_tipousuario(FlaskForm):
    descricao = StringField('Descrição:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    status = SelectField('Situação:', coerce=int, choices=[(0, 'Ativo'),(1, 'Inativo')], render_kw={'readonly': True})
    salvar = SubmitField('Salvar')    

##################################################################################################################################
#PROJETOS
##################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: projetos
#TIPO: edição
#TABELA: tb_cliente
#---------------------------------------------------------------------------------------------------------------------------------
class frm_editar_projeto(FlaskForm):
    nome_projeto = StringField('Nome:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite o nome do projeto"})
    datainicio_projeto = DateField('Início:')
    datafim_projeto = DateField('Final:',)
    desc_projeto = TextAreaField('Descrição:', [validators.DataRequired(), validators.Length(min=1, max=500)], render_kw={"placeholder": "digite o descritivo"})
    cod_usuario = SelectField('Tipo:', coerce=int, choices=[(g.cod_user, g.name_user) for g in tb_user.query.all()])
    status_projeto = SelectField('Situação:', coerce=int, choices=[(0, 'Ativo'),(1, 'Inativo')])
    salvar = SubmitField('Salvar')    

#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: tipo de usuário
#TIPO: visualização
#TABELA: tb_cliente
#---------------------------------------------------------------------------------------------------------------------------------
class frm_visualizar_projeto(FlaskForm):
    nome_projeto = StringField('Nome:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    datainicio_projeto = DateField('Inicío:', render_kw={'readonly': True})
    datafim_projeto = DateField('Final:', render_kw={'readonly': True})
    desc_projeto = TextAreaField('Descrição:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    cod_usuario = SelectField('Tipo:', coerce=int, choices=[(g.cod_user, g.name_user) for g in tb_user.query.all()], render_kw={'readonly': True})
    status_projeto = SelectField('Situação:', coerce=int, choices=[(0, 'Ativo'),(1, 'Inativo')], render_kw={'readonly': True})
    salvar = SubmitField('Salvar')

##################################################################################################################################
#BACKLOGS
##################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: backlogs
#TIPO: edição
#TABELA: tb_cliente
#---------------------------------------------------------------------------------------------------------------------------------
class frm_editar_backlog(FlaskForm):
    titulo_backlog = StringField('Título:', [validators.DataRequired(), validators.Length(min=1, max=500)], render_kw={"placeholder": "digite o nome do projeto"})
    desc_backlog = TextAreaField('Descrição:', [validators.DataRequired(), validators.Length(min=1, max=500)], render_kw={"placeholder": "digite o nome do projeto"})
    datacriacao_backlog = DateField('Data início:')
    dataconclusao_backlog = DateField('Data conclusão:')
    obs_backlog = TextAreaField('Observações:', [validators.DataRequired(), validators.Length(min=1, max=500)], render_kw={"placeholder": "digite o descritivo"})
    status_backlog = SelectField('Situação:', coerce=int, choices=[(0, 'Ativo'),(1, 'Inativo')])
    estimativa_backlog = DecimalField('Tempo estimado em horas:')
    dependencias_backlog = TextAreaField('Dependências de outros backlogs:', [validators.DataRequired(), validators.Length(min=1, max=500)], render_kw={"placeholder": "digite se houver dependencia de outros backlogs para conclusão"})
    criterios_backlog = TextAreaField('Critérios de aceitação:', [validators.DataRequired(), validators.Length(min=1, max=500)], render_kw={"placeholder": "digite os critérios de aceitação do backlog"})
    esforco_backlog = SelectField('Matriz esforço valor:', coerce=int, choices=[(0, 'Esforço Baixo - Valor Baixo'),(1, 'Esforço Baixo - Valor Alto'),(2, 'Esforço Alto - Valor Baixo'),(3, 'Esforço Alto - Valor Alto')])
    prioridade_backlog = SelectField('Prioridade:', coerce=int, choices=[(0, 'Alta'),(1, 'Média'),(2, 'Baixa')])
    salvar = SubmitField('Salvar')    

#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: tipo de usuário
#TIPO: visualização
#TABELA: tb_cliente
#---------------------------------------------------------------------------------------------------------------------------------
class frm_visualizar_backlog(FlaskForm):
    titulo_backlog = StringField('Título:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    desc_backlog = TextAreaField('Descrição:', [validators.DataRequired(), validators.Length(min=1, max=500)], render_kw={'readonly': True})
    datacriacao_backlog = DateField('Data início:', render_kw={'readonly': True})
    dataconclusao_backlog = DateField('Data conclusão:', render_kw={'readonly': True})
    obs_backlog = TextAreaField('Observações:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    status_backlog = SelectField('Situação:', coerce=int, choices=[(0, 'Ativo'),(1, 'Inativo')], render_kw={'readonly': True})
    estimativa_backlog = DecimalField('Tempo estimado em horas:', render_kw={'readonly': True})
    dependencias_backlog = TextAreaField('Dependências de outros backlogs:', [validators.DataRequired(), validators.Length(min=1, max=500)], render_kw={'readonly': True})
    criterios_backlog = TextAreaField('Critérios de aceitação:', [validators.DataRequired(), validators.Length(min=1, max=500)], render_kw={'readonly': True})
    esforco_backlog = SelectField('Matriz esforço valor:', coerce=int, choices=[(0, 'Esforço Baixo - Valor Baixo'),(1, 'Esforço Baixo - Valor Alto'),(2, 'Esforço Alto - Valor Baixo'),(3, 'Esforço Alto - Valor Alto')], render_kw={'readonly': True})
    prioridade_backlog = SelectField('Prioridade:', coerce=int, choices=[(0, 'Alta'),(1, 'Média'),(2, 'Baixa')])    
    salvar = SubmitField('Salvar')        


