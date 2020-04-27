from app import app, db
from app.models import User, Rooms
from app.fill_forms import LoginForm, RegistrationForm, JoinForm, HostForm
from flask import render_template, flash, request, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse


@app.route('/',methods = ['GET','POST'])
@login_required
def index():
	join_form = JoinForm()
	if join_form.validate_on_submit():
		roomtemp = Rooms.query.filter_by(roomname = join_form.room_name.data).first()
		if roomtemp is not None:
			return "Congrats you have joined room :" + join_form.room_name.data
		else :
			flash("Invalid room name entered")
			return redirect(url_for('index'))
	host_form = HostForm(prefix = "host_form")
	if host_form.validate_on_submit():
		roomtemp = Rooms.query.filter_by(roomname = host_form.room_name.data).first()
		if roomtemp is None:
			roomh = Rooms(roomname = host_form.room_name.data, hostname = current_user.username)
			db.session.add(roomh)
			db.session.commit()
			flash('Congrats You host a room now')
			return "Welcome to room : " + host_form.room_name.data
		else:
			flash('Room Already exist')
			return redirect(url_for('index'))
	return render_template("index.html", title='Home Page',join_form = join_form, host_form = host_form)

@app.route('/login', methods = ['GET','POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username = form.username.data).first()
		if user is None or not user.check_password(form.password.data):
			print("USER = ",user is None)
			flash('Invalid username or password')
			return redirect(url_for('login'))
		login_user(user, remember = form.remember_me.data)
		next_page = request.args.get('next')
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('index')
		return redirect(next_page)
	return render_template('login.html', title  = 'Login',form  = form)

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))

@app.route('/register',methods = ['GET','POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(username = form.username.data)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('Congrats, you are now a register user!')
		return redirect(url_for('login'))
	return render_template('register.html',title = 'Register' , form = form)



if __name__ == '__main__':
	app.run(debug = True)