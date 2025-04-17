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

DROPBOX_ACCESS_TOKEN = 'sl.u.AFoR3VQP7u0n4z7SpP0W777vNBmyokyGagwLVmKbk2BwOvQIDEnr3ndIYFesUBfiC-K4kyAS7aBQ2IxrQvUOSL_E1qrC3bGJUFt6J61FpTiv-z6oKQUm_W71mCFn2nazLzB5RY7IJv1C05xlNEvOFJiIEq0Eu62HGi80mVn4NlyeCQLiof8UO1X_JKbgMbnNLx9obPAkKj__Xf3c-e59UXjuPoBwXXNXV-8IC_EgjDbyDfc1-cgZCwunW7xGbKR5LoZBCGy4pXa1RExvCnvMHOHP3AXMON51o9o7ES8VNgjAFxTewbZOLQsC7wczrv1HTjy508VnY12G3eDrXzyTQZ-HBCqgJQkl6GOeJkPtxqfo7FlI4491k1ou_Vfv13EBnU56YpgcT1FIKl_cThyH5JpnJwPEDZfc-f5ZOtfSbNKwocFL6GUUqO2K1NKnIhVVWaTrTGxiw2k195WJAw03PeTH17Btxznh_HKxld4T10t79vzHUavc-nFJ9NI6fL1WpOJ2YC19V-Pojw_PH0qsxJYNEL9j5hjynhjYL02VQbx96I7NSG8h8UhTKvKX_tOM1sz4kxeigPbDpY-l-RNqjpRvYjGQWBaUgFTqkCOARSl9SiZIgE0QRrquixvbP9XCa4cYeEt3CZcyZ4pYwlVsmU2LkkYZGjja34J4pWEOtWqJjfNp9abDYICEcmyifETLH6rNuhFEdbEJ5So-1bxKJHxfgsNN4wVEGG7uYhRXYcuywAYocgU0N6FqtAfbqbz-8tEwvUfaPA0iajYQUgL-TRgl8lYWNQAhv9NdbQlIoMlRcQ2s0l0MR4LMTTbOj9kz0V0y_k85YZDDknKE8DO-0mDLd1I7r0xjaPqsTRZueHgkpwDgyrwVR5LZAw8a_qOud1uyLZBq84O6OjP63LmVaK8PGsEZ_S7sszBckUzD1wUmUyu8S8YgJeJy_u9G8ytse1ZNjJW_GXx7FwDLdvaGVV7jIuRI-FT2AUFv6BhkdgCYY157gKYaD5DyMOVEPkyoePYgB2sYWvWfhoIo8cZyJNxpVwvcoP2hO7alZJP3BCXLQsVsUw339YP6lW5zY9ZDTkxuUDdcx-EpwZx5pB7hSlJrMw9MqlD1HAQAIAIpI9ddQIJgZOx-8ZQyrsdoPKvYcH4gvbONa9S67e1xYgyVBiCBu9cX2QEv3FPDk9KwyZqrNaIq1t-p6W8nkGRuBgcnkkI0ELYDe6l4zNQ8Ori27vQdMm4XHa7yFFG-EE01Bc9yRitlP9K8DskQXlG_5mHQM4RFbE0gENBIaRuyTOjWKmALKYxlkuYDcG0FwMHMbz0uww'
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
