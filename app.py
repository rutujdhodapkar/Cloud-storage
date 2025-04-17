# app.py
# -*- coding: utf-8 -*-
from flask import (
    Flask, request, render_template,
    jsonify, Response, redirect, url_for, session
)
from werkzeug.utils import secure_filename
import dropbox, time, unicodedata, re

app = Flask(__name__)
app.secret_key = 'super-secret-key-15010'     # rotate this in prod
app.config['JSON_AS_ASCII'] = False

DROPBOX_ACCESS_TOKEN = 'sl.u.AFqCxBAU7FetY1CXAQ-jY6bwsJoY4fkFhNUpyi3wSLHO3AF1WlmJ1QN-EGZGr8v1cOamjkeIIt1HHVzWLwYVpS4G-hRHj9KATBXYui3OFbY0VnbACt5lbZw8hLrwP94xShZfpVbmor-MBYtoa35sqG26zIodCbADEY3JQH_4wsX0gYr8RZypFu2t-H6zLZfqXq_cOq5JpKaYInJ2slN6h26BvP8ECeR38noq0uAk8147XulmtQQOTrYiI0a31WSi_IRxnBCgPsR4CMzNZq9ksyvP3eIFuzUbfHduxJA7oqfOCboPORY95HNmsvgJ8nXaPbU1s9gGrdgQ0MtK0gUXK7oxmPBY8dxlVc3DhcwK0vCcOHCxxxDQ7Lq5iLzbyc2pNyder3doZUoup-zLY_9une3o0-qf5arHf_Dx8p5cGZYZXpXYKBSm--pc2-WE0TO-QuDo7p1-FO9xuVxIi7Gq72ExQS283KWHi9Sz_KxcIPMVRLGg3LjZzBhScdVogs1ZuDvCl1TK48UKYpgXVDGz9EhDBRcZKyaRLOg9Tuq7HBh25NnVg23slZqfd8GCPmwY9Kvx3RqHRPzvzmDra2w5nm7ws1XLRDPfkK0Cdeybvn_pbK55LNKoPul8yM7WnUm3_xzid6tKrokuQoFkd_tVBde21BnoDrXY97ObK9pp_KEyGxRZtcbXy2V_atUVfZj8gtPXfL6klitbq7IfmlePKAagZIckxA24JRSzWHdKdkCemKe0zcAV1g_Js7AWizKtWVSI9aPzSDiVbdS6lNhMfk64739LXnmanSf2BquVz7EI94shtgjxjdKDGsYz8lDMk5ImAKf-9H0HcRcEE_zRe-ab5fZaqpTsm3UwQwgZnw8U_n7Pzm0qI7-iUDv-pjs-oJYP7dXhwLEE_2wZGbjd-tfabcRKGpoqXBlnfkyTkh2iTfY-j_uzL7DMCdb1049aOS79Agym5lORPh_UHcVDh5getGs7nONPMiiaPMZGJC27ZMUDmxptXHIOFxZRXAaZLgfldlIm53r5l9wmBKnNJhM8IY85T6-C4povV-w5rgmKKWhLOv2AfU5itMkgKSMLRVJrpXhPhOoBiqyR7Kw7lNWOQ1N4D5tKr_9yjqKkXlIyEME2nYJd7AiPGRgBpRopfj_VY2S8ajfF1DraUAUbMCCjjkNfEe0BNSpBkFpvoYOrK4skp023CIyWdk1A93qoqTNKhtJ9GYKgcWDiwzuOqmVLQY5lRL68JN--_RZj3llvxC3a3zDJAfgB1tgLfLu06tm53yxsECiBoJ4q_M5sd7iQ'
dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)

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
    data = request.get_json()
    pw = data.get('password', '')
    if pw == OWNER_PASSWORD:
        session['role'] = 'owner'
        return jsonify({'status': 'ok'})
    if pw == ADMIN_PASSWORD:
        session['role'] = 'admin'
        return jsonify({'status': 'ok'})
    return jsonify({'status': 'bad'}), 401

@app.route('/set_client')
def set_client():
    session['role'] = 'client'
    return redirect(url_for('files_page'))

@app.route('/files_page')
def files_page():
    role = session.get('role')
    if role not in ('owner', 'admin', 'client'):
        return redirect(url_for('home'))
    return render_template('files.html', role=role)

@app.route('/upload', methods=['POST'])
def upload_file():
    if session.get('role') not in ('admin', 'owner'):
        return Response('Forbidden', status=403)
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
        return jsonify({'status': 'forbidden'}), 403
    data = request.get_json()
    name = data.get('name')
    if name:
        dbx.files_delete_v2(f'/{name}')
        return jsonify({'status': 'deleted'})
    return jsonify({'status': 'no name'}), 400

@app.route('/files', methods=['GET'])
def list_files():
    entries = dbx.files_list_folder('').entries
    out = []
    for e in entries:
        if isinstance(e, dropbox.files.FileMetadata):
            temp = dbx.files_get_temporary_link(e.path_display).link
            out.append({'name': e.name, 'link': temp})
    return jsonify(out)

if __name__ == '__main__':
    app.run(debug=True)
