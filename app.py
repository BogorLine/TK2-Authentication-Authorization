from flask import Flask, redirect, request, session, render_template, url_for
import requests
import secrets
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = secrets.token_hex(16) 

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:5000/callback" 
AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
USER_INFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

# masukin email kalian!
ANGGOTA_KELOMPOK = ["akhtareijaz@gmail.com", "azzahraanjelikaborselano@gmail.com",]

# backend
@app.route("/")
def index():
    user = session.get('user')
    role = "Guest"
    
    if user and user['email'] in ANGGOTA_KELOMPOK:
        role = "Admin"
            
    return render_template("index.html", user=user, role=role)

@app.route("/login")
def login():
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile"
    }
    req_url = requests.Request('GET', AUTH_URL, params=params).prepare().url
    return redirect(req_url)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "Gagal login. Kode tidak ditemukan.", 400

    token_data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI
    }
    token_resp = requests.post(TOKEN_URL, data=token_data)
    access_token = token_resp.json().get("access_token")

    if not access_token:
        return "Gagal mendapatkan access token.", 400

    headers = {"Authorization": f"Bearer {access_token}"}
    user_resp = requests.get(USER_INFO_URL, headers=headers)
    
    session['user'] = user_resp.json()
    
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(port=5000, debug=True)