from flask import Flask, request, redirect, url_for, render_template_string, session
import sqlite3
import bcrypt
import re

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ---------- DATABASE SETUP ----------
def is_valid_password(password):
    if (re.search(r"[A-Z]", password) and   # uppercase
        re.search(r"[a-z]", password) and   # lowercase
        re.search(r"[0-9]", password) and   # number
        re.search(r"[^A-Za-z0-9]", password)):  # special char
        return True
    return False

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

def get_animalsdb():
    conn = sqlite3.connect("animals.db")
    conn.row_factory = sqlite3.Row
    return conn


def init_animalsdb():
    conn = get_animalsdb()
    conn.execute("DROP TABLE IF EXISTS animals")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS animals (
            animal_name TEXT PRIMARY KEY, 
            habitat TEXT,
            food TEXT,
            image TEXT
        )
    """)

    conn.execute("""
        INSERT INTO animals (animal_name, habitat, food, image)
        VALUES ("Hyena", "Savanna", "Meat", "image of hyena") 
    """) #add file for images and rename
    conn.commit()
    conn.close()


init_db()
init_animalsdb()


# ---------- STYLE ----------
base_style = """
<style>
body {
    font-family: Papyrus, fantasy;
    background: #f4f6f8;
    display: flex;
    justify-content: center;
    align-items: flex-start; #center
    height: 100vh;
    padding: 20px;
    box-sizing: border-box;
}
.card {
    background: #accbff;
    padding: 25px;
    border-radius: 10px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    width: 300px;
    text-align: center;
    margin-bottom: 20px; 
}

}
.main-card-wrapper {
    width; 90%;
    max-width: 1200px;
    display: flex;
    flex-direction: column;
    align-items: center;
}
.animal-container {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 20px;
    width: 100%;
    margin-top: 20px;
    margin-bottom: 20px;
}
.animal-card {
    flex: 0 0 auto;
    wifth: 280px;
    padding: 15px;
    box-sizing: border-box;
}
.animal-card img {
    max-width: 100%;
    height: auto;
    border-radius: 5px;
    margin-bottom: 10px;
}
input {
    width: 90%;
    padding: 8px;
    margin: 8px 0;
    border: 1px solid #ccc;
    border-radius: 4px;
}
button {
    padding: 10px;
    width: 60%;
    background: #4188ff;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    marin: 5px;
}
button:hover {
    background: #2a6edc;
}
.error {
    color: red;
    margin-top: 10px;
}
</style>
"""

login_page = f"""{base_style}
<div class="card">
<h2>Login</h2>
<form method="POST">
  <input name="username" placeholder="Username"><br>
  <input name="password" type="password" placeholder="Password"><br>
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
  <button type="submit">Sign Up</button>
</form>
<a href="/">Back to login</a>
<p class="error">{{{{ error }}}}</p>
</div>
"""

main_animal_page = f"""{base_style}
<div class="main-card-wrapper card">
    <h2>AniVision</h2>
    <h3>Welcome, {{{{ username }}}}!</h3>
    <p>Contribute to our animal loving community today!</p>
    <div class="animal-container">
        {{% for animal in animals %}}
        <div class="animal-card card">
            <img src="{{{{image_file}}}}" alt="{{{{animals.animal_name}}}}">
            <h4>{{{{animal_name}}}}</h4>
            <p><strong>Habitat</strong> {{{{animals.habitat}}}}</p>
            <p><strong>Food</strong> {{{{animals.food}}}}</p>
        </div>
        {{% endfor %}} 
    </div>
    <div style="margin-top: 20px;">
    <a href="/additional_information"><button>Add Animal Info</button></a>
    <a href="/logout"><button>Logout</button></a>
    </div>
</div>
"""   

additional_information_page = f"""{base_style}
<div class="card">
<h2>Add More Information</h2>
<form method="POST">
    <input type="text" name="animal_name" placeholder="Animal Name" required><br>
    <input type="text" name="habitat" placeholder="Habitat" required><br>
    <input type="food" name="food" placeholder="Food" required><br>
    <input type="file" name="image_file" accept="image/*" required><br>
    <button type="submit">Add Animal</button>
</form>
<a href="/main_animal">Back to Animals</a>
<p class="error">{{{{ error }}}}</p>
<a href="logout"><button>Logout</button></a>
</div>
"""

# ---------- ROUTES ----------
@app.route("/", methods=["GET", "POST"])
def login():
    error = ""
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        ).fetchone()
        conn.close()

        # user['password'] is bytes in SQLite; check with bcrypt
        if user and bcrypt.checkpw(password.encode("utf-8"), user["password"]):
            session["user"] = username
            return redirect(url_for("main_animal"))
        else:
            error = "Incorrect username or password"

    return render_template_string(login_page, error=error)




@app.route("/register", methods=["GET", "POST"])
def register():
    error = ""
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        if not username or not password:
            error = "Fields cannot be empty"
        elif not is_valid_password(password):
            error = "Password must include uppercase, lowercase, number, and special character"
        else:
            conn = get_db()
            try:
                # Hash password with bcrypt
                hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

                conn.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, hashed_pw)
                )
                conn.commit()

                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                conn.rollback()
                error = "Username already exists"
            except Exception:
                conn.rollback()
                error = "Unexpected error during registration"
            finally:
                conn.close()

    return render_template_string(register_page, error=error)

@app.route("/main_animal")
def main_animal(): 
    #main page with initialized animal
    error = ""
    if "user" not in session:
        return redirect(url_for("login"))
    
    conn = get_animalsdb()
    animals = conn.execute("SELECT * FROM animals").fetchall()
    conn.close()

    
    # conn = get_animalsdb()
    # if request.method == "POST":
    #     animal_name = request.form.get("animal_name")
    #     habitat = request.form.get("habitat")
    #     food = requiest.form.get("food")
    #     image_file = request.form.get("image_file")

    #     conn = get_animalsdb()
    #     animal = conn.execute(
    #         "SELECT * FROM animals WHERE animal_name=?",
    #         (animal_name, habitat, food, image_file,
    #     ).fetchall()
    #     conn.close()

    # else: 
    #     animal_name = request.form.get("animal_name")
    #     habitat = request.form.get("habitat")
    #     food = request.form.get("food")
    #     image_file = request.form.get("image_file")
    #     conn.execute(
    #         "INSERT INTO animals (animal_name, habitat, food, image) VALUES (?, ?, ?, ?)", 
    #         (animal_name, habitat, food, image_file)
    #     )
    #     conn.commit()
    #     conn.close()

    return render_template_string(main_animal_page, username=session["user"], animals=animals)

@app.route("/additional_information", methods=["GET", "POST"])
#@app.route("/additional_information")
def additional_information():
    if "user" not in session:
        return redirect(url_for("login"))

    error = ""
    if request.method == "POST":
        animal_name = request.form.get("animal_name")
        habitat = request.form.get("habitat")
        food = request.form.get("food")
        image_file = request.form.get("image_file")

        if not animal_name or not habitat or not food or not food or not image_file:
            error = "All fields are required"
        else: 
            conn = get_animalsdb()
            try: 
                conn.execute(
                    "INSERT INTO animals (animal_name, habitat, food, image) VALUES (?, ?, ?, ?)",
                    (animal_name, habitat, food, image_file)
                )
                conn.commit()
                return redirect(url_for("main_animal")) 
                #redirects main page after adding
            except sqlite3.IntegrityError:
                conn.rollback()
                error = "Animal with name already exists"
            # except Exception as e:
            #     conn.rollback()
            #     error = f"An error occured: {e}"
            finally:
                conn.close()

    return render_template_string(additional_information_page, username=session["user"], error=error)


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

# ---------- RUN ----------
app.run(host="0.0.0.0", port=5000)