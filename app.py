# app.py
# -*- coding: utf-8 -*-
import os, time, unicodedata, re
from flask import (
    Flask, request, render_template,
    jsonify, Response, redirect, url_for, session
)
from werkzeug.utils import secure_filename
import dropbox

app = Flask(__name__)
app.secret_key = 'super-secret-key-15010'   # rotate this in prod
app.config['JSON_AS_ASCII'] = False

# — TOKEN PERSISTENCE —
TOKEN_FILE = 'token.txt'
DEFAULT_TOKEN = 'sl.u.AFpbqha2KTAJ5enhxSAHWUItC_qHhZtQXecAGDeNt3ecmIpbqWyRp1-CXwV1O7nUCXWxoeQ2xwbnmYsg7iHKzAORamlFSjQp8b5bsQm9vW9S9LO5I6iaVq8Ri_oW3EgZbipMROMN8vtfdQEbB7-hLUU9lISnqSs_mg8YbAqdnzk8uQugrOwTASQk1I3mtu5T88W-RGnQpIw75eyfgl7FhGfdbF4Hp2Pya9d1oyias1Pvw_CXR88MlM2fj3iz490UxSmXpudtXoQZqJxjCb2QlI1a697IFxUQGC_e4fOBWm033osX1EOEmvmm4L77tvzvjFA-vaqds5gCXb67vfO_ni-31_bTRL8ezgxOkK2sj3kZxaCN3DqoqjnO17fY-XLHsVm-zyi3jLK7lY0LRJ3_dPyzGp7fQK_SPhoL51h-8geswH-mWAOxXJLQPcO6bs3BuMxho5n3vfeQOzXs8Q4wQcF7nTPCBxInVP_juTX0Tvh2pdI_Bu6oZn_EwpOKs3IUxP6U5NhR45mM3QoEKFi8qq14OuudKuT2y-HnmBz2bRoD2oo1XU9KLqSd1Dea8zg5vm6GmIZKOHTQjdtJCKOPRiFQxXJkKrc0ep77mREQFcX04V40X-mmDI8785-38YXY2wzLWhqDUsUSbK52j94vFuX_cyp8aSRl4UgWKXsMmdMs7Qb7nAO_KjvDVz-gb8Gs5cep2vN2-X5CIgLyAxfx-TGkOYkYsbwOhfEU_8OP2THGqoxhOd9wLD0ZBZwL8Sj6nQqLre5sZAPt6igTok7rSPUH32eZ_NcNZ2lTpKuyDA-H2ZZnVpn_optLSFuF-YNyLWLVhE5XZ5Og3_NDlff0qpEzBpaD6y07mWFvKptuNszfCHAK_qu1LbaO-z9Q3S6FZXZuA8yNE8qMDskARYBCRhdKu4fVnXdE-oELq_51qrGPfr4iOpvhu9qnim93ZZzM5o0xRcxADfxdNY-iha-x1ykopG5bhFXa9S1iymRu6ewM5SJuM9Tr3iGcvoxc3CgwHXuBR4rtLo7dnsj_JUKgIn_GuRKI0stZU1tstxoezYB5nk-OLIEY3qbRElKtGqcM4ivOVb2r0Ys2_ZnG791EikJCufsq69QLNBFxHZHA1SRvaJYeOOyw8adZXSWfZJP_QIhA9WSRCV0jHJ8tTgye5XCml9zEy_lMmEfzG4aJSXvicwwd0M53qPTm-FcwsgAima4jtZAj0CaaWyrGnXSAAc6-df9y9JXnuruBWDgUCbpul-h44Km-nWaue078pgZ1_TkRcdtfprndrjcIHsUHUj2BAojz4Zj0cJFbFJb_W1x4rA'

def load_token():
    if os.path.exists(TOKEN_FILE):
        return open(TOKEN_FILE).read().strip()
    open(TOKEN_FILE, 'w').write(DEFAULT_TOKEN)
    return DEFAULT_TOKEN

def save_token(token: str):
    with open(TOKEN_FILE, 'w') as f:
        f.write(token)

ACCESS_TOKEN = load_token()
dbx = dropbox.Dropbox(ACCESS_TOKEN)

# — ROLES & PASSWORDS —
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
        session['role'] = 'owner'; return jsonify({'status':'ok'})
    if pw == ADMIN_PASSWORD:
        session['role'] = 'admin'; return jsonify({'status':'ok'})
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
    custom = request.form.get('custom_name','').strip()
    url = request.form.get('url')
    if f and f.filename:
        filename = custom or f.filename
        fn = sanitize_filename(filename)
        dbx.files_upload(f.read(), f'/{fn}', mode=dropbox.files.WriteMode.overwrite)
        return Response('File uploaded 😎', content_type='text/plain; charset=utf-8')
    if url:
        ts = int(time.time())
        fn = f'link_{ts}.txt'
        dbx.files_upload(url.encode('utf-8'), f'/{fn}', mode=dropbox.files.WriteMode.overwrite)
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

@app.route('/rename', methods=['POST'])
def rename_file():
    if session.get('role') not in ('admin','owner'):
        return jsonify({'status':'forbidden'}), 403
    data = request.get_json()
    old, new = data.get('old'), data.get('new','').strip()
    if old and new:
        try:
            dbx.files_move_v2(f'/{old}', f'/{sanitize_filename(new)}', autorename=False)
            return jsonify({'status':'renamed'})
        except Exception as e:
            return jsonify({'status':'error','error':str(e)}), 500
    return jsonify({'status':'invalid'}), 400

@app.route('/files', methods=['GET'])
def list_files():
    out = []
    for e in dbx.files_list_folder('').entries:
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
    return jsonify({'status':'no token'}), 400

if __name__ == '__main__':
    app.run(debug=True)
