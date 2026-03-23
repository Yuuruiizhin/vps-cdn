import os
from flask import Flask, request, render_template, url_for, send_from_directory, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def is_image(filename):
    ext = filename.lower().split('.')[-1]
    return ext in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg']

@app.route('/')
def index():
    files_list = []
    for f in os.listdir(app.config['UPLOAD_FOLDER']):
        if not f.startswith('.'):
            files_list.append({
                "name": f,
                "is_img": is_image(f),
                "url": url_for('download_file', name=f, _external=True)
            })
    return render_template('index.html', files=files_list)

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    if file and file.filename:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({"success": True})
    return jsonify({"error": "Fallo al subir"}), 400

@app.route('/delete/<name>', methods=['DELETE'])
def delete_file(name):
    try:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], name))
        return jsonify({"success": True})
    except:
        return jsonify({"error": "No se pudo borrar"}), 400

@app.route('/cdn/<name>')
def download_file(name):
    return send_from_directory(app.config['UPLOAD_FOLDER'], name)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

