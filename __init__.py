from flask import Flask, render_template, request, flash, redirect, url_for, session, logging
import pymysql
from data import Articles
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from flask.ext.sqlalchemy import SQLAlchemy
import pymysql.cursors
Articles = Articles()


app = Flask(__name__)
# this userpass assumes you did not create a password for your database
# and the database username is the default, 'root'
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='',
                             db='pytest',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
#tesst connect
@app.route('/test')
def testdb():
    if db.session.query('1').from_statement('SELECT 1').all():
        return 'It works.'
    else:
        return 'Something is broken.'
@app.route('/')
def index():
    return render_template("home.html")

#about
@app.route('/about')
def about():
	return render_template("about.html")
#Articles
@app.route('/articles')
def articles():
	return render_template("articles.html", articles = Articles)
#article
@app.route('/article/<string:id>')
def article(id):
	return render_template("article.html" ,id = id )
#registerform

class RegisterForm(Form):
	name = StringField('Name', [validators.Length(min = 1, max = 50 )])
	username = StringField('Username', [validators.Length(min = 1, max = 50 )])
	email = StringField('Email', [validators.Length(min = 1, max = 50),validators.email()])
	password = PasswordField('Password', 
		[validators.Length(min = 6, max = 20),
		validators.DataRequired(),
		validators.EqualTo('confirm', message = "Password do not match")

		])
	confirm = PasswordField('Confirm Password')
@app.route('/register',methods = ['GET', 'POST'])
def register():
	form =RegisterForm(request.form)
	if request.method == 'POST' and form.validate():
		name = form.name.data
		email = form.email.data
		username = form.username.data
		password = sha256_crypt.encrypt(str(form.password.data))
		#create
		with connection.cursor() as cursor:
			cursor.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email,username,password))
			connection.commit()
		connection.close()
		flash('register succsess','success')
		return redirect(url_for("index"))
	return render_template('register.html',form = form)
  	

#logins
@app.route("/login", methods = ['GET', 'POST'])
def login():
	if request.method =='POST':
		username = request.form['username']
		password_confirm = request.form['password']

		#get by ussername
		with connection.cursor() as cursor:
			result = cursor.execute("SELECT * FROM users WHERE username = %s", username)
			if result > 0:
				data = cursor.fetchone()
				password = data['password']
				#compe
				if sha256_crypt.verify(password_confirm, password):
					#pass
					session['logged_in'] = True
					session['username']  = username
					flash('login success', 'success')
					return redirect(url_for('dashboard'))
				else:
					error = 'Password fail'
					return  render_template("login.html", error = error)
				connection.close()
			else:
				error = 'Username not found'
				return  render_template("login.html", error = error)

	return render_template("login.html")
@app.route("/dashboard")
def dashboard():
	return render_template('dashboard.html')


if __name__ == "__main__":
	app.secret_key = 'secret123'
	app.run(debug =True)

