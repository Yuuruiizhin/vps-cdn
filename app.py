import os
import mimetypes
from flask import Flask, request, render_template, send_file, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
# CORS habilitado para que los recursos carguen en otras webs (CDN)
CORS(app, resources={r"/cdn/*": {"origins": "*"}})

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024 

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def get_file_type(filename):
    ext = filename.lower().split('.')[-1]
    if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg']: return 'image'
    if ext in ['mp4', 'webm', 'ogg']: return 'video'
    return 'other'

@app.route('/')
def index():
    files_list = []
    for f in os.listdir(app.config['UPLOAD_FOLDER']):
        if not f.startswith('.'):
            ftype = get_file_type(f)
            files_list.append({
                "name": f,
                "type": ftype,
                "relative_url": f"/cdn/{f}"
            })
    return render_template('index.html', files=files_list)

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    if file and file.filename:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({"success": True})
    return jsonify({"error": "Error al subir"}), 400

@app.route('/delete/<name>', methods=['DELETE'])
def delete_file(name):
    try:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], name))
        return jsonify({"success": True})
    except:
        return jsonify({"error": "Error al borrar"}), 400

@app.route('/cdn/<name>')
def serve_cdn(name):
    path = os.path.join(app.config['UPLOAD_FOLDER'], name)
    if not os.path.exists(path): return "404", 404
    mimetype, _ = mimetypes.guess_type(path)
    return send_file(path, mimetype=mimetype, as_attachment=False)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

