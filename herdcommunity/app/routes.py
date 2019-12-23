# local imports
from app import app, db
from app.forms import SignupForm, LoginForm
from app.models import User, Destination, Association

# library imports
import copy
from flask import render_template, request, redirect, url_for
from flask_login import current_user, login_user, login_required

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/list')
@login_required
def list():
    # NOTE: Temporarily cutting off 1st 3 elements of array bc there are items
        # that it won't let me remove from DB
    destinations = Destination.query.all()[3:]
    context = []
    for d in destinations:
        tmp = {'num_visits_by_current_user': 0, 'friends_visited': [], 'num_visits_by_friends': 0}
        for assoc in d.users:
            if assoc.user.user_id == current_user.user_id:
                tmp['num_visits_by_current_user'] = assoc.num_visits
            if assoc.user in current_user.friends:
                tmp['friends_visited'].append(assoc.user)
                tmp['num_visits_by_friends'] += assoc.num_visits
        context.append(tmp)

    return render_template('list.html', destinations=enumerate(destinations), context=context)

# TODO: maybe fold this functionality into /list instead of redirecting? (might avoid annoying scrolling to top)
@app.route('/change_num_visits')
def change_num_visits():
    # find needed association between user and destination
    dest_index = int(request.args.get('dest_index'))
    value = int(request.args.get('value'))
    dest = Destination.query.all()[3:][dest_index]
    assoc_found = False
    for assoc in dest.users:
        if assoc.user.user_id == current_user.user_id:
            # update nunmber of visits
            assoc.num_visits = max(assoc.num_visits + value, 0) # ensure value can't go below 0
            assoc_found = True
            break
            
    # if no association exists, must be created
    if not assoc_found:
        new_assoc = Association(num_visits=max(value, 0))
        new_assoc.user = current_user
        dest.users.append(new_assoc)
        dest.num_visits = max(dest.num_visits + value, 0)
        db.session.add(new_assoc)

    db.session.commit()
    return redirect(url_for('list'))

def check_user_exists(user_email):
    users = User.query.all()
    for u in users:
        if u.email and u.email.lower() == user_email:
            return True
    return False

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # if user is already logged in
        if current_user.is_authenticated and current_user.email == form.email.data:
            print('User {} is already logged in. Navigating to destinations list'.format(current_user))
            return redirect(url_for('list'))

        # log in user, if they exist
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            print('Could not find user with email {}'.format(form.email.data))
            # TODO: flash error message
            return redirect(url_for('login'))
        login_user(user, remember=True)
        
        # redirect user either to list or to previous page
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('list')
        return redirect(next_page)

    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        # TODO: if user already exists, send them straight to list
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None:
            print('User {} already exists. Logging them in'.format(user))
            login_user(user, remember=True)
            return redirect(url_for('list'))
        
        # register user in database
        new_user = User(name=form.name.data, email=form.email.data)
        db.session.add(new_user)

        print('registering user: {}'.format(new_user))
        db.session.commit()

        # after user signs up, send them to page to select friends

    return render_template('signup.html', form=form)

@app.route('/add_friends', methods=['GET', 'POST'])
def add_friends():
    users = User.query.all()
    users = filter(lambda u: u.user_id != current_user.user_id, users)

    # update friends if form submitted
    if request.method == 'POST':
        friend_ids = request.form.getlist('friend_checkbox')
        for friend_id in friend_ids:
            friend = User.query.get(int(friend_id))
            print('adding friend ', friend_id)
            current_user.add_friend(friend)

        # TODO: allow unfriending people?
        
        db.session.commit()

        # redirect to list
        return redirect(url_for('list'))

    return render_template('add_friends.html', users=users, current_friends=current_user.friends)