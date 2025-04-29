from datetime import datetime
from flask import Flask, jsonify, request
from flask_migrate import Migrate
from models import db, Todo, User
from auth import auth
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity


app = Flask(__name__)

# Konfigurera SQLite-databasen
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'din-hemliga-nyckel'  # Byt ut mot en säker nyckel i produktion

# Initiera databasen
db.init_app(app)
jwt = JWTManager(app)

app.register_blueprint(auth, url_prefix='/auth')

# Skapa databastabeller
with app.app_context():
    db.create_all()

migrate = Migrate(app, db)


@app.route('/todos', methods=['POST'])
@jwt_required()
def create_todo():
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data or 'title' not in data:
        return jsonify({"error": "Titel krävs"}), 400
    
    new_todo = Todo(
        title=data['title'],
        completed=data.get('completed', False),
        deadline=datetime.fromisoformat(data['deadline']) if 'deadline' in data else None,
        category=data.get('category'),
        user_id=user_id
    )

    db.session.add(new_todo)
    db.session.commit()

    return jsonify(new_todo.to_dict()), 201

@app.route('/todos', methods=['GET'])
@jwt_required()
def get_todos():
    user_id = get_jwt_identity()
    # Hämta query params med request.args.get()
    status = request.args.get('status')  # Filter på status (completed)
    category = request.args.get('category')  # Filter på kategori
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)

    # Skapa query baserat på filtreringsparametrar
    query = Todo.query.filter(Todo.user_id == user_id)

    total_todos = query.count()

    if status is not None:
        completed = status.lower() == 'true'
        query = query.filter(Todo.completed == completed)

    if category:
        query = query.filter(Todo.category == category)

    # Paginera resultat
    todos = query.limit(limit).offset(offset).all()


    todo_list = []
    for todo in todos:
        todo_list.append(todo.to_dict())

    page = (offset // limit) + 1 if limit > 0 else 1
    next_offset= page * limit
    pages = (total_todos + limit - 1) // limit if limit > 0 else 1
    next_link = f'http://127.0.0.1:5000/todos?limit={limit}&offset={next_offset}'

    return jsonify({
        'data': todo_list,
        'meta': {
            'total': total_todos,
            'limit': limit,
            'offset': offset,
            'page': (offset // limit) + 1 if limit > 0 else 1,
            'pages': (total_todos + limit - 1) // limit if limit > 0 else 1,
            'next': next_link,
            'previous': f'?limit={limit}&offset={10}'
        }
    })

@app.route('/todos/search', methods=['GET'])
def search_todo():
    search_term = request.args.get('q')
    if not search_term:
        return jsonify({'error': 'Sökterm krävs'}), 400
    
    print(search_term)
    
    todos = Todo.query.filter(Todo.title.like(f'%{search_term}%'))

    return jsonify([todo.to_dict() for todo in todos])


@app.route('/todos/<int:todo_id>', methods=['GET'])
@jwt_required()
def get_todo(todo_id):
    user_id = get_jwt_identity()
    print('inside function')
    todo = Todo.query.get_or_404(todo_id)
    if todo.user_id == user_id:
        return jsonify(todo.to_dict())
    return jsonify({"message": "no todo with that id"}), 404

@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    data = request.get_json()

    if 'title' in data:
        todo.title = data['title']
    if 'completed' in data:
        todo.completed = data['completed']
    if 'deadline' in data:
        todo.deadline = datetime.fromisoformat(data['deadline'])
    if 'category' in data:
        todo.category = data['category']

    db.session.commit()
    if todo.completed:
        db.session.delete(todo)
    return jsonify(todo.to_dict())

@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    if todo.completed:
        db.session.delete(todo)
        db.session.commit()
    else:
        return jsonify({'message': 'todon är inte klar'})
    return jsonify({'message': 'Todo borttagen'}), 204

# Extra funktionalitet: Sortera efter deadline
@app.route('/todos/sort/deadline', methods=['GET'])
def get_todos_sorted_by_deadline():
    todos = Todo.query.order_by(Todo.deadline.asc()).all()
    return jsonify([todo.to_dict() for todo in todos])

# Extra funktionalitet: Filtrera efter kategori
@app.route('/todos/category/<category>', methods=['GET'])
def get_todos_by_category(category):
    todos = Todo.query.filter_by(category=category).all()
    return jsonify([todo.to_dict() for todo in todos])


@app.route('/todos/stats', methods=['GET'])
def get_todo_stats():
    total_count = Todo.query.count()

    status_stats = db.session.query(
        Todo.completed,
        db.func.count(Todo.id)
    ).group_by(Todo.completed).all()
    print(status_stats)

    # Konvertera till dictionary för enklare användning
    status_dict = {
        'completed': 0,
        'active': 0
    }

    for completed, count in status_stats:
        if completed:
            status_dict['completed'] = count
        else:
            status_dict['active'] = count

    category_stats = db.session.query(
        Todo.category,
        db.func.count(Todo.id)
    ).group_by(Todo.category).all()

        # Konvertera till dictionary
    category_dict = {}
    for category, count in category_stats:
        category_name = category if category else 'uncategorized'
        category_dict[category_name] = count

    # Returnera sammanlagd statistik
    return jsonify({
        'total': total_count,
        'by_status': status_dict,
        'by_category': category_dict
    })



@app.route('/')
def hello_world():
    return 'Välkommen till Todo API!'

if __name__ == '__main__':
    app.run(debug=True)