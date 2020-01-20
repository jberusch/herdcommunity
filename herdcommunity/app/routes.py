# local imports
from app import app, db
from app.email import send_email
from app.forms import SignupForm, LoginForm, SearchForm
from app.models import User, Destination, Association
from app.helpers import ulog, delete_log

# library imports
import os
from random import shuffle
from operator import attrgetter
from werkzeug.urls import url_parse
from flask_login import current_user, login_user, login_required, logout_user
from flask import render_template, request, redirect, url_for, jsonify, flash

def check_dest_visited_by_user(user_dests, target_dest):
    for assoc in user_dests:
        if target_dest == assoc.destination and assoc.num_visits > 0:
            return True
    return False

@app.route('/')
@app.route('/index')
def index():
    recommendations = []
    if current_user.is_authenticated:
        dests = Destination.query.filter_by(region=current_user.region).all()
        # randomly order destinations
        shuffle(dests)

        i = 0
        while i < len(dests) - 1:
            # recommend destination if some friends have visited
            for friend in current_user.friends:
                if len(recommendations) >= 3:
                    break
                if check_dest_visited_by_user(friend.destinations, dests[i]) \
                        and not check_dest_visited_by_user(current_user.destinations, dests[i]):
                    recommendations.append(dests[i])
                    i += 1
                    continue
            i += 1

    print(recommendations)
    return render_template('index.html', recommendations=recommendations)

@app.route('/list', methods=['GET', 'POST'])
@login_required
def list():
    form = SearchForm()
    page_number = request.args.get('page', 1, type=int)
    region = request.args.get('region', current_user.region)
    
    # update user's region if they selected a different one
    if region != current_user.region:
        current_user.region = region
        db.session.commit()
    
    if form.validate_on_submit():
        # user has searched for destination
        search_term = '%{}%'.format(form.dq.data)
        # get destinations by search_term
        destinations_paginated = Destination.query.filter_by(region=region).filter(Destination.name.ilike(search_term)).order_by(Destination.num_visits.desc()).order_by(Destination.destination_id).paginate(page_number, app.config['DESTINATIONS_PER_PAGE'], False)

    else:
        # user has accessed page normally
        # get destinations by region
        destinations_paginated = Destination.query.filter_by(region=region).order_by(Destination.num_visits.desc()).order_by(Destination.destination_id).paginate(page_number, app.config['DESTINATIONS_PER_PAGE'], False)
        
    # create next and previous URLs for pagination
    next_url = url_for('list', page=destinations_paginated.next_num, region=region) \
        if destinations_paginated.has_next else None
    prev_url = url_for('list', page=destinations_paginated.prev_num, region=region) \
        if destinations_paginated.has_prev else None

    # compile visit numbers for each destination
    destinations = destinations_paginated.items
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

    return render_template('list.html', destinations=enumerate(destinations), context=context, region=region, current_user=current_user,
                            next_url=next_url, prev_url=prev_url, page_number=page_number, num_dests=app.config['DESTINATIONS_PER_PAGE'], form=form)

# change the number of times current user has visited a destination
# triggered by +/- buttons in list.html
@app.route('/change_num_visits', methods=['POST'])
def change_num_visits():
    destination_id = int(request.form['destination_id'])
    value = int(request.form['value'])

    dest = Destination.query.get(destination_id)
    # find needed association between user and destination
    assoc_found = False
    new_num_visits = 1
    for assoc in dest.users:
        if assoc.user.user_id == current_user.user_id:
            # update number of visits
            assoc.num_visits = max(assoc.num_visits + value, 0) # ensure value can't go below 0
            # get value to give back to webpage
            new_num_visits = assoc.num_visits
            assoc_found = True

            # if user decreases visits to 0, remove the association entirely
            if new_num_visits == 0:
                db.session.delete(assoc)

            break
            
    # if no association exists, must be created
    if not assoc_found:
        new_assoc = Association(num_visits=max(value, 0))
        new_assoc.user = current_user
        dest.users.append(new_assoc)
        db.session.add(new_assoc)
    
    # update overall number of visits for destination
    dest.num_visits = max(dest.num_visits + value, 0)

    db.session.commit()
    return jsonify({'new_num_visits': new_num_visits})

@app.route('/delete_destination', methods=['POST'])
def delete_destination():
    destination_id = int(request.form['destination_id'])
    dest = Destination.query.get(destination_id)
    print('Deleting', dest)

    # delete any associations destination is in
    for assoc in dest.users:
        db.session.delete(assoc)

    # delete destination itself
    db.session.delete(dest)
    db.session.commit()
    ulog('delete_destination -> user {} deleting destination {}'.format(current_user.username, dest))
    return {}

@app.route('/user/<username>')
@login_required
def user(username):
    # log usage
    ulog('user -> page access for username {}'.format(username))

    user = User.query.filter_by(username=username).first_or_404()
    destinations = sorted(user.destinations, key=attrgetter('num_visits'), reverse=True)
    
    return render_template('user.html', user=user, destinations=destinations)

def check_user_exists(username):
    users = User.query.all()
    for u in users:
        if u.username and u.username.lower() == username:
            return True
    return False

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # if user is already logged in
        if current_user.is_authenticated and current_user.username == form.username.data:
            print('User {} is already logged in. Navigating to destinations list'.format(current_user))
            return redirect(url_for('list'))

        # log in user, if they exist
        user = User.query.filter_by(username=form.username.data).first()
        if user is None:
            msg = 'Could not find user with username {}'.format(form.username.data)            
            print(msg)
            flash(msg)
            return redirect(url_for('login'))
        login_user(user, remember=True)

        # log usage
        print('login by user {}'.format(user))
        
        # redirect user either to list or to previous page
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('list')
        return redirect(next_page)

    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # print('-------------\nemail:', app.config['MAIL_PASSWORD'])
    # print(os.environ.get('MAIL_PASSWORD'))
    # print(os.getkey())

    form = SignupForm()
    if form.validate_on_submit():

        # TODO: if user already exists, send them straight to list
        print('Attempting to sign in user with information: ', form.username.data, form.email.data, form.name.data)

        user = User.query.filter_by(username=form.username.data).first()
        if user is not None:
            msg = 'There is already an account with the username {}'.format(form.username.data)            
            print(msg)
            flash(msg)
            return redirect(url_for('signup'))

        user = User.query.filter_by(email=form.email.data).first()
        if user is not None:
            msg = 'There is already an account with the email {}'.format(form.email.data)
            print(msg)
            flash(msg)
            return redirect(url_for('signup'))
        
        # register user in database
        new_user = User(username=form.username.data, name=form.name.data, email=form.email.data, friends=[], destinations=[])
        print('registering user: {}'.format(new_user))
        db.session.add(new_user)
        db.session.commit()
        # log in new user
        login_user(new_user, remember=True)

        # notify admins that new user signed up
            # NOTE: NOT WORKING
            # send_email('New User Signup', app.config['ADMINS'][0], ['asroth43@gmail.com', 'joeberusch@gmail.com'], '', '<h2>New User Signup</h2>')

        # after user signs up, send them to page to select friends
        return redirect(url_for('add_friends'))

    return render_template('signup.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/add_friends', methods=['GET', 'POST'])
@login_required
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

    return render_template('add_friends.html', users=users, 
                            current_friends=current_user.friends if current_user.friends else [])