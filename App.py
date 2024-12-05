# ===================================
# Importação de Bibliotecas Necessárias
# ===================================

from flask import Flask, jsonify, request  # Para criar rotas, manipular requisições e respostas.
from flask_sqlalchemy import SQLAlchemy    # Para integração com o banco de dados.
from flask_cors import CORS                # Para permitir requisições de diferentes origens (CORS).
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user  # Para autenticação de usuários.




# ===================================
# Configuração do Aplicativo Flask
# ===================================

app = Flask(__name__)  # Inicializa a aplicação Flask.
app.config['SECRET_KEY'] = "minha_chave_123"  # Chave secreta para sessões e segurança.

# Configuração do banco de dados (SQLite neste caso).
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'

# Inicialização de extensões do Flask.
db = SQLAlchemy(app)  # Configura o SQLAlchemy com a aplicação Flask.
login_manager = LoginManager()  # Configura o gerenciador de autenticação de login.
login_manager.init_app(app)  # Integra o gerenciador de login ao aplicativo Flask.
login_manager.login_view = 'login'  # Define a rota padrão para login.
CORS(app)  # Habilita CORS para permitir requisições de diferentes origens.




# ===================================
# Modelagem de Dados
# ===================================

# Modelo da tabela "User" (usuários).
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)  # Identificador único do usuário.
    username = db.Column(db.String(80), nullable=False, unique=True)  # Nome de usuário único.
    password = db.Column(db.String(80), nullable=True)  # Senha do usuário.
    cart = db.relationship('CartItem', backref='user', lazy=True)

# Modelo da tabela "Product" (produtos).
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Identificador único do produto.
    name = db.Column(db.String(120), nullable=False)  # Nome do produto (obrigatório).
    price = db.Column(db.Float, nullable=False)  # Preço do produto (obrigatório).
    description = db.Column(db.Text, nullable=True)  # Descrição do produto (opcional).

# Modelo de Tabela "CartItem" (carrinhos)
class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Identificador único do id do Carrinho.
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)




# ===================================
# Autenticação de Usuários
# ===================================

# Carregamento de usuários para o gerenciador de login.
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # Busca o usuário pelo ID no banco de dados.

# Rota para autenticação de usuários (login).
@app.route('/login', methods=["POST"])
def login():
    data = request.json  # Obtém os dados enviados na requisição.
    user = User.query.filter_by(username=data.get("username")).first()  # Busca o usuário pelo nome.

    # Verifica se o usuário existe e se a senha está correta.
    if user and data.get("password") == user.password:
        login_user(user)  # Realiza o login do usuário.
        return jsonify({"message": "Login realizado com sucesso"})

    # Caso contrário, retorna uma mensagem de erro.
    return jsonify({"message": "Credenciais inválidas"}), 401






# ===================================
# Rota para Logout
# ===================================
@app.route('/logout', methods=["POST"])
@login_required
def logout():
    logout_user()  # Finaliza a sessão do usuário autenticado.
    return jsonify({"message": "Logout realizado com sucesso"})  # Retorna mensagem de confirmação.



# ===================================
# Rotas e Funcionalidades da API
# ===================================

# Rota para adicionar um produto.
@app.route('/api/products/add', methods=["POST"])
@login_required
def add_product():
    data = request.json  # Obtém os dados enviados na requisição.
    # Verifica se os campos obrigatórios estão presentes.
    if 'name' in data and 'price' in data:
        product = Product(
            name=data["name"],
            price=data["price"],
            description=data.get("description", "")  # Define uma descrição padrão, se não fornecida.
        )
        db.session.add(product)  # Adiciona o produto ao banco de dados.
        db.session.commit()  # Salva as alterações.
        return jsonify({"message": "Produto adicionado com sucesso"})
    return jsonify({"message": "Dados inválidos para o produto"}), 400


# Rota para deletar um produto.
@app.route('/api/products/delete/<int:product_id>', methods=["DELETE"])
@login_required
def delete_product(product_id):
    product = Product.query.get(product_id)  # Busca o produto pelo ID.
    if product:
        db.session.delete(product)  # Remove o produto do banco de dados.
        db.session.commit()  # Salva as alterações.
        return jsonify({"message": "Produto deletado com sucesso"})
    return jsonify({"message": "Produto não encontrado"}), 404


# Rota para obter os detalhes de um produto.
@app.route('/api/products/<int:product_id>', methods=["GET"])
def get_product_details(product_id):
    product = Product.query.get(product_id)  # Busca o produto pelo ID.
    if product:
        return jsonify({
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "description": product.description
        }), 200
    return jsonify({"message": "Produto não encontrado"}), 404


# Rota para atualizar um produto.
@app.route('/api/products/update/<int:product_id>', methods=["PUT"])
@login_required
def update_product(product_id):
    product = Product.query.get(product_id)  # Busca o produto pelo ID.
    if not product:
        return jsonify({"message": "Produto não encontrado"}), 404

    data = request.json
    if 'name' in data:
        product.name = data['name']  # Atualiza o nome, se fornecido.
    if 'price' in data:
        product.price = data['price']  # Atualiza o preço, se fornecido.
    if 'description' in data:
        product.description = data['description']  # Atualiza a descrição, se fornecida.

    db.session.commit()  # Salva as alterações.
    return jsonify({'message': 'Produto atualizado com sucesso'})


# Rota para listar todos os produtos.
@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.all()  # Busca todos os produtos no banco de dados.
    product_list = [
        {"id": product.id, "name": product.name, "price": product.price}
        for product in products
    ]
    return jsonify(product_list)




# =======================================
#  Rota para Adicionar no Carrinho
# =======================================
@app.route('/api/cart/add/<int:product_id>', methods=["POST"])
@login_required
def add_to_cart(product_id):
    # Usuario 
    user = User.query.get(int(current_user.id))
    # Produto
    product = Product.query.get(int(product_id))

    if user and product:
        cart_item = CartItem(user_id=user.id, product_id=product.id)
        db.session.add(cart_item)
        db.session.commit()
        return jsonify({"message": "O Item foi adicionado com Sucesso"}), 200
    return jsonify({"message": "Falha ao adiciona ao Carrinho"}), 400




# =======================================
#  Rota para Remover no Carrinho
# =======================================
@app.route('/api/cart/remove/<int:product_id>', methods=["DELETE"])
@login_required
def remove_from_cart(product_id):
    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        return jsonify({"message": "O Item foi Removido com Sucesso"}), 200
    return jsonify({"message": "Falha ao Remover ao Carrinho"}), 400



# =======================================
#  Rota de listagem dos item Cart
# =======================================
@app.route('/api/cart', methods=["GET"])
@login_required
def view_cart():
    #Usuario
    user = User.query.get(int(current_user.id))
    cart_itens = user.cart
    cart_content = []
    for cart_item in cart_itens:
        product = Product.query.get(cart_item.product_id)
        cart_content.append({
            "id": cart_item.id,
            "user_id": cart_item.user_id,
            "product_id": cart_item.product_id,
            "product_name": product.name,
            "product_price": product.price
        })
    return jsonify(cart_content)




# =======================================
#  Rota de checkout dos Carts
# =======================================
@app.route('/api/cart/checkout', methods=["POST"])
@login_required
def checkout():
    user = User.query.get(int(current_user.id))
    cart_itens = user.cart
    for cart_item in cart_itens:
        db.session.delete(cart_item)
    db.session.commit()
    return jsonify({"message": "Checkout com sucesso. carrinho foi limpo"})





# ===================================
# Inicialização do Servidor
# ===================================
if __name__ == "__main__":
    app.run(debug=True)  # Inicia o servidor em modo de depuração.
