from flask import Flask, render_template, request, flash, redirect, url_for
import mysql.connector

# Connect to MySQL (ensure MySQL server is running)
db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="attendify"
)

db_cursor = db_connection.cursor()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'it is what it is manas'

@app.route('/', methods=['GET','POST'] )
def index():
    if request.method == 'POST':
        email = request.form.get('username')
        password = request.form.get('password')
        try:
            db_cursor.execute("SELECT * FROM teachers WHERE Email = '"+email+"';")
            val = db_cursor.fetchall()
            if (email==val[0][2] and password==val[0][3]):
                flash('Logged in successfully!', category='success')
                return redirect(url_for('dashboard'))
        except:
            flash('lol', category='success')
        
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == "__main__":
    app.run(debug=True)