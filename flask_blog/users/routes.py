from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from flask_blog import db, bcrypt
from flask_blog.models import User, Post
from flask_blog.users.forms import(RegistrationForm, LoginForm, UpdateAccountForm, 
                                   RequestResetForm, ResetPasswordForm)
from flask_blog.users.utils import save_picture, send_reset_email


users = Blueprint('users', __name__)



@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, 
            email=form.email.data, 
            password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Acoount created for {form.username.data}!, you can login now', 
            'success')
        return redirect(url_for('users.login'))

    return render_template('register.html', title='register', form=form)

# login page


@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            next_page = request.args.get('next')
            login_user(user, remember=form.remember.data)
            print(next_page)
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('login unsuccessful pls check your email and password')
    return render_template('login.html', title='login', form=form)

# logout function


@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))


# user account page
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return (posts, user)

@users.route('/account/<string:username>', methods=['GET', 'POST'])
@login_required
def account(username):
    posts, user = user_posts(username)
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        db.session.commit()
        flash('your account has been updated!', 'success')
        return redirect(url_for('users.account', 
            username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static',
     filename='profile_pics/' + user.image_file)
    return render_template('account.html', title='account',
         image_file=image_file, form=form, posts=posts, user=user)



@users.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instruction to reset the password', 'warning')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset Password',
         form=form)

@users.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if not user:
        flask('Token is invlaid or expired', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f'Your password has been reset successfully', 
            'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='reset_password',
         form=form)