from flask import Flask, render_template, request, redirect
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

def connectDB():
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database='postgres',
        user='postgres',
        password=os.getenv('DB_PASSWORD'),
        port=5432
    )

def executeSQL(sql, params=None, fetch=False):
    db = connectDB()
    cursor = db.cursor()

    cursor.execute(sql, params)

    resultado = None

    if fetch:
        resultado = cursor.fetchall()

    db.commit()

    cursor.close()
    db.close()

    return resultado


@app.route('/')
def index():
    sql = 'SELECT * FROM registros'

    resultado = executeSQL(sql, fetch=True)

    return render_template('testes.html', resultDB=resultado)


@app.route('/registros/cadastrar', methods=['POST'])
def cadFunc():
    registro = request.form['registro']
    nome = request.form['nome_contato']
    telefone = request.form['telefone_contato']

    sql = '''
        INSERT INTO registros (registro, nome_contato, telefone_contato)
        VALUES (%s, %s, %s)
    '''

    executeSQL(sql, (registro, nome, telefone))

    return redirect('/')


@app.route('/registros', methods=['GET'])
def pesFunc():
    pesquisa = request.args.get('q', '')

    sql = '''
        SELECT * FROM registros
        WHERE CAST(id AS TEXT) = %s
        OR registro ILIKE %s
    '''

    resultado = executeSQL(sql, (pesquisa, f'%{pesquisa}%'), fetch=True)

    return render_template('index.html', resultDB=resultado)


@app.route('/registros/atualizar', methods=['POST'])
def attFunc():
    id = request.form['id']
    nome = request.form['nome']
    telefone = request.form['telefone']

    sql = '''
        UPDATE registros
        SET nome = %s,
            telefone = %s
        WHERE id = %s
    '''

    executeSQL(sql, (nome, telefone, id))

    return redirect('/')


@app.route('/registros/deletar', methods=['POST'])
def remFunc():
    id = request.form['id']

    sql = 'DELETE FROM registros WHERE id = %s'

    executeSQL(sql, (id))

    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)