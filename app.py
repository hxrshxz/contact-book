from flask import Flask, render_template, request, redirect, url_for, jsonify
import mysql.connector

app = Flask(__name__)

db_config = {
    'user': 'root',
    'password': '', 
    'host': 'localhost',
    'database': 'contact_book',
    'auth_plugin': 'mysql_native_password' 
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

# Initialize database
def initialize_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            phone VARCHAR(20),
            email VARCHAR(100),
            address VARCHAR(200),
            notes TEXT
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

initialize_db()

@app.route('/')
def home():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM contacts')
    contacts = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', contacts=contacts)

@app.route('/add', methods=['POST'])
def add_contact():
        data = request.form
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO contacts (name, phone, email, address, notes)
            VALUES (%s, %s, %s, %s, %s)
        ''', (data['name'], data['phone'], data['email'], data['address'], data['notes']))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('home'))

@app.route('/delete/<int:id>')
def delete_contact(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM contacts WHERE id = %s', (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('home'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_contact(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        data = request.form
        cursor.execute('''
            UPDATE contacts SET
            name = %s,
            phone = %s,
            email = %s,
            address = %s,
            notes = %s
            WHERE id = %s
        ''', (data['name'], data['phone'], data['email'], data['address'], data['notes'], id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('home'))
    
    cursor.execute('SELECT * FROM contacts WHERE id = %s', (id,))
    contact = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('edit.html', contact=contact)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT * FROM contacts 
        WHERE name LIKE %s 
        OR phone LIKE %s 
        OR email LIKE %s 
        OR address LIKE %s
    ''', (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)