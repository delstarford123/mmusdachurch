import firebase_admin
from firebase_admin import credentials, db
from flask import Flask, render_template, request

app = Flask(__name__)

# ==========================================
# FIREBASE SETUP
# ==========================================

# 1. Load the service account key (Make sure the file is in the same folder)
cred = credentials.Certificate("serviceAccountKey.json")

# 2. Initialize the app with the specific Database URL
# IMPORTANT: Replace the URL below with YOUR specific Firebase Realtime Database URL
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://mmusdachurch-d2455-default-rtdb.firebaseio.com/' 
})

# ==========================================
# CORE PAGES
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

# --- MODIFIED REGISTER ROUTE ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # 1. Get data from HTML form
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        residence = request.form.get('residence')
        
        # 2. Create a dictionary for the database
        member_data = {
            'name': name,
            'email': email,
            'phone': phone,
            'residence': residence
        }

        # 3. Save to Firebase under the 'members' node
        # push() generates a unique ID for each new member
        ref = db.reference('members')
        ref.push(member_data)

        print(f"SAVED TO FIREBASE: {name} from {residence}")
        
        return render_template('dashboard.html') 
    return render_template('register.html')

# --- MODIFIED ATTENDANCE ROUTE ---
@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    if request.method == 'POST':
        # 1. Get data from HTML form
        name = request.form.get('name')
        date = request.form.get('date')
        service = request.form.get('service')
        
        # 2. Create a dictionary for the database
        attendance_data = {
            'name': name,
            'date': date,
            'service': service
        }

        # 3. Save to Firebase under the 'attendance' node
        ref = db.reference('attendance')
        ref.push(attendance_data)
        
        print(f"ATTENDANCE SAVED: {name} for {service}")
        
        return render_template('dashboard.html')
    return render_template('attendance.html')

# ==========================================
# RESIDENCE / STATE ROUTES
# ==========================================

@app.route('/koromatangi')
def koromatangi():
    return render_template('koro.html')

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