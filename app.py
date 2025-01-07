from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///wardrobe.db')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'gizli-anahtar-123')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Upload klasörünü oluştur
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

CATEGORIES = {
    'ust_giyim': {
        'name': 'Üst Giyim',
        'subcategories': ['Tişört', 'Gömlek', 'Kazak', 'Sweatshirt', 'Ceket', 'Mont', 'Bluz']
    },
    'alt_giyim': {
        'name': 'Alt Giyim',
        'subcategories': ['Pantolon', 'Şort', 'Etek', 'Jean', 'Tayt']
    },
    'elbise': {
        'name': 'Elbise',
        'subcategories': ['Günlük Elbise', 'Gece Elbisi', 'Tulum']
    },
    'ayakkabi': {
        'name': 'Ayakkabı',
        'subcategories': ['Spor Ayakkabı', 'Topuklu', 'Bot', 'Sandalet', 'Terlik']
    },
    'aksesuar': {
        'name': 'Aksesuar',
        'subcategories': ['Çanta', 'Kemer', 'Şal', 'Takı', 'Şapka', 'Gözlük']
    }
}

class Clothing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    main_category = db.Column(db.String(50), nullable=False)
    sub_category = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(50))
    image_path = db.Column(db.String(200))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

class Outfit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    items = db.Column(db.String(500))  # Comma-separated clothing IDs
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    clothes = Clothing.query.all()
    outfits = Outfit.query.all()
    return render_template('index.html', clothes=clothes, outfits=outfits)

@app.route('/add_clothing', methods=['GET', 'POST'])
def add_clothing():
    if request.method == 'POST':
        name = request.form['name']
        main_category = request.form['main_category']
        sub_category = request.form['sub_category']
        color = request.form['color']
        
        # Fotoğraf yükleme işlemi
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Benzersiz dosya adı oluştur
                filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_path = f"uploads/{filename}"
        
        new_clothing = Clothing(
            name=name,
            main_category=main_category,
            sub_category=sub_category,
            color=color,
            image_path=image_path
        )
        db.session.add(new_clothing)
        db.session.commit()
        flash('Kıyafet başarıyla eklendi!', 'success')
        return redirect(url_for('home'))
    
    return render_template('add_clothing.html', categories=CATEGORIES)

@app.route('/get_subcategories/<main_category>')
def get_subcategories(main_category):
    if main_category in CATEGORIES:
        return {'subcategories': CATEGORIES[main_category]['subcategories']}
    return {'subcategories': []}

@app.route('/create_outfit', methods=['GET', 'POST'])
def create_outfit():
    if request.method == 'POST':
        name = request.form['name']
        items = request.form.getlist('items')
        items_str = ','.join(map(str, items))
        
        new_outfit = Outfit(name=name, items=items_str)
        db.session.add(new_outfit)
        db.session.commit()
        flash('Kombin başarıyla oluşturuldu!', 'success')
        return redirect(url_for('home'))
    
    clothes = Clothing.query.all()
    return render_template('create_outfit.html', clothes=clothes)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 