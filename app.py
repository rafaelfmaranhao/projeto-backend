from flask import Flask, request, jsonify
import pymysql
from flask_jwt_extended import JWTManager, create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = SECRET_KEY

jwt = JWTManager(app)


def connectDB():
    return pymysql.connect(
        host=os.getenv('DB_HOST'),
        database='medidor_plus',
        user='root',
        password=os.getenv('DB_PASSWORD')
    )

def executeSQL(sql, params=None, fetch=None):
    db = connectDB()
    cursor = db.cursor()

    resultado = cursor.execute(sql, params)

    if fetch == 'all':
        resultado = cursor.fetchall()
    elif fetch == 'one':
        resultado = cursor.fetchone()

    db.commit()
    cursor.close()
    db.close()

    return resultado


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

        usuario = executeSQL(sql, (email), fetch='one')

        if not usuario:
            return jsonify({
                'success': False,
                'message': 'Email ou senha inválidos'
            }), 401

        senha_correta = check_password_hash(
            usuario[3],
            senha
        )

        if not senha_correta:
            return jsonify({
                'success': False,
                'message': 'Email ou senha inválidos'
            }), 401

        token = create_access_token(
            identity=str(usuario[0])
        )

        return jsonify({
            'success': True,
            'message': 'Login realizado com sucesso',

            'token': token,

            'usuario': {
                'id': usuario[0],
                'nome': usuario[1],
                'email': usuario[2]
            }

        }), 200

    except Exception as err:
        return jsonify({
            'success': False,
            'message': str(err)
        }), 500


@app.route('/cadastro', methods=['POST'])
def cadastrar():
    try:
        dados = request.get_json()

        if not dados:
            return jsonify({
                'success': False,
                'message': 'JSON inválido'
            })

        nome = dados.get('nome')
        email = dados.get('email')
        senha = dados.get('senha')

        if not nome or not email or not senha:
            return jsonify({
                'success': False,
                'message': 'Email e senha são obrigatórios'
            }), 400
        
        if len(senha) < 6:
            return jsonify({
                'success': False,
                'message': 'Senha deve ter pelo menos 6 caracteres'
            })
        
        db = connectDB()
        cursor = db.cursor()

        sql = '''
            SELECT email
            FROM usuarios
            WHERE email = %s
        '''
        cursor.execute(sql, (email))
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
            'message': str(err)
        })
    

#################### Imóveis ####################
@app.route('/imoveis', methods=['GET'])
def pesq_imovel():
    usuario_id = request.args.get('usuario_id')
    pesquisa = request.args.get('q', '')

    resultado = None

    if pesquisa == '':
        sql = '''
            SELECT id, nome 
            FROM imoveis
            WHERE fk_usuarios_id = '%s'
        '''
        resultado = executeSQL(sql, (usuario_id), fetch='all')
    
    else:
        sql = '''
            SELECT id, nome 
            FROM imoveis
            WHERE fk_usuarios_id = %s
            AND id = %s
            OR nome = %s
        '''
        resultado = executeSQL(sql, (usuario_id, pesquisa, f'%{pesquisa}%'), fetch='all')

    return jsonify(resultado)


@app.route('/imoveis/cadastrar', methods=['POST'])
def cad_imovel():
    dados = request.get_json()

    if not dados:
        return jsonify({
            'success': False,
            'message': 'JSON Inválido'
        })

    nome = dados.get('nome')
    fk_usuarios_id = dados.get('fk_usuarios_id')

    sql = '''
        INSERT INTO imoveis (nome, fk_usuarios_id)
        VALUES (%s, %s);
    '''
    executeSQL(sql, (nome, fk_usuarios_id))

    return jsonify({
        'success': True,
        'message': 'Cadastrado com sucesso',
        'imoveis_id': ''
    })


@app.route('/imoveis/atualizar', methods=['PUT'])
def att_imovel():
    dados = request.get_json()

    if not dados:
        return jsonify({
            'success': False,
            'message': 'JSON Inválido'
        })

    id = dados.get('id')
    nome = dados.get('nome')

    sql = '''
        UPDATE imoveis
        SET nome = %s
        WHERE id = %s
    '''
    executeSQL(sql, (nome, id))

    return jsonify({
        'success': True,
        'message': 'Atualizado com sucesso'
    })


@app.route('/imoveis/deletar', methods=['DELETE'])
def del_imovel():
    dados = request.get_json()

    if not dados:
        return jsonify({
            'success': False,
            'message': 'JSON Inválido'
        })

    id = dados.get('id')

    sql = 'DELETE FROM imoveis WHERE id = %s'
    executeSQL(sql, (id))

    return jsonify({
        'success': True,
        'message': 'Deletado com sucesso.'
    })


#################### Medidores ####################
@app.route('/medidores', methods=['GET'])
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
        resultado = executeSQL(sql, (imoveis_id), fetch='all')

    else:
        sql = '''
            SELECT id, unidade, identificador, tipo
            FROM medidores
            WHERE fk_imoveis_id = %s
            AND unidade = %s
            OR identificador = %s
        '''
        resultado = executeSQL(sql, (imoveis_id, pesquisa, f'%{pesquisa}%'), fetch='all')

    return jsonify(resultado)


@app.route('/medidores/cadastrar', methods=['POST'])
def cad_medidor():
    dados = request.get_json()

    if not dados:
        return jsonify({
            'success': False,
            'message': 'JSON Inválido'
        })

    unidade = dados.get('unidade')
    identificador = dados.get('identificador')
    tipo = dados.get('tipo')
    fk_imoveis_id = dados.get('fk_imoveis_id')

    sql = '''
        INSERT INTO medidores (unidade, identificador, tipo, fk_imoveis_id)
        VALUES (%s, %s, %s, %s)
    '''
    executeSQL(sql, (unidade, identificador, tipo, fk_imoveis_id))

    return jsonify({
        'success': True,
        'message': 'Cadastrado com sucesso.'
    })


@app.route('/medidores/atualizar', methods=['PUT'])
def att_medidor():
    dados = request.get_json()

    if not dados:
        return jsonify({
            'success': False,
            'message': 'JSON Inválido'
        })

    id = dados.get('id')
    unidade = dados.get('unidade')
    identificador = dados.get('identificador')

    sql = '''
        UPDATE medidores
        SET unidade = %s,
            identificador = %s
        WHERE id = %s
    '''
    executeSQL(sql, (unidade, identificador, id))

    return jsonify({
        'success': True,
        'message': 'Atualizado com sucesso.'
    })


@app.route('/medidores/deletar', methods=['DELETE'])
def del_medidor():
    dados = request.get_json()

    if not dados:
        return jsonify({
            'success': False,
            'message': 'JSON Inválido'
        })

    id = dados.get('id')

    sql = 'DELETE FROM medidores WHERE id = %s'
    executeSQL(sql, (id))

    return jsonify({
        'success': True,
        'message': 'Deletado com sucesso.'
    })


#################### Leituras ####################
@app.route('/leituras', methods=['GET'])
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
        resultado = executeSQL(sql, (medidor_id), fetch='all')

    else:
        sql = '''
            SELECT id, leitura, data_leitura
            FROM leituras
            WHERE fk_medidor_id = %s
            AND leitura = %s
            OR data_leitura = %s
        '''
        resultado = executeSQL(sql, (medidor_id, pesquisa, f'%{pesquisa}%'), fetch='all')

    return jsonify(resultado)


@app.route('/leituras/cadastrar')
def cad_leitura():
    dados = request.get_json()

    if not dados:
        return jsonify({
            'success': False,
            'message': 'JSON Inválido'
        })

    leitura = dados.get('leitura')
    data_leitura = dados.get('data_leitura') or None
    medidor_id = dados.get('medidor_id')

    sql = '''
        INSERT INTO leituras (leitura, data_leitura, fk_medidor_id)
        VALUES (%s, %s, %s)
    '''
    executeSQL(sql, (leitura, data_leitura, medidor_id))

    return jsonify({
        'success': True,
        'message': 'Cadastrado com sucesso.'
    })


@app.route('/leituras/atualizar', methods=['PUT'])
def att_leitura():
    dados = request.get_json()

    if not dados:
        return jsonify({
            'success': False,
            'message': 'JSON Inválido'
        })

    id = dados.get('id')
    leitura = dados.get('leitura')
    data_leitura = dados.get('data_leitura')

    sql = '''
        UPDATE medidores
        SET leitura = %s,
            data_leitura = %s
        WHERE id = %s
    '''
    executeSQL(sql, (leitura, data_leitura, id))

    return jsonify({
        'success': True,
        'message': 'Atualizado com sucesso.'
    })


@app.route('/leituras/deletar', methods=['DELETE'])
def del_leituras():
    dados = request.get_json()

    if not dados:
        return jsonify({
            'success': False,
            'message': 'JSON Inválido'
        })

    id = dados.get('id')

    sql = 'DELETE FROM medidores WHERE id = %s'
    executeSQL(sql, (id))

    return jsonify({
        'success': True,
        'message': 'Deletado com sucesso.'
    })


if __name__ == '__main__':
    app.run(debug=True)