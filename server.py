#!/usr/bin/env python3
import os
import sqlite3

from flask import Flask, jsonify, make_response, redirect, render_template, request, session, url_for

import settings
import json
from llamaapi import LlamaAPI
import re
import sandbox
from utils.highlighter import format

app = Flask(__name__)
app.config.from_object(settings)
llama = LlamaAPI("LL-HBi6JM821yWlnqGnNvW9YjrZ1vDbAKZuv3Itd561KfDnou4Xl61scomeLRNcqbr7")

# Helper functions
def _get_message(id=None):
    """Return a list of message objects (as dicts)"""
    with sqlite3.connect(app.config['DATABASE']) as conn:
        c = conn.cursor()

        if id:
            id = int(id)  # Ensure that we have a valid id value to query
            q = "SELECT * FROM messages WHERE id=? ORDER BY dt DESC"
            rows = c.execute(q, (id,))

        else:
            q = "SELECT * FROM messages ORDER BY dt DESC"
            rows = c.execute(q)

        return [{'id': r[0], 'dt': r[1], 'message': r[2]} for r in rows]


def _add_message(message):
    with sqlite3.connect(app.config['DATABASE']) as conn:
        c = conn.cursor()
        q = "INSERT INTO messages VALUES (NULL, datetime('now', 'localtime'),?)"
        c.execute(q, (message, ))
        conn.commit()
        return c.lastrowid


def _delete_message(ids):
    with sqlite3.connect(app.config['DATABASE']) as conn:
        c = conn.cursor()
        q = "DELETE FROM messages WHERE id=?"

        # Try/catch in case 'ids' isn't an iterable
        try:
            for i in ids:
                c.execute(q, (int(i),))
        except TypeError:
            c.execute(q, (int(ids),))

        conn.commit()


# Standard routing (server-side rendered pages)
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        msg = request.form['message']
        _add_message(msg)
        while True:
            response = get_llm_response(msg)
            print(f"========RESPONSE========\n{response}\n========END========")

            if (re.search(r'```(?:python)?(.*?)```', response, re.DOTALL | re.IGNORECASE)) is not None:
                response = (re.search(r'```(?:python)?(.*?)```', response, re.DOTALL | re.IGNORECASE))
            
            else:
                response = (re.search(r'---(?:python)?(.*?)---', response, re.DOTALL | re.IGNORECASE))
                
                if response is None:
                    continue

            response = response.group(1).strip()
            sandbox_response = sandbox.get_error(response)

            print(f"=====CODE MATCHED. EVALUATION: {sandbox_response}=====\n")

            if sandbox_response is not None:
                _add_message(format(response))
                break

        redirect(url_for('home'))

    return render_template('index.html', messages=_get_message())

def get_llm_response(message):
    api_request_json = {
        "messages": [
            {"role": "system", "content": "You are a system that helps users in debugging Python programs delimited with ``` at start and finish. Keep your messages short. Your task is to provide complex and long python programs with one or more critical errors and no comments. The user's task is to identify the errors in the code and correct them. Do not write code snippets, instead focus on whole, longer programs."},
            {"role": "user", "content": message},
        ],
        "parameters": {"temperature":0.9}
    }

    # Execute the Request
    response = llama.run(api_request_json)
    output = json.dumps(response.json(), indent=2)
    data = json.loads(output)
    data = data['choices'][0]['message']['content']

    return data

@app.route('/about')
def about():
    return render_template('test.html', highlighted_code=format())


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not 'logged_in' in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # This little hack is needed for testing due to how Python dictionary keys work
        _delete_message([k[6:] for k in request.form.keys()])
        redirect(url_for('admin'))

    messages = _get_message()
    messages.reverse()

    return render_template('admin.html', messages=messages)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME'] or request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid username and/or password'
        else:
            session['logged_in'] = True
            return redirect(url_for('admin'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))


# RESTful routing (serves JSON to provide an external API)
@app.route('/messages/api', methods=['GET'])
@app.route('/messages/api/<int:id>', methods=['GET'])
def get_message_by_id(id=None):
    messages = _get_message(id)
    if not messages:
        return make_response(jsonify({'error': 'Not found'}), 404)

    return jsonify({'messages': messages})


@app.route('/messages/api', methods=['POST'])
def create_message():
    if not request.json or not 'message' in request.json:
        return make_response(jsonify({'error': 'Bad request'}), 400)

    id = _add_message(request.json['message'])

    return get_message_by_id(id), 201


@app.route('/messages/api/<int:id>', methods=['DELETE'])
def delete_message_by_id(id):
    _delete_message(id)
    return jsonify({'result': True})


if __name__ == '__main__':

    # Test whether the database exists; if not, create it and create the table
    if not os.path.exists(app.config['DATABASE']):
        try:
            conn = sqlite3.connect(app.config['DATABASE'])

            # Absolute path needed for testing environment
            sql_path = os.path.join(app.config['APP_ROOT'], 'db_init.sql')
            cmd = open(sql_path, 'r').read()
            c = conn.cursor()
            c.execute(cmd)
            conn.commit()
            conn.close()
        except IOError:
            print("Couldn't initialize the database, exiting...")
            raise
        except sqlite3.OperationalError:
            print("Couldn't execute the SQL, exiting...")
            raise

    app.run(host='0.0.0.0')