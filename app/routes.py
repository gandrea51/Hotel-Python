from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, Hotel, Room, Service, Booking
from .utils import convert, is_password_valid, is_email_valid
from . import db

main = Blueprint('main', __name__)

@main.app_context_processor
def inject_user():
    if current_user.is_authenticated:
        return {'current_user': current_user}
    return {'current_user': None}

'''
    ERROR
'''
@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_code=404, error_message="La pagina che stai cercando non esiste."), 404

@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', error_code=500, error_message="Errore interno del server. Per favore riprova più tardi."), 500

@main.app_errorhandler(403)
def forbidden(e):
    return render_template('error.html', error_code=403, error_message="Accesso negato. Non hai i permessi necessari per accedere a questa pagina."), 403

'''
    HOME PAGE
'''
@main.route('/')
def welcome():
    return render_template('welcome.html')

@main.route('/home')
@login_required
def home():
    if current_user.is_authenticated:
        if current_user.role != 'Client':
            user_count = User.query.filter_by(role = 'Client').count()
            return render_template('home.html', user = current_user, user_count = user_count)
        else: 
            return render_template('home.html', user = current_user)
    else: 
        return redirect(url_for('main.login'))

'''
    USER
'''
@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')

        is_valid, error_message = is_email_valid(email)
        if not is_valid:
            flash(error_message, 'danger')
            return redirect(url_for('main.register'))
        password = request.form.get('password')

        is_valid, error_message = is_password_valid(password)
        if not is_valid:
            flash(error_message, 'danger')
            return redirect(url_for('main.register'))
        password = generate_password_hash(password)

        phone = request.form.get('phone')
        role = request.form.get('role')

        user = User(name = name, email = email, password = password, phone = phone, role = role)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('main.login'))
    
    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email = email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.home'))
    
    return render_template('login.html')

@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.welcome'))

@main.route('/user/<int:id>')
@login_required
def user_profile(id):      
    user = db.session.get(User, id)
    if not user:
        return render_template('error.html', error_message="L'utente richiesto non è stato trovato.")
    msg = ""
    books = []

    bookings = Booking.query.filter_by(user_id = user.id).all()
    if bookings:
        books = bookings
    else:
        msg = "Non hai ancora effettuato prenotazioni.<br><br>Esplora gli hotel disponibili e prenota subito la tua prossima vacanza.<br><br>Approfitta delle imperdibili offerte speciali!"

    return render_template('user_profile.html', user = user, msg = msg, books = books)

@main.route('/password', methods=['GET', 'POST'])
def password():
    if request.method == 'POST':
        old = request.form.get('old')
        new = request.form.get('new')
        is_valid, error_message = is_password_valid(new)
        if not is_valid:
            flash(error_message, 'danger')
            return redirect(url_for('main.password'))
        new = generate_password_hash(new)

        if check_password_hash(current_user.password, old):
            current_user.password = new
            db.session.commit()
            return redirect(url_for('main.home'))
        else:
            return render_template('error.html', error_message="La password attuale è errata. Riprovare.")

    return render_template('password.html')

@main.route('/email', methods=['GET', 'POST'])
def email():
    if request.method == 'POST':
        old = request.form.get('old')
        new = request.form.get('new')

        is_valid, error_message = is_email_valid(new)
        if not is_valid:
            flash(error_message, 'danger')
            return redirect(url_for('main.email'))
        
        if old == current_user.email:
            current_user.email = new
            db.session.commit()
            return redirect(url_for('main.home'))
        else: 
            return render_template('error.html', error_message="L'indirizzo email attuale è errato. Riprovare")

    return render_template('email.html')

@main.route('/phone', methods=['GET', 'POST'])
def phone():
    if request.method == 'POST':
        new = request.form.get('new')
        current_user.phone = new 
        db.session.commit()
        return redirect(url_for('main.home'))

    return render_template('phone.html')

'''
    HOTEL
'''
@main.route('/hotel')
def hotel_index():       
    hotels = Hotel.query.all()
    return render_template('hotel_index.html', hotels = hotels)

@main.route('/hotel/create', methods=['GET', 'POST'])
@login_required
def hotel_create():
    if request.method == 'POST':
        hotel = Hotel(
            name = request.form['name'],
            address = request.form['address'],
            room = request.form['room'],
            description = request.form['description'],
            star = request.form['star']
        )
        db.session.add(hotel)
        db.session.commit()        
        return redirect(url_for('main.hotel_index'))
    
    return render_template('hotel_create.html')

@main.route('/hotel/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def hotel_edit(id):
    hotel = Hotel.query.get(id)
    if not hotel:
        return render_template('error.html', error_message="L'hotel richiesto non è stato trovato.")
    if request.method == 'POST':
        hotel.name = request.form['name'],
        hotel.address = request.form['address'],
        hotel.room = request.form['room'],
        hotel.description = request.form['description'],
        hotel.star = request.form['star']
        db.session.commit()        
        return redirect(url_for('main.hotel_index'))
    
    return render_template('hotel_edit.html', hotel = hotel)

@main.route('/hotel/<int:id>/delete', methods=['POST'])
@login_required
def hotel_delete(id):
    hotel = Hotel.query.get(id)
    if not hotel:
        return render_template('error.html', error_message="L'hotel richiesto non è stato trovato.")
    db.session.delete(hotel)
    db.session.commit()
    return redirect(url_for('main.hotel_index'))

'''
    ROOM
'''
@main.route('/room')
def room_index():       
    rooms = Room.query.all()
    return render_template('room_index.html', rooms = rooms)

@main.route('/room/create', methods=['GET', 'POST'])
@login_required
def room_create():
    if request.method == 'POST':
        room = Room(
            type = request.form['type'],
            description = request.form['description']
        )
        db.session.add(room)
        db.session.commit()        
        return redirect(url_for('main.room_index'))
    
    return render_template('room_create.html')

@main.route('/room/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def room_edit(id):
    room = Room.query.get(id)
    if not room:
        return render_template('error.html', error_message="La camera richiesta non è stato trovata.")
    if request.method == 'POST':
        room.type = request.form['type']
        room.description = request.form['description']
        db.session.commit()        
        return redirect(url_for('main.room_index'))
    
    return render_template('room_edit.html', room = room)

@main.route('/room/<int:id>/delete', methods=['POST'])
@login_required
def room_delete(id):
    room = Room.query.get(id)
    if not room:
        return render_template('error.html', error_message="La camera richiesta non è stato trovata.")
    db.session.delete(room)
    db.session.commit()
    return redirect(url_for('main.room_index'))

'''
    SERVICE
'''
@main.route('/service')
def service_index():       
    services = Service.query.all()
    return render_template('service_index.html', services = services)

@main.route('/service/create', methods=['GET', 'POST'])
@login_required
def service_create():
    if request.method == 'POST':
        service = Service(
            name = request.form['name'],
            description = request.form['description'],
            price = request.form['price'],
            duration = request.form['duration'],
            available = request.form['available']
        )
        db.session.add(service)
        db.session.commit()        
        return redirect(url_for('main.service_index'))
    
    return render_template('service_create.html')

@main.route('/service/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def service_edit(id):
    service = Service.query.get(id)
    if not service:
        return render_template('error.html', error_message="Il servizio richiesto non è stato trovato.")
    if request.method == 'POST':
        service.name = request.form['name'],
        service.description = request.form['description'],
        service.price = request.form['price'],
        service.duration = request.form['duration'],
        service.available = request.form['available']
        db.session.commit()        
        return redirect(url_for('main.serivce_index'))
    
    return render_template('service.edit.html', service = service)

@main.route('/service/<int:id>/delete', methods=['POST'])
@login_required
def service_delete(id):
    service = Service.query.get(id)
    if not service:
        return render_template('error.html', error_message="Il servizio richiesto non è stato trovato.")
    db.session.delete(service)
    db.session.commit()
    return redirect(url_for('main.service_index'))
'''
    BOOKING
'''
