import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session
from supabase import create_client, Client
from google import genai
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'hv_global_elite_key'

# --- 1. PRO CONNECTIONS ---
# Replace these with your actual Supabase details from Step 1
SUPABASE_URL = "YOUR_SUPABASE_URL"
SUPABASE_KEY = "YOUR_SUPABASE_ANON_KEY"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Gemini AI Setup
client = genai.Client(api_key="YOUR_GEMINI_API_KEY")

# --- 2. THE ROUTES ---
@app.route('/')
def home():
    if 'user' not in session: return redirect(url_for('login'))
    # Fetch posts from Supabase
    response = supabase.table("posts").select("*").order("created_at", desc=True).execute()
    return render_template('index.html', feed_posts=response.data, current_user=session['user']['username'])

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        username = request.form.get('username')
        
        # Create user in Supabase Auth
        user = supabase.auth.sign_up({"email": email, "password": password})
        if user:
            # Store profile info in a custom table
            supabase.table("profiles").insert({"id": user.user.id, "username": username}).execute()
            session['user'] = {"id": user.user.id, "username": username}
            return redirect(url_for('home'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        res = supabase.auth.sign_in_with_password({"email": request.form.get('email'), "password": request.form.get('password')})
        if res.user:
            profile = supabase.table("profiles").select("username").eq("id", res.user.id).single().execute()
            session['user'] = {"id": res.user.id, "username": profile.data['username']}
            return redirect(url_for('home'))
    return render_template('login.html')

# Vercel needs this to run
if __name__ == '__main__':
    app.run()
  
