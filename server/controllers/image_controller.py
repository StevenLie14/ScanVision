from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify, send_file,send_from_directory
from flask_login import login_required
from datetime import datetime
from models.document import Document
from models.image import Image
from app import db
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import uuid
import numpy as np
import io
from io import BytesIO
import os
import cv2
import pytesseract
from pytesseract import Output
from paddleocr import PaddleOCR, draw_ocr
from PIL import Image as Pil_Image
import base64


image_controller = Blueprint('image_controller', __name__)
folder_path = os.getenv('IMAGE_FOLDER')


def getFilteredImage(image, filter_type):
    filtered_img = image
    
    if filter_type == 'enhance':
        filtered_img = cv2.convertScaleAbs(filtered_img, alpha=1.1, beta=10)
    elif filter_type == 'grayscale':
        filtered_img = cv2.cvtColor(filtered_img, cv2.COLOR_BGR2GRAY)
        filtered_img = cv2.cvtColor(filtered_img, cv2.COLOR_GRAY2BGR)
    elif filter_type == 'equ': 
        filtered_img = cv2.cvtColor(filtered_img, cv2.COLOR_BGR2GRAY)
        filtered_img = cv2.equalizeHist(filtered_img)
        filtered_img = cv2.cvtColor(filtered_img, cv2.COLOR_GRAY2BGR)
    elif filter_type == 'manequ':  
        filtered_img = cv2.cvtColor(filtered_img, cv2.COLOR_BGR2GRAY)
        hist, _ = np.histogram(filtered_img.flatten(), 256, [0, 256])
        cdf = hist.cumsum()
        cdf = ( (cdf - cdf.min()) * 255 ) / (cdf.max() - cdf.min())
        cdf = np.uint8(cdf)
        filtered_img= cdf[filtered_img.flatten()]
        filtered_img = cv2.cvtColor(filtered_img,cv2.COLOR_GRAY2BGR)
        filtered_img = np.reshape(filtered_img,image.shape)
    elif filter_type == 'bw': 
        filtered_img = cv2.cvtColor(filtered_img, cv2.COLOR_BGR2GRAY)
        _, filtered_img = cv2.threshold(filtered_img, 127, 255, cv2.THRESH_BINARY)
        filtered_img = cv2.cvtColor(filtered_img, cv2.COLOR_GRAY2BGR)
    elif filter_type == 'invert': 
        filtered_img = cv2.bitwise_not(filtered_img)
    elif filter_type == 'original':
        filtered_img = image
    
    return filtered_img

def rotate_image(image,angle,hori_flip=0,vert_flip=0):
    angle = int(angle)
    image = np.rot90(image,angle)
    if hori_flip == 1:
        image = np.fliplr(image)
    if vert_flip == 1:
        image = np.flipud(image)
    
    return image

def preprocess(img,x,y,w,h,width,height):
    print(x,y,w,h,width,height)
    if x is not None and y is not None and w is not None and h is not None:
        img = img[int(y):int(y+h), int(x):int(x+w)]
    if width is not None and height is not None:
        img = cv2.resize(img, (int(width), int(height)))
    return img
        
@image_controller.route('/<id>', methods=['GET', 'DELETE','POST'])
@login_required
def edit(id):
    from main import app
    if request.method == 'POST':
        image = Image.query.filter_by(id=id).first()
        if not image:
            return jsonify({"message": "Image not found"}), 404
        
        image_path = os.path.join('static', image.path)
        
        if not os.path.exists(image_path):
            return jsonify({"message": "Image not found"}), 404
        
        img =cv2.imread(image_path)
        width = int(request.args.get('width')) if request.args.get('width') else None
        height = int(request.args.get('height')) if request.args.get('height') else None 
        
        x = float(request.args.get('x')) if request.args.get('x') else None
        y = float(request.args.get('y')) if request.args.get('y') else None
        w = float(request.args.get('w')) if request.args.get('w') else None
        h = float(request.args.get('h')) if request.args.get('h') else None
        
        img = preprocess(img,x,y,w,h,width,height)
            
        filter_type = request.args.get('filter')
        filtered_img = getFilteredImage(img, filter_type)
        
        split_ratio = request.args.get('split', default=0) 
        try:
            split_ratio = float(split_ratio)
        except ValueError:
            split_ratio = 0 

        split_ratio = max(0, min(split_ratio, 100))
        
        angle_type = request.args.get('angle',default=0)
        hori_flip = int(request.args.get('hori',default=0))
        vert_flip = int(request.args.get('vert',default=0))
        img = rotate_image(img,angle_type,hori_flip,vert_flip)
        
        filtered_img = getFilteredImage(img, request.args.get('filter'))
        
        cv2.imwrite(image_path, filtered_img)
        
        image.updated_at = datetime.now()
        db.session.add(image)
        db.session.commit()
        
        return jsonify({"message": "Image updated successfully"}), 200
    if request.method == 'DELETE':
        image = Image.query.filter_by(id=id).first()
        if not image:
            flash('Image not found', 'error')
            return jsonify({"message": "Image not found"}), 404
        
        if os.path.exists(os.path.join('static', image.path)):
            os.remove(os.path.join('static', image.path))
            
        document = Document.query.filter_by(id=image.document_id).first()
        
        
        db.session.delete(image)
        db.session.commit()

        remaining_images = document.images.order_by(Image.file_number).all()
        if not remaining_images:
            db.session.delete(document)
            db.session.commit()
            print(os.path.join('static',folder_path, document.id))
            
            if os.path.exists(os.path.join('static',folder_path, document.id)):
                os.rmdir(os.path.join('static',folder_path, document.id))
                
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
    return render_template('editor.html', image=image,id=id)



@image_controller.route('filter/<id>', methods=['GET'])
@login_required
def image_filter(id):
    image = Image.query.filter_by(id=id).first()
    if not image:
        return jsonify({"message": "Image not found"}), 404
    
    image_path = os.path.join('static', image.path)

    if not os.path.exists(image_path):
        return jsonify({"message": "Image not found"}), 404
        
    img = cv2.imread(image_path)
    if img is None:
        return jsonify({"message": "Image not found"}), 404
    
    width = int(request.args.get('width')) if request.args.get('width') else None
    height = int(request.args.get('height')) if request.args.get('height') else None 
    
    x = float(request.args.get('x')) if request.args.get('x') else None
    y = float(request.args.get('y')) if request.args.get('y') else None
    w = float(request.args.get('w')) if request.args.get('w') else None
    h = float(request.args.get('h')) if request.args.get('h') else None
    
    img = preprocess(img,x,y,w,h,width,height)
        
    filter_type = request.args.get('filter')
    filtered_img = getFilteredImage(img, filter_type)
    
    split_ratio = request.args.get('split', default=0) 
    try:
        split_ratio = float(split_ratio)
    except ValueError:
        split_ratio = 0 

    split_ratio = max(0, min(split_ratio, 100))
    
    angle_type = request.args.get('angle',default=0)
    hori_flip = int(request.args.get('hori',default=0))
    vert_flip = int(request.args.get('vert',default=0))
    img = rotate_image(img,angle_type,hori_flip,vert_flip)
    
    filtered_img = rotate_image(filtered_img,angle_type,hori_flip,vert_flip)
    split_index = int(img.shape[1] * (1 - split_ratio / 100))

    combined_img = np.concatenate(
        (img[:, :split_index], filtered_img[:, split_index:]), 
        axis=1
    )
    
    
    _, buffer = cv2.imencode('.jpg', combined_img)
    img_io = io.BytesIO(buffer)
    
    return send_file(img_io, mimetype='image/jpeg')

@image_controller.route('histogram/<id>', methods=['GET'])
@login_required
def histogram(id):
    image = Image.query.filter_by(id=id).first()
    if not image:
        return jsonify({"message": "Image not found"}), 404
    
    image_path = os.path.join('static', image.path)

    if not os.path.exists(image_path):
        return jsonify({"message": "Image not found"}), 404
        
    img = cv2.imread(image_path)
    if img is None:
        return jsonify({"message": "Image not found"}), 404
    
    filter_type = request.args.get('filter')
    filtered_img = getFilteredImage(img, filter_type)

    gray = cv2.cvtColor(filtered_img, cv2.COLOR_BGR2GRAY)
    h = img.shape[0]
    w = img.shape[1]

    gray_counter = np.zeros(256, dtype=int)
    for i in range(h):
        for j in range(w):
            gray_counter[gray[i][j]] += 1
            
    plt.plot(gray_counter)
    plt.ylabel('quantity')
    plt.xlabel('intensity')
    plt.title('Histogram')
    plt.axis([0, 256, 0, gray_counter.max()])

    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='jpg')
    img_buffer.seek(0)
    plt.close()
    
    return send_file(img_buffer, mimetype='image/jpeg')




@image_controller.route('ocr/<id>', methods=['GET'])
@login_required
def ocr(id):
    image = Image.query.filter_by(id=id).first()
    if not image:
        return jsonify({"message": "Image not found"}), 404

    image_path = os.path.join('static', image.path)
    if not os.path.exists(image_path):
        return jsonify({"message": "Image not found"}), 404

    ocr = PaddleOCR()

    result = ocr.ocr(image_path)

    boxes = [line[0] for line in result[0]]  
    txts = [line[1][0] for line in result[0]] 

    img = Pil_Image.open(image_path).convert('RGB')
    img_array = np.array(img)
    for box in boxes:
        points = np.array(box, dtype=np.int32)
        cv2.polylines(img_array, [points], isClosed=True, color=(0, 255, 0), thickness=2)
    # im_show = draw_ocr(np.array(img), boxes, txts, scores, font_path='C:/Windows/Fonts/Arial.ttf')

    im_show = Pil_Image.fromarray(img_array)
    im_show = cv2.cvtColor(np.array(im_show), cv2.COLOR_RGB2BGR)

    _, buffer = cv2.imencode('.jpg', im_show)
    img_io = io.BytesIO(buffer)

    return render_template('ocr.html', ocr_img=base64.b64encode(img_io.getvalue()).decode('utf-8'), ocr_text=txts, ocr_box=boxes,image=image)

@image_controller.route('download/<id>', methods=['GET'])
@login_required
def download_img(id):
    image = Image.query.filter_by(id=id).first()
    if not image:
        return jsonify({"message": "Image not found"}), 404

    image_path = os.path.join('static', image.path)
    
    
    if not os.path.exists(image_path):
        return jsonify({"message": "Image file not found on server"}), 404

    img = cv2.imread(image_path)
    _, img_encoded = cv2.imencode('.jpg', img)
    img_bytes = img_encoded.tobytes()

    return send_file(
        io.BytesIO(img_bytes),
        mimetype='image/jpeg',
        as_attachment=True,
        download_name=f'{id}.jpg'
    )
    
    
    


    
    
