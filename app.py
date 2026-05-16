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
        cursor = db.cursor()

        sql = """
            SELECT id, nome, email, senha_hash
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
            'message': 'Usuário cadastrado com sucesso.'
        })

    except Exception as err:
        return jsonify({
            'success': False,
            'message': str(err)
        })



@app.route('/medidores/cadastrar', methods=['POST'])
def cad_medidor():
    dados = request.get_json()

    medidor = dados['medidor']
    nome = dados['nome_contato']
    telefone = dados['telefone_contato']

    sql = '''
        INSERT INTO medidores (medidor, nome_contato, telefone_contato)
        VALUES (%s, %s, %s)
    '''
    executeSQL(sql, (medidor, nome, telefone))

    return jsonify({
        'success': True,
        'message': 'Cadastrado com sucesso.'
    })


@app.route('/medidores', methods=['GET'])
def pesq_medidor():
    pesquisa = request.args.get('q', '')

    sql = '''
        SELECT * FROM medidores
        WHERE CAST(id AS TEXT) = %s
        OR medidor ILIKE %s
    '''
    resultado = executeSQL(sql, (pesquisa, f'%{pesquisa}%'), fetch=True)

    return ''

@app.route('/medidores/<int:id>')
def pag_medidor(id):
    return ''


@app.route('/medidores/atualizar', methods=['PUT'])
def att_medidor():
    dados = request.get_json()

    id = dados['id']
    nome = dados['nome']
    telefone = dados['telefone']

    sql = '''
        UPDATE medidores
        SET nome = %s,
            telefone = %s
        WHERE id = %s
    '''
    executeSQL(sql, (nome, telefone, id))

    return ''


@app.route('/medidores/deletar', methods=['DELETE'])
def del_medidor():
    dados = request.get_json()

    id = dados['id']

    sql = 'DELETE FROM medidores WHERE id = %s'
    executeSQL(sql, (id))

    return ''


# Leituras
@app.route('/leituras/<int:medidor_id>')
def cad_leitura(medidor_id):
    dados = request.get_json()

    leitura = dados['leitura']
    data_leitura = dados['data_leitura'] or None
    tipo = dados['tipo']

    sql = '''
        INSERT INTO leituras (leitura, data_leitura, fk_medidor_id)
        VALUES (%s, %s, %s)
    '''
    executeSQL(sql, (leitura, data_leitura, medidor_id))

    return ''


@app.route('/leituras/atualizar', methods=['PUT'])
def att_leitura():
    dados = request.get_json()

    id = dados['id']
    nome = dados['nome']
    telefone = dados['telefone']

    sql = '''
        UPDATE medidores
        SET nome = %s,
            telefone = %s
        WHERE id = %s
    '''
    executeSQL(sql, (nome, telefone, id))

    return ''


@app.route('/leituras/deletar', methods=['DELETE'])
def del_leituras():
    dados = request.get_json()

    id = dados['id']

    sql = 'DELETE FROM medidores WHERE id = %s'
    executeSQL(sql, (id))

    return ''


if __name__ == '__main__':
    app.run(debug=True)