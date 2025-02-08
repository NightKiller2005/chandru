from flask import *
from flask_mail import Mail, Message
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import bcrypt
import os
import random 
import string 
from datetime import datetime, timedelta
from time import time


app = Flask(__name__)

app.secret_key = 'supersecretkey'  # Replace with your secret key

# Configuration for Flask-Mail
# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'flasklogin24@gmail.com'  # Update with your Gmail address
app.config['MAIL_PASSWORD'] = 'svms iwli mprg pnnz'  # Update with your Gmail password
app.config['MAIL_DEFAULT_SENDER'] = 'flasklogin24@gmail.com'  # Update with your Gmail address

mail = Mail(app)


# Connect to MongoDB Atlas
client = MongoClient('mongodb+srv://flaskuser17:8MOK8vPPRUh1VTMb@cluster0.uxkt8vq.mongodb.net/')
db = client['COTP']
users_collection = db['Users']

@app.route('/')
def index():
    return render_template('Index.html')


# Route to handle login
# Route to handle login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check if email and password match
        user = users_collection.find_one({'email': email, 'password': password})
        if user:
            # Generate OTP
            otp = str(random.randint(1000, 9999))

            # Store OTP in session
            session['otp'] = otp
            session['email'] = email

            # Send OTP via email
            msg = Message('Your OTP', recipients=[email])
            msg.body = f'Your OTP is {otp}'
            mail.send(msg)

            # Redirect to OTP verification page
            return redirect(url_for('otppage'))

        # If user not found or password doesn't match, show login page again with error message
        flash('Invalid email or password. Please try again.', 'error')
        return render_template('Login.html')

    return render_template('Login.html')




@app.route('/send_otp', methods=['GET', 'POST'])
def send_otp():
    if request.method == 'POST':
        email = session.get('email')  # Get email from session
        print("Email retrieved from session:", email)  # Debugging print statement
        otp = str(random.randint(1000, 9999))
        session['otp'] = otp

        msg = Message('Your OTP', recipients=[email])
        msg.body = f'Your OTP is {otp}'
        try:
            mail.send(msg)
            print("Email sent successfully!")  # Debugging print statement
        except Exception as e:
            print("Error sending email:", e)  # Debugging print statement

        return render_template('OTP.html')

    # Handle GET request (if any)
    return redirect(url_for('otppage'))  # Redirect to index or any other appropriate page



# Route to handle OTP verification
@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    user_otp = request.form['otp']
    generated_otp = session.get('otp')

    print("User OTP:", user_otp)  # Debugging print statement
    print("Generated OTP:", generated_otp)  # Debugging print statement

    if user_otp == generated_otp:
        flash('OTP verified successfully!', 'success')
        print("Redirecting to loggedin page...")  # Debugging print statement
        return redirect(url_for('loggedin'))
    else:
        flash('Invalid OTP, please try again.', 'danger')
        print("Redirecting to login page...")  # Debugging print statement
        return redirect(url_for('login'))



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    success = None
    server_error = None
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        # Create a dictionary to hold user data
        user_data = {
            'name': name,
            'email': email,
            'password': password
        }

        try:
            # Insert user data into the database
            users_collection.insert_one(user_data)
            print("User signed up successfully:", user_data)
            success = 'Account created successfully.'
        except DuplicateKeyError:
            error = 'User already exists!'
        except Exception as e:
            print("Server error:", e)
            server_error = 'Server error. Please try again later.'

    # Render signup form for GET requests and if there are any messages
    return render_template('Signup.html', error=error, success=success, server_error=server_error)




@app.route('/loggedin')
def loggedin():
    return 'You are logged in!'

@app.route('/otppage')
def otppage():
    return render_template('OTP.html')
if __name__ == '__main__':
    app.secret_key = 'your_secret_key'  # Required for flash messages
    app.run(debug=True)
