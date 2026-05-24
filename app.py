from flask import Flask, request, jsonify
import pymysql
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
from flask_cors import CORS
from flask_mail import Mail, Message
import random
from datetime import datetime

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')

app = Flask(__name__)
CORS(app)

app.config['JWT_SECRET_KEY'] = SECRET_KEY
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False
jwt = JWTManager(app)


def connect_db():
    return pymysql.connect(
        host=os.getenv('DB_HOST'),
        database='medidor_plus',
        user='root',
        password=os.getenv('DB_PASSWORD')
    )

def execute_sql(sql, params=None, fetch=None):
    db = connect_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    try:
        resultado = cursor.execute(sql, params)

        if fetch == 'all':
            resultado = cursor.fetchall()
        elif fetch == 'one':
            resultado = cursor.fetchone()
        else:
            resultado = cursor.lastrowid

        db.commit()
        return resultado
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        try:
            db.close()
        except Exception:
            pass


#################### Auth ####################
@app.route('/login', methods=['POST'])
def login():
    try:
        dados = request.get_json()

        if not dados:
            return jsonify({
                'success': False,
                'message': 'JSON inválido'
            }), 400

        email = dados.get('email')
        senha = dados.get('senha')

        if not email or not senha:
            return jsonify({
                'success': False,
                'message': 'Email e senha são obrigatórios'
            }), 400

        sql = """
            SELECT id, nome, email, senha_hash
            FROM usuarios
            WHERE email = %s;
        """

        usuario = execute_sql(sql, (email,), fetch='one')

        if not usuario:
            return jsonify({
                'success': False,
                'message': 'Email ou senha inválidos'
            }), 401

        senha_correta = check_password_hash(
            usuario['senha_hash'],
            senha
        )

        if not senha_correta:
            return jsonify({
                'success': False,
                'message': 'Email ou senha inválidos'
            }), 401

        token = create_access_token(
            identity=str(usuario['id'])
        )

        return jsonify({
            'success': True,
            'message': 'Login realizado com sucesso',

            'token': token,

            'usuario': {
                'id': usuario['id'],
                'nome': usuario['nome'],
                'email': usuario['email']
            }

        }), 200

    except Exception as err:
        return jsonify({
            'success': False,
            'message': 'Erro interno no servidor',
            'error': str(err)
        }), 500


@app.route('/cadastro', methods=['POST'])
def cadastrar():
    try:
        dados = request.get_json()

        if not dados:
            return jsonify({
                'success': False,
                'message': 'JSON inválido'
            }), 400

        nome = dados.get('nome')
        email = dados.get('email')
        senha = dados.get('senha')

        if not nome or not email or not senha:
            return jsonify({
                'success': False,
                'message': 'Nome, email e senha são obrigatórios'
            }), 400
        
        if len(senha) < 6:
            return jsonify({
                'success': False,
                'message': 'Senha deve ter pelo menos 6 caracteres'
            })
        
        db = connect_db()
        cursor = db.cursor()

        sql = '''
            SELECT email
            FROM usuarios
            WHERE email = %s
        '''
        cursor.execute(sql, (email,))
        verifica_email = cursor.fetchone()

        if verifica_email:
            cursor.close()
            db.close()

            return jsonify({
                'success': False,
                'message': 'Email já cadastrado'
            }), 409
        
        senha_hash = generate_password_hash(senha)

        sql = """
            INSERT INTO usuarios (nome, email, senha_hash)
            VALUES (%s, %s, %s)
        """

        cursor.execute(sql, (nome, email, senha_hash))
        db.commit()

        cursor.close()
        db.close()

        return jsonify({
            'success': True,
            'message': 'Usuário cadastrado com sucesso'
        })

    except Exception as err:
        return jsonify({
            'success': False,
            'message': 'Erro interno no servidor',
            'error': str(err)
        }), 500
    

@app.route('/recuperarSenha', methods=['POST'])
def recuperar_senha():
    global codigo_rec_gerado

    dados = request.get_json()
    email = dados.get('email')

    sql = '''
        SELECT id
        FROM usuarios
        WHERE email = %s
    '''
    try:
        resultado = execute_sql(sql, (email,), fetch='one')

        if resultado:
            app.config['MAIL_SERVER'] = 'smtp.gmail.com'
            app.config['MAIL_PORT'] = 587
            app.config['MAIL_USE_TLS'] = True
            app.config['MAIL_USERNAME'] = 'medidorplus@gmail.com'
            app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
            mail = Mail(app)
            msg = Message(
                subject='Recuperação de Senha',
                sender='medidorplus@gmail.com',
                recipients=[email]
            )
            nome = execute_sql('SELECT nome FROM usuarios WHERE email = %s', (email), fetch='one')['nome']
            codigo_rec_gerado = random.randint(100000, 999999)

            msg.body = f'Olá, {nome}! Seu código de recuperação é: {codigo_rec_gerado}.'
            mail.send(msg)

            return jsonify({
                'success': True,
                'message': 'E-mail de recuperação enviado',
                'email': email
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'E-mail não encontrado'
            }), 404

    except Exception as err:
        return jsonify({
            'success': False,
            'message': 'Erro ao recuperar senha',
            'error': str(err)
        }), 500


@app.route('/validarCodigo', methods=['POST'])
def validar_codigo():

    dados = request.get_json()
    codigo_rec_recebido = dados.get('codigo')

    if codigo_rec_recebido != codigo_rec_gerado:
        return jsonify({
            'success': False,
            'message': 'Código de recuperação inválido'
        }), 400
    
    return jsonify({
        'success': True,
        'message': 'Código validado'
    }), 200


@app.route('/atualizarSenha', methods=['PUT'])
def atualizar_senha():

    dados = request.get_json()
    email = dados.get('email')
    novaSenha = dados.get('novaSenha')

    if len(novaSenha) < 6:
        return jsonify({
            'success': False,
            'message': 'A senha precisa ter pelo menos 6 caracteres'
        })
    
    senha_hash = generate_password_hash(novaSenha)
    
    sql = '''
        UPDATE usuarios
        SET senha_hash = %s
        WHERE email = %s
    '''
    try:
        execute_sql(sql, (senha_hash, email,), fetch='one')
        return jsonify({
            'success': True,
            'message': 'Senha atualizada com sucesso'
        }), 200

    except Exception as err:
        return jsonify({
            'success': False,
            'message': 'Erro ao atualizar senha',
            'erro': str(err)
        })


#################### Imóveis ####################
@app.route('/imoveis', methods=['GET'])
@jwt_required()
def pesq_imovel():
    usuario_id = get_jwt_identity()
    pesquisa = request.args.get('q', '')

    resultado = None

    if pesquisa == '':
        sql = '''
            SELECT id, nome 
            FROM imoveis
            WHERE fk_usuarios_id = %s
        '''
        resultado = execute_sql(sql, (usuario_id,), fetch='all')
    
    else:
        sql = '''
            SELECT id, nome 
            FROM imoveis
            WHERE fk_usuarios_id = %s
            AND (nome LIKE %s OR id = %s)
        '''
        resultado = execute_sql(sql, (usuario_id, f'%{pesquisa}%', pesquisa), fetch='all')

    return jsonify(resultado)


@app.route('/imoveis/cadastrar', methods=['POST'])
@jwt_required()
def cad_imovel():
    dados = request.get_json()

    if not dados:
        return jsonify({
            'success': False,
            'message': 'JSON Inválido'
        }), 400

    nome = dados.get('nome')
    fk_usuarios_id = get_jwt_identity()

    if not nome:
        return jsonify({'success': False, 'message': 'Nome é obrigatório'}), 400

    sql = '''
        INSERT INTO imoveis (nome, fk_usuarios_id)
        VALUES (%s, %s);
    '''
    resultado = execute_sql(sql, (nome, fk_usuarios_id))

    return jsonify({
        'success': True,
        'message': 'Cadastrado com sucesso',
        'id': resultado
    })


@app.route('/imoveis/atualizar', methods=['PUT'])
@jwt_required()
def att_imovel():
    dados = request.get_json()

    if not dados:
        return jsonify({
            'success': False,
            'message': 'JSON Inválido'
        }), 400

    id = dados.get('id')
    nome = dados.get('nome')

    if not id or not nome:
        return jsonify({'success': False, 'message': 'id e nome são obrigatórios'}), 400

    sql = '''
        UPDATE imoveis
        SET nome = %s
        WHERE id = %s
    '''
    execute_sql(sql, (nome, id))

    return jsonify({
        'success': True,
        'message': 'Atualizado com sucesso'
    })


@app.route('/imoveis/deletar', methods=['DELETE'])
@jwt_required()
def del_imovel():
    dados = request.get_json()

    if not dados:
        return jsonify({
            'success': False,
            'message': 'JSON Inválido'
        }), 400

    id = dados.get('id')

    if not id:
        return jsonify({'success': False, 'message': 'id é obrigatório'}), 400

    sql = 'DELETE FROM imoveis WHERE id = %s'
    execute_sql(sql, (id,))

    return jsonify({
        'success': True,
        'message': 'Deletado com sucesso.'
    })


#################### Medidores ####################
@app.route('/medidores', methods=['GET'])
@jwt_required()
def pesq_medidor():
    imoveis_id = request.args.get('id')
    pesquisa = request.args.get('q', '')

    resultado = None

    if pesquisa == '':
        sql = '''
            SELECT id, unidade, identificador, tipo
            FROM medidores
            WHERE fk_imoveis_id = %s
        '''
        resultado = execute_sql(sql, (imoveis_id,), fetch='all')

    else:
        sql = '''
            SELECT id, unidade, identificador, tipo
            FROM medidores
            WHERE fk_imoveis_id = %s
            AND (unidade LIKE %s OR identificador LIKE %s)
        '''
        resultado = execute_sql(sql, (imoveis_id, pesquisa, f'%{pesquisa}%'), fetch='all')

    return jsonify(resultado)


@app.route('/medidores/cadastrar', methods=['POST'])
@jwt_required()
def cad_medidor():
    dados = request.get_json()

    if not dados:
        return jsonify({
            'success': False,
            'message': 'JSON Inválido'
        }), 400

    unidade = dados.get('unidade')
    identificador = dados.get('identificador')
    tipo = dados.get('tipo')
    fk_imoveis_id = dados.get('fk_imoveis_id')

    if not unidade or not identificador or not tipo or not fk_imoveis_id:
        return jsonify({'success': False, 'message': 'unidade, identificador, tipo e fk_imoveis_id são obrigatórios'}), 400

    sql = '''
        INSERT INTO medidores (unidade, identificador, tipo, fk_imoveis_id)
        VALUES (%s, %s, %s, %s)
    '''
    execute_sql(sql, (unidade, identificador, tipo, fk_imoveis_id))

    return jsonify({
        'success': True,
        'message': 'Cadastrado com sucesso.'
    })


@app.route('/medidores/atualizar', methods=['PUT'])
@jwt_required()
def att_medidor():
    dados = request.get_json()

    if not dados:
        return jsonify({
            'success': False,
            'message': 'JSON Inválido'
        }), 400

    id = dados.get('id')
    unidade = dados.get('unidade')
    identificador = dados.get('identificador')

    if not id or not unidade or not identificador:
        return jsonify({'success': False, 'message': 'id, unidade e identificador são obrigatórios'}), 400

    sql = '''
        UPDATE medidores
        SET unidade = %s,
            identificador = %s
        WHERE id = %s
    '''
    execute_sql(sql, (unidade, identificador, id))

    return jsonify({
        'success': True,
        'message': 'Atualizado com sucesso.'
    })


@app.route('/medidores/deletar', methods=['DELETE'])
@jwt_required()
def del_medidor():
    dados = request.get_json()

    if not dados:
        return jsonify({
            'success': False,
            'message': 'JSON Inválido'
        }), 400

    id = dados.get('id')

    if not id:
        return jsonify({'success': False, 'message': 'id é obrigatório'}), 400

    sql = 'DELETE FROM medidores WHERE id = %s'
    execute_sql(sql, (id,))

    return jsonify({
        'success': True,
        'message': 'Deletado com sucesso.'
    })


#################### Leituras ####################
@app.route('/leituras', methods=['GET'])
@jwt_required()
def pesq_leitura():
    medidor_id = request.args.get('id')
    pesquisa = request.args.get('q', '')

    resultado = None

    if pesquisa == '':
        sql = '''
            SELECT id, leitura, data_leitura
            FROM leituras
            WHERE fk_medidor_id = %s
        '''
        resultado = execute_sql(sql, (medidor_id,), fetch='all')

    else:
        sql = '''
            SELECT id, leitura, data_leitura
            FROM leituras
            WHERE fk_medidor_id = %s
            AND (leitura = %s OR data_leitura LIKE %s)
        '''
        resultado = execute_sql(sql, (medidor_id, pesquisa, f'%{pesquisa}%'), fetch='all')

    return jsonify(resultado)


@app.route('/leituras/cadastrar', methods=['POST'])
@jwt_required()
def cad_leitura():
    dados = request.get_json()

    if not dados:
        return jsonify({
            'success': False,
            'message': 'JSON Inválido'
        }), 400

    leitura = dados.get('leitura')
    data_leitura = dados.get('data_leitura') or None
    medidor_id = dados.get('medidor_id')

    if leitura is None or medidor_id is None:
        return jsonify({'success': False, 'message': 'leitura e medidor_id são obrigatórios'}), 400

    if data_leitura:
        try:
            datetime.fromisoformat(data_leitura)
        except Exception:
            return jsonify({'success': False, 'message': 'Formato de data inválido. Use YYYY-MM-DD'}), 400

    sql = '''
        INSERT INTO leituras (leitura, data_leitura, fk_medidor_id)
        VALUES (%s, %s, %s)
    '''
    execute_sql(sql, (leitura, data_leitura, medidor_id))

    return jsonify({
        'success': True,
        'message': 'Cadastrado com sucesso.'
    })


@app.route('/leituras/atualizar', methods=['PUT'])
@jwt_required()
def att_leitura():
    dados = request.get_json()

    if not dados:
        return jsonify({
            'success': False,
            'message': 'JSON Inválido'
        }), 400

    id = dados.get('id')
    leitura = dados.get('leitura')
    data_leitura = dados.get('data_leitura')

    if not id or leitura is None:
        return jsonify({'success': False, 'message': 'id e leitura são obrigatórios'}), 400

    if data_leitura:
        try:
            datetime.fromisoformat(data_leitura)
        except Exception:
            return jsonify({'success': False, 'message': 'Formato de data inválido. Use YYYY-MM-DD'}), 400

    sql = '''
        UPDATE leituras
        SET leitura = %s,
            data_leitura = %s
        WHERE id = %s
    '''
    execute_sql(sql, (leitura, data_leitura, id))

    return jsonify({
        'success': True,
        'message': 'Atualizado com sucesso.'
    })


@app.route('/leituras/deletar', methods=['DELETE'])
@jwt_required()
def del_leituras():
    dados = request.get_json()

    if not dados:
        return jsonify({
            'success': False,
            'message': 'JSON Inválido'
        }), 400

    id = dados.get('id')

    if not id:
        return jsonify({'success': False, 'message': 'id é obrigatório'}), 400

    sql = 'DELETE FROM leituras WHERE id = %s'
    execute_sql(sql, (id,))

    return jsonify({
        'success': True,
        'message': 'Deletado com sucesso.'
    })


if __name__ == '__main__':
    app.run(debug=True)