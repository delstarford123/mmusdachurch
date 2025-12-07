import os
import datetime
from threading import Thread  # NEW: For background tasks
import firebase_admin
from firebase_admin import credentials, db
from flask import Flask, render_template, request
from flask_mail import Mail, Message

app = Flask(__name__)

# ==========================================
# 1. FIREBASE CONFIGURATION
# ==========================================
if os.path.exists('/etc/secrets/serviceAccountKey.json'):
    cred = credentials.Certificate("/etc/secrets/serviceAccountKey.json")
else:
    cred = credentials.Certificate("serviceAccountKey.json")

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://mmusdachurch-d2455-default-rtdb.firebaseio.com/'
})

# ==========================================
# 2. EMAIL CONFIGURATION
# ==========================================
# ==========================================
# 2. EMAIL CONFIGURATION
# ==========================================
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465               # CHANGED: Back to 465
app.config['MAIL_USE_TLS'] = False          # CHANGED: TLS False
app.config['MAIL_USE_SSL'] = True           # CHANGED: SSL True

# The email account that SENDS the emails
app.config['MAIL_USERNAME'] = 'delstarfordisaiah@gmail.com'
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'frdj huaq peso lipb')
mail = Mail(app)

# ==========================================
# 3. HELPER FUNCTION: SEND EMAIL IN BACKGROUND
# ==========================================
def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
            # Add flush=True to force the log to appear immediately
            print(f"Background Email Sent: {msg.subject}", flush=True) 
        except Exception as e:
            # Add flush=True here too
            print(f"Background Email Failed: {e}", flush=True)
def send_background_email(subject, recipient, body, attachment_name=None, attachment_data=None):
    msg = Message(subject,
                  sender=app.config['MAIL_USERNAME'],
                  recipients=[recipient])
    msg.body = body
    
    if attachment_name and attachment_data:
        msg.attach(attachment_name, "text/plain", attachment_data)

    # This line starts a separate "thread" so the website doesn't wait
    Thread(target=send_async_email, args=(app, msg)).start()

# ==========================================
# 4. ROUTES
# ==========================================

@app.route('/')
def main():
    return render_template('main.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/sermons')
def sermons():
    return render_template('sermons.html')

@app.route('/pastor')
def pastor():
    return render_template('pastors details.html')

@app.route('/tithes')
def tithes():
    return render_template('tiths and offering.html')

@app.route('/churchmembers')
def churchmembers():
    ref = db.reference('members')
    data = ref.get()
    return render_template('churchmembers.html', members_data=data)

# --- REGISTER ROUTE (UPDATED) ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        residence = request.form.get('residence')
        reg_date = datetime.date.today().strftime("%Y-%m-%d")
        
        member_data = {
            'name': name, 'email': email, 'phone': phone,
            'residence': residence, 'joined_date': reg_date
        }

        # Save to DB
        ref = db.reference('members')
        ref.push(member_data)

        # 1. Send Welcome Email (Background)
        welcome_body = f"Dear {name},\n\nWelcome to MMUSDA! Your registration is confirmed.\n\nBlessings,\nSecretariat"
        send_background_email("Welcome to MMUSDA Family!", email, welcome_body)

        # 2. Send Admin Alert (Background)
        record_content = f"Name: {name}\nEmail: {email}\nPhone: {phone}\nResidence: {residence}\nDate: {reg_date}"
        send_background_email(f"New Member: {name}", 'omondidelstarford@gmail.com', 
                              "See attached record.", "member_record.txt", record_content)
        
        return render_template('dashboard.html') 
    return render_template('register.html')

# --- ATTENDANCE ROUTE (UPDATED) ---
@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        date = request.form.get('date')
        service = request.form.get('service')
        
        attendance_data = {
            'name': name, 'email': email, 'date': date, 'service': service
        }
        
        # Save to DB
        ref = db.reference('attendance')
        ref.push(attendance_data)
        
        # 1. Send Encouragement Email (Background)
        encourage_body = f"Dear {name},\n\nThank you for attending the {service} on {date}. God bless you!"
        send_background_email(f"Attendance: {date}", email, encourage_body)

        # 2. Send Admin Record (Background)
        record_content = f"OFFICIAL ATTENDANCE\nName: {name}\nService: {service}\nDate: {date}"
        send_background_email(f"Attendance Record: {name}", 'omondidelstarford@gmail.com', 
                              "New attendance signed.", "attendance_record.txt", record_content)
        
        return render_template('dashboard.html')

    return render_template('attendance.html')

# --- RESIDENCE ROUTES ---
@app.route('/koromatangi')
def koromatangi(): return render_template('koro.html')

@app.route('/teazone')
def teazone(): return render_template('teazone.html')

@app.route('/sichirai')
def sichirai(): return render_template('sich.html')

@app.route('/mmust_block')
def mmust_block(): return render_template('mmust.html')

@app.route('/lurambi')
def lurambi(): return render_template('lurambi.html')

@app.route('/malava')
def malava(): return render_template('malava.html')

@app.route('/shinyalu')
def shinyalu(): return render_template('shinyalu.html')

if __name__ == '__main__':
    app.run(debug=True)