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
    tb_clientes,\
    tb_contratos,\
    tb_contrato_arquivos,\
    tb_aditivos
from helpers import \
    frm_pesquisa, \
    frm_editar_senha,\
    frm_editar_usuario,\
    frm_visualizar_usuario, \
    frm_visualizar_tipousuario,\
    frm_editar_tipousuario,\
    frm_visualizar_cliente,\
    frm_editar_cliente,\
    frm_editar_contrato,\
    frm_visualizar_contrato,\
    frm_editar_aditivo,\
    frm_visualizar_aditivo,\
    frm_editar_contrato_arquivo
    

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
#CLIENTE
##################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: cliente
#FUNÇÃO: listar
#PODE ACESSAR: administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/cliente', methods=['POST','GET'])
def cliente():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('cliente')))         
    page = request.args.get('page', 1, type=int)
    form = frm_pesquisa()   
    pesquisa = form.pesquisa.data
    if pesquisa == "":
        pesquisa = form.pesquisa_responsiva.data
    
    if pesquisa == "" or pesquisa == None:     
        clientes = tb_clientes.query.order_by(tb_clientes.nomerazao_cliente)\
        .paginate(page=page, per_page=ROWS_PER_PAGE , error_out=False)
    else:
        clientes = tb_clientes.query.order_by(tb_clientes.nomerazao_cliente)\
        .filter(tb_clientes.nomerazao_cliente.ilike(f'%{pesquisa}%'))\
        .paginate(page=page, per_page=ROWS_PER_PAGE, error_out=False)        
    return render_template('cliente.html', titulo='Cliente', clientes=clientes, form=form)

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: novoCliente
#FUNÇÃO: formulario de inclusão
#PODE ACESSAR: administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/novoCliente')
def novoCliente():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('novoCliente'))) 
    form = frm_editar_cliente()
    return render_template('novoCliente.html', titulo='Novo Cliente', form=form)

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: criarCliente
#FUNÇÃO: inclusão no banco de dados
#PODE ACESSAR: administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/criarCliente', methods=['POST',])
def criarCliente():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('criarCliente')))     
    form = frm_editar_cliente(request.form)
    if not form.validate_on_submit():
        flash('Por favor, preencha todos os dados','danger')
        return redirect(url_for('criarCliente'))
    nomerazao_cliente  = form.nomerazao_cliente.data
    nomefantasia_cliente = form.nomefantasia_cliente.data
    end_cliente = form.end_cliente.data
    numend_cliente = form.numend_cliente.data
    bairro_cliente = form.bairro_cliente.data
    cidade_cliente = form.cidade_cliente.data
    uf_cliente = form.uf_cliente.data
    complemento_cliente = form.complemento_cliente.data
    cnpj_cliente = form.nomerazao_cliente.data
    status = form.status.data
    cliente = tb_clientes.query.filter_by(cnpj_cliente=cnpj_cliente).first()
    if cliente:
        flash ('Patrocinador já existe','danger')
        return redirect(url_for('cliente')) 
    novoCliente = tb_clientes(nomerazao_cliente=nomerazao_cliente,\
                            nomefantasia_cliente = nomefantasia_cliente,\
                            end_cliente = end_cliente,\
                            numend_cliente = numend_cliente,\
                            bairro_cliente = bairro_cliente,\
                            cidade_cliente = cidade_cliente,\
                            uf_cliente = uf_cliente,\
                            complemento_cliente = complemento_cliente,\
                            cnpj_cliente = cnpj_cliente,\
                            status_cliente=status)
    flash('Cliente criado com sucesso!','success')
    db.session.add(novoCliente)
    db.session.commit()
    return redirect(url_for('cliente'))

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: visualizarCliente
#FUNÇÃO: formulario de visualização
#PODE ACESSAR: administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/visualizarCliente/<int:id>')
def visualizarCliente(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('visualizarCliente')))  
    cliente = tb_clientes.query.filter_by(cod_cliente=id).first()
    form = frm_visualizar_cliente()
    form.nomerazao_cliente.data = cliente.nomerazao_cliente
    form.nomefantasia_cliente.data = cliente.nomefantasia_cliente
    form.end_cliente.data = cliente.end_cliente
    form.numend_cliente.data = cliente.numend_cliente
    form.bairro_cliente.data = cliente.bairro_cliente
    form.cidade_cliente.data = cliente.cidade_cliente
    form.uf_cliente.data = cliente.uf_cliente
    form.complemento_cliente.data = cliente.complemento_cliente
    form.cnpj_cliente.data = cliente.cnpj_cliente
    form.status.data = cliente.status_cliente
    return render_template('visualizarCliente.html', titulo='Visualizar Cliente', id=id, form=form)   

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: editarCliente
##FUNÇÃO: formulário de edição
#PODE ACESSAR: administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/editarCliente/<int:id>')
def editarCliente(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('editarCliente')))  
    cliente = tb_clientes.query.filter_by(cod_cliente=id).first()
    form = frm_editar_cliente()
    form.nomerazao_cliente.data = cliente.nomerazao_cliente
    form.nomefantasia_cliente.data = cliente.nomefantasia_cliente
    form.end_cliente.data = cliente.end_cliente
    form.numend_cliente.data = cliente.numend_cliente
    form.bairro_cliente.data = cliente.bairro_cliente
    form.cidade_cliente.data = cliente.cidade_cliente
    form.uf_cliente.data = cliente.uf_cliente
    form.complemento_cliente.data = cliente.complemento_cliente
    form.cnpj_cliente.data = cliente.cnpj_cliente
    form.status.data = cliente.status_cliente
    return render_template('editarCliente.html', titulo='Editar Cliente', id=id, form=form)   

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: atualizarCliente
#FUNÇÃO: alterar informações no banco de dados
#PODE ACESSAR: administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/atualizarCliente', methods=['POST',])
def atualizarCliente():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('atualizarCliente')))      
    form = frm_editar_cliente(request.form)
    if form.validate_on_submit():
        id = request.form['id']
        cliente = tb_clientes.query.filter_by(cod_cliente=request.form['id']).first()
        cliente.nomerazao_cliente = form.nomerazao_cliente.data
        cliente.nomefantasia_cliente = form.nomefantasia_cliente.data
        cliente.end_cliente = form.end_cliente.data
        cliente.numend_cliente = form.numend_cliente.data
        cliente.bairro_cliente = form.bairro_cliente.data
        cliente.cidade_cliente = form.cidade_cliente.data
        cliente.uf_cliente = form.uf_cliente.data
        cliente.complemento_cliente = form.complemento_cliente.data
        cliente.cnpj_cliente = form.cnpj_cliente.data
        cliente.status_cliente = form.status.data
        db.session.add(cliente)
        db.session.commit()
        flash('Patrocinador atualizado com sucesso!','success')
    else:
        flash('Favor verificar os campos!','danger')
    return redirect(url_for('visualizarCliente', id=request.form['id']))

##################################################################################################################################
#CONTRATOS
##################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: contrato
#FUNÇÃO: listar
#PODE ACESSAR: administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/contrato', methods=['POST','GET'])
def contrato():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('evento')))         
    page = request.args.get('page', 1, type=int)
    form = frm_pesquisa()   
    pesquisa = form.pesquisa.data
    if pesquisa == "":
        pesquisa = form.pesquisa_responsiva.data
    
    if pesquisa == "" or pesquisa == None:     
        contratos = tb_contratos.query\
        .join(tb_clientes, tb_clientes.cod_cliente==tb_contratos.cod_cliente)\
        .add_columns(tb_clientes.nomerazao_cliente, tb_contratos.cod_contrato, tb_contratos.datavalidade_contrato, tb_contratos.status_contrato)\
        .order_by(tb_contratos.datavalidade_contrato)\
        .paginate(page=page, per_page=ROWS_PER_PAGE , error_out=False)
    else:
        contratos = tb_contratos.query\
        .join(tb_clientes, tb_clientes.cod_cliente==tb_contratos.cod_cliente)\
        .add_columns(tb_clientes.nomerazao_cliente, tb_contratos.cod_contrato, tb_contratos.datavalidade_contrato, tb_contratos.status_contrato)\
        .order_by(tb_contratos.datavalidade_contrato)\
        .filter(tb_contratos.nomerazao_cliente.ilike(f'%{pesquisa}%'))\
        .paginate(page=page, per_page=ROWS_PER_PAGE, error_out=False)        
    return render_template('contrato.html', titulo='Eventos', contratos=contratos, form=form)

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: novoContrato
#FUNÇÃO: formulario de inclusão
#PODE ACESSAR: administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/novoContrato')
def novoContrato():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('novoContrato'))) 
    form = frm_editar_contrato()
    return render_template('novoContrato.html', titulo='Novo Contrato', form=form)

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: criarContrato
#FUNÇÃO: inclusão no banco de dados
#PODE ACESSAR: administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/criarContrato', methods=['POST',])
def criarContrato():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('criarContrato')))     
    form = frm_editar_contrato(request.form)
    if not form.validate_on_submit():
        flash('Por favor, preencha todos os dados','danger')
        return redirect(url_for('criarContrato'))
    cod_cliente  = form.cod_cliente.data
    obj_contrato = form.obj_contrato.data
    datavalidade_contrato = form.datavalidade_contrato.data
    status_contrato = form.status_contrato.data
    contrato = tb_contratos.query.filter_by(obj_contrato=obj_contrato).first()
    if contrato:
        flash ('Contrato já existe','danger')
        return redirect(url_for('cliente')) 
    novoContrato = tb_contratos(cod_cliente=cod_cliente,\
                            obj_contrato = obj_contrato,\
                            datavalidade_contrato = datavalidade_contrato,\
                            status_contrato=status_contrato)
    flash('Contrato criado com sucesso!','success')
    db.session.add(novoContrato)
    db.session.commit()
    return redirect(url_for('contrato'))

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: visualizarContrato
#FUNÇÃO: formulario de visualização
#PODE ACESSAR: administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/visualizarContrato/<int:id>')
def visualizarContrato(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('visualizarContrato')))  
    contrato = tb_contratos.query.filter_by(cod_contrato=id).first()
    contrato_arquivos = tb_contrato_arquivos.query.filter_by(cod_contrato=id).all()

    aditivos = tb_aditivos.query.order_by(tb_aditivos.data_aditivo)\
        .filter(tb_aditivos.cod_contrato == id)
    nomes_arquivos = [arquivo.arquivo_contrato_arquivo for arquivo in contrato_arquivos]
    form = frm_visualizar_contrato()
    form.cod_cliente.data = contrato.cod_cliente
    form.obj_contrato.data = contrato.obj_contrato
    form.datavalidade_contrato.data = contrato.datavalidade_contrato
    form.status_contrato.data = contrato.status_contrato
    return render_template('visualizarContrato.html', titulo='Visualizar Contrato', id=id, form=form,nomes_arquivos=nomes_arquivos,contrato_arquivos=contrato_arquivos,aditivos=aditivos)   

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: editarContrato
##FUNÇÃO: formulário de edição
#PODE ACESSAR: administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/editarContrato/<int:id>')
def editarContrato(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('editarContrato')))  
    contrato = tb_contratos.query.filter_by(cod_contrato=id).first()
    form = frm_editar_contrato()
    form.cod_cliente.data = contrato.cod_cliente
    form.obj_contrato.data = contrato.obj_contrato
    form.datavalidade_contrato.data = contrato.datavalidade_contrato
    form.status_contrato.data = contrato.status_contrato
    return render_template('editarContrato.html', titulo='Editar Contrato', id=id, form=form)   

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: atualizarContrato
#FUNÇÃO: alterar informações no banco de dados
#PODE ACESSAR: administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/atualizarContrato', methods=['POST',])
def atualizarContrato():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('atualizarContrato')))      
    form = frm_editar_contrato(request.form)
    if form.validate_on_submit():
        id = request.form['id']
        contrato = tb_contratos.query.filter_by(cod_contrato=request.form['id']).first()
        contrato.cod_cliente = form.cod_cliente.data
        contrato.obj_contrato = form.obj_contrato.data
        contrato.datavalidade_contrato = form.datavalidade_contrato.data
        contrato.status_contrato = form.status_contrato.data
        db.session.add(contrato)
        db.session.commit()
        flash('Contrato atualizado com sucesso!','success')
    else:
        flash('Favor verificar os campos!','danger')
    return redirect(url_for('visualizarContrato', id=request.form['id']))

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: novoContratoArquivo
#FUNÇÃO: inclusão de arquivos banco de dados
#PODE ACESSAR: administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/novoContratoArquivo/<int:id>')
def novoContratoArquivo(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('novoSolicitacaoFoto'))) 
    form = frm_editar_contrato_arquivo()
    return render_template('novoContratoArquivo.html', titulo='Inserir imagens', form=form, id=id)

@app.route('/contrato_arquivo/<int:id>', methods=['POST'])
def contrato_arquivo(id):
    arquivo = request.files['arquivo_contrato_arquivo']
    nome_arquivo = secure_filename(arquivo.filename)
    nome_base, extensao = os.path.splitext(nome_arquivo)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    nome_unico = f"{nome_base}_{timestamp}{extensao}"
    caminho_arquivo = os.path.join(app.config['UPLOAD_PATH'], nome_unico)
    arquivo.save(caminho_arquivo)

    flash('Arquivo carregado com sucesso!','success')
    novoContratoArquivo = tb_contrato_arquivos(cod_contrato=id,arquivo_contrato_arquivo=nome_unico)
    db.session.add(novoContratoArquivo)
    db.session.commit()
    return redirect(url_for('novoContratoArquivo',id=id))


@app.route('/excluirArquivo/<int:id>')
def excluirArquivo(id):
    arquivo_foto = tb_contrato_arquivos.query.filter_by(cod_contrato_arquivo=id).first()
    idcontrato = arquivo_foto.cod_solicitacao
    caminho_arquivo = os.path.join(app.config['UPLOAD_PATH'], arquivo_foto.arquivo_contrato_arquivo)
    try:
        os.remove(caminho_arquivo)
        msg = "Arquivo excluído com sucesso!"
    except Exception as e:
        msg = f"Ocorreu um erro ao excluir o arquivo: {e}"

    apagarArqvuio = tb_contrato_arquivos.query.filter_by(cod_contrato_arquivo=id).one()
    db.session.delete(apagarArqvuio)
    db.session.commit()

    flash('Arquivo apagado com sucesso!','success')
    return redirect(url_for('visualizarContrato',id=idcontrato))


##################################################################################################################################
#ADITIVOS
##################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: novoAditivo
#FUNÇÃO: formulario de inclusão
#PODE ACESSAR: administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/novoAditivo/<int:id>')
def novoAditivo(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('novoAditivo'))) 
    form = frm_editar_aditivo()
    return render_template('novoAditivo.html', titulo='Novo Aditivo', form=form,id=id)

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: criarAditivo
#FUNÇÃO: inclusão no banco de dados
#PODE ACESSAR: administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/criarAditivo/<int:id>', methods=['POST',])
def criarAditivo(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('criarAditivo')))     
    form = frm_editar_aditivo(request.form)
    if not form.validate_on_submit():
        flash('Por favor, preencha todos os dados','danger')
        return redirect(url_for('criarContrato'))
    cod_contrato  = id
    desc_aditivo = form.desc_aditivo.data
    data_aditivo = form.data_aditivo.data
    status_aditivo = form.status_aditivo.data
    aditivo = tb_aditivos.query.filter_by(desc_aditivo=desc_aditivo).first()
    if aditivo:
        flash ('Aditivo já existe','danger')
        return redirect(url_for('aditivo')) 
    novoAditivo = tb_aditivos(cod_contrato=cod_contrato,\
                            desc_aditivo = desc_aditivo,\
                            data_aditivo = data_aditivo,\
                            status_aditivo=status_aditivo)
    flash('Aditivo criado com sucesso!','success')
    db.session.add(novoAditivo)
    db.session.commit()
    return redirect(url_for('visualizarContrato',id=id))

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: visualizarAditivo
#FUNÇÃO: formulario de visualização
#PODE ACESSAR: administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/visualizarAditivo/<int:id>')
def visualizarAditivo(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('visualizarAditivo')))  
    aditivo = tb_aditivos.query.filter_by(cod_aditivo=id).first()
    idcontrato = aditivo.cod_contrato
    form = frm_visualizar_aditivo()
    form.desc_aditivo.data = aditivo.desc_aditivo
    form.data_aditivo.data = aditivo.data_aditivo
    form.status_aditivo.data = aditivo.status_aditivo
    return render_template('visualizarAditivo.html', titulo='Visualizar Aditivo', id=id, form=form, idcontrato=idcontrato)   

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: editarAditivo
##FUNÇÃO: formulário de edição
#PODE ACESSAR: administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/editarAditivo/<int:id>')
def editarAditivo(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('editarAditivo')))  
    aditivo = tb_aditivos.query.filter_by(cod_aditivo=id).first()
    idcontrato = aditivo.cod_contrato
    form = frm_editar_aditivo()
    form.desc_aditivo.data = aditivo.desc_aditivo
    form.data_aditivo.data = aditivo.data_aditivo
    form.status_aditivo.data = aditivo.status_aditivo
    return render_template('editarAditivo.html', titulo='Editar Aditivo', id=id, form=form)   

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: atualizarAditivo
#FUNÇÃO: alterar informações no banco de dados
#PODE ACESSAR: administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/atualizarAditivo', methods=['POST',])
def atualizarAditivo():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('atualizarAditivo')))      
    form = frm_editar_aditivo(request.form)
    if form.validate_on_submit():
        id = request.form['id']
        aditivo = tb_aditivos.query.filter_by(cod_aditivo=id).first()
        aditivo.desc_aditivo = form.desc_aditivo.data
        aditivo.data_aditivo = form.data_aditivo.data
        aditivo.status_aditivo = form.status_aditivo.data
        db.session.add(aditivo)
        db.session.commit()
        flash('Aditivo atualizado com sucesso!','success')
    else:
        flash('Favor verificar os campos!','danger')
    return redirect(url_for('visualizarAditivo', id=request.form['id']))