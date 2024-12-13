from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify, send_file
from flask_login import login_user, logout_user, login_required,current_user
from datetime import datetime
from models.document import Document
from models.image import Image
from models.user import User
from app import db
import fitz
import uuid
import os
import io

file_controller = Blueprint('file_controller', __name__)
folder_path = os.getenv('IMAGE_FOLDER')

@file_controller.route('/<id>', methods=['GET','DELETE'])
@login_required
def file(id):
    if request.method == 'DELETE':
        docs = Document.query.filter_by(id = id).first()
        if not docs:
            flash('Document not found', 'error')
            return jsonify({"message": "Document not found"}), 404
        db.session.delete(docs)
        db.session.commit()
        try:
            os.rmdir(os.path.join(folder_path, id))
        except FileNotFoundError:
            pass 
        flash('Document deleted successfully', 'success')
        return jsonify({"message": "Document deleted successfully"}), 200
    docs= Document.query.filter_by(id = id).first()
    if not docs:
        return redirect(url_for('file_controller.docs_list'))
    return render_template('upload.html', docs=docs)

@file_controller.route('/list', methods=['GET'])
@login_required
def docs_list():
    docs_list = Document.query.filter_by(user_id=current_user.id).order_by(Document.updated_at.desc()).all()
    return render_template('document.html', docs_list=docs_list)

@file_controller.route('/download/<id>', methods=['GET'])
@login_required
def download_docs(id):
    docs = Document.query.filter_by(id=id).first()
    if not docs:
        flash('Document not found', 'error')
        return jsonify({"message": "Document not found"}), 404 
    
    pdf = fitz.open()
    
    for image in docs.images:
        image_path = os.path.join('static', image.path)
        img = fitz.open(image_path)
        if img is None:
            print('nt')
        print(img)
        pdf.insert_file(img)
        
    pdf_bytes = io.BytesIO()
    pdf.save(pdf_bytes)
    pdf_bytes.seek(0)
    
    return send_file(pdf_bytes, as_attachment=True, download_name=docs.name, mimetype='application/pdf')

        
        

    


@file_controller.route('/upload', methods=['POST'])
def upload_file():
    from main import app
    from app import db
    
    if current_user.is_authenticated == False:
        return jsonify({"error" : "Not Authenticated"}),401
    
    if 'file' not in request.files:
        flash('No file part', 'error')
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'error')
        return jsonify({"error": "No selected file"}), 400

    docs_uuid = str(uuid.uuid4())
    docs = Document(id=docs_uuid,user_id=current_user.id, name=file.filename, created_at=datetime.now(),updated_at=datetime.now())
    if not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'],docs_uuid)):
        os.mkdir(os.path.join(app.config['UPLOAD_FOLDER'],docs_uuid))
    db.session.add(docs)
    
    if file and file.filename.endswith('.pdf'):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'],docs_uuid,'/', file.filename)
        file.save(filepath)

        with fitz.open(filepath) as pdf:
            for page_number, page in enumerate(pdf, start=1):
                pix = page.get_pixmap()
                img_uuid = str(uuid.uuid4())
                
                file_path = f"{app.config['UPLOAD_FOLDER']}{docs_uuid}/{img_uuid}.png"
                image_path = f"{folder_path}{docs_uuid}/{img_uuid}.png"
                pix.save(file_path)

                image = Image(id=img_uuid,document_id=docs_uuid, path=image_path, file_number=page_number, created_at=datetime.now(),updated_at=datetime.now())
                db.session.add(image)
        
        db.session.commit()
        return jsonify({"message": "File uploaded successfully", "id": docs_uuid}), 200

    elif file and file.filename.endswith('.jpg') or file.filename.endswith('.jpeg') or file.filename.endswith('.png'):
        img_uuid = str(uuid.uuid4())
        file_path = f"{app.config['UPLOAD_FOLDER']}{docs_uuid}/{img_uuid}.png"
        image_path = f"{folder_path}{docs_uuid}/{img_uuid}.png"
        file.save(file_path)
        image = Image(id=img_uuid,document_id=docs_uuid, path=image_path, file_number=1, created_at=datetime.now(),updated_at=datetime.now())
        db.session.add(image)
        db.session.commit()
        return jsonify({"message": "File uploaded successfully", "id": docs_uuid}), 200

    
    return jsonify({"error": "Unsupported file type"}), 400

@file_controller.route('/add/<id>', methods=['POST'])
@login_required
def add_image(id):
    from main import app
    from app import db
    if 'file' not in request.files:
        flash('No file part', 'error')
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'error')
        return jsonify({"error": "No selected file"}), 400
    
    doc = Document.query.filter_by(id=id).first()
    if not doc:
        flash('Document not found', 'error')
        return jsonify({"error": "Document not found"}), 404

    if not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'],id)):
        os.mkdir(os.path.join(app.config['UPLOAD_FOLDER'],id))
        
    doc.updated_at = datetime.now()
    
    index = doc.images.count()
        
    if file and file.filename.endswith('.pdf'):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'],id,'/', file.filename)
        file.save(filepath)

        with fitz.open(filepath) as pdf:
            for page_number, page in enumerate(pdf, start=1):
                pix = page.get_pixmap()
                img_uuid = str(uuid.uuid4())
                
                file_path = f"{app.config['UPLOAD_FOLDER']}{id}/{img_uuid}.png"
                image_path = f"{folder_path}{id}/{img_uuid}.png"
                pix.save(file_path)
                index+=1
                image = Image(id=img_uuid,document_id=id, path=image_path, file_number=index, created_at=datetime.now(),updated_at=datetime.now())
                db.session.add(image)
        
        db.session.commit()
        return jsonify({"message": "File uploaded successfully", "id": id}), 200

    if file and file.filename.endswith('.jpg') or file.filename.endswith('.jpeg') or file.filename.endswith('.png'):
        img_uuid = str(uuid.uuid4())
        file_path = f"{app.config['UPLOAD_FOLDER']}{id}/{img_uuid}.png"
        image_path = f"{folder_path}{id}/{img_uuid}.png"
        file.save(file_path)
        index+=1
        image = Image(id=img_uuid,document_id=id, path=image_path, file_number=index, created_at=datetime.now(),updated_at=datetime.now())
        db.session.add(image)
        db.session.commit()
        return jsonify({"message": "File uploaded successfully", "id": id}), 200

    return jsonify({"error": "Unsupported file type"}), 400
    
@file_controller.route('/edit/<id>', methods=['POST'])
@login_required
def change_docs_name(id):
    doc = Document.query.filter_by(id=id).first()
    if not doc:
        flash('Document not found', 'error')
        return jsonify({"error": "Document not found"}), 404
    
    name = request.json.get('name')
    if not name or name== "":
        flash('Invalid name provided', 'error')
        return jsonify({"error": "Invalid name provided"}), 400
    
    doc.name = name
    doc.updated_at = datetime.now()
    db.session.add(doc)
    db.session.commit()
    flash('Document name updated successfully', 'success')
    return jsonify({"message": "Document name updated successfully", "new_name": doc.name}), 200
    
