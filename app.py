from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify   
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
from flask_migrate import Migrate
import daily_monthlyData
import filter_data
app = Flask(__name__)
app.secret_key = 'rwewerwf#3243@2d'  # Replace with your actual secret key

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    selected_options = db.Column(db.String(255))
    years = db.Column(db.Integer)
    params = db.Column(db.String(255))

# Initialize Database within Application Context
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password1 = request.form['password1']
        password2 = request.form['password2']
        if(len(username)<4):
            flash("Username must be greater than 3 characters", category="error")
        elif(password1!=password2):
            flash("Password doesn't match", category="error")
        elif(len(password1)<4):
            flash("Password must be atleast 4 characters", category="error")
        else:
            hashed_password = generate_password_hash(password1, method='pbkdf2:sha256')
            new_user = User(username=username, password_hash=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please login.', category="success")
            return redirect(url_for('index'))

    return render_template('register.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password_hash, password):
        session['user_id'] = user.id
        session['username'] = user.username
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid username or password')
        return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        df = pd.read_csv('./static/ind_nifty50list.csv')
        Company_Name = list(df['Company Name'])
        Symbol = list(df['Symbol'])
        company_list = []
        user = User.query.filter_by(username=session['username']).first()
        selected_options = user.selected_options or ""
        selected_options = selected_options.split(",")
        # print(selected_options)
        for i in range(len(Company_Name)):
            if Symbol[i] in selected_options:
                company_list.append([Company_Name[i], Symbol[i], 'checked'])
            else:   
                company_list.append([Company_Name[i], Symbol[i],''])
        # user.years = 1
        years = user.years or 1
        print(years)
        selected_options.remove('')
        data_frame = daily_monthlyData.store_stocks(selected_options,[years]*len(selected_options))
        htmlcode = daily_monthlyData.plot_to_html(data_frame)
        return render_template('welcome.html', username=session['username'],company_list=company_list,graphcode=htmlcode)
    else:
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('index'))
@app.route('/update_selection', methods=['POST'])
def update_selection():
    checkbox_id = request.form['checkbox_id']
    selected = request.form['selected'] == 'true'
    # Retrieve the current user
    user = User.query.filter_by(username=session['username']).first()

    # Update the selected state in the database
    selected_options = user.selected_options or ""
    selected_options_set = set(selected_options.split(','))
    if selected:
        selected_options_set.add(checkbox_id)
    else:
        selected_options_set.discard(checkbox_id)
    selected_options_set.discard('True')
    selected_options_set.discard('False')
    user.selected_options = ','.join(selected_options_set)
    db.session.commit()
    # print(user.selected_options)
    return 'OK'
@app.route('/process_input', methods=['POST'])
def process_input():
    user_input = request.form['selected_year']
    user = User.query.filter_by(username=session['username']).first()
    print(user_input)
    user.years = user_input
    db.session.commit()
    return "OK"
@app.route('/filter', methods=['GET','POST'])
def filter():
    if 'user_id' in session:
        df = pd.read_csv('./static/ind_nifty50list.csv')
        user = User.query.filter_by(username=session['username']).first()
        param = user.params or ""
        param_ls  = ['open_pr','close_pr','daily_inc','average','trades_per_vol']
        if param not in param_ls:
            param = 'open_pr'
        data = filter_data.filtered_data()
        table = filter_data.table_const(data)
        table_html = filter_data.table_to_html(table,param)
        return render_template('filter.html', username=session['username'],table_html=table_html,param=param)
    else:
        return redirect(url_for('index'))    
@app.route('/update_filter', methods=['POST'])
def update_filter():
    user = User.query.filter_by(username=session['username']).first()
    user.params = user.params or ""
    user.params = request.form['params']
    db.session.commit()
    return "OK"
if __name__ == '__main__':
    app.run(debug=True)