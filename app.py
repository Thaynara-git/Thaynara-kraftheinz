import os
from datetime import datetime

from flask import Flask, redirect, render_template, request, send_from_directory, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect


app = Flask(__name__, static_folder='static')
csrf = CSRFProtect(app)

# WEBSITE_HOSTNAME exists only in production environment
if 'WEBSITE_HOSTNAME' not in os.environ:
    # local development, where we'll use environment variables
    print("Loading config.development and environment variables from .env file.")
    app.config.from_object('azureproject.development')
else:
    # production
    print("Loading config.production.")
    app.config.from_object('azureproject.production')

app.config.update(
    SQLALCHEMY_DATABASE_URI=app.config.get('DATABASE_URI'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)

# Initialize the database connection
db = SQLAlchemy(app)

# Enable Flask-Migrate commands "flask db init/migrate/upgrade" to work
migrate = Migrate(app, db)

# The import must be done after db initialization due to circular import issue
from models import Topico, Review

@app.route('/', methods=['GET'])
def index():
    print('Request for index page received')
    topicos = Topico.query.all()
    return render_template('index.html', topicos=topicos)

@app.route('/<int:id>', methods=['GET'])
def details(id):
    topico = Topico.query.where(Topico.id == id).first()
    reviews = Review.query.where(Review.topico == id)
    return render_template('details.html', topico=topico, reviews=reviews)

@app.route('/create', methods=['GET'])
def create_topico():
    print('Request for add restaurant page received')
    return render_template('create_topico.html')

@app.route('/add', methods=['POST'])
@csrf.exempt
def add_topico():
    try:
        titulo = request.values.get('titulo')
        categoria = request.values.get('categoria')
        descricao = request.values.get('descricao')
    except (KeyError):
        # Redisplay the question voting form.
        return render_template('add_restaurant.html', {
            'error_message': "You must include a restaurant name, address, and description",
        })
    else:
        topico = Topico()
        topico.titulo = titulo
        topico.categoria = categoria
        topico.descricao = descricao
        db.session.add(topico)
        db.session.commit()

        return redirect(url_for('details', id=topico.id))

@app.route('/review/<int:id>', methods=['POST'])
@csrf.exempt
def add_review(id):
    try:
        usuario = request.values.get('usuario')
        nota = request.values.get('nota')
        texto_review = request.values.get('texto_review')
    except (KeyError):
        #Redisplay the question voting form.
        return render_template('add_review.html', {
            'error_message': "Error adding review",
        })
    else:
        review = Review()
        review.topico = id
        review.data_review = datetime.now()
        review.usuario = usuario
        review.nota = int(nota)
        review.texto_review = texto_review
        db.session.add(review)
        db.session.commit()

    return redirect(url_for('details', id=id))

@app.context_processor
def utility_processor():
    def star_rating(id):
        reviews = Review.query.where(Review.topico == id)

        notas = []
        review_count = 0
        for review in reviews:
            notas += [review.nota]
            review_count += 1

        avg_rating = sum(notas) / len(notas) if notas else 0
        stars_percent = round((avg_rating / 5.0) * 100) if review_count > 0 else 0
        return {'avg_rating': avg_rating, 'review_count': review_count, 'stars_percent': stars_percent}

    return dict(star_rating=star_rating)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run()
