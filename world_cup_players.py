import pandas as pd
import requests
from bs4 import BeautifulSoup
from wikidata.client import Client 

# years = ("1930", "1934", "1938", "1950", "1954")
years = ("1930", "1934", "1938")
results = pd.DataFrame(columns = ["Year", "Name", "Country", "DoB", "DoD", "Alive", "Past Tense"])
base = "https://en.wikipedia.org"

# Scan squad tables for each year
for year in years:
    response = requests.get(base + "/wiki/{}_FIFA_World_Cup_squads".format(year))
    soup = BeautifulSoup(response.text, 'html.parser')
    tables = soup.findAll('table', {"class": "sortable wikitable plainrowheaders"}) # table class used in wiki squad pages 

    for table in tables:
        for tr in table.findAll("tr", {"class": "nat-fs-player"}): # tr class used in wiki squad pages
            player_link = player_name = player_dob = player_dod = player_alive = None
            player_country = table.find_previous("span", {"class": "mw-headline"}).text
            ths = tr.findAll("th", {"scope": "row"})
            
            for th in ths:
                player_name = th.text.rstrip("\n")
                is_alive = False

                # load player wiki
                response = requests.get(base + th.find('a')['href'])
                player_soup = BeautifulSoup(response.text, 'html.parser')
                wikidata_item = player_soup.find("li", {"id": "t-wikibase"})

                # try wikidata birth and death properties
                if wikidata_item:
                    wikidata_id = wikidata_item.find("a")["href"].split("/")[-1]
                    entity = Client().get(wikidata_id, load=True)
                    date_of_birth = date_of_death_list = date_of_death = place_of_death_list = place_of_death = None

                    try:
                        date_of_birth = entity.attributes["claims"]["P569"][0]['mainsnak']['datavalue']['value']['time']
                    except:
                        pass
                    
                    try:
                        date_of_death_list = entity.attributes["claims"]["P570"]
                        date_of_death = date_of_death_list[0]['mainsnak']['datavalue']['value']['time']
                    except:
                        try:
                            place_of_death_list = entity.attributes["claims"]["P20"] 
                        except:
                            pass

                    is_alive = not date_of_death_list and not place_of_death_list

                # check if " was " in opening sentence
                opening_paragraph = player_soup.find("p", {"class":None}).get_text()
                opening_sentence = opening_paragraph.split(". ")[0]
                is_was = " was " in opening_sentence

            print(year, player_name, player_country, date_of_birth, date_of_death, is_alive, is_was)
            results.loc[len(results)] = (year, player_name, player_country, date_of_birth, date_of_death, is_alive, is_was)