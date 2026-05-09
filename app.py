from flask import Flask, request, jsonify, send_from_directory
import sqlite3
import os
import hashlib

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lifelink.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
        rating INTEGER NOT NULL DEFAULT 5, comment TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    c.execute('''CREATE TABLE IF NOT EXISTS donors (
        id INTEGER PRIMARY KEY AUTOINCREMENT, full_name TEXT NOT NULL,
        age INTEGER NOT NULL, phone TEXT NOT NULL, city TEXT NOT NULL,
        blood_group TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    # 1. ADDED 'phone TEXT' TO REQUESTS TABLE
    c.execute('''CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT, patient_name TEXT NOT NULL,
        blood_group TEXT NOT NULL, phone TEXT, units INTEGER DEFAULT 1,
        status TEXT DEFAULT 'Pending', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    c.execute('''CREATE TABLE IF NOT EXISTS blood_banks (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
        city TEXT NOT NULL, lat REAL NOT NULL, lng REAL NOT NULL, phone TEXT)''')

    # 2. ADDED 'full_name, phone, city, blood_group' TO USERS TABLE
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, full_name TEXT, username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL, phone TEXT, city TEXT, blood_group TEXT, password TEXT NOT NULL,
        role TEXT DEFAULT 'user', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    c.execute('''CREATE TABLE IF NOT EXISTS blood_inventory (
        blood_group TEXT PRIMARY KEY, units INTEGER DEFAULT 0)''')

    c.execute('SELECT COUNT(*) FROM blood_banks')
    if c.fetchone()[0] == 0:
        c.executemany('INSERT INTO blood_banks (name,city,lat,lng,phone) VALUES (?,?,?,?,?)', [  ('Red Cross Blood Bank','Mumbai',19.076,72.8777,'+912212345678'),
            ('Lifeline Blood Center','Delhi',28.6139,77.209,'+911198765432'),
            ('City Blood Bank','Bangalore',12.9716,77.5946,'+918012345678'),
            ('Heart Beat Center','Chennai',13.0827,80.2707,'+914412345678'),
            ('Save Life Bank','Kolkata',22.5726,88.3639,'+913312345678'),
            ('Gorakhpur Blood Center','Gorakhpur',26.7606,83.3732,'+915512345678'),
            ('Lucknow Blood Bank','Lucknow',26.8467,80.9462,'+915221234567'),
            ('Pune Blood Center','Pune',18.5204,73.8567,'+912012345678'),
            ('Hyderabad Blood Bank','Hyderabad',17.385,78.4867,'+914012345678'),
            ('Jaipur Blood Center','Jaipur',26.9124,75.7873,'+911411234567'),
            ('Patna Blood Bank','Patna',25.6093,85.1376,'+916121234567'),
            ('Bhopal Blood Center','Bhopal',23.2599,77.4126,'+917551234567'),
            ('BRD Medical College Blood Bank','Gorakhpur',26.7514,83.3770,'+915513456789'),
            ('District Hospital Blood Bank','Gorakhpur',26.7590,83.3710,'+915513456790'),
            ('Red Cross Blood Bank Gorakhpur','Gorakhpur',26.7630,83.3680,'+915513456791'),
            ('Apollo Blood Centre','Gorakhpur',26.7560,83.3910,'+915513456794'),
            ('Yashoda Hospital Blood Bank','Gorakhpur',26.7420,83.3650,'+915513456795'),
            ('Metro Blood Bank','Gorakhpur',26.7700,83.3580,'+915513456796'),
            ('Baba Raghav Das Medical College','Deoria',26.4970,83.7670,'+915561234567'),
            ('District Hospital Blood Bank','Basti',26.8015,82.7420,'+915541234567'),
            ('District Hospital Blood Bank','Maharajganj',26.9230,83.5550,'+915521234567'),
            ('District Hospital Blood Bank','Kushinagar',26.7470,83.8870,'+915551234567'),
            ('Sanjay Gandhi PGIMS','Lucknow',26.8467,80.9462,'+915221234567'),
            ('KGMU Blood Centre','Lucknow',26.9124,80.9462,'+915221987654'),
            ('BHU Trauma Centre','Varanasi',25.2690,83.0100,'+915421234567'),
            ('Lumbini Zonal Hospital','Lumbini (Nepal)',26.9500,83.2800,'+977-71-580432'),
            ('District Hospital','Azamgarh',26.0640,83.1840,'+915461234567')])
    c.execute('SELECT COUNT(*) FROM blood_inventory')
    if c.fetchone()[0] == 0:
                c.executemany('INSERT INTO blood_inventory (blood_group, units) VALUES (?,?)', [
            ('O+', 450), ('B+', 300), ('A+', 250), ('AB+', 60),
            ('O-', 50),  ('A-', 40),  ('B-', 30),  ('AB-', 20)])

    # 3. ADDED PHONE NUMBERS TO DUMMY REQUEST DATA
    c.execute('SELECT COUNT(*) FROM requests')
    if c.fetchone()[0] == 0:
               c.executemany('INSERT INTO requests (patient_name,blood_group,phone,units,status) VALUES (?,?,?,?,?)', [
            ('RTA Victim - NH 28 Accident','O+','+919876543210',3,'Pending'),
            ('Maternity Bleeding - District Hospital','B+','+918765432109',2,'Pending'),
            ('Thalassemia Major Child - BRD','O+','+917654321098',1,'Pending'),
            ('Open Heart Surgery - Apollo','O-','+916543210987',2,'Pending'),
            ('Dengue Shock Syndrome','AB+','+915432109876',1,'Pending'),
            ('Accident Case - Deoria Highway','O+','+914321098765',2,'Accepted'),
            ('Surgery Patient - KGMU Lucknow','A+','+913210987654',1,'Accepted'),
            ('Dengue Patient - Basti','B+','+912109876543',1,'Accepted'),
            ('Maternity Emergency - Gorakhpur','A-','+911198877665',1,'Accepted'),
            ('Railway Accident - Chauri Chaura','O+','+919900887766',2,'Accepted'),
            ('Routine Transfusion - BRD','B-','+918800776655',1,'Accepted'),
            ('Surgery - Varanasi BHU','AB+','+917700665544',2,'Accepted'),
            ('Cancelled Order - Wrong Group','AB-','+916600554433',1,'Rejected'),
            ('Duplicate Request - Withdrawn','A+','+915500443322',1,'Rejected'),
            ('Patient Transferred - Lucknow','B+','+914400332211',2,'Rejected')])
    c.execute('SELECT COUNT(*) FROM donors')
    if c.fetchone()[0] == 0:
              c.executemany('INSERT INTO donors (full_name,age,phone,city,blood_group) VALUES (?,?,?,?,?)', [
            ('Arun Tiwari',28,'+919876543210','Gorakhpur','O+'),
            ('Shivam Mishra',24,'+918765432109','Gorakhpur','B+'),
            ('Priya Gupta',32,'+917654321098','Deoria','A+'),
            ('Vikram Singh',26,'+916543210987','Gorakhpur','O-'),
            ('Neha Verma',22,'+915432109876','Maharajganj','AB+'),
            ('Rohit Kumar',35,'+914321098765','Gorakhpur','O+'),
            ('Anjali Yadav',29,'+913210987654','Kushinagar','B+'),
            ('Karan Mehta',27,'+912109876543','Gorakhpur','A+'),
            ('Pooja Reddy',23,'+911198877665','Gorakhpur','AB-'),
            ('Sanjay Srivastava',40,'+919988776655','Basti','O+'),
            ('Meena Devi',33,'+918877665544','Gorakhpur','B-'),
            ('Arjun Nair',26,'+917766554433','Lucknow','A-'),
            ('Ravi Tiwari',31,'+916655443322','Gorakhpur','O+'),
            ('Suman Shukla',28,'+915544332211','Gorakhpur','A+'),
            ('Akhil Raj',25,'+914433221100','Deoria','B+'),
            ('Kavita Joshi',30,'+913322110099','Gorakhpur','O+'),
            ('Manish Gupta',34,'+912211009988','Azamgarh','AB+'),
            ('Sakshi Mishra',21,'+911100998877','Gorakhpur','A+'),
            ('Rajesh Yadav',45,'+919900887766','Gorakhpur','O+'),
            ('Swati Pandey',26,'+918800776655','Maharajganj','B+'),
            ('Amit Pandey',29,'+917700665544','Gorakhpur','O-'),
            ('Nisha Singh',24,'+916600554433','Kushinagar','A-'),
            ('Vishal Srivastava',38,'+915500443322','Deoria','B+'),
            ('Ritu Jaiswal',27,'+914400332211','Gorakhpur','AB+'),
            ('Gaurav Sharma',32,'+913300221100','Basti','O+'),
            ('Anita Tiwari',36,'+912200110099','Gorakhpur','A+'),
            ('Prashant Verma',23,'+911100009988','Gorakhpur','B-'),
            ('Deepak Chauhan',41,'+919999887766','Azamgarh','O+'),
            ('Surbhi Singh',25,'+918888776655','Gorakhpur','AB-'),
            ('Rahul Pandey',30,'+917777665544','Gorakhpur','O+')])
    c.execute('SELECT COUNT(*) FROM reviews')
    if c.fetchone()[0] == 0:
        c.executemany('INSERT INTO reviews (name,rating,comment) VALUES (?,?,?)', [
            ('Arun Tiwari',5,"LifeLink saved my uncles life during an accident."),
            ('Dr. Priya',4,'Very useful for us at BRD Medical College.')])

    c.execute("SELECT COUNT(*) FROM users WHERE role='admin'")
    if c.fetchone()[0] == 0:
        pw = hashlib.sha256('admin123'.encode()).hexdigest()
        c.execute('INSERT INTO users (username,email,password,role) VALUES (?,?,?,?)',
                  ('admin','admin@lifelink.com',pw,'admin'))

    conn.commit()
    conn.close()
    print("  Realistic Gorakhpur Database Loaded!")

# ==========================================
# PUBLIC API ROUTES
# ==========================================

@app.route('/api/get_reviews.php')
def get_reviews():
    conn = get_db()
    rows = conn.execute('SELECT name,rating,comment,created_at as date FROM reviews ORDER BY created_at DESC').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/post_review.php', methods=['POST'])
def post_review():
    name = request.form.get('name','').strip()
    rating = request.form.get('rating','5')
    comment = request.form.get('comment','').strip()
    if not name or not comment:
        return jsonify({'status':'error','message':'All fields required'})
    conn = get_db()
    conn.execute('INSERT INTO reviews (name,rating,comment) VALUES (?,?,?)',(name,int(rating),comment))
    conn.commit()
    conn.close()
    return jsonify({'status':'success','message':'Review submitted'})

@app.route('/api/get_banks.php', methods=['POST'])
def get_banks():
    city = request.form.get('city','').strip()
    conn = get_db()
    if city:
        rows = conn.execute('SELECT * FROM blood_banks WHERE LOWER(city) LIKE ? ORDER BY city',(f'%{city.lower()}%',)).fetchall()
    else:
        rows = conn.execute('SELECT * FROM blood_banks ORDER BY city').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/register_donor.php', methods=['POST'])
def register_donor():
    name = request.form.get('fullName','').strip()
    age = request.form.get('age','')
    phone = request.form.get('phone','').strip()
    city = request.form.get('city','').strip()
    blood_group = request.form.get('bloodGroup','').strip()
    if not all([name,age,phone,city,blood_group]):
        return jsonify({'status':'error','message':'All fields required'})
    try:
        age = int(age)
        if not (18 <= age <= 65):
            return jsonify({'status':'error','message':'Age must be 18-65'})
    except ValueError:
        return jsonify({'status':'error','message':'Invalid age'})
    if blood_group not in ['A+','A-','B+','B-','O+','O-','AB+','AB-']:
        return jsonify({'status':'error','message':'Invalid blood group'})
    conn = get_db()
    conn.execute('INSERT INTO donors (full_name,age,phone,city,blood_group) VALUES (?,?,?,?,?)',(name,age,phone,city,blood_group))
    conn.execute('UPDATE blood_inventory SET units = units + 1 WHERE blood_group = ?', (blood_group,))
    conn.commit()
    conn.close()
    return jsonify({'status':'success','message':'Donor registered successfully'})

# 4. UPDATED POST REQUEST TO ACCEPT PHONE
@app.route('/api/post_request.php', methods=['POST'])
def post_request():
    patient_name = request.form.get('patientName','').strip()
    blood_group = request.form.get('bloodGroup','').strip()
    phone = request.form.get('phone','').strip()
    units = request.form.get('units','1')
    if not patient_name or not blood_group:
        return jsonify({'status':'error','message':'Patient name and blood group required'})
    conn = get_db()
    conn.execute('INSERT INTO requests (patient_name,blood_group,phone,units) VALUES (?,?,?,?)',(patient_name,blood_group,phone,int(units)))
    conn.commit()
    conn.close()
    return jsonify({'status':'success','message':'Blood request posted'})

# 5. UPDATED GET REQUESTS TO RETURN PHONE
@app.route('/api/get_requests.php')
def get_requests_public():
    conn = get_db()
    rows = conn.execute('SELECT patient_name,blood_group,phone,status FROM requests ORDER BY created_at DESC').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

# 6. UPDATED USER REGISTER FOR NEW FIELDS (Name, Phone, City, Blood Group)
@app.route('/api/user_register.php', methods=['POST'])
@app.route('/api/user_register.php', methods=['POST'])
def user_register():
    full_name = request.form.get('fullName','').strip()
    email = request.form.get('email','').strip()
    phone = request.form.get('phone','').strip()
    city = request.form.get('city','').strip()
    blood_group = request.form.get('bloodGroup','').strip()
    password = request.form.get('password','')
    if not all([email,password]):
        return jsonify({'status':'error','message':'Email and password required'})
    
    # FIX: Auto-generate username from email (shanti23@gmail.com -> shanti23)
    username = email.split('@')[0] if email else 'user'
    
    hashed = hashlib.sha256(password.encode()).hexdigest()
    conn = get_db()
    if conn.execute('SELECT id FROM users WHERE email=?',(email,)).fetchone():
        conn.close()
        return jsonify({'status':'error','message':'Email already exists'})
    
    # FIX: Added 'username' to the INSERT statement
    conn.execute('INSERT INTO users (full_name, username, email, phone, city, blood_group, password, role) VALUES (?,?,?,?,?,?,?,?)',(full_name, username, email, phone, city, blood_group, hashed, 'user'))
    conn.commit()
    conn.close()
    return jsonify({'status':'success','message':'Registration successful'})

# 7. UPDATED USER LOGIN TO USE EMAIL INSTEAD OF USERNAME
@app.route('/api/user_login.php', methods=['POST'])
def user_login():
    email = request.form.get('email','').strip()
    password = request.form.get('password','')
    if not email or not password:
        return jsonify({'status':'error','message':'Email and password required'})
    hashed = hashlib.sha256(password.encode()).hexdigest()
    conn = get_db()
    user = conn.execute('SELECT id,full_name FROM users WHERE email=? AND password=?',(email,hashed)).fetchone()
    conn.close()
    if user:
        return jsonify({'status':'success','message':'Login successful','user_id':user['id'],'name':user['full_name']})
    return jsonify({'status':'error','message':'Invalid credentials'})

# ==========================================
# ADMIN API ROUTES (Unchanged)
# ==========================================

@app.route('/api/admin_login.php', methods=['POST'])
def admin_login():
    username = request.form.get('username','').strip()
    password = request.form.get('password','')
    if not username or not password:
        return jsonify({'status':'error','message':'All fields required'})
    hashed = hashlib.sha256(password.encode()).hexdigest()
    conn = get_db()
    admin = conn.execute('SELECT id FROM users WHERE username=? AND password=? AND role=?',(username,hashed,'admin')).fetchone()
    conn.close()
    if admin:
        return jsonify({'status':'success','message':'Admin login successful'})
    return jsonify({'status':'error','message':'Invalid admin credentials'})

@app.route('/api/admin/get_stock.php')
def admin_get_stock():
    conn = get_db()
    rows = conn.execute('SELECT * FROM blood_inventory ORDER BY units DESC').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/admin/get_requests.php')
def admin_get_requests():
    conn = get_db()
    rows = conn.execute('SELECT * FROM requests ORDER BY created_at DESC').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/admin/get_donors.php')
def admin_get_donors():
    conn = get_db()
    rows = conn.execute('SELECT * FROM donors ORDER BY created_at DESC').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/admin/update_request.php', methods=['POST'])
def admin_update_request():
    req_id = request.form.get('id')
    status = request.form.get('status')
    if not req_id or not status:
        return jsonify({'status':'error','message':'Missing parameters'})
    conn = get_db()
    if status == 'Accepted':
        req = conn.execute('SELECT * FROM requests WHERE id=?',(req_id,)).fetchone()
        stock = conn.execute('SELECT units FROM blood_inventory WHERE blood_group=?', (req['blood_group'],)).fetchone()
        if not stock or stock['units'] < req['units']:
            conn.close()
            return jsonify({'status':'error', 'message': f'Not enough {req["blood_group"]} blood in stock!'})
        conn.execute('UPDATE blood_inventory SET units = units - ? WHERE blood_group = ?', (req['units'], req['blood_group']))
    conn.execute('UPDATE requests SET status=? WHERE id=?',(status,req_id))
    conn.commit()
    conn.close()
    return jsonify({'status':'success','message':f'Request {status} successfully!'})

# ==========================================
# STATIC FILE SERVING
# ==========================================

@app.route('/')
def index():
    return send_from_directory('.','index.html')

@app.route('/<path:f>')
def static_files(f):
    if os.path.exists(f):
        return send_from_directory('.',f)
    return jsonify({'error':'Not found'}),404

if __name__ == '__main__':
    init_db()
    print("\n" + "="*50)
    print("   LifeLink Flask + SQLite Server")
    print("   Open: http://localhost:5000")
    print("   Admin: admin / admin123")
    print("="*50 + "\n")
    app.run(host='0.0.0.0', port=5000, debug=True)