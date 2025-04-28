from datetime import datetime
from flask import Flask, jsonify, request
from models import db, Todo


app = Flask(__name__)

# Konfigurera SQLite-databasen
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initiera databasen
db.init_app(app)

# Skapa databastabeller
with app.app_context():
    db.create_all()

todos = []


@app.route('/todos', methods=['POST'])
def create_todo():
    data = request.get_json()

    if not data or 'title' not in data:
        return jsonify({"error": "Titel krävs"}), 400
    
    new_todo = Todo(
        title=data['title'],
        completed=data.get('completed', False),
        deadline=datetime.fromisoformat(data['deadline']) if 'deadline' in data else None,
        category=data.get('category')
    )

    db.session.add(new_todo)
    db.session.commit()

    return jsonify(new_todo.to_dict()), 201

@app.route('/todos', methods=['GET'])
def get_todos():

    # Hämta query params med request.args.get()
    status = request.args.get('status')  # Filter på status (completed)
    s = request.query_string
    print(s)
    category = request.args.get('category')  # Filter på kategori
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)

    # Skapa query baserat på filtreringsparametrar
    query = Todo.query

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

    return jsonify(todo_list)

@app.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    print('inside function')
    todo = Todo.query.get_or_404(todo_id)
    return jsonify(todo.to_dict())

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


@app.route('/')
def hello_world():
    return 'Välkommen till Todo API!'

if __name__ == '__main__':
    app.run(debug=True)