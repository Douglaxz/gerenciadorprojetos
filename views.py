# importação de dependencias
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, session, flash, url_for, send_from_directory,send_file,jsonify
from flask_qrcode import QRcode
from werkzeug.utils import secure_filename
import time
from datetime import date, timedelta
from gerenciadorprojetos import app, db
app.app_context().push()
db.create_all()
from sqlalchemy import func
from models import tb_user,\
    tb_usertype,\
    tb_projetos,\
    tb_backlogs,\
    tb_tarefas
from helpers import \
    frm_pesquisa, \
    frm_editar_senha,\
    frm_editar_usuario,\
    frm_visualizar_usuario, \
    frm_visualizar_tipousuario,\
    frm_editar_tipousuario,\
    frm_visualizar_projeto,\
    frm_editar_projeto,\
    frm_visualizar_backlog,\
    frm_editar_backlog,\
    frm_visualizar_tarefa,\
    frm_editar_tarefa    

# ITENS POR PÁGINA
from config import ROWS_PER_PAGE, CHAVE
from flask_bcrypt import generate_password_hash, Bcrypt, check_password_hash

import string
import random
import numbers
import os

##################################################################################################################################
#GERAL
##################################################################################################################################


@app.route("/qrcode", methods=["GET"])
def get_qrcode():
    # please get /qrcode?data=<qrcode_data>
    data = request.args.get("data", "")
    return send_file(qrcode(data, mode="raw"), mimetype="image/png")

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: index
#FUNÇÃO: mostrar pagina principal
#PODE ACESSAR: todos
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/')
def index():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login'))        
    return render_template('index.html', titulo='Bem vindos')

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: logout
#FUNÇÃO: remover seção usuário
#PODE ACESSAR: todos
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/logout', methods = ['GET', 'POST'])
def logout():
    session['usuario_logado'] = None
    flash('Logout efetuado com sucesso','success')
    return redirect(url_for('login'))

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: login
#FUNÇÃO: iniciar seção do usuário
#PODE ACESSAR: todos
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/login')
def login():
    return render_template('login2.html')

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: autenticar
#FUNÇÃO: autenticar
#PODE ACESSAR: todos
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/autenticar', methods = ['GET', 'POST'])
def autenticar():
    usuario = tb_user.query.filter_by(login_user=request.form['usuario']).first()
    senha = check_password_hash(usuario.password_user,request.form['senha'])
    if usuario:
        if senha:
            session['usuario_logado'] = usuario.login_user
            session['nomeusuario_logado'] = usuario.name_user
            session['tipousuario_logado'] = usuario.cod_usertype
            session['coduser_logado'] = usuario.cod_user
            flash(usuario.name_user + ' Usuário logado com sucesso','success')
            #return redirect('/')
            return redirect('/')
        else:
            flash('Verifique usuário e senha', 'danger')
            return redirect(url_for('login'))
    else:
        flash('Usuário não logado com sucesso','success')
        return redirect(url_for('login'))

##################################################################################################################################
#USUARIOS
##################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: usuario
#FUNÇÃO: listar
#PODE ACESSAR: administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/usuario', methods=['POST','GET'])
def usuario():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('usuario')))        
    form = frm_pesquisa()
    page = request.args.get('page', 1, type=int)
    pesquisa = form.pesquisa.data
    if pesquisa == "":
        pesquisa = form.pesquisa_responsiva.data

    if pesquisa == "" or pesquisa == None:    
        usuarios = tb_user.query\
        .join(tb_usertype, tb_usertype.cod_usertype==tb_user.cod_usertype)\
        .add_columns(tb_user.login_user, tb_user.cod_user, tb_user.name_user, tb_user.status_user, tb_usertype.desc_usertype)\
        .order_by(tb_user.name_user)\
        .paginate(page=page, per_page=ROWS_PER_PAGE, error_out=False)
    else:
        usuarios = tb_user.query\
        .filter(tb_user.name_user.ilike(f'%{pesquisa}%'))\
        .join(tb_usertype, tb_usertype.cod_usertype==tb_user.cod_usertype)\
        .add_columns(tb_user.login_user, tb_user.cod_user, tb_user.name_user, tb_user.status_user, tb_usertype.desc_usertype)\
        .order_by(tb_user.name_user)\
        .paginate(page=page, per_page=ROWS_PER_PAGE, error_out=False)


    return render_template('usuarios.html', titulo='Usuários', usuarios=usuarios, form=form)

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: novoUsuario
#FUNÇÃO: formulário inclusão
#PODE ACESSAR: administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/novoUsuario')
def novoUsuario():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('novoUsuario')))     
    form = frm_editar_usuario()
    return render_template('novoUsuario.html', titulo='Novo Usuário', form=form)

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: criarUsuario
#FUNÇÃO: inclusão no banco de dados
#PODE ACESSAR: administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/criarUsuario', methods=['POST',])
def criarUsuario():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login',proxima=url_for('criarUsuario')))      
    form = frm_editar_usuario(request.form)
    if not form.validate_on_submit():
        flash('Por favor, preencha todos os dados','danger')
        return redirect(url_for('novoUsuario'))
    nome  = form.nome.data
    status = form.status.data
    login = form.login.data
    tipousuario = form.tipousuario.data
    email = form.email.data
    #criptografar senha
    senha = generate_password_hash("teste@12345").decode('utf-8')
    usuario = tb_user.query.filter_by(name_user=nome).first()
    if usuario:
        flash ('Usuário já existe','danger')
        return redirect(url_for('index')) 
    novoUsuario = tb_user(name_user=nome, status_user=status, login_user=login, cod_usertype=tipousuario, password_user=senha, email_user=email)
    db.session.add(novoUsuario)
    db.session.commit()
    flash('Usuário criado com sucesso','success')
    return redirect(url_for('usuario'))

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: criarUsuarioexterno - NÃO DISPONIVEL NESTA VERSAO
#FUNÇÃO: formulário de inclusão
#PODE ACESSAR: todos
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/criarUsuarioexterno', methods=['POST',])
def criarUsuarioexterno():    
    nome  = request.form['nome']
    status = 0
    email = request.form['email']
    localarroba = email.find("@")
    login = email[0:localarroba]
    tipousuario = 2
    #criptografar senha
    senha = generate_password_hash(request.form['senha']).decode('utf-8')
    usuario = tb_user.query.filter_by(name_user=nome).first()
    if usuario:
        flash ('Usuário já existe','danger')
        return redirect(url_for('login')) 
    novoUsuario = tb_user(name_user=nome, status_user=status, login_user=login, cod_usertype=tipousuario, password_user=senha, email_user=email)
    db.session.add(novoUsuario)
    db.session.commit()
    flash('Usuário criado com sucesso, favor logar com ele','success')
    return redirect(url_for('login'))  

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: visualizarUsuario
#FUNÇÃO: formulario de visualização
#PODE ACESSAR: administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/visualizarUsuario/<int:id>')
def visualizarUsuario(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('visualizarUsuario')))    
    usuario = tb_user.query.filter_by(cod_user=id).first()
    form = frm_visualizar_usuario()
    form.nome.data = usuario.name_user
    form.status.data = usuario.status_user
    form.login.data = usuario.login_user
    form.tipousuario.data = usuario.cod_usertype
    form.email.data = usuario.email_user
    return render_template('visualizarUsuario.html', titulo='Visualizar Usuário', id=id, form=form)   

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: editarUsuario
#FUNÇÃO: formulario de edição
#PODE ACESSAR: administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/editarUsuario/<int:id>')
def editarUsuario(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('editarUsuario/<int:id>')))  
    usuario = tb_user.query.filter_by(cod_user=id).first()
    form = frm_editar_usuario()
    form.nome.data = usuario.name_user
    form.status.data = usuario.status_user
    form.login.data = usuario.login_user
    form.tipousuario.data = usuario.cod_usertype
    form.email.data = usuario.email_user
    return render_template('editarUsuario.html', titulo='Editar Usuário', id=id, form=form)    
       
#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: atualizarUsuario
#FUNÇÃO: alteração no banco de dados
#PODE ACESSAR: administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/atualizarUsuario', methods=['POST',])
def atualizarUsuario():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('atualizarUsuario')))          
    form = frm_editar_usuario(request.form)
    if not form.validate_on_submit():
        flash('Por favor, preencha todos os dados','danger')
        return redirect(url_for('atualizarUsuario'))
    id = request.form['id']
    usuario = tb_user.query.filter_by(cod_user=request.form['id']).first()
    usuario.name_user = form.nome.data
    usuario.status_user = form.status.data
    usuario.login_user = form.login.data
    usuario.cod_uertype = form.tipousuario.data
    db.session.add(usuario)
    db.session.commit()
    flash('Usuário alterado com sucesso','success')
    return redirect(url_for('visualizarUsuario', id=request.form['id']))

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: editarSenhaUsuario
#FUNÇÃO: formulario de edição
#PODE ACESSAR: todos
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/editarSenhaUsuario/')
def editarSenhaUsuario():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('visualizarUsuario')))    
    form = frm_editar_senha()
    return render_template('trocarsenha.html', titulo='Trocar Senha', id=id, form=form)  

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: trocarSenhaUsuario
#FUNÇÃO: alteração no banco de dados
#PODE ACESSAR: todos
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/trocarSenhaUsuario', methods=['POST',])
def trocarSenhaUsuario():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('atualizarUsuario')))          
    form = frm_editar_senha(request.form)
    if form.validate_on_submit():
        id = session['coduser_logado']
        usuario = tb_user.query.filter_by(cod_user=id).first()
        if form.senhaatual.data != usuario.password_user:
            flash('senha atual incorreta','danger')
            return redirect(url_for('editarSenhaUsuario'))

        if form.senhaatual.data != usuario.password_user:
            flash('senha atual incorreta','danger')
            return redirect(url_for('editarSenhaUsuario')) 

        if form.novasenha1.data != form.novasenha2.data:
            flash('novas senhas não coincidem','danger')
            return redirect(url_for('editarSenhaUsuario')) 
        usuario.password_user = generate_password_hash(form.novasenha1.data).decode('utf-8')
        db.session.add(usuario)
        db.session.commit()
        flash('senha alterada com sucesso!','success')
    else:
        flash('senha não alterada!','danger')
    return redirect(url_for('editarSenhaUsuario')) 

##################################################################################################################################
#TIPO DE USUARIOS
##################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: tipousuario
#FUNÇÃO: listar
#PODE ACESSAR: administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/tipousuario', methods=['POST','GET'])
def tipousuario():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('tipousuario')))         
    page = request.args.get('page', 1, type=int)
    form = frm_pesquisa()   
    pesquisa = form.pesquisa.data
    if pesquisa == "":
        pesquisa = form.pesquisa_responsiva.data
    
    if pesquisa == "" or pesquisa == None:     
        tiposusuario = tb_usertype.query.order_by(tb_usertype.desc_usertype)\
        .paginate(page=page, per_page=ROWS_PER_PAGE , error_out=False)
    else:
        tiposusuario = tb_usertype.query.order_by(tb_usertype.desc_usertype)\
        .filter(tb_usertype.desc_usertype.ilike(f'%{pesquisa}%'))\
        .paginate(page=page, per_page=ROWS_PER_PAGE, error_out=False)        
    return render_template('tipousuarios.html', titulo='Tipo Usuário', tiposusuario=tiposusuario, form=form)

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: novoTipoUsuario
#FUNÇÃO: formulario de inclusão
#PODE ACESSAR: administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/novoTipoUsuario')
def novoTipoUsuario():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('novoTipoUsuario'))) 
    form = frm_editar_tipousuario()
    return render_template('novoTipoUsuario.html', titulo='Novo Tipo Usuário', form=form)

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: criarTipoUsuario
#FUNÇÃO: inclusão no banco de dados
#PODE ACESSAR: administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/criarTipoUsuario', methods=['POST',])
def criarTipoUsuario():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('criarTipoUsuario')))     
    form = frm_editar_tipousuario(request.form)
    if not form.validate_on_submit():
        flash('Por favor, preencha todos os dados','danger')
        return redirect(url_for('criarTipoUsuario'))
    desc  = form.descricao.data
    status = form.status.data
    tipousuario = tb_usertype.query.filter_by(desc_usertype=desc).first()
    if tipousuario:
        flash ('Tipo Usuário já existe','danger')
        return redirect(url_for('tipousuario')) 
    novoTipoUsuario = tb_usertype(desc_usertype=desc, status_usertype=status)
    flash('Tipo de usuário criado com sucesso!','success')
    db.session.add(novoTipoUsuario)
    db.session.commit()
    return redirect(url_for('tipousuario'))

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: visualizarTipoUsuario
#FUNÇÃO: formulario de visualização
#PODE ACESSAR: administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/visualizarTipoUsuario/<int:id>')
def visualizarTipoUsuario(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('visualizarTipoUsuario')))  
    tipousuario = tb_usertype.query.filter_by(cod_usertype=id).first()
    form = frm_visualizar_tipousuario()
    form.descricao.data = tipousuario.desc_usertype
    form.status.data = tipousuario.status_usertype
    return render_template('visualizarTipoUsuario.html', titulo='Visualizar Tipo Usuário', id=id, form=form)   

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: editarTipoUsuario
##FUNÇÃO: formulário de edição
#PODE ACESSAR: administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/editarTipoUsuario/<int:id>')
def editarTipoUsuario(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('editarTipoUsuario')))  
    tipousuario = tb_usertype.query.filter_by(cod_usertype=id).first()
    form = frm_editar_tipousuario()
    form.descricao.data = tipousuario.desc_usertype
    form.status.data = tipousuario.status_usertype
    return render_template('editarTipoUsuario.html', titulo='Editar Tipo Usuário', id=id, form=form)   

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: atualizarTipoUsuario
#FUNÇÃO: alterar informações no banco de dados
#PODE ACESSAR: administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/atualizarTipoUsuario', methods=['POST',])
def atualizarTipoUsuario():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('atualizarTipoUsuario')))      
    form = frm_editar_tipousuario(request.form)
    if form.validate_on_submit():
        id = request.form['id']
        tipousuario = tb_usertype.query.filter_by(cod_usertype=request.form['id']).first()
        tipousuario.desc_usertype = form.descricao.data
        tipousuario.status_usertype = form.status.data
        db.session.add(tipousuario)
        db.session.commit()
        flash('Tipo de usuário atualizado com sucesso!','success')
    else:
        flash('Favor verificar os campos!','danger')
    return redirect(url_for('visualizarTipoUsuario', id=request.form['id']))


##################################################################################################################################
#PROJETOS
##################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: cliente
#FUNÇÃO: listar
#PODE ACESSAR: administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/projeto', methods=['POST','GET'])
def projeto():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('cliente')))         
    page = request.args.get('page', 1, type=int)
    form = frm_pesquisa()   
    pesquisa = form.pesquisa.data
    if pesquisa == "":
        pesquisa = form.pesquisa_responsiva.data
    
    if pesquisa == "" or pesquisa == None:     
        projetos = tb_projetos.query.order_by(tb_projetos.nome_projeto)\
        .paginate(page=page, per_page=ROWS_PER_PAGE , error_out=False)
    else:
        projetos = tb_projetos.query.order_by(tb_projetos.nome_projeto)\
        .filter(tb_projetos.nome_projeto.ilike(f'%{pesquisa}%'))\
        .paginate(page=page, per_page=ROWS_PER_PAGE, error_out=False)        
    return render_template('projetos.html', titulo='Projetos', projetos=projetos, form=form)

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: novoProjeto
#FUNÇÃO: formulario de inclusão
#PODE ACESSAR: administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/novoProjeto')
def novoProjeto():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('novoProjeto'))) 
    form = frm_editar_projeto()
    return render_template('novoProjeto.html', titulo='Novo Projeto', form=form)

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: criarProjeto
#FUNÇÃO: inclusão no banco de dados
#PODE ACESSAR: administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/criarProjeto', methods=['POST',])
def criarProjeto():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('criarProjeto')))     
    form = frm_editar_projeto(request.form)
    if not form.validate_on_submit():
        flash('Por favor, preencha todos os dados','danger')
        return redirect(url_for('criarProjeto'))
    nome_projeto  = form.nome_projeto.data
    datainicio_projeto = form.datainicio_projeto.data
    datafim_projeto = form.datafim_projeto.data
    desc_projeto = form.desc_projeto.data
    cod_usuario = form.cod_usuario.data
    status_projeto = form.status_projeto.data
    projeto = tb_projetos.query.filter_by(nome_projeto=nome_projeto).first()
    if projeto:
        flash ('Projeto já existe','danger')
        return redirect(url_for('cliente')) 
    novoProjeto = tb_projetos(nome_projeto=nome_projeto,\
                            datainicio_projeto = datainicio_projeto,\
                            datafim_projeto = datafim_projeto,\
                            desc_projeto = desc_projeto,\
                            cod_usuario = cod_usuario,\
                            status_projeto=status_projeto)
    flash('Projeto criado com sucesso!','success')
    db.session.add(novoProjeto)
    db.session.commit()
    return redirect(url_for('projeto'))

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: visualizarProjeto
#FUNÇÃO: formulario de visualização
#PODE ACESSAR: administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/visualizarProjeto/<int:id>')
def visualizarProjeto(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('visualizarProjeto')))  
    projeto = tb_projetos.query.filter_by(cod_projeto=id).first()
    backlogs = tb_backlogs.query.filter_by(cod_projeto=id).all()
    form = frm_visualizar_projeto()
    form.nome_projeto.data = projeto.nome_projeto
    form.datainicio_projeto.data = projeto.datainicio_projeto
    form.datafim_projeto.data = projeto.datafim_projeto
    form.desc_projeto.data = projeto.desc_projeto
    form.cod_usuario.data = projeto.cod_usuario
    form.status_projeto.data = projeto.status_projeto
    return render_template('visualizarProjeto.html', titulo='Visualizar Projeto', id=id, form=form, backlogs=backlogs)   

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: editarProjeto
##FUNÇÃO: formulário de edição
#PODE ACESSAR: administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/editarProjeto/<int:id>')
def editarProjeto(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('editarProjeto')))  
    projeto = tb_projetos.query.filter_by(cod_projeto=id).first()
    form = frm_editar_projeto()
    form.nome_projeto.data = projeto.nome_projeto
    form.datainicio_projeto.data = projeto.datainicio_projeto
    form.datafim_projeto.data = projeto.datafim_projeto
    form.desc_projeto.data = projeto.desc_projeto
    form.cod_usuario.data = projeto.cod_usuario
    form.status_projeto.data = projeto.status_projeto
    return render_template('editarProjeto.html', titulo='Editar Projeto', id=id, form=form)   

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: atualizarProjeto
#FUNÇÃO: alterar informações no banco de dados
#PODE ACESSAR: administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/atualizarProjeto', methods=['POST',])
def atualizarProjeto():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('atualizarCliente')))      
    form = frm_editar_projeto(request.form)
    if form.validate_on_submit():
        id = request.form['id']
        projeto = tb_projetos.query.filter_by(cod_projeto=request.form['id']).first()
        projeto.nome_projeto = form.nome_projeto.data
        projeto.datainicio_projeto = form.datainicio_projeto.data
        projeto.datafim_projeto = form.datafim_projeto.data
        projeto.desc_projeto = form.desc_projeto.data
        projeto.cod_usuario = form.cod_usuario.data
        projeto.status_projeto = form.status_projeto.data
        db.session.add(projeto)
        db.session.commit()
        flash('Projeto atualizado com sucesso!','success')
    else:
        flash('Favor verificar os campos!','danger')
    return redirect(url_for('visualizarProjeto', id=request.form['id']))

##################################################################################################################################
#BACKLOG
##################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: novoBacklog
#FUNÇÃO: formulario de inclusão
#PODE ACESSAR: administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/novoBacklog/<int:id>')
def novoBacklog(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('novoBacklog'))) 
    form = frm_editar_backlog()
    return render_template('novoBacklog.html', titulo='Novo Backlog', form=form,id=id)

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: criarBacklog
#FUNÇÃO: inclusão no banco de dados
#PODE ACESSAR: administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/criarBacklog', methods=['POST',])
def criarBacklog():
    id = request.form['id']
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('novoBacklog',id=id)))     
    form = frm_editar_backlog(request.form)
    if not form.validate_on_submit():
        flash('Por favor, preencha todos os dados','danger')
        return redirect(url_for('novoBacklog',id=id))
    titulo_backlog  = form.titulo_backlog.data
    desc_backlog  = form.desc_backlog.data
    datacriacao_backlog = form.datacriacao_backlog.data
    dataconclusao_backlog = form.dataconclusao_backlog.data
    prioridade_backlog = form.prioridade_backlog.data
    estimativa_backlog = form.estimativa_backlog.data
    dependencias_backlog = form.dependencias_backlog.data
    datacriacao_backlog = form.datacriacao_backlog.data
    esforco_backlog = form.esforco_backlog.data
    status_backlog = form.status_backlog.data
    obs_backlog = form.obs_backlog.data
    criterios_backlog = form.criterios_backlog.data
    cod_projeto = id
    backlog = tb_backlogs.query.filter_by(desc_backlog=desc_backlog).first()
    if backlog:
        flash ('Blacklog já existe','danger')
        return redirect(url_for('visualizarProjeto',id=id)) 
    novoBacklog = tb_backlogs(desc_backlog=desc_backlog,\
                            titulo_backlog = titulo_backlog,\
                            datacriacao_backlog = datacriacao_backlog,\
                            dataconclusao_backlog = dataconclusao_backlog,\
                            prioridade_backlog = prioridade_backlog,\
                            estimativa_backlog = estimativa_backlog,\
                            dependencias_backlog = dependencias_backlog,\
                            esforco_backlog = esforco_backlog,\
                            obs_backlog = obs_backlog,\
                            criterios_backlog = criterios_backlog,\
                            cod_projeto = cod_projeto,\
                            status_backlog=status_backlog)
    flash('Backlog criado com sucesso!','success')
    db.session.add(novoBacklog)
    db.session.commit()
    return redirect(url_for('visualizarProjeto',id=id))

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: visualizarBacklog
#FUNÇÃO: formulario de visualização
#PODE ACESSAR: administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/visualizarBacklog/<int:id><int:idprojeto>')
def visualizarBacklog(id,idprojeto):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('visualizarBacklog')))  
    backlog = tb_backlogs.query.filter_by(cod_backlog=id).first()
    form = frm_visualizar_backlog()
    form.desc_backlog.data = backlog.desc_backlog
    form.titulo_backlog.data = backlog.titulo_backlog
    form.datacriacao_backlog.data = backlog.datacriacao_backlog
    form.prioridade_backlog.data = backlog.prioridade_backlog
    form.estimativa_backlog.data = backlog.estimativa_backlog
    form.dependencias_backlog.data = backlog.dependencias_backlog
    form.datacriacao_backlog.data = backlog.datacriacao_backlog
    form.obs_backlog.data = backlog.dataconclusao_backlog
    form.esforco_backlog.data = backlog.esforco_backlog
    form.status_backlog.data = backlog.status_backlog
    form.obs_backlog.data = backlog.obs_backlog
    form.criterios_backlog.data = backlog.criterios_backlog
    
    return render_template('visualizarBacklog.html', titulo='Visualizar Backlog', id=id, form=form,idprojeto=idprojeto)   

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: editarBacklog
##FUNÇÃO: formulário de edição
#PODE ACESSAR: administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/editarBacklog/<int:id>')
def editarBacklog(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('editarBacklog')))  
    backlog = tb_backlogs.query.filter_by(cod_backlog=id).first()
    form = frm_editar_backlog()
    form.titulo_backlog.data = backlog.titulo_backlog
    form.desc_backlog.data = backlog.desc_backlog
    form.datacriacao_backlog.data = backlog.datacriacao_backlog
    form.prioridade_backlog.data = backlog.prioridade_backlog
    form.estimativa_backlog.data = backlog.estimativa_backlog
    form.dependencias_backlog.data = backlog.dependencias_backlog
    form.datacriacao_backlog.data = backlog.datacriacao_backlog
    form.obs_backlog.data = backlog.dataconclusao_backlog
    form.esforco_backlog.data = backlog.esforco_backlog
    form.status_backlog.data = backlog.status_backlog
    form.obs_backlog.data = backlog.obs_backlog
    form.criterios_backlog.data = backlog.criterios_backlog
    idprojeto = backlog.cod_projeto
    
    return render_template('editarBacklog.html', titulo='Editar Backlog', id=id, form=form, idprojeto=idprojeto)   

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: atualizarBacklog
#FUNÇÃO: alterar informações no banco de dados
#PODE ACESSAR: administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/atualizarBacklog', methods=['POST',])
def atualizarBacklog():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('atualizarBacklog')))      
    form = frm_editar_backlog(request.form)
    if form.validate_on_submit():
        id = request.form['id']
        idprojeto = request.form['idprojeto']
        backlog = tb_backlogs.query.filter_by(cod_backlog=request.form['id']).first()
        backlog.titulo_backlog = form.titulo_backlog.data
        backlog.desc_backlog = form.desc_backlog.data
        backlog.prioridade_backlog = form.prioridade_backlog.data
        backlog.estimativa_backlog = form.estimativa_backlog.data
        backlog.dependencias_backlog = form.dependencias_backlog.data
        backlog.criterios_backlog = form.criterios_backlog.data
        backlog.datacriacao_backlog = form.datacriacao_backlog.data
        backlog.dataconclusao_backlog = form.dataconclusao_backlog.data
        backlog.obs_backlog = form.obs_backlog.data
        backlog.status_backlog = form.status_backlog.data
        backlog.esforco_backlog = form.esforco_backlog.data 
        backlog.criterios_backlog = form.criterios_backlog.data 
        db.session.add(backlog)
        db.session.commit()
        flash('Backlog atualizado com sucesso!','success')
    else:
        flash('Favor verificar os campos!','danger')
    return redirect(url_for('visualizarBacklog', id=request.form['id'], idprojeto=idprojeto))

##################################################################################################################################
#TAREFAS
##################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: novoTarefa
#FUNÇÃO: formulario de inclusão
#PODE ACESSAR: administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/novoTarefa/<int:id>')
def novoTarefa(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('novoTarefa'))) 
    form = frm_editar_backlog()
    return render_template('novoTarefa.html', titulo='Novo Tarefa', form=form,id=id)

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: criarTarefa
#FUNÇÃO: inclusão no banco de dados
#PODE ACESSAR: administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/criarTarefa', methods=['POST',])
def criarTarefa():
    id = request.form['id']
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('novoTarefa',id=id)))     
    form = frm_editar_tarefa(request.form)
    if not form.validate_on_submit():
        flash('Por favor, preencha todos os dados','danger')
        return redirect(url_for('novoTarefa',id=id))
    titulo_tarefa  = form.titulo_tarefa.data
    descricao_tarefa  = form.descricao_tarefa.data
    datacriacao_tarefa= form.datacriacao_tarefa.data
    dataconclusao_tarefa = form.dataconclusao_tarefa.data
    prioridade_tarefa = form.prioridade_tarefa.data
    estimativa_tarefa = form.estimativa_tarefa.data
    status_tarefa = form.status_tarefa.data
    obs_tarefa = form.obs_tarefa.data
    cod_usuario = form.cod_usuario.data
    tarefa = tb_tarefas.query.filter_by(descricao_tarefa=descricao_tarefa).first()
    if tarefa:
        flash ('Blacklog já existe','danger')
        return redirect(url_for('visualizarProjeto',id=id)) 
    novoTarefa = tb_backlogs(titulo_tarefa=titulo_tarefa,\
                            descricao_tarefa = descricao_tarefa,\
                            datacriacao_tarefa = datacriacao_tarefa,\
                            dataconclusao_tarefa = dataconclusao_tarefa,\
                            prioridade_tarefa = prioridade_tarefa,\
                            estimativa_tarefa = estimativa_tarefa,\
                            obs_tarefa = obs_tarefa,\
                            cod_usuario = cod_usuario,\
                            cod_backlog = id,\
                            status_tarefa=status_tarefa)
    flash('Tarefa criado com sucesso!','success')
    db.session.add(novoTarefa)
    db.session.commit()
    return redirect(url_for('visualizarBacklog',id=id))

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: visualizarTarefa
#FUNÇÃO: formulario de visualização
#PODE ACESSAR: administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/visualizarTarefa/<int:id><int:idbacklog>')
def visualizarTarefa(id,idbacklog):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('visualizarTarefa')))  
    tarefa = tb_tarefas.query.filter_by(cod_tarefa=id).first()
    form = frm_visualizar_tarefa()
    form.titulo_tarefa.data = tarefa.titulo_tarefa
    form.descricao_tarefa.data = tarefa.descricao_tarefa
    form.datacriacao_tarefa.data = tarefa.datacriacao_tarefa
    form.dataconclusao_tarefa.data = tarefa.dataconclusao_tarefa
    form.prioridade_tarefa.data = tarefa.prioridade_tarefa
    form.estimativa_tarefa.data = tarefa.estimativa_tarefa
    form.status_tarefa.data = tarefa.status_tarefa
    form.obs_tarefa.data = tarefa.obs_tarefa
    form.cod_usuario.data = tarefa.cod_usuario
    
    return render_template('visualizarTarefa.html', titulo='Visualizar Tarefa', id=id, form=form,idbacklog=idbacklog)   

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: editarTarefa
##FUNÇÃO: formulário de edição
#PODE ACESSAR: administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/editarTarefa/<int:id>')
def editarTarefa(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('editarTarefa')))  
    tarefa = tb_tarefas.query.filter_by(cod_tarefa=id).first()
    form = frm_editar_tarefa()
    form.titulo_tarefa.data = tarefa.titulo_tarefa
    form.descricao_tarefa.data = tarefa.descricao_tarefa
    form.datacriacao_tarefa.data = tarefa.datacriacao_tarefa
    form.dataconclusao_tarefa.data = tarefa.dataconclusao_tarefa
    form.prioridade_tarefa.data = tarefa.prioridade_tarefa
    form.estimativa_tarefa.data = tarefa.estimativa_tarefa
    form.status_tarefa.data = tarefa.status_tarefa
    form.obs_tarefa.data = tarefa.obs_tarefa
    form.cod_usuario.data = tarefa.cod_usuario
    idbacklog = tarefa.cod_backlog
    
    return render_template('editarTarefa.html', titulo='Editar Tarefa', id=id, form=form, idbacklog=idbacklog)   

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: atualizarTarefa
#FUNÇÃO: alterar informações no banco de dados
#PODE ACESSAR: administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/atualizarTarefa', methods=['POST',])
def atualizarTarefa():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('atualizarTarefa')))      
    form = frm_editar_backlog(request.form)
    if form.validate_on_submit():
        id = request.form['id']
        idbacklog = request.form['idbacklog']
        tarefa = tb_tarefas.query.filter_by(cod_tarefa=request.form['id']).first()
        tarefa.titulo_tarefa = form.titulo_tarefa.data
        tarefa.descricao_tarefa = form.descricao_tarefa.data
        tarefa.prioridade_tarefa = form.prioridade_tarefa.data
        tarefa.estimativa_tarefa = form.estimativa_tarefa.data
        tarefa.datacriacao_tarefa = form.datacriacao_tarefa.data
        tarefa.dataconclusao_tarefa = form.dataconclusao_tarefa.data
        tarefa.obs_tarefa = form.obs_tarefa.data
        tarefa.status_tarefa = form.status_tarefa.data
        tarefa.cod_usuario = form.cod_usuario.data
        db.session.add(tarefa)
        db.session.commit()
        flash('Tarefa atualizado com sucesso!','success')
    else:
        flash('Favor verificar os campos!','danger')
    return redirect(url_for('visualizarTarefa', id=request.form['id'], idbacklog=idbacklog))