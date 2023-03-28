#importações
import os
from gerenciadorprojetos import app, db
from models import tb_user, tb_usertype,tb_clientes
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
#CLIENTES
##################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: tipo de usuário
#TIPO: edição
#TABELA: tb_cliente
#---------------------------------------------------------------------------------------------------------------------------------
class frm_editar_cliente(FlaskForm):
    nomerazao_cliente = StringField('Razão Social:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite a razão social do cliente"})
    nomefantasia_cliente = StringField('Nome Fantasia:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite o nome fantasoa do cliente"})
    end_cliente = StringField('Endereço:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite o endereço do cliente"})
    numend_cliente = StringField('Nº:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite o número do endereço do cliente"})
    bairro_cliente = StringField('Bairro:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite o bairro do cliente"})
    cidade_cliente = StringField('Cidade:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite a cidade do cliente"})
    uf_cliente = StringField('Uf:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite a uf cliente"})
    complemento_cliente = StringField('Complemento:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite o complemento do endereço do cliente"})
    cnpj_cliente = StringField('CNPJ:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite o cnpj do cliente"})
    status = SelectField('Situação:', coerce=int, choices=[(0, 'Ativo'),(1, 'Inativo')])
    salvar = SubmitField('Salvar')    

#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: tipo de usuário
#TIPO: visualização
#TABELA: tb_cliente
#---------------------------------------------------------------------------------------------------------------------------------
class frm_visualizar_cliente(FlaskForm):
    nomerazao_cliente = StringField('Razão Social:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    end_cliente = StringField('Endereço:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    numend_cliente = StringField('Nº:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    bairro_cliente = StringField('Bairro:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    cidade_cliente = StringField('Cidade:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    uf_cliente = StringField('Uf:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    complemento_cliente = StringField('Complemento:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    cnpj_cliente = StringField('CNPJ:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    status = SelectField('Situação:', coerce=int, choices=[(0, 'Ativo'),(1, 'Inativo')], render_kw={'readonly': True})
    salvar = SubmitField('Salvar')        


##################################################################################################################################
#CONTRATO
##################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: contrato
#TIPO: edição
#TABELA: tb_contrato
#---------------------------------------------------------------------------------------------------------------------------------
class frm_editar_contrato(FlaskForm):
    cod_cliente = SelectField('Cliente:', coerce=int,  choices=[(g.cod_cliente, g.nomerazao_cliente) for g in tb_clientes.query.order_by('nomerazao_cliente')])
    obj_contrato = StringField('Objeto:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite o nome do evento"})
    datavalidade_contrato = DateField('Validade:', render_kw={"placeholder": "digite o ano do evento"})
    status_contrato = SelectField('Situação:', coerce=int, choices=[(0, 'Ativo'),(1, 'Inativo')])
    salvar = SubmitField('Salvar')    

#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: contrato
#TIPO: visualização
#TABELA: tb_contrato
#---------------------------------------------------------------------------------------------------------------------------------
class frm_visualizar_contrato(FlaskForm):
    cod_cliente = SelectField('Cliente:', coerce=int,  choices=[(g.cod_cliente, g.nomerazao_cliente) for g in tb_clientes.query.order_by('nomerazao_cliente')], render_kw={'readonly': True})
    obj_contrato = StringField('Objeto:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    datavalidade_contrato = DateField('Validade:', render_kw={'readonly': True})
    status_contrato = SelectField('Situação:', coerce=int, choices=[(0, 'Ativo'),(1, 'Inativo')], render_kw={'readonly': True})
    salvar = SubmitField('Salvar')

##################################################################################################################################
#CONTRATO / ARQUIVO
##################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: contrato / arquivo
#TIPO: edição
#TABELA: tb_contrato_arquivo
#---------------------------------------------------------------------------------------------------------------------------------
class frm_editar_contrato_arquivo(FlaskForm):
    arquivo_contrato_arquivo = FileField('Arquivo:', [validators.DataRequired()], render_kw={"placeholder": "selecionar imagem"})
    salvar = SubmitField('Salvar')

##################################################################################################################################
#ADITIVOS
##################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: aditivo
#TIPO: edição
#TABELA: tb_aditivos
#---------------------------------------------------------------------------------------------------------------------------------
class frm_editar_aditivo(FlaskForm):
    desc_aditivo = StringField('Objeto:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite o descritivo do aditivo"})
    data_aditivo = DateField('Data:', render_kw={"placeholder": "digite a data do aditivo"})
    status_aditivo = SelectField('Situação:', coerce=int, choices=[(0, 'Ativo'),(1, 'Inativo')])
    salvar = SubmitField('Salvar')    

#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: aditivo
#TIPO: visualização
#TABELA: tb_aditivos
#---------------------------------------------------------------------------------------------------------------------------------
class frm_visualizar_aditivo(FlaskForm):
    desc_aditivo = StringField('Objeto:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    data_aditivo = DateField('Data:', render_kw={'readonly': True})
    status_aditivo = SelectField('Situação:', coerce=int, choices=[(0, 'Ativo'),(1, 'Inativo')], render_kw={'readonly': True})
    salvar = SubmitField('Salvar')