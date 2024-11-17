from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify
from flask_login import login_user, logout_user, login_required,current_user
from datetime import datetime
from server.models.document import Document
from server.models.image import Image
import fitz
import uuid
import os


file_controller = Blueprint('file_controller', __name__)  

@file_controller.route('/<id>', methods=['GET'])
def file(id):
    return render_template('upload.html', id=id)


@file_controller.route('/upload', methods=['POST'])
def upload_file():
    from server.main import app
    from server.app import db
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    docs_uuid = str(uuid.uuid4())
    docs = Document(id=docs_uuid,user_id=current_user.id, name=file.filename, created_at=datetime.now(),updated_at=datetime.now())
    if not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'],docs_uuid)):
        os.mkdir(os.path.join(app.config['UPLOAD_FOLDER'],docs_uuid))
    db.session.add(docs)
    
    if file and file.filename.endswith('.pdf'):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        # file.save(filepath)

        images = []
        with fitz.open(filepath) as pdf:
            for page_number, page in enumerate(pdf, start=1):
                pix = page.get_pixmap()
                img_uuid = str(uuid.uuid4())
                
                image_path = f"{app.config['UPLOAD_FOLDER']}{docs_uuid}/{img_uuid}.png"
                pix.save(image_path)
                images.append(image_path)

                image = Image(id=img_uuid,document_id=docs_uuid, path=image_path, file_number=page_number, created_at=datetime.now(),updated_at=datetime.now())
                db.session.add(image)
        
        db.session.commit()

        return jsonify({"images": images}), 200

    elif file and file.filename.endswith('.jpg') or file.filename.endswith('.jpeg') or file.filename.endswith('.png'):
        img_uuid = str(uuid.uuid4())
        filepath = os.path.join(app.config['UPLOAD_FOLDER'],docs_uuid,'/', img_uuid)
        file.save(filepath)
        image = Image(id=img_uuid,document_id=docs_uuid, path=image_path, file_number=1, created_at=datetime.now(),updated_at=datetime.now())
        db.session.add(image)
        db.session.commit()
        return jsonify({"image": filepath}), 200
    
    return jsonify({"error": "Unsupported file type"}), 400