# SLV Tailor Shop — Installation & Deployment Guide

## Owner Information
- **Shop Name:** SLV Tailor Shop
- **Owner:** KEMPANARASIMHAIAH
- **Phone:** 9535536981
- **Address:** Arasanakunte, Solur Hobli, Magadi Taluk, Bangalore - 562127

---

## 🚀 Quick Start (Local / Testing)

### Step 1: Install Python
Download Python 3.10+ from https://www.python.org/downloads/
Make sure to check "Add Python to PATH" during installation.

### Step 2: Extract Project Files
Unzip `slv_tailor_shop.zip` to a folder, e.g.:
```
C:\Users\YourName\slv_tailor_shop\   (Windows)
/home/yourname/slv_tailor_shop/      (Linux/Mac)
```

### Step 3: Open Terminal / Command Prompt
Navigate to the project folder:
```bash
cd slv_tailor_shop
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Run the Website
```bash
python app.py
```

### Step 6: Open in Browser
Open your browser and go to:
```
http://localhost:5000
```

**Admin Panel:** http://localhost:5000/admin/login
- Username: `admin`
- Password: `admin@slv2024`

> ⚠️ **Change the admin password immediately after first login!**
> Go to your database file and update the password hash.

---

## 📁 Project Structure

```
slv_tailor_shop/
├── app.py                    ← Main Flask application
├── requirements.txt          ← Python dependencies
├── database/
│   ├── db.py                 ← Database functions & schema
│   └── slv_tailor.db         ← SQLite database (auto-created)
├── utils/
│   ├── auth.py               ← Password hashing & login check
│   └── pdf_gen.py            ← PDF invoice generator
├── static/
│   ├── css/
│   │   └── style.css         ← All website styles
│   ├── js/
│   │   └── main.js           ← JavaScript interactions
│   ├── images/
│   │   ├── designs/          ← Static design images (optional)
│   │   └── uploads/          ← Admin-uploaded images (auto-created)
│   └── invoices/             ← Generated PDF invoices (auto-created)
└── templates/
    ├── user/
    │   ├── base.html         ← User site base layout
    │   ├── home.html         ← Homepage
    │   ├── designs.html      ← Design gallery
    │   ├── prices.html       ← Stitching prices
    │   ├── booking.html      ← Booking form
    │   ├── about.html        ← About page
    │   └── contact.html      ← Contact page
    └── admin/
        ├── base.html         ← Admin base layout
        ├── login.html        ← Admin login
        ├── dashboard.html    ← Admin dashboard
        ├── categories.html   ← Manage categories
        ├── designs.html      ← Manage designs
        ├── prices.html       ← Manage prices
        ├── orders.html       ← View all orders
        ├── order_detail.html ← Single order view
        ├── billing.html      ← Billing records
        ├── create_bill.html  ← New invoice form
        └── invoice_view.html ← View/print invoice
```

---

## 🗄️ Database Tables

| Table             | Purpose                          |
|-------------------|----------------------------------|
| `users`           | Admin login credentials          |
| `dress_categories`| Dress types (Shirt, Blouse, etc.)|
| `design_images`   | Gallery images with categories   |
| `price_list`      | Stitching prices per category    |
| `customer_orders` | Bookings from customers          |
| `invoices`        | Bills with payment details       |

---

## 🌐 Making the Website Public (IMPORTANT)

> ⚠️ **Currently, this website only runs on your own computer.**
> To make it accessible to everyone on the internet, you need:

### Step 1: Buy a Domain Name
Recommended domains for SLV Tailor Shop:
- **slvtailorshop.in** ← Best choice (India domain)
- **slvtailors.com**
- **slvtailor.in**
- **kempanarasimhaiah.in**

**Where to buy:**
| Provider | Website | Price (approx.) |
|----------|---------|-----------------|
| Hostinger | hostinger.in | ₹700–₹1,200/year |
| GoDaddy | godaddy.com | ₹800–₹1,500/year |
| Namecheap | namecheap.com | $10–$15/year |
| BigRock | bigrock.in | ₹700–₹1,200/year |

### Step 2: Buy Web Hosting
You need a server to host your Flask website.

**Recommended: Hostinger VPS or Shared Hosting**

**Option A — Hostinger Shared Hosting (Easiest, ~₹2,500/year):**
1. Go to hostinger.in
2. Buy a Python-compatible hosting plan
3. Upload your files via File Manager
4. Set up the Python app (they have 1-click setup)

**Option B — Hostinger VPS (More control, ~₹700/month):**
```bash
# After getting VPS access via SSH:
sudo apt update && sudo apt install python3-pip nginx -y
cd /var/www/
git clone <your-project> slv_tailor_shop
cd slv_tailor_shop
pip3 install -r requirements.txt
pip3 install gunicorn

# Run with Gunicorn
gunicorn -w 2 -b 127.0.0.1:5000 app:app &
```

**Option C — Railway.app (Free tier available):**
1. Go to railway.app
2. Connect your GitHub repository
3. Deploy with one click
4. Add your domain in settings

**Option D — PythonAnywhere (Beginner-friendly, Free tier):**
1. Go to pythonanywhere.com
2. Create a free account
3. Upload your project files
4. Create a new Web App → Flask
5. Set source code path and WSGI file

### Step 3: Connect Domain to Hosting
After buying both domain and hosting:
1. Log into your domain registrar (e.g., Hostinger)
2. Go to DNS settings
3. Add an **A record**: `@ → your-server-IP`
4. Add a **CNAME**: `www → your-server-IP`
5. Wait 24–48 hours for DNS propagation

### Step 4: Enable HTTPS (SSL Certificate)
Most hosting providers offer free SSL. Enable it for secure `https://` access.

---

## ⚙️ Production Configuration

Before going live, update `app.py`:

```python
# Change this line:
app.secret_key = 'slv_tailor_shop_secret_key_2024'
# To a strong random key:
app.secret_key = 'some-very-long-random-string-change-this-NOW'

# Also set debug=False:
app.run(debug=False, host='0.0.0.0', port=5000)
```

### Using Gunicorn (Production Server)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Nginx Config (if using VPS)
```nginx
server {
    listen 80;
    server_name slvtailorshop.in www.slvtailorshop.in;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /var/www/slv_tailor_shop/static;
        expires 30d;
        add_header Cache-Control "public";
    }
}
```

---

## 🔒 Security Checklist

- [ ] Change default admin password
- [ ] Change `secret_key` in app.py
- [ ] Set `debug=False` in production
- [ ] Enable HTTPS (SSL certificate)
- [ ] Keep regular database backups
- [ ] Restrict admin URL access if needed

---

## 📱 Features Summary

### User Website
- ✅ Home page with hero, categories, featured designs
- ✅ Design gallery with search & filter (Men's / Women's / Kurtha Necks)
- ✅ Stitching price list
- ✅ Online booking form
- ✅ About page with shop info
- ✅ Contact page with location

### Admin Panel (/admin)
- ✅ Secure login with password hashing
- ✅ Dashboard with stats (orders, revenue, designs)
- ✅ Add/Edit/Delete dress categories
- ✅ Upload and manage design images
- ✅ Update stitching prices
- ✅ View and manage customer orders
- ✅ Create bills / invoices
- ✅ View and print invoices
- ✅ Download PDF invoices
- ✅ Export orders & invoices as CSV
- ✅ Auto-generated bill numbers (SLV0001, SLV0002...)
- ✅ Auto balance calculation

### Billing System
- ✅ Auto bill number generation
- ✅ Customer name, age, phone, address
- ✅ Dress type and measurements
- ✅ Booking & delivery dates
- ✅ Advance and final amount
- ✅ Auto balance calculation
- ✅ Printable invoice
- ✅ PDF download
- ✅ Shop branding on every invoice

---

## 🛠️ Customization

### Change Admin Password
Connect to database using any SQLite browser (DB Browser for SQLite):
```sql
-- Or reset via Python:
python3 -c "
from utils.auth import hash_password
print(hash_password('your-new-password'))
"
-- Then update the database:
-- UPDATE users SET password_hash='<output>' WHERE username='admin';
```

### Add Your Own Design Images
1. Log into admin: `/admin/login`
2. Go to Designs → Add Design
3. Select category, enter name, upload image
4. Mark as Featured to show on homepage

### Update Prices
1. Log into admin
2. Go to Prices → Add Price
3. Select category and enter new price

---

## 📞 Support

For technical assistance contact your developer, or refer to:
- Flask Documentation: https://flask.palletsprojects.com
- SQLite Documentation: https://sqlite.org/docs.html
- Hostinger Support: https://support.hostinger.in

---

*SLV Tailor Shop · KEMPANARASIMHAIAH · Magadi Taluk, Bangalore*
