from flask import Flask, request, jsonify
import pymysql
from flask_jwt_extended import JWTManager, create_access_token
from werkzeug.security import check_password_hash
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
    cursor = db.cursor()

    resultado = cursor.execute(sql, params)

    if fetch:
        resultado = cursor.fetchall()

    db.commit()

    cursor.close()
    db.close()

    return resultado


@app.route('/login', methods=['POST'])
def login():
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

    try:
        db = connectDB()
        cursor = db.cursor()

        sql = """
            SELECT id, nome, email, cargo
            FROM usuarios
            WHERE email = %s AND senha = %s
        """

        cursor.execute(sql, (email, senha))
        usuario = cursor.fetchone()
        db.close()

        if usuario:
            payload = {
                'id': usuario[0],
                'email': usuario[2],
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=12)
            }

            token = jwt.encode(
                payload,
                SECRET_KEY,
                algorithm='HS256'
            )

            return jsonify({
                'success': True,
                'token': token,
                'usuario': {
                    'id': usuario[0],
                    'nome': usuario[1],
                    'email': usuario[2],
                    'cargo': usuario[3]
                }
            }), 200

        return jsonify({
            'success': False,
            'message': 'Email ou senha inválidos'
        }), 401

    except Exception as e:

        return jsonify({
            'success': False,
            'message': str(e)
        }), 500



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

    return render_template('index.html', resultDB=resultado)

@app.route('/registros/<int:id>')
def pag_registro(id):
    return render_template('registro.html', id=id)


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

    return redirect('/')


@app.route('/registros/deletar', methods=['DELETE'])
def del_registro():
    dados = request.get_json()

    id = dados['id']

    sql = 'DELETE FROM registros WHERE id = %s'
    executeSQL(sql, (id))

    return redirect('/')


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

    return redirect(f'/registro/{registro_id}')


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

    return redirect('/')


@app.route('/registros/deletar', methods=['DELETE'])
def del_registro():
    dados = request.get_json()

    id = dados['id']

    sql = 'DELETE FROM registros WHERE id = %s'
    executeSQL(sql, (id))

    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)