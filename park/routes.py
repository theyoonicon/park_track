from flask import Blueprint, jsonify, request
import sqlite3

park_bp = Blueprint('park', __name__)
DATABASE = 'park.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@park_bp.route('/', methods=['GET'])
def get_park_data():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM park_data')
    rows = cur.fetchall()
    park_data = [dict(row) for row in rows]
    conn.close()
    return jsonify(park_data)

@park_bp.route('/', methods=['POST'])
def add_park_data():
    new_data = request.get_json()
    conn = get_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO park_data (time, event, type) VALUES (?, ?, ?)',
                (new_data['time'], new_data['event'], new_data['type']))
    conn.commit()
    conn.close()
    return jsonify(new_data), 201

@park_bp.route('/<int:id>', methods=['PUT'])
def update_park_data(id):
    update_data = request.get_json()
    conn = get_db()
    cur = conn.cursor()
    cur.execute('UPDATE park_data SET time = ?, event = ?, type = ? WHERE id = ?',
                (update_data['time'], update_data['event'], update_data['type'], id))
    conn.commit()
    conn.close()
    return jsonify(update_data), 200

@park_bp.route('/<int:id>', methods=['DELETE'])
def delete_park_data(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM park_data WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return '', 204
