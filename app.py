import datetime
import json
import jwt
from database import get_db
from flask import Flask, jsonify, request, render_template, g
from functools import wraps

app = Flask(__name__)
api_username = 'admin'
api_password = 'password'


def protected(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if auth and auth.username == api_username and auth.password == api_password:
            return f(*args, **kwargs)
        return jsonify({'message': 'Authentication failed'}), 403
    return decorated


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def login_page():
    return render_template('login.html')


@app.route('/member', methods=['GET'])
@protected
def get_members():
    db = get_db()
    members_cur = db.execute('select * from members')
    members = members_cur.fetchall()
    return_values = []
    for member in members:
        member_dict = {}
        member_dict['id'] = member['id']
        member_dict['name'] = member['name']
        member_dict['email'] = member['email']
        member_dict['level'] = member['level']
        return_values.append(member_dict)

    return jsonify({'members': return_values})


@app.route('/member/<int:member_id>', methods=['GET'])
@protected
def get_member(member_id):
    db = get_db()
    member_cur = db.execute('select * from members where id = ?', [member_id])
    member = member_cur.fetchone()
    if member:
        member_dict = {}
        member_dict['id'] = member['id']
        member_dict['name'] = member['name']
        member_dict['email'] = member['email']
        member_dict['level'] = member['level']
        return jsonify(member_dict)
    else:
        return jsonify({'message': 'User not found'})


@app.route('/member', methods=['POST'])
def add_member():
    data = request.get_json()
    name = data['name']
    email = data['email']
    level = data['level']
    db = get_db()
    db.execute('insert into members(name, email, level) values (?, ?, ?)', [name, email, level])
    db.commit()

    member_cur = db.execute('select * from members where name = ? and email = ?', [name, email])
    new_member = member_cur.fetchone()
    return jsonify({'id': new_member['id'], 'name': new_member['name'], 'email': new_member['email'], 'level': new_member['level']},)


@app.route('/member/<int:member_id>', methods=['PUT', 'PATCH'])
def edit_member(member_id):
    data = request.get_json()
    name = data['name']
    email = data['email']
    level = data['level']
    db = get_db()
    db.execute('update members set name = ?, email = ?, level = ? where id = ?', [name, email, level, member_id])
    db.commit()
    member = db.execute('select * from members where id = ?', [member_id])
    member = member.fetchone()
    return jsonify({'id': member['id'], 'name': member['name'], 'email': member['email'], 'level': member['level']}, )


@app.route('/member/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    db = get_db()
    db.execute('delete from members where id = ?', [member_id])
    db.commit()
    return jsonify({'message':'Delete complete'})


if __name__ == '__main__':
    app.run()