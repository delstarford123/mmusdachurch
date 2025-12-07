import os
import firebase_admin
from firebase_admin import credentials, db
from flask import Flask, render_template, request
from flask_mail import Mail, Message

app = Flask(__name__)

# ==========================================
# 1. FIREBASE CONFIGURATION
# ==========================================
# Check if we are on Render (look in /etc/secrets) or Local (look in current folder)
if os.path.exists('/etc/secrets/serviceAccountKey.json'):
    # This path is for the Render Server
    cred = credentials.Certificate("/etc/secrets/serviceAccountKey.json")
else:
    # This path is for your Local Computer
    cred = credentials.Certificate("serviceAccountKey.json")

# Initialize Firebase
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://mmusdachurch-d2455-default-rtdb.firebaseio.com/'
})

# ==========================================
# 2. EMAIL CONFIGURATION
# ==========================================
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587               # CHANGED: Use Port 587 instead of 465
app.config['MAIL_USE_TLS'] = True           # CHANGED: Turn TLS ON
app.config['MAIL_USE_SSL'] = False
# The email account that SENDS the emails (must match the App Password)
app.config['MAIL_USERNAME'] = 'delstarfordisaiah@gmail.com'

# The App Password provided
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'frdj huaq peso lipb')

mail = Mail(app)

# ==========================================
# 3. CORE PAGES
# ==========================================

@app.route('/')
def main():
    return render_template('main.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/pastor')
def pastor():
    return render_template('pastors details.html')

@app.route('/tithes')
def tithes():
    return render_template('tiths and offering.html')

# ==========================================
# 4. FUNCTIONAL ROUTES (Register, Attendance)
# ==========================================

from flask import Flask, render_template, request
from flask_mail import Mail, Message
import datetime # Import datetime to capture the registration date

# ... (Your existing imports and config remain the same) ...

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # 1. Get data from HTML form
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        residence = request.form.get('residence')
        
        # Get today's date automatically
        reg_date = datetime.date.today().strftime("%Y-%m-%d")
        
        # 2. Create a dictionary for the database
        member_data = {
            'name': name,
            'email': email,
            'phone': phone,
            'residence': residence,
            'joined_date': reg_date
        }

        # 3. Save to Firebase under the 'members' node
        ref = db.reference('members')
        ref.push(member_data)

        print(f"SAVED TO FIREBASE: {name} from {residence}")

        # ==========================================
        # 4. EMAIL LOGIC (New Addition)
        # ==========================================
        try:
            # --- Email A: To the New Member (Welcome Message) ---
            msg_member = Message(f"Welcome to MMUSDA Family!",
                                 sender='delstarfordisaiah@gmail.com',
                                 recipients=[email])
            
            msg_member.body = f"""
            Dear {name},

            Welcome to the MMUSDA Church family! We are delighted to have you join us.
            
            Your registration has been received and recorded. We look forward to fellowshiping with you in the {residence} residence and at church.

            "The Lord bless you and keep you; the Lord make his face shine on you and be gracious to you." - Numbers 6:24-25

            Blessings,
            MMUSDA Secretariat
            """
            mail.send(msg_member)
            print(f"Welcome email sent to {name}")

            # --- Email B: To Deaconry/Admin (Official Registration Record) ---
            msg_admin = Message(f"New Member Alert: {name}",
                                sender='delstarfordisaiah@gmail.com',
                                recipients=['omondidelstarford@gmail.com'])
            
            msg_admin.body = f"A new member has joined the church via the website.\n\nName: {name}\nResidence: {residence}\nPhone: {phone}\n\nSee attached official record."
            
            # Create the attachment content
            record_content = f"""
            OFFICIAL MEMBER REGISTRATION RECORD
            -----------------------------------
            Name:      {name}
            Email:     {email}
            Phone:     {phone}
            Residence: {residence}
            Date:      {reg_date}
            Status:    Active
            -----------------------------------
            Verified via MMUSDA Website Portal
            """
            
            # Attach the text file
            msg_admin.attach("member_record.txt", "text/plain", record_content)
            
            mail.send(msg_admin)
            print("Registration record sent to Admin.")

        except Exception as e:
            print(f"Email Error: {e}")
            # We continue so the user sees the dashboard even if email fails
        
        return render_template('dashboard.html') 
    
    return render_template('register.html')

@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    if request.method == 'POST':
        # 1. Capture data form
        name = request.form.get('name')
        email = request.form.get('email')
        date = request.form.get('date')
        service = request.form.get('service')
        
        # 2. Save to Firebase
        attendance_data = {
            'name': name,
            'email': email,
            'date': date,
            'service': service
        }
        ref = db.reference('attendance')
        ref.push(attendance_data)
        
        # 3. SEND EMAILS
        try:
            # --- Email A: To the Member (Encouragement) ---
            msg_member = Message(f"Attendance Confirmation: {date}",
                                 sender='delstarfordisaiah@gmail.com',
                                 recipients=[email])
            
            msg_member.body = f"""
            Dear {name},

            This email confirms your attendance for the {service} on {date}.

            We noticed your presence and we appreciate your commitment. 
            Please continue with the good work; God has a purpose for you.
            
            "Let us not become weary in doing good, for at the proper time we will reap a harvest if we do not give up." - Galatians 6:9

            Blessings,
            MMUSDA Deaconry Department
            """
            mail.send(msg_member)
            print(f"Encouragement email sent to {name}")

            # --- Email B: To Deaconry (The Official Record) ---
            msg_admin = Message(f"New Attendance Record: {name}",
                                sender='delstarfordisaiah@gmail.com',
                                recipients=['omondidelstarford@gmail.com'])
            
            msg_admin.body = f"A new member has signed the registry.\n\nName: {name}\nService: {service}\nDate: {date}\n\nSee attached official record."
            
            # Create the attachment content
            record_content = f"OFFICIAL ATTENDANCE RECORD\n--------------------------\nName: {name}\nDate: {date}\nService: {service}\nStatus: Present\nSigned: Digitally via MMUSDA Website"
            
            # Attach the text file
            msg_admin.attach("attendance_record.txt", "text/plain", record_content)
            
            mail.send(msg_admin)
            print("Record sent to Deaconry.")

        except Exception as e:
            print(f"Email Error: {e}")
            # We continue even if email fails so the user doesn't get an error page
        
        return render_template('dashboard.html')

    return render_template('attendance.html')


@app.route('/churchmembers')
def churchmembers():
    # 1. Reference the 'members' node in Firebase
    ref = db.reference('members')
    
    # 2. Get the data
    data = ref.get()
    
    # 3. Pass this data to the HTML template
    return render_template('churchmembers.html', members_data=data)

# ==========================================
# 5. RESIDENCE / STATE ROUTES
# ==========================================

@app.route('/koromatangi')
def koromatangi():
    return render_template('koro.html')
@app.route('/sermons')
def sermons():
    return render_template('sermons.html')
@app.route('/teazone')
def teazone():
    return render_template('teazone.html')

@app.route('/sichirai')
def sichirai():
    return render_template('sich.html')

@app.route('/mmust_block')
def mmust_block():
    return render_template('mmust.html')

@app.route('/lurambi')
def lurambi():
    return render_template('lurambi.html')

@app.route('/malava')
def malava():
    return render_template('malava.html')

@app.route('/shinyalu')
def shinyalu():
    return render_template('shinyalu.html')

# ==========================================
# APP ENTRY POINT
# ==========================================

if __name__ == '__main__':
    app.run(debug=True)