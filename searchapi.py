from flask import Flask, request
import requests
from bs4 import BeautifulSoup

def get_status(response):
    soup = BeautifulSoup(response.content, 'html.parser')

    div = soup.find('div', {'id': 'mw-content-text'})

    div2 = div.find('div', {'class': 'mw-parser-output'})

    table = div2.find('table', {'class': 'wikitable'})

    table = table.find_next('table', {'class': 'wikitable'})

    def get_value(row, col):
        tr_tag = table.find_all('tr')[row]
        td_tags = tr_tag.find_all('td')
        if len(td_tags) > col:
            td_tag = td_tags[col]
            try:
                return td_tag.text.strip()
            except AttributeError:
                return None

    hpbase = get_value(1,3)
    hpfull = get_value(1,2)
    dsbase = get_value(2,3)
    dsfull = get_value(2,2)
    atbase = get_value(3,3)
    atfull = get_value(3,2)
    atkspeed = get_value(4,2)
    ctbase = get_value(5,3)
    ctfull = get_value(5,2)
    hitrate = get_value(6,2)
    debase = get_value(7,3)
    defull = get_value(7,2)
    evbase = get_value(8,3)
    evfull = get_value(8,2)

    variables = { "hpbase": hpbase, "hpfull": hpfull,"dsbase": dsbase, "dsfull": dsfull,"atbase": atbase, 
                    "atfull": atfull, "atkspeed": atkspeed,"ctbase": ctbase,"ctfull": ctfull,
                    "hitrate": hitrate,"debase": debase,"defull": defull,"evbase": evbase,"evfull": evfull}

    for var_name, var_value in variables.items():
        print(f"{var_name}: {var_value}")

def get_image(response):
        soup = BeautifulSoup(response.content, 'html.parser')

        div = soup.find('div', {'id': 'mw-content-text'}) 

        table = div.find('table', {'id': 'scraper-infobox'})

        tr = table.find('tr')

        div2 = soup.find('div', {'id': 'scraper-digimon-image'}) 

        center = div2.find('center')

        a = center.find('a')

        if a:
            img = a.find('img')
            
            if img:
                img_url = img['src']
                print(f'https://dmowiki.com{img_url}')

        else:
            print(f'Error {response.status_code}: Unable to retrieve the webpage.')

app = Flask(__name__)

@app.route('/<digimon_name>')
def get_digimon_page():
    try:
        digimon_name = input("What digimon are you looking for: ").replace(' ', '_')
        url = f'https://dmowiki.com/{digimon_name}'
        response = requests.get(url)
        if response.status_code == 200:
            digimon_data = get_status(response)
            digimon_image = get_image(response)
            return digimon_data, digimon_image
        
        elif response.status_code == 404:
            search_url = f'https://dmowiki.com/Special:Search/{digimon_name}'
            response = requests.post(search_url)
            digimon_name = digimon_name.replace('_', '+')
            if response.status_code == 200:
                if response.url == f'https://dmowiki.com/index.php?title=Special:Search&search={digimon_name}':
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    div = soup.find('div', {'id': 'mw-content-text'})
                    
                    div2 = div.find('div', {'class': 'searchresults'})
                    
                    div3 = div2.find('div', {'class': 'mw-search-result-heading'})
                    
                    a = div3.find_all('a')
                    
                    for link in a:
                        response = requests.get(f'https://dmowiki.com{link["href"]}')
                        if response.status_code == 200:
                            digimon_data = get_status(response)
                            digimon_image = get_image(response)
                            return digimon_data, digimon_image
                        else:
                            print(f'Error {response.status_code}: Unable to retrieve the webpage.')
                            break
                    
                else:
                    digimon_data = get_status(response)
                    digimon_image = get_image(response)
                    return digimon_data, digimon_image

    except:
        print(f'Error {response.status_code}: Unable to retrieve the webpage.')
    
get_digimon_page()

if __name__ == '__main__':
    app.run(debug=True)