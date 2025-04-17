# -*- coding: utf-8 -*-
import os, time, unicodedata, re
from flask import (
    Flask, request, render_template,
    jsonify, Response, redirect, url_for, session
)
from werkzeug.utils import secure_filename
import dropbox

app = Flask(__name__)
app.secret_key = 'super-secret-key-15010'   # rotate in prod
app.config['JSON_AS_ASCII'] = False

# ——— TOKEN PERSISTENCE —————————————————————————————
TOKEN_FILE = 'token.txt'
DEFAULT_TOKEN = 'sl.u.AFqCxBAU7FetY1CXAQ‑…<snip>…M5sd7iQ'

def load_token():
    if os.path.exists(TOKEN_FILE):
        return open(TOKEN_FILE, 'r').read().strip()
    with open(TOKEN_FILE, 'w') as f:
        f.write(DEFAULT_TOKEN)
    return DEFAULT_TOKEN

def save_token(token: str):
    with open(TOKEN_FILE, 'w') as f:
        f.write(token)

ACCESS_TOKEN = load_token()
dbx = dropbox.Dropbox(ACCESS_TOKEN)

# ——— ROLES & PASSWORDS ————————————————————————————
ADMIN_PASSWORD = '15010'
OWNER_PASSWORD = 'Rutuj@openfile'

def sanitize_filename(fn: str) -> str:
    nfkd = unicodedata.normalize('NFKD', fn)
    ascii_only = nfkd.encode('ascii', 'ignore').decode('ascii')
    safe = secure_filename(ascii_only)
    return re.sub(r'[^A-Za-z0-9._-]', '_', safe) or f"file_{int(time.time())}"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    pw = request.get_json().get('password','')
    if pw == OWNER_PASSWORD:
        session['role'] = 'owner'
        return jsonify({'status':'ok'})
    if pw == ADMIN_PASSWORD:
        session['role'] = 'admin'
        return jsonify({'status':'ok'})
    return jsonify({'status':'bad'}), 401

@app.route('/set_client')
def set_client():
    session['role'] = 'client'
    return redirect(url_for('files_page'))

@app.route('/files_page')
def files_page():
    role = session.get('role')
    if role not in ('owner','admin','client'):
        return redirect(url_for('home'))
    return render_template('files.html', role=role)

@app.route('/upload', methods=['POST'])
def upload_file():
    if session.get('role') not in ('admin','owner'):
        return Response('Forbidden', 403)
    f = request.files.get('file')
    url = request.form.get('url')
    if f and f.filename:
        fn = sanitize_filename(f.filename)
        path = f'/{fn}'
        dbx.files_upload(f.read(), path, mode=dropbox.files.WriteMode.overwrite)
        return Response('File uploaded 😎', content_type='text/plain; charset=utf-8')
    if url:
        ts = int(time.time())
        fn = f'link_{ts}.txt'
        path = f'/{fn}'
        dbx.files_upload(url.encode('utf-8'), path, mode=dropbox.files.WriteMode.overwrite)
        return Response('URL saved 😈', content_type='text/plain; charset=utf-8')
    return Response('Nothing to do 🤷‍♂️', content_type='text/plain; charset=utf-8')

@app.route('/delete', methods=['POST'])
def delete_file():
    if session.get('role') != 'owner':
        return jsonify({'status':'forbidden'}), 403
    name = request.get_json().get('name')
    if name:
        dbx.files_delete_v2(f'/{name}')
        return jsonify({'status':'deleted'})
    return jsonify({'status':'no name'}), 400

@app.route('/files', methods=['GET'])
def list_files():
    entries = dbx.files_list_folder('').entries
    out = []
    for e in entries:
        if isinstance(e, dropbox.files.FileMetadata):
            link = dbx.files_get_temporary_link(e.path_display).link
            out.append({'name': e.name, 'link': link})
    return jsonify(out)

@app.route('/set_token', methods=['POST'])
def set_token():
    if session.get('role') not in ('admin','owner'):
        return jsonify({'status':'forbidden'}), 403
    token = request.get_json().get('token','').strip()
    if token:
        save_token(token)
        global dbx
        dbx = dropbox.Dropbox(token)
        return jsonify({'status':'token updated'})
    return jsonify({'status':'no token provided'}), 400

if __name__ == '__main__':
    app.run(debug=True)
