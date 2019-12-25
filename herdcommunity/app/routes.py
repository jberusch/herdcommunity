# local imports
from app import app, db
from app.forms import SignupForm, LoginForm
from app.models import User, Destination, Association

# library imports
from flask import render_template, request, redirect, url_for, jsonify
from flask_login import current_user, login_user, login_required

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/list')
@login_required
def list():
    page_number = request.args.get('page', 1, type=int)
    region = request.args.get('region', 'Nashville')
    destinations_paginated = Destination.query.filter_by(region=region).order_by(Destination.num_visits.desc()).paginate(page_number, app.config['DESTINATIONS_PER_PAGE'], False)
    
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
                print(assoc.user.username)
                tmp['num_visits_by_friends'] += assoc.num_visits
        context.append(tmp)

    # create next and previous URLs for pagination
    next_url = url_for('list', page=destinations_paginated.next_num) \
        if destinations_paginated.has_next else None
    prev_url = url_for('list', page=destinations_paginated.prev_num) \
        if destinations_paginated.has_prev else None

    return render_template('list.html', destinations=enumerate(destinations), context=context,
                            next_url=next_url, prev_url=prev_url, page_number=page_number, num_dests=app.config['DESTINATIONS_PER_PAGE'])

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

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    
    return render_template('user.html', user=user, destinations=user.destinations)

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
            print('Could not find user with username {}'.format(form.username.data))
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
        print('Attempting to sign in user with information: ', form.username.data, form.email.data, form.name.data)

        user = User.query.filter_by(username=form.username.data).first()
        if user is not None:
            print('User {} already exists. Logging them in'.format(user))
            login_user(user, remember=True)
            return redirect(url_for('list'))
        
        # register user in database
        # TODO: prevent duplicate emails
        new_user = User(username=form.username.data, name=form.name.data, email=form.email.data, friends=[], destinations=[])
        db.session.add(new_user)

        print('registering user: {}'.format(new_user))
        db.session.commit()

        # after user signs up, send them to page to select friends
        return redirect(url_for('add_friends'))

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

    return render_template('add_friends.html', users=users, 
                            current_friends=current_user.friends if current_user.friends else [])