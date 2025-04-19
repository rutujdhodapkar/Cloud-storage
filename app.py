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
DEFAULT_TOKEN = 'sl.u.AFp0dcFvFq5snqc_B4OkjiCUKjOf9cEKYkm1uTzIB5hZtnWw-SKET5urzwoMHbOe1H4klCfNRsGruFoGt69jKY4UexQkU00rIEP-eOcBK7dZwq-X14g8R-vkNMAyljsq6BaxTfYXa-2qHobYJF4A9D73jBnsnzI2yHp3eDJmQQpB45LG5I6FLpAu_hT3qOGvEqo2RczsBXla-RaXiqlb7c2OMLopuMU_d5t4DSGB1EtYby57DT5Ob_K7ofdQdkRIN7CpZgQkEoXyG4PN-DXWo0Ehq6oPvI_im2CXVIFdAZHoup-YIJK98tjyuFyvgK9FMqOHFZwCRc-y64USXX8CEpjuFccyIWIyTsbiMNg14ZSxNKHKp6UDbGJhi8ywe8FeLTI4ixNNBQdkPr42gbZ73qF2F2QNEwZxiDk_gbYyIcBcRoDOb8om-3i9EPlArLQgGzM6zmNryIDnMkk5kcWh6-2nrZx-pXRG2owfrbcCj_4YANAmZb9XMOUHDPX0mThNAqeubNpC0dEuC22FlR6Ypl-fJSnTCmx0HmHa2xHcSwJ6sutE-gYpWw3d5vvIkHmt6nBzUYRF74GpIOvhye1_r0QWg-Y0Z_k2U3_4P_dwjQVcr0C5er0iDJhbFGcjNK8Y1vRqg4yFsWrd-i0wrhu-eqe9zFbUeLsuPj4RK5ioAeG2ZCwIADbi8g8pDDTRqswSjVV2cyddi3hwnq44j3T4u1XjGORGfuSigCOXvhM4Pzjf0q97oPRUuS_reK7omob727TA2kM0CgJb-_vhZ8dZPB3JFAXH5HRgnkgye31Swm4VtLEpHWK8wKyN3PHdvMHHiajuSz-_ZZRdZ7h5S_jD_d5puLFzjNZGHRbpg3-cL7usgKwy0FSqD9aW2ZtHDzrU6P79u9q7Zk1mDJT9iN5h_gDu_LDtNfmoCXAWQFz8cJD7M6Gx8hM2955TgM6VbGCGHiiSW3ZOZrEdtQ4_CzXStmfsqo2LICopw_WnrWEiwdXRoObm3N8cGy0Xy_8sxkVQW4eW7nemXH7hCS1zxVBmLjz_2tUqZ8f75avJqDJIR_5VOII3BoXlxYe6zCgynPsNGdmzKWzq4z8xEmq3V0vBlDGmo9H7H5ZnGtadgWH6itWNGpd0fg881sYJwW74O8Zis5ZJiBRYOG93Fs9RSWszje9SUjJzM-Vj6U6JhzBW-yb4vgzXx78CekRSKs-hscVwrSNyQGRlnIgnKAXtlAftptdglvmu8OUuuGV8r78T-f-yprqNwz2laL0Mjd9MXYE1knoYZjx2DEPpWCal4XCo1wL7MtI4yUuV8lCdmj6SPs9KWg'
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
