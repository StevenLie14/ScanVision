from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify
from flask_login import login_user, logout_user, login_required,current_user
from datetime import datetime
from server.models.document import Document
from server.models.image import Image
from server.models.user import User
from server.app import db
import fitz
import uuid
import os


image_controller = Blueprint('image_controller', __name__)
folder_path = os.getenv('IMAGE_FOLDER')

@image_controller.route('/<id>', methods=['GET', 'DELETE'])
@login_required
def edit(id):
    if request.method == 'DELETE':
        image = Image.query.filter_by(id=id).first()
        if not image:
            flash('Image not found', 'error')
            return jsonify({"message": "Image not found"}), 404
        
        document = Document.query.filter_by(id=image.document_id).first()
        
        db.session.delete(image)
        db.session.commit()

        remaining_images = document.images.order_by(Image.file_number).all()
        if not remaining_images:
            db.session.delete(document)
            db.session.commit()
            flash('Document deleted successfully', 'success')
            return jsonify({"message": "Document deleted successfully"}), 200
        
        for idx, image in enumerate(remaining_images, start=1):
            image.file_number = idx
            image.updated_at = datetime.now() 
            db.session.add(image)
        
        db.session.commit()
        flash('Image deleted successfully', 'success')
        return jsonify({"message": "Image deleted and file numbers reordered successfully"}), 200
    
    image = Image.query.filter_by(id=id).first()
    if not image:
        return redirect(url_for('file_controller.docs_list'))
    return render_template('editor.html', image=image)



    