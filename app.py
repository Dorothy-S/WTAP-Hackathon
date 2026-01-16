# Remove the scaffold fix - it's not needed for Flask 3.x
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'  # Change this in production!

# File to store user data
USERS_FILE = 'users.json'

def load_users():
    """Load users from JSON file"""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    """Save users to JSON file"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

@app.route('/')
def home():
    """Render the main page"""
    return render_template('try.html')

@app.route('/mentors/<specialty>')
def mentors(specialty):
    """Render mentors page for a specialty"""
    if 'user' not in session:
        # Store the specialty they wanted to view
        session['redirect_after_login'] = f'/mentors/{specialty}'
        return redirect(url_for('login'))
    
    # Map specialty to title
    specialty_titles = {
        'cybersecurity': 'Cybersecurity',
        'software-dev': 'Software Development', 
        'data-science': 'Data Science'
    }
    
    title = specialty_titles.get(specialty, specialty)
    return render_template('try.html', specialty=title, user=session['user'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        users = load_users()
        
        if username in users and check_password_hash(users[username]['password'], password):
            # Login successful
            session['user'] = users[username]
            
            # Redirect to where they wanted to go, or home
            redirect_to = session.pop('redirect_after_login', url_for('home'))
            return redirect(redirect_to)
        else:
            error = 'Invalid username or password'
            return render_template('login.html', error=error)
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle new user registration"""
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        user_type = request.form.get('user_type', 'mentee')
        
        # Validation
        if not all([name, username, password, confirm_password]):
            error = 'All fields are required'
            return render_template('register.html', error=error)
        
        if password != confirm_password:
            error = 'Passwords do not match'
            return render_template('register.html', error=error)
        
        users = load_users()
        
        if username in users:
            error = 'Username already exists'
            return render_template('register.html', error=error)
        
        # Create new user
        users[username] = {
            'name': name,
            'username': username,
            'password': generate_password_hash(password),
            'type': user_type  # 'mentor' or 'mentee'
        }
        
        save_users(users)
        
        # Auto-login after registration
        session['user'] = users[username]
        return redirect(url_for('home'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """Log out the user"""
    session.pop('user', None)
    return redirect(url_for('home'))

@app.route('/profile')
def profile():
    """Show user profile"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Profile - Tech Mentor</title>
        <style>
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }}
            .profile-container {{
                background: white;
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
                max-width: 500px;
                width: 100%;
            }}
            h1 {{ color: #2d3436; margin-bottom: 30px; text-align: center; }}
            .info {{ margin-bottom: 20px; }}
            .label {{ font-weight: 600; color: #636e72; }}
            .value {{ color: #2d3436; margin-top: 5px; }}
            .links {{ margin-top: 30px; text-align: center; }}
            .links a {{
                display: inline-block;
                margin: 0 10px;
                padding: 10px 20px;
                background: #6c5ce7;
                color: white;
                text-decoration: none;
                border-radius: 8px;
                transition: all 0.3s;
            }}
            .links a:hover {{ background: #5a4fcf; }}
        </style>
    </head>
    <body>
        <div class="profile-container">
            <h1>Profile</h1>
            <div class="info">
                <div class="label">Name:</div>
                <div class="value">{session['user']['name']}</div>
            </div>
            <div class="info">
                <div class="label">Username:</div>
                <div class="value">{session['user']['username']}</div>
            </div>
            <div class="info">
                <div class="label">Account Type:</div>
                <div class="value">{session['user']['type'].title()}</div>
            </div>
            <div class="links">
                <a href="/">Back to Home</a>
                <a href="/logout">Logout</a>
            </div>
        </div>
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(debug=True, port=5000)