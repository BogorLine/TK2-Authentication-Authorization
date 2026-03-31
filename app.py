from flask import Flask, redirect, request, session, render_template_string, url_for
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
ANGGOTA_KELOMPOK = ["akhtareijaz@gmail.com", ""]

# frontend
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Authentication & Authorization</title>
    <style>
        body { font-family: Arial, sans-serif; transition: background-color 0.5s; padding: 20px;}
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
    </style>
</head>
<body id="halaman-utama">
    <div class="container">
        <h1>Biodata Kelompok BogorLine</h1>
        <ul>
            <li>Akhtar Eijaz Putranto (2406495571)</li>
            <li>Anya Aleena Wardhany (2406401773)</li>
            <li>Azzahra Anjelika Borselano (2406419663)</li>
            <li>Jessica Tandra (2406355445)</li>
            <li>Petrus Wermasaubun (2406344542)</li>
        </ul>
        <hr>
        
        {% if user %}
            <h3>Halo, {{ user['email'] }}!</h3>
            <p>Status Akses: <strong>{{ role }}</strong></p>
            
            {% if role == 'Admin' %}
                <div style="background: #f0f8ff; padding: 15px; border-radius: 5px; margin-bottom: 15px;">
                    <h4>⚙️ Panel Admin (Authorization Berhasil)</h4>
                    <label>Ubah Warna Background Web:</label>
                    <input type="color" id="warnaBackground" onchange="ubahWarna()">
                </div>
                
                <script>
                    // JavaScript sederhana untuk manipulasi DOM (mengubah warna)
                    function ubahWarna() {
                        let warnaDipilih = document.getElementById("warnaBackground").value;
                        document.getElementById("halaman-utama").style.backgroundColor = warnaDipilih;
                    }
                </script>
            {% else %}
                <p style="color: gray;"><i>Kamu login sebagai Guest. Hanya anggota kelompok yang dapat mengubah tampilan web.</i></p>
            {% endif %}
            
            <a href="/logout"><button style="background: red; color: white; border: none; padding: 10px;">Logout</button></a>
        
        {% else %}
            <p>Silakan login untuk melihat fitur khusus anggota kelompok.</p>
            <a href="/login"><button style="background: blue; color: white; border: none; padding: 10px;">Login with Google</button></a>
        {% endif %}
    </div>
</body>
</html>
"""

# backend
@app.route("/")
def index():
    user = session.get('user')
    role = "Guest"
    
    if user and user['email'] in ANGGOTA_KELOMPOK:
        role = "Admin"
            
    return render_template_string(HTML_PAGE, user=user, role=role)

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