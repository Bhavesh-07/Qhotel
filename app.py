from flask import Flask, request, render_template, session, redirect, url_for, jsonify
import os
from core.database import (
    get_db_connection,
    get_settings,
    ensure_admin_user,
    verify_admin_credentials,
    Error,
)
from core.email_utils import send_smtp_email

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'change-me-in-production')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = os.getenv('SESSION_COOKIE_SECURE', 'false').lower() == 'true'
app.config['BOOTSTRAP_ADMIN_USERNAME'] = os.getenv('ADMIN_BOOTSTRAP_USERNAME', 'admin')
app.config['BOOTSTRAP_ADMIN_PASSWORD'] = os.getenv('ADMIN_BOOTSTRAP_PASSWORD', 'change-me-in-production')

@app.route('/')
def index():
    return render_template('index.html', active_page='index')

@app.route('/about')
def about():
    return render_template('about.html', active_page='about')

@app.route('/service')
def service():
    return render_template('service.html', active_page='service')

@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html', active_page='portfolio')

@app.route('/investment')
def investment():
    return render_template('investment.html', active_page='investment')

@app.route('/contact')
def contact():
    return render_template('contact.html', active_page='contact')

@app.route('/news')
def news():
    return render_template('news.html', active_page='about')

@app.route('/team')
def team():
    return render_template('team.html', active_page='about')

@app.route('/leadership')
def leadership():
    return render_template('leadership.html', active_page='about')

@app.route('/accounting')
def accounting():
    return render_template('accounting.html', active_page='service')

@app.route('/operations')
def operations():
    return render_template('operations.html', active_page='service')

@app.route('/technology')
def technology():
    return render_template('technology.html', active_page='service')

@app.route('/sales-and-marketing')
def sales_marketing():
    return render_template('sales-and-marketing.html', active_page='service')

@app.route('/revenue-management')
def revenue_management():
    return render_template('revenue-management.html', active_page='service')

@app.route('/construction-and-pip-management')
def construction_pip():
    return render_template('construction-and-pip-management.html', active_page='service')

@app.route('/detailed-list-of-services')
def detailed_services():
    return render_template('detailed-list-of-services.html', active_page='service')

@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy-policy.html')

@app.route('/sitemap')
def sitemap():
    return render_template('sitemap.html')

# Admin Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    ensure_admin_user(
        app.config['BOOTSTRAP_ADMIN_USERNAME'],
        app.config['BOOTSTRAP_ADMIN_PASSWORD'],
    )
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if verify_admin_credentials(username, password):
            session['logged_in'] = True
            return redirect(url_for('view_submissions'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/admin/submissions')
def view_submissions():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('dashboard.html')

# API Endpoints
@app.route('/api/settings', methods=['GET', 'POST'])
def api_settings():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    if request.method == 'POST':
        data = request.json
        try:
            cursor = conn.cursor()
            for key, value in data.items():
                query = "INSERT INTO settings (setting_key, setting_value) VALUES (%s, %s) ON DUPLICATE KEY UPDATE setting_value=%s"
                cursor.execute(query, (key, value, value))
            conn.commit()
            return jsonify({'success': True})
        except Error as e:
            return jsonify({'error': str(e)}), 500
        finally:
            cursor.close()
            conn.close()
    else:
        return jsonify(get_settings())

@app.route('/api/submissions')
def api_submissions():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
        
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
        
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as total FROM contacts")
        total_records = cursor.fetchone()['total']
        total_pages = (total_records + per_page - 1) // per_page
        
        cursor.execute("SELECT * FROM contacts ORDER BY created_at DESC LIMIT %s OFFSET %s", (per_page, offset))
        contacts = cursor.fetchall()
        
        for c in contacts:
            c['created_at'] = c['created_at'].strftime('%b %d, %Y %H:%M')
            
        return jsonify({
            'contacts': contacts,
            'total_pages': total_pages,
            'current_page': page
        })
    finally:
        cursor.close()
        conn.close()

# Contact Submission
@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    data = request.form
    first_name = data.get('fname', '')
    last_name = data.get('lname', '')
    email = data.get('email', '')
    phone = data.get('phoneno', '')
    message = data.get('messagearea', '')

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = "INSERT INTO contacts (first_name, last_name, email, phone, message) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(query, (first_name, last_name, email, phone, message))
            conn.commit()
            
            subject = f"New Contact Inquiry: {first_name} {last_name}"
            placeholders = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'phone': phone,
                'message': message
            }
            send_smtp_email(subject, "", placeholders=placeholders)
            
            return "1"
        except Error as e:
            print(f"Database error: {e}")
            return "0"
        finally:
            cursor.close()
            conn.close()
    return "0"

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    port = int(os.getenv('PORT', '9999'))
    app.run(debug=debug_mode, port=port)
