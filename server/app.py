#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class Login(Resource):
    def post(self):
        user = User.query.filter_by(username=request.json['username']).first()

        if user:
            session['user_id'] = user.id
            return jsonify(user.to_dict())
        else:
            return jsonify({'message': 'User not found'}), 404

api.add_resource(Login, '/login')

class Logout(Resource):
    def delete(self):
        session['user_id'] = None
        return {'message': '204: No Content'}, 204

api.add_resource(Logout, '/logout')

class CheckSession(Resource):
    def get(self):
        user = User.query.filter(User.id == session.get('user_id')).first()
        print(user)
        if user:
            return user.to_dict(), 200
        else:
            return  {}, 401
        
api.add_resource(CheckSession, '/check_session')

class ClearSession(Resource):

    def delete(self):
    
        session.pop('page_views', None)
        session.pop('user_id', None)

        return {}, 204

class IndexArticle(Resource):
    
    def get(self):
        articles = [article.to_dict() for article in Article.query.all()]
        return articles, 200

class ShowArticle(Resource):

    def get(self, id):
        session['page_views'] = 0 if not session.get('page_views') else session.get('page_views')
        session['page_views'] += 1

        if session['page_views'] <= 3:

            article = Article.query.filter(Article.id == id).first()
            if article:
                return jsonify(article.to_dict()), 200
            else:
                return jsonify({'message': 'Article not found'}), 404
        else:
            return jsonify({'message': 'Maximum pageview limit reached'}), 401


api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
