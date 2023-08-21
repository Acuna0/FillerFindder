"""
.py file that was "scratch" work to make sure logic was working as intended
"""

import requests
from bs4 import BeautifulSoup


if __name__=='__main__':
    try:
        user_show = input(f"Enter Show Name: ").strip()
        user_show_fix = user_show.replace(' ', '-')
        user_episode = int(input(f"Enter Episode Number: "))
    
        URL = "https://www.animefillerlist.com/shows/" + user_show_fix
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, "html.parser")
        results = soup.find(class_="EpisodeList")

        if isinstance(results, type(None)):
            raise TypeError
        else:
            total_episodes = len(results.find_all('td', class_ = 'Date'))

        if user_episode < 1 or total_episodes < user_episode:
            raise ValueError

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
                if str(user_episode) == element.find('td', class_ = "Number").text.strip():
                    episode_type = element.find('td', class_ = "Type").text.strip()
                    episode_title = element.find('td', class_ = "Title").text.strip()
                    print(f'Episode {user_episode} of {user_show.title()} titled "{episode_title}"\n'
                            f'is {episode_type}.')
                    found_status = True
                    break
            if not found_status:
                for element in canon_list_elements:
                    if str(user_episode) == element.find('td', class_ = "Number").text.strip():
                        episode_type = element.find('td', class_ = "Type").text.strip()
                        episode_title = element.find('td', class_ = "Title").text.strip()
                        print(f'Episode {user_episode} of {user_show.title()} titled "{episode_title}"\n'
                                f'is {episode_type}.')
                        found_status = True
                        break
    except ValueError:
        print(f'That episode of {user_show.capitalize()} does not exist.')
    except TypeError:
        print(f'Please enter a valid show title and episode.')