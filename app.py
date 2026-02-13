import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'thrift_shop_secret_key')

# Upload Configuration
UPLOAD_FOLDER = 'static/img/products'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# MySQL Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'thrift_db'
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def log_activity(username, action, item_name):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        # Create table if not exists (defensive)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50),
                action VARCHAR(100),
                item_name VARCHAR(100),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            INSERT INTO activity_logs (username, action, item_name) 
            VALUES (%s, %s, %s)
        """, (username, action, item_name))
        conn.commit()
        cursor.close()
        conn.close()

# --- Routes ---

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if user:
                session['username'] = user['username']
                session['full_name'] = user['full_name']
                session['role'] = user.get('role', 'Staff')  # Store role in session
                return redirect(url_for('dashboard'))
            else:
                return render_template('login.html', error="Username atau Password salah!")
        return render_template('login.html', error="Koneksi database bermasalah!")
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', full_name=session['full_name'])

@app.route('/inventory')
def inventory():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Get filter and sort parameters
    category_filter = request.args.get('category', '')
    condition_filter = request.args.get('condition', '')
    sort_by = request.args.get('sort', 'date_desc')
    
    conn = get_db_connection()
    items = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        
        # Build query with filters
        query = "SELECT * FROM inventory WHERE 1=1"
        params = []
        
        if category_filter:
            query += " AND category = %s"
            params.append(category_filter)
        
        if condition_filter:
            query += " AND item_condition = %s"
            params.append(condition_filter)
        
        # Add sorting
        if sort_by == 'price_asc':
            query += " ORDER BY price ASC"
        elif sort_by == 'price_desc':
            query += " ORDER BY price DESC"
        elif sort_by == 'stock_asc':
            query += " ORDER BY stock ASC"
        elif sort_by == 'stock_desc':
            query += " ORDER BY stock DESC"
        elif sort_by == 'date_asc':
            query += " ORDER BY entry_date ASC"
        else:  # date_desc (default)
            query += " ORDER BY entry_date DESC"
        
        cursor.execute(query, params)
        items = cursor.fetchall()
        cursor.close()
        conn.close()
    
    # Get unique categories and conditions for filter dropdowns
    categories = ['Atasan', 'Bawahan', 'Pakaian Luar', 'Alas Kaki', 'Aksesoris']
    conditions = ['Baru', 'Seperti Baru', 'Bagus', 'Layak Pakai']
    
    return render_template('inventory.html', 
                         items=items, 
                         role=session.get('role', 'Staff'),
                         categories=categories,
                         conditions=conditions,
                         selected_category=category_filter,
                         selected_condition=condition_filter,
                         selected_sort=sort_by)

# API for Charts
@app.route('/api/dashboard_data')
def dashboard_data():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    data = {'stock_levels': [], 'sales_per_day': []}
    if conn:
        cursor = conn.cursor(dictionary=True)
        
        # Stock levels per category
        cursor.execute("SELECT category, SUM(stock) as total_stock FROM inventory GROUP BY category")
        data['stock_levels'] = cursor.fetchall()
        
        # Sales last 7 days
        cursor.execute("""
            SELECT DATE(sale_date) as date, SUM(total_price) as revenue 
            FROM sales 
            WHERE sale_date >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            GROUP BY DATE(sale_date)
            ORDER BY DATE(sale_date) ASC
        """)
        data['sales_per_day'] = cursor.fetchall()
        
        cursor.close()
        conn.close()
    
    return jsonify(data)

# CRUD Inventory
@app.route('/inventory/add', methods=['POST'])
def add_item():
    if 'username' not in session: return redirect(url_for('login'))
    
    name = request.form['name']
    category = request.form['category']
    price = request.form['price']
    stock = request.form['stock']
    condition = request.form['condition']
    image_url = request.form.get('image_url', 'default-product.png')
    
    if not image_url:
        image_url = 'default-product.png'
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO inventory (name, category, price, stock, item_condition, image_url) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, category, price, stock, condition, image_url))
        conn.commit()
        cursor.close()
        conn.close()
        log_activity(session['username'], 'Tambah Barang', name)
    
    return redirect(url_for('inventory'))

@app.route('/inventory/edit/<int:id>', methods=['POST'])
def edit_item(id):
    if 'username' not in session: return redirect(url_for('login'))
    
    name = request.form['name']
    category = request.form['category']
    price = request.form['price']
    stock = request.form['stock']
    condition = request.form['condition']
    image_url = request.form.get('image_url', 'default-product.png')
    
    if not image_url:
        image_url = 'default-product.png'
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE inventory 
            SET name=%s, category=%s, price=%s, stock=%s, item_condition=%s, image_url=%s 
            WHERE id=%s
        """, (name, category, price, stock, condition, image_url, id))
        conn.commit()
        cursor.close()
        conn.close()
        log_activity(session['username'], 'Edit Barang', name)
    
    return redirect(url_for('inventory'))

@app.route('/inventory/sell/<int:id>')
def sell_item(id):
    if 'username' not in session: return redirect(url_for('login'))
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        # Check stock
        cursor.execute("SELECT name, stock, price FROM inventory WHERE id = %s", (id,))
        item = cursor.fetchone()
        
        if item and item['stock'] > 0:
            # Add to sales
            cursor.execute("""
                INSERT INTO sales (product_id, quantity, total_price) 
                VALUES (%s, 1, %s)
            """, (id, item['price']))
            
            # Update stock
            cursor.execute("UPDATE inventory SET stock = stock - 1 WHERE id = %s", (id,))
            
            conn.commit()
            log_activity(session['username'], 'Penjualan', item['name'])
            
        cursor.close()
        conn.close()
    
    return redirect(url_for('inventory'))

@app.route('/inventory/delete/<int:id>')
def delete_item(id):
    if 'username' not in session: return redirect(url_for('login'))
    
    # Role-based access: Only Admin can delete
    if session.get('role') != 'Admin':
        return redirect(url_for('inventory'))  # Staff cannot delete
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        # Get item name for logging before deletion
        cursor.execute("SELECT name FROM inventory WHERE id = %s", (id,))
        item = cursor.fetchone()
        item_name = item['name'] if item else 'Unknown'
        
        cursor.execute("DELETE FROM inventory WHERE id = %s", (id,))
        conn.commit()
        cursor.close()
        conn.close()
        log_activity(session['username'], 'Hapus Barang', item_name)
    
    return redirect(url_for('inventory'))

@app.route('/reports')
def reports():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    sales_history = []
    sold_out_items = []
    activity_logs = []
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        
        # Get sales history with product names
        cursor.execute("""
            SELECT s.*, i.name as product_name, i.category 
            FROM sales s 
            JOIN inventory i ON s.product_id = i.id 
            ORDER BY s.sale_date DESC
        """)
        sales_history = cursor.fetchall()
        
        # Get sold out items
        cursor.execute("SELECT * FROM inventory WHERE stock = 0")
        sold_out_items = cursor.fetchall()
        
        # Get activity logs (Admin only)
        if session.get('role') == 'Admin':
            cursor.execute("SELECT * FROM activity_logs ORDER BY timestamp DESC LIMIT 50")
            activity_logs = cursor.fetchall()
        
        cursor.close()
        conn.close()
    
    return render_template('reports.html', 
                           sales=sales_history, 
                           sold_out=sold_out_items,
                           logs=activity_logs,
                           role=session.get('role', 'Staff'))

if __name__ == '__main__':
    app.run(debug=True)
