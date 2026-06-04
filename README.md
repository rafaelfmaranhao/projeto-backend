# Backend Medidor Plus

Documentação do backend Flask para o projeto `medidor_plus`.

## Visão geral

Este backend fornece APIs para autenticação, cadastro de usuários, CRUD de imóveis, medidores e leituras. Ele utiliza:

- Flask
- PyMySQL
- Flask-JWT-Extended
- dotenv
- Werkzeug para hashing de senhas

## Configuração

1. Crie um ambiente virtual Python.
2. Instale as dependências em `requirements.txt`.
3. Crie um arquivo `.env` com as variáveis de ambiente necessárias.
4. Execute o backend com:

```bash
python app.py
```

## Variáveis de ambiente

O `app.py` usa estas variáveis:

- `SECRET_KEY` — chave secreta para JWT
- `DB_HOST` — host do banco MySQL
- `DB_PASSWORD` — senha do usuário MySQL

O banco configurado é `medidor_plus` e o usuário usado no código é `root`.

## Resposta padrão

A maioria das rotas retorna JSON com os campos:

- `success` (boolean)
- `message` (string)
- campos extras conforme a rota

---

## Autenticação

### `POST /login`

Recebe JSON:

```json
{
  "email": "usuario@exemplo.com",
  "senha": "senha123"
}
```

Retorna em caso de sucesso:

```json
{
  "success": true,
  "message": "Login realizado com sucesso",
  "token": "<jwt>",
  "usuario": {
    "id": 1,
    "nome": "Nome",
    "email": "usuario@exemplo.com"
  }
}
```

Status possíveis:

- `400` — JSON inválido ou campos faltando
- `401` — email ou senha inválidos
- `500` — erro interno

### `POST /cadastro`

Recebe JSON:

```json
{
  "nome": "Rafael Maranhão",
  "email": "rafael@exemplo.com",
  "senha": "senha123"
}
```

Retorna:

```json
{
  "success": true,
  "message": "Usuário cadastrado com sucesso"
}
```

Status possíveis:

- `400` — JSON inválido, campos faltando, senha curta
- `409` — email já cadastrado

---

## Imóveis

Todas as rotas de `imoveis` exigem JWT no cabeçalho `Authorization: Bearer <token>`.

### `GET /imoveis`

Query params:

- `q` opcional para busca por `id` ou `nome`

Exemplo:

```http
GET /imoveis?q=Apartamento
Authorization: Bearer <token>
```

Retorna lista de imóveis do usuário autenticado.

### `POST /imoveis/cadastrar`

Recebe JSON:

```json
{
  "nome": "Apartamento 101"
}
```

O backend usa o usuário atual do JWT para preencher `fk_usuarios_id`.

Retorna:

```json
{
  "success": true,
  "message": "Cadastrado com sucesso",
  "imoveis_id": 123
}
```

### `PUT /imoveis/atualizar`

Recebe JSON:

```json
{
  "id": 1,
  "nome": "Apartamento 102"
}
```

### `DELETE /imoveis/deletar`

Recebe JSON:

```json
{
  "id": 1
}
```

---

## Medidores

Todas as rotas de `medidores` exigem JWT.

### `GET /medidores`

Query params:

- `id`: id do imóvel (`fk_imoveis_id`)
- `q`: termo de busca opcional

Exemplo:

```http
GET /medidores?id=2&q=Ap+102
Authorization: Bearer <token>
```

### `POST /medidores/cadastrar`

Recebe JSON:

```json
{
  "unidade": "Ap 102",
  "identificador": "23456",
  "tipo": "energia",
  "fk_imoveis_id": 2
}
```

### `PUT /medidores/atualizar`

Recebe JSON:

```json
{
  "id": 5,
  "unidade": "Ap 102",
  "identificador": "23456"
}
```

### `DELETE /medidores/deletar`

Recebe JSON:

```json
{
  "id": 5
}
```

---

## Leituras

Todas as rotas de `leituras` exigem JWT.

### `GET /leituras`

Query params:

- `id`: id do medidor (`fk_medidor_id`)
- `q`: termo de busca opcional para valor de leitura ou data

### `POST /leituras/cadastrar`

Recebe JSON:

```json
{
  "leitura": 123.45,
  "data_leitura": "25/05/2026 12:00",
  "medidor_id": 7
}
```

### `PUT /leituras/atualizar`

Recebe JSON:

```json
{
  "id": 10,
  "leitura": 124.00,
  "data_leitura": "26/05/2026 18:30"
}
```

### `DELETE /leituras/deletar`

Recebe JSON:

```json
{
  "id": 10
}
```

---

## Observações importantes

- O backend usa JWT para identificar o usuário atual em rotas protegidas.
- Em `POST /imoveis/cadastrar`, o `fk_usuarios_id` não precisa ser enviado pelo front; ele é extraído do token.
- Os campos obrigatórios recebem status `400` quando faltam.
- A data hora de leitura deve estar em formato D/M/Y 24 horas `dd/mm/YYYY HH:MM`.
- O banco é MySQL e o código usa `pymysql`.

## Como testar

1. Faça cadastro em `/cadastro`.
2. Faça login em `/login` e pegue o token.
3. Use o token em `Authorization: Bearer <token>` no cabeçalho para acessar as rotas protegidas.
