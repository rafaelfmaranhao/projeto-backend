from flask import Flask, request, jsonify
import pymysql
from flask_jwt_extended import JWTManager, create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
import datetime 
import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = SECRET_KEY
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=2)

jwt = JWTManager(app)


def connectDB():
    return pymysql.connect(
        host=os.getenv('DB_HOST'),
        database='medidor_plus',
        user='root',
        password=os.getenv('DB_PASSWORD')
    )

def executeSQL(sql, params=None, fetch=False):
    db = connectDB()
    cursor = db.cursor(dictionary=True)

    resultado = cursor.execute(sql, params)

    if fetch:
        resultado = cursor.fetchall()

    db.commit()
    cursor.close()
    db.close()

    return resultado


@app.route('/login', methods=['POST'])
def login():

    try:
        dados = request.get_json()

        if not dados:
            return jsonify({
                'success': False,
                'message': 'JSON inválido'
            }), 400

        email = dados['email']
        senha = dados['senha']

        if not email or not senha:
            return jsonify({
                'success': False,
                'message': 'Email e senha são obrigatórios'
            }), 400

        db = connectDB()
        cursor = db.cursor(dictionary=True)

        sql = """
            SELECT id, nome, email, senha_hash, cargo
            FROM usuarios
            WHERE email = %s;
        """

        cursor.execute(sql, (email,))
        usuario = cursor.fetchone()

        cursor.close()
        db.close()

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
            identity=str(usuario['id']),
            additional_claims={
                'cargo': usuario['cargo']
            }
        )

        return jsonify({
            'success': True,
            'message': 'Login realizado com sucesso',

            'token': token,

            'usuario': {
                'id': usuario['id'],
                'nome': usuario['nome'],
                'email': usuario['email'],
                'cargo': usuario['cargo']
            }

        }), 200

    except Exception as err:
        return jsonify({
            'success': False,
            'message': str(err)
        }), 500

@app.route('/cadastro')
def cadastrar():
    try:
        dados = request.get_json()

    except Exception as err:
        return jsonify({
            'success': False,
            'message': str(err)
        })



@app.route('/registros/cadastrar', methods=['POST'])
def cad_registro():
    dados = request.get_json()

    registro = dados['registro']
    nome = dados['nome_contato']
    telefone = dados['telefone_contato']

    sql = '''
        INSERT INTO registros (registro, nome_contato, telefone_contato)
        VALUES (%s, %s, %s)
    '''
    executeSQL(sql, (registro, nome, telefone))

    return jsonify({
        'success': True,
        'message': 'Cadastrado com sucesso.'
    })


@app.route('/registros', methods=['GET'])
def pesq_registro():
    pesquisa = request.args.get('q', '')

    sql = '''
        SELECT * FROM registros
        WHERE CAST(id AS TEXT) = %s
        OR registro ILIKE %s
    '''
    resultado = executeSQL(sql, (pesquisa, f'%{pesquisa}%'), fetch=True)

    return ''

@app.route('/registros/<int:id>')
def pag_registro(id):
    return ''


@app.route('/registros/atualizar', methods=['PUT'])
def att_registro():
    dados = request.get_json()

    id = dados['id']
    nome = dados['nome']
    telefone = dados['telefone']

    sql = '''
        UPDATE registros
        SET nome = %s,
            telefone = %s
        WHERE id = %s
    '''
    executeSQL(sql, (nome, telefone, id))

    return ''


@app.route('/registros/deletar', methods=['DELETE'])
def del_registro():
    dados = request.get_json()

    id = dados['id']

    sql = 'DELETE FROM registros WHERE id = %s'
    executeSQL(sql, (id))

    return ''


# Leituras
@app.route('/leituras/<int:registro_id>')
def cad_leitura(registro_id):
    dados = request.get_json()

    leitura = dados['leitura']
    data_leitura = dados['data_leitura'] or None
    tipo = dados['tipo']

    sql = '''
        INSERT INTO leituras (leitura, data_leitura, fk_registro_id)
        VALUES (%s, %s, %s)
    '''
    executeSQL(sql, (leitura, data_leitura, registro_id))

    return ''


@app.route('/leituras/atualizar', methods=['PUT'])
def att_leitura():
    dados = request.get_json()

    id = dados['id']
    nome = dados['nome']
    telefone = dados['telefone']

    sql = '''
        UPDATE registros
        SET nome = %s,
            telefone = %s
        WHERE id = %s
    '''
    executeSQL(sql, (nome, telefone, id))

    return ''


@app.route('/registros/deletar', methods=['DELETE'])
def del_registro():
    dados = request.get_json()

    id = dados['id']

    sql = 'DELETE FROM registros WHERE id = %s'
    executeSQL(sql, (id))

    return ''


if __name__ == '__main__':
    app.run(debug=True)