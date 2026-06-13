from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file, g
from database.db import init_db, get_db
from utils.auth import login_required, hash_password, check_password
from utils.pdf_gen import generate_invoice_pdf
import os
import json
from datetime import datetime
import re

app = Flask(__name__)
app.secret_key = 'slv_tailor_shop_secret_key_2024'
app.config['UPLOAD_FOLDER'] = 'static/images/uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ─────────────────────────────────────────────
# USER ROUTES
# ─────────────────────────────────────────────

@app.route('/')
def home():
    db = get_db()
    categories = db.execute('SELECT * FROM dress_categories WHERE active=1').fetchall()
    featured = db.execute('SELECT di.*, dc.name as category_name FROM design_images di JOIN dress_categories dc ON di.category_id=dc.id WHERE di.featured=1 LIMIT 6').fetchall()
    return render_template('user/home.html', categories=categories, featured=featured)

@app.route('/about')
def about():
    return render_template('user/about.html')

@app.route('/contact')
def contact():
    return render_template('user/contact.html')

@app.route('/designs')
def designs():
    db = get_db()
    category_id = request.args.get('category', '')
    gender = request.args.get('gender', '')
    search = request.args.get('search', '')
    query = 'SELECT di.*, dc.name as category_name FROM design_images di JOIN dress_categories dc ON di.category_id=dc.id WHERE 1=1'
    params = []
    if category_id:
        query += ' AND di.category_id=?'
        params.append(category_id)
    if gender:
        query += ' AND dc.gender=?'
        params.append(gender)
    if search:
        query += ' AND (di.name LIKE ? OR di.description LIKE ?)'
        params += [f'%{search}%', f'%{search}%']
    designs = db.execute(query, params).fetchall()
    categories = db.execute('SELECT * FROM dress_categories WHERE active=1').fetchall()
    return render_template('user/designs.html', designs=designs, categories=categories,
                           selected_category=category_id, selected_gender=gender, search=search)

@app.route('/prices')
def prices():
    db = get_db()
    prices = db.execute('SELECT pl.*, dc.name as category_name, dc.gender FROM price_list pl JOIN dress_categories dc ON pl.category_id=dc.id ORDER BY dc.gender, dc.name').fetchall()
    return render_template('user/prices.html', prices=prices)

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    db = get_db()
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        age = request.form.get('age', '').strip()
        address = request.form.get('address', '').strip()
        dress_type = request.form.get('dress_type', '').strip()
        measurements = request.form.get('measurements', '').strip()
        delivery_date = request.form.get('delivery_date', '').strip()
        remarks = request.form.get('remarks', '').strip()
        if not all([name, phone, dress_type]):
            return render_template('user/booking.html', error='Please fill in all required fields.',
                                   categories=db.execute('SELECT * FROM dress_categories WHERE active=1').fetchall())
        db.execute('''INSERT INTO customer_orders (name, phone, age, address, dress_type, measurements,
                      booking_date, delivery_date, remarks, status) VALUES (?,?,?,?,?,?,?,?,?,?)''',
                   (name, phone, age, address, dress_type, measurements,
                    datetime.now().strftime('%Y-%m-%d'), delivery_date, remarks, 'pending'))
        db.commit()
        return render_template('user/booking.html', success=True,
                               categories=db.execute('SELECT * FROM dress_categories WHERE active=1').fetchall())
    categories = db.execute('SELECT * FROM dress_categories WHERE active=1').fetchall()
    return render_template('user/booking.html', categories=categories)

# ─────────────────────────────────────────────
# ADMIN ROUTES
# ─────────────────────────────────────────────

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if 'admin_id' in session:
        return redirect(url_for('admin_dashboard'))
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username=? AND role="admin"', (username,)).fetchone()
        if user and check_password(password, user['password_hash']):
            session['admin_id'] = user['id']
            session['admin_name'] = user['username']
            return redirect(url_for('admin_dashboard'))
        error = 'Invalid username or password.'
    return render_template('admin/login.html', error=error)

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('admin_login'))

@app.route('/admin')
@login_required
def admin_dashboard():
    db = get_db()
    stats = {
        'total_orders': db.execute('SELECT COUNT(*) FROM customer_orders').fetchone()[0],
        'pending_orders': db.execute('SELECT COUNT(*) FROM customer_orders WHERE status="pending"').fetchone()[0],
        'total_designs': db.execute('SELECT COUNT(*) FROM design_images').fetchone()[0],
        'total_categories': db.execute('SELECT COUNT(*) FROM dress_categories').fetchone()[0],
        'total_invoices': db.execute('SELECT COUNT(*) FROM invoices').fetchone()[0],
        'revenue': db.execute('SELECT COALESCE(SUM(final_amount),0) FROM invoices').fetchone()[0],
    }
    recent_orders = db.execute('SELECT * FROM customer_orders ORDER BY id DESC LIMIT 5').fetchall()
    return render_template('admin/dashboard.html', stats=stats, recent_orders=recent_orders)

# --- Categories ---
@app.route('/admin/categories')
@login_required
def admin_categories():
    db = get_db()
    cats = db.execute('SELECT * FROM dress_categories ORDER BY gender, name').fetchall()
    return render_template('admin/categories.html', categories=cats)

@app.route('/admin/categories/add', methods=['POST'])
@login_required
def admin_add_category():
    db = get_db()
    name = request.form['name'].strip()
    gender = request.form['gender']
    description = request.form.get('description', '').strip()
    db.execute('INSERT INTO dress_categories (name, gender, description, active) VALUES (?,?,?,1)', (name, gender, description))
    db.commit()
    return redirect(url_for('admin_categories'))

@app.route('/admin/categories/edit/<int:cid>', methods=['POST'])
@login_required
def admin_edit_category(cid):
    db = get_db()
    db.execute('UPDATE dress_categories SET name=?, gender=?, description=?, active=? WHERE id=?',
               (request.form['name'], request.form['gender'], request.form.get('description',''),
                1 if request.form.get('active') else 0, cid))
    db.commit()
    return redirect(url_for('admin_categories'))

@app.route('/admin/categories/delete/<int:cid>')
@login_required
def admin_delete_category(cid):
    db = get_db()
    db.execute('DELETE FROM dress_categories WHERE id=?', (cid,))
    db.commit()
    return redirect(url_for('admin_categories'))

# --- Designs ---
@app.route('/admin/designs')
@login_required
def admin_designs():
    db = get_db()
    designs = db.execute('SELECT di.*, dc.name as cat_name FROM design_images di JOIN dress_categories dc ON di.category_id=dc.id ORDER BY di.id DESC').fetchall()
    categories = db.execute('SELECT * FROM dress_categories WHERE active=1').fetchall()
    return render_template('admin/designs.html', designs=designs, categories=categories)

@app.route('/admin/designs/add', methods=['POST'])
@login_required
def admin_add_design():
    db = get_db()
    name = request.form['name'].strip()
    category_id = request.form['category_id']
    description = request.form.get('description', '').strip()
    featured = 1 if request.form.get('featured') else 0
    image_url = ''
    if 'image' in request.files:
        file = request.files['image']
        if file and allowed_file(file.filename):
            from werkzeug.utils import secure_filename
            import uuid
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"{uuid.uuid4().hex}.{ext}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            image_url = f"/static/images/uploads/{filename}"
    db.execute('INSERT INTO design_images (name, category_id, description, image_url, featured) VALUES (?,?,?,?,?)',
               (name, category_id, description, image_url, featured))
    db.commit()
    return redirect(url_for('admin_designs'))

@app.route('/admin/designs/delete/<int:did>')
@login_required
def admin_delete_design(did):
    db = get_db()
    design = db.execute('SELECT * FROM design_images WHERE id=?', (did,)).fetchone()
    if design and design['image_url']:
        try:
            path = design['image_url'].lstrip('/')
            if os.path.exists(path):
                os.remove(path)
        except:
            pass
    db.execute('DELETE FROM design_images WHERE id=?', (did,))
    db.commit()
    return redirect(url_for('admin_designs'))

# --- Prices ---
@app.route('/admin/prices')
@login_required
def admin_prices():
    db = get_db()
    prices = db.execute('SELECT pl.*, dc.name as cat_name, dc.gender FROM price_list pl JOIN dress_categories dc ON pl.category_id=dc.id').fetchall()
    categories = db.execute('SELECT * FROM dress_categories WHERE active=1').fetchall()
    return render_template('admin/prices.html', prices=prices, categories=categories)

@app.route('/admin/prices/add', methods=['POST'])
@login_required
def admin_add_price():
    db = get_db()
    db.execute('INSERT OR REPLACE INTO price_list (category_id, stitch_type, price, description) VALUES (?,?,?,?)',
               (request.form['category_id'], request.form['stitch_type'], request.form['price'], request.form.get('description','')))
    db.commit()
    return redirect(url_for('admin_prices'))

@app.route('/admin/prices/delete/<int:pid>')
@login_required
def admin_delete_price(pid):
    db = get_db()
    db.execute('DELETE FROM price_list WHERE id=?', (pid,))
    db.commit()
    return redirect(url_for('admin_prices'))

# --- Orders ---
@app.route('/admin/orders')
@login_required
def admin_orders():
    db = get_db()
    status = request.args.get('status', '')
    query = 'SELECT * FROM customer_orders'
    params = []
    if status:
        query += ' WHERE status=?'
        params.append(status)
    query += ' ORDER BY id DESC'
    orders = db.execute(query, params).fetchall()
    return render_template('admin/orders.html', orders=orders, selected_status=status)

@app.route('/admin/orders/<int:oid>')
@login_required
def admin_order_detail(oid):
    db = get_db()
    order = db.execute('SELECT * FROM customer_orders WHERE id=?', (oid,)).fetchone()
    invoice = db.execute('SELECT * FROM invoices WHERE order_id=?', (oid,)).fetchone()
    return render_template('admin/order_detail.html', order=order, invoice=invoice)

@app.route('/admin/orders/update_status/<int:oid>', methods=['POST'])
@login_required
def admin_update_order_status(oid):
    db = get_db()
    db.execute('UPDATE customer_orders SET status=? WHERE id=?', (request.form['status'], oid))
    db.commit()
    return redirect(url_for('admin_order_detail', oid=oid))

# --- Billing ---
@app.route('/admin/billing')
@login_required
def admin_billing():
    db = get_db()
    invoices = db.execute('SELECT inv.*, co.name as customer_name, co.phone FROM invoices inv LEFT JOIN customer_orders co ON inv.order_id=co.id ORDER BY inv.id DESC').fetchall()
    return render_template('admin/billing.html', invoices=invoices)

@app.route('/admin/billing/create', methods=['GET', 'POST'])
@login_required
def admin_create_bill():
    db = get_db()
    if request.method == 'POST':
        order_id = request.form.get('order_id') or None
        customer_name = request.form['customer_name'].strip()
        phone = request.form['phone'].strip()
        age = request.form.get('age', '').strip()
        address = request.form.get('address', '').strip()
        dress_type = request.form['dress_type'].strip()
        measurements = request.form.get('measurements', '').strip()
        booking_date = request.form['booking_date']
        delivery_date = request.form['delivery_date']
        advance_amount = float(request.form.get('advance_amount', 0))
        final_amount = float(request.form['final_amount'])
        remarks = request.form.get('remarks', '').strip()
        balance = final_amount - advance_amount
        # Auto bill number
        last = db.execute('SELECT bill_number FROM invoices ORDER BY id DESC LIMIT 1').fetchone()
        if last:
            try:
                num = int(last['bill_number'].replace('SLV', '')) + 1
            except:
                num = 1001
        else:
            num = 1001
        bill_number = f'SLV{num:04d}'
        db.execute('''INSERT INTO invoices (bill_number, order_id, customer_name, phone, age, address,
                      dress_type, measurements, booking_date, delivery_date, advance_amount, final_amount,
                      balance_amount, remarks, created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                   (bill_number, order_id, customer_name, phone, age, address, dress_type, measurements,
                    booking_date, delivery_date, advance_amount, final_amount, balance, remarks,
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        db.commit()
        inv_id = db.execute('SELECT id FROM invoices WHERE bill_number=?', (bill_number,)).fetchone()['id']
        return redirect(url_for('admin_view_invoice', inv_id=inv_id))
    orders = db.execute('SELECT * FROM customer_orders WHERE status != "completed" ORDER BY id DESC').fetchall()
    return render_template('admin/create_bill.html', orders=orders, today=datetime.now().strftime('%Y-%m-%d'))

@app.route('/admin/billing/<int:inv_id>')
@login_required
def admin_view_invoice(inv_id):
    db = get_db()
    invoice = db.execute('SELECT * FROM invoices WHERE id=?', (inv_id,)).fetchone()
    return render_template('admin/invoice_view.html', invoice=invoice)

@app.route('/admin/billing/<int:inv_id>/pdf')
@login_required
def admin_download_invoice(inv_id):
    db = get_db()
    invoice = db.execute('SELECT * FROM invoices WHERE id=?', (inv_id,)).fetchone()
    pdf_path = generate_invoice_pdf(dict(invoice))
    return send_file(pdf_path, as_attachment=True, download_name=f'SLV_Invoice_{invoice["bill_number"]}.pdf')

# --- Export ---
@app.route('/admin/export/orders')
@login_required
def admin_export_orders():
    import csv, io
    db = get_db()
    orders = db.execute('SELECT * FROM customer_orders ORDER BY id DESC').fetchall()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Name', 'Phone', 'Age', 'Address', 'Dress Type', 'Booking Date', 'Delivery Date', 'Status', 'Remarks'])
    for o in orders:
        writer.writerow([o['id'], o['name'], o['phone'], o['age'], o['address'], o['dress_type'],
                         o['booking_date'], o['delivery_date'], o['status'], o['remarks']])
    output.seek(0)
    from flask import Response
    return Response(output.getvalue(), mimetype='text/csv',
                    headers={'Content-Disposition': 'attachment;filename=orders_export.csv'})

@app.route('/admin/export/invoices')
@login_required
def admin_export_invoices():
    import csv, io
    db = get_db()
    invoices = db.execute('SELECT * FROM invoices ORDER BY id DESC').fetchall()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Bill No', 'Customer', 'Phone', 'Dress Type', 'Booking Date', 'Delivery Date',
                     'Advance', 'Final Amount', 'Balance', 'Created At'])
    for inv in invoices:
        writer.writerow([inv['bill_number'], inv['customer_name'], inv['phone'], inv['dress_type'],
                         inv['booking_date'], inv['delivery_date'], inv['advance_amount'],
                         inv['final_amount'], inv['balance_amount'], inv['created_at']])
    output.seek(0)
    from flask import Response
    return Response(output.getvalue(), mimetype='text/csv',
                    headers={'Content-Disposition': 'attachment;filename=invoices_export.csv'})

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
