from flask import Flask, request, redirect, url_for, render_template_string, session
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ---------- DATABASE SETUP ----------
def get_db():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------- STYLE ----------
base_style = """
<style>
body {
    font-family: Papyrus, fantasy;
    background: #f4f6f8;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
}
.card {
    background: #accbff;
    padding: 25px;
    border-radius: 10px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    width: 300px;
    text-align: center;
}
input {
    width: 90%;
    padding: 8px;
    margin: 8px 0;
}
button {
    padding: 10px;
    width: 60%;
    background: #4188ff;
    color: white;
    border: none;
}
.error {
    color: red;
}
</style>
"""

login_page = f"""{base_style}
<div class="card">
<h2>Login</h2>
<form method="POST">
  <input name="username" placeholder="Username"><br>
  <input name="password" type="password" placeholder="Password"><br>
  <label for="favorite_animal">Choose your favorite animal:</label>
  <select name="favorite_animal" id="favorite_animal">
    <option value="cat">Cat</option>
    <option value="dog">Dog</option>
    <option value="hyena">Hyena</option>
    <option value="horse">Horse</option>
  </select>
  <button type="submit">Login</button>
</form>
<a href="/register">Create an account</a>
<p class="error">{{{{ error }}}}</p>
</div>
"""

register_page = f"""{base_style}
<div class="card">
<h2>Register</h2>
<form method="POST">
  <input name="username" placeholder="Username"><br>
  <input name="password" type="password" placeholder="Password"><br>
   <select name="favorite_animal" id="favorite_animal">
    <option value="cat">Cat</option>
    <option value="dog">Dog</option>
    <option value="hyena">Hyena</option>
    <option value="horse">Horse</option>
  </select>
  <button type="submit">Sign Up</button>
</form>
<a href="/">Back to login</a>
<p class="error">{{{{ error }}}}</p>
</div>
"""

favorite_animal_page = f"""{base_style}
<div class="card">
<h2>Welcome to AniVision!</h2>
<h3>Welcome, {{{{ username }}}}!</h3>
<p>Here is a vision board of your favorite animal1</p>
<a href="/logout"><button>Logout</button></a>
</div>
"""

# ---------- ROUTES ----------
@app.route("/", methods=["GET", "POST"])
def login():
    error = ""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        ).fetchone()
        conn.close()

        if user:
            session["user"] = username
            return redirect(url_for("fav_anim"))
        else:
            error = "Incorrect username or password"

        if favorite_animal == "hyena":
            <img src= "hyena.jpg" alt="Hyena">   ###left off here
    return render_template_string(login_page, error=error)

@app.route("/register", methods=["GET", "POST"])
def register():
    error = ""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if not username or not password:
            error = "Fields cannot be empty"
        else:
            try:
                conn = get_db()
                conn.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, password)
                )
                conn.commit()
                conn.close()
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                error = "Username already exists"

    return render_template_string(register_page, error=error)

@app.route("/favorite_animal")
def fav_anim():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template_string(favorite_animal_page, username=session["user"])

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

# ---------- RUN ----------
app.run(host="0.0.0.0", port=5000)