from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Note, Show
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from bs4 import BeautifulSoup
from . import db
from flask_login import login_required, login_user, logout_user, current_user

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('You\'ve been logged in', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Failed Password Attempt. Try again.', category='error')
        else:
            flash('User email does not exist', category='error')
    return render_template('login_page.html', user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()

        if user:
            flash('Account already exists with that email', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 characters.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(password1, method='sha512'))
            db.session.add(new_user)
            db.session.commit()
            user = User.query.filter_by(email=email).first()
            login_user(user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))
    elif request.method == 'GET':
        pass
    return render_template('sign_up.html', user=current_user)

@auth.route('/home', methods=['GET', 'POST'])
@login_required
def find_show():
    if request.method == 'POST':
        eps_num = request.form.get('epsNum').strip()
        show_name = request.form.get('showName')

        URL = "https://www.animefillerlist.com/shows/" + show_name.replace(' ', '-')

        page = requests.get(URL)
        soup = BeautifulSoup(page.content, "html.parser")
        results = soup.find(class_="EpisodeList")

        if isinstance(results, type(None)):
            flash('Show typed incorrectly or does not exist', category='error')
        else:
            total_episodes = len(results.find_all('td', class_ = 'Date'))
        if eps_num < 1 or total_episodes < eps_num:
            flash('That episode does not exists', category='error')
        
        canon_list = results.find_all(
            "td", string=lambda text: " canon" in text.lower()
        )
        filler_mixed_list = results.find_all(
            "td", string=lambda text: "filler" in text.lower()
        )

        canon_list_elements = [
            tr_element.parent for tr_element in canon_list
        ]

        filler_list_elements = [
            tr_element.parent for tr_element in filler_mixed_list
        ]

        found_status = False
        while not found_status:
            for element in filler_list_elements:
                if str(eps_num) == element.find('td', class_ = "Number").text.strip():
                    episode_type = element.find('td', class_ = "Type").text.strip()
                    episode_title = element.find('td', class_ = "Title").text.strip()
                    print(f'Episode {eps_num} of {show_name.title()} titled "{episode_title}"\n'
                            f'is {episode_type}.')
                    found_status = True
                    break
            if not found_status:
                for element in canon_list_elements:
                    if str(eps_num) == element.find('td', class_ = "Number").text.strip():
                        episode_type = element.find('td', class_ = "Type").text.strip()
                        episode_title = element.find('td', class_ = "Title").text.strip()
                        print(f'Episode {eps_num} of {show_name.title()} titled "{episode_title}"\n'
                                f'is {episode_type}.')
                        found_status = True
                        break
        new_show = Show(show_name=show_name, eps_num=eps_num, show_title=episode_title, status=episode_type, user_id=current_user.id)
        db.session.add(new_show)
        db.session.commit()
        flash('Show Added!', category='success')
        return redirect(url_for('views.home'))
    elif request.method == 'GET':
        pass
    return render_template('home_page.html', user=current_user)