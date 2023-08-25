from flask import Blueprint, render_template, flash, jsonify, request
from flask_login import login_required, current_user
from bs4 import BeautifulSoup
from .models import Show
import json, requests
from . import db


views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    """
    Function that displays home page. If homepage is POST request then scrape of website occurs with user input and data
    is stored in database. User login required to access page.

    Returns:
        function: returns user to homepage (refreshes if already there)
    """
    if request.method == 'POST':
        eps_num = request.form.get('epsNum').strip()
        show_name = request.form.get('showName').strip().title()

        URL = "https://www.animefillerlist.com/shows/" + show_name.replace(' ', '-')
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, "html.parser")
        results = soup.find(class_="EpisodeList")

        if isinstance(results, type(None)):
            flash('Show entered incorrectly or does not exist', category='error')
            return render_template('home_page.html', user=current_user)
        else:
            total_episodes = len(results.find_all('td', class_ = 'Date'))
        if eps_num == '' or not eps_num.isdigit():
            flash('Show entered incorrectly or does not exist', category='error')
            return render_template('home_page.html', user=current_user)
        else:
            if int(eps_num) < 1 or total_episodes < int(eps_num):
                flash('That episode does not exists', category='error')
                return render_template('home_page.html', user=current_user)
        
        manga_canon = results.find_all(
            "td", string=lambda text: "manga canon" in text.lower()
        )
        filler_mixed_list = results.find_all(
            "td", string=lambda text: "filler" in text.lower()
        )
        anime_canon = results.find_all(
            "td", string=lambda text: "anime canon" in text.lower()
        )

        manga_canon_elements = [
            tr_element.parent for tr_element in manga_canon
        ]

        filler_list_elements = [
            tr_element.parent for tr_element in filler_mixed_list
        ]
        anime_canon_elements = [
            tr_element.parent for tr_element in anime_canon
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
                for element in anime_canon_elements:
                    if str(eps_num) == element.find('td', class_ = "Number").text.strip():
                        episode_type = element.find('td', class_ = "Type").text.strip()
                        episode_title = element.find('td', class_ = "Title").text.strip()
                        print(f'Episode {eps_num} of {show_name.title()} titled "{episode_title}"\n'
                                f'is {episode_type}.')
                        found_status = True
                        break
            if not found_status:
                for element in manga_canon_elements:
                    if str(eps_num) == element.find('td', class_ = "Number").text.strip():
                        episode_type = element.find('td', class_ = "Type").text.strip()
                        episode_title = element.find('td', class_ = "Title").text.strip()
                        print(f'Episode {eps_num} of {show_name.title()} titled "{episode_title}"\n'
                                f'is {episode_type}.')
                        found_status = True
                        break
        new_show = Show(show_name=show_name, eps_num=eps_num, show_title=episode_title,
                        status=episode_type, user_id=current_user.id)
        db.session.add(new_show)
        db.session.commit()
        flash('Show Added!', category='success')
    elif request.method == 'GET':
        pass
    return render_template('home_page.html', user=current_user)

@views.route("/delete-show", methods=['POST'])
def delete_show():  
    """
    Function that occurs after button request from home.html that loads JSON request from index.js and grabs
    show ID to delete it from the database (users profile).

    Returns:
        response object: empty (refreshes page).
    """
    show = json.loads(request.data) 
    showId = show['showId']
    actshow = Show.query.get(showId)
    if actshow:
        if actshow.user_id == current_user.id:
            db.session.delete(actshow)
            db.session.commit()

    return jsonify({ })
