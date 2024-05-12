import pymongo
import requests
import plotly.graph_objs as go
import json
import matplotlib.pyplot as plt
from flask import Flask, redirect, render_template, request, url_for, session
from flask_session import Session

from BDmongo import *
from datetime import datetime
#API key
XI_API_KEY = "43fd3e0df818d835e6b144ad21a7765a"
#Url pour mongo

import requests



def get_similar_track(api_key, artist, track, page=1, limit=10):
    url = 'http://ws.audioscrobbler.com/2.0/'
    params = {
        'method': 'track.getsimilar',
        'artist': artist,
        'track': track,
        'api_key': api_key,
        'format': 'json',
        'page': page,
        'limit': limit
    }
    response = requests.get(url, params=params)
    data = response.json()
    if not data or not data.get('similartracks', {}).get('track', []):
        return None
    tracks = data.get('similartracks', {}).get('track', [])
    tracks_info_list = []
    for index, track in enumerate(tracks, start=1):
        name = track.get('name')
        match = track.get('match')
        artist_name = track.get('artist', {}).get('name')
        track_info = {
            'index': index,
            'track_name': name.lower(),
            'match': match,
            'artist_name': artist_name.lower()
        }
        tracks_info_list.append(track_info)
    return tracks_info_list


def get_info_charttags(api_key, chart_type, page=1, limit=10):
    url = 'http://ws.audioscrobbler.com/2.0/'
    params = {
        'method': f'chart.gettop{chart_type}',
        'api_key': api_key,
        'format': 'json',
        'page': page,
        'limit': limit
    }
    response = requests.get(url, params=params)
    data = response.json()
    if not data or not data.get('tags', {}).get('tag', []):
        return None
    tags = data.get('tags', {}).get('tag', [])
    tag_info_list = []
    for index, tag in enumerate(tags, start=1):
        name = tag.get('name')
        reach = tag.get('reach')
        taggings = tag.get('taggings')
        tag_info = {
            'index': index,
            'name': name,
            'reach': reach,
            'taggings':taggings
        }
        tag_info_list.append(tag_info)
    
    return tag_info_list



def get_info_chartartist(api_key, chart_type, page=1, limit=10):
    url = 'http://ws.audioscrobbler.com/2.0/'
    params = {
        'method': f'chart.gettop{chart_type}',
        'api_key': api_key,
        'format': 'json',
        'page': page,
        'limit': limit
    }
    response = requests.get(url, params=params)
    data = response.json()
    if not data or not data.get('artists', {}).get('artist', []):
        return None
    artists = data.get('artists', {}).get('artist', [])
    artist_info_list = []
    for index, artist in enumerate(artists, start=1):
        name = artist.get('name')
        playcount = artist.get('playcount')
        listeners = artist.get('listeners')
        artist_info = {
            'index': index,
            'name': name.lower(),
            'playcount': playcount,
            'listeners': listeners
        }
        artist_info_list.append(artist_info)
    return artist_info_list


def get_info_chart(api_key, chart_type, page=1, limit=10):
    url = 'http://ws.audioscrobbler.com/2.0/'
    params = {
        'method': f'chart.gettop{chart_type}',
        'api_key': api_key,
        'format': 'json',
        'page': page,
        'limit': limit
    }
    response = requests.get(url, params=params)
    data = response.json()
    if not data or not data.get('tracks', {}).get('track', []):
        return None
    tracks = data.get('tracks', {}).get('track', [])
    track_info_list = []
    for track in tracks:
        track_info = {
            'name': track.get('name'),
            'playcount': track.get('playcount'),
            'listeners': track.get('listeners'),
            'artist': track.get('artist', {}).get('name')
        }
        track_info_list.append(track_info)
    return track_info_list
    

def get_tag_info(api_key, tag):
    url = 'http://ws.audioscrobbler.com/2.0/'
    params = {
        'method': 'tag.getinfo',
        'tag': tag,
        'api_key': api_key,
        'format': 'json'
    }
    response = requests.get(url, params=params)
    data = response.json()
    if 'tag' not in data or not data['tag'].get('name'):
        return None
    tag_info = data.get('tag', {})
    tag_result = {
        'name': tag_info.get('name').lower(),
        'total': tag_info.get('total'),
        'reach': tag_info.get('reach'),
        'tagging': tag_info.get('tagging'),
        'streamable': tag_info.get('streamable'),
        'wiki': {
            'summary': tag_info.get('wiki', {}).get('summary'),
            'content': tag_info.get('wiki', {}).get('content')
        }
    }
    return tag_result




def get_artist_info(api_key, artist):
    url = 'http://ws.audioscrobbler.com/2.0/'
    params = {
        'method': 'artist.getinfo',
        'artist': artist,
        'api_key': api_key,
        'format': 'json'
    }
    response = requests.get(url, params=params)
    data = response.json()
    if not data or not data.get('artist', {}):
        return None
    artist_data = data.get('artist', {})

    listeners_str = artist_data.get('stats').get('listeners')
    listeners_int = int(listeners_str.replace(',', '')) if listeners_str else None 
    artist_info = {
        'name': data['artist']['name'].lower(),
        'listeners': listeners_int,
        'similar_artists': []
    }

    similar_artists = data['artist'].get('similar', {}).get('artist', [])
    for similar_artist in similar_artists:
        similar_artist_info = {
            'name': similar_artist['name'].lower()
        }
        artist_info['similar_artists'].append(similar_artist_info)

    return artist_info


def get_album_info(api_key, artist, album):
    params = {
        'method': 'album.getinfo',
        'api_key': api_key,
        'artist': artist,
        'album': album,
        'format': 'json'
    }
    response = requests.get('http://ws.audioscrobbler.com/2.0/', params=params)
    data = response.json()
    if not data or not data.get('album', {}):
        return None
    album_data = data.get('album', {})
    listeners_str = album_data.get('listeners')
    listeners_int = int(listeners_str.replace(',', '')) if listeners_str else None 
    playcount_str = album_data.get('playcount')
    playcount_int = int(playcount_str.replace(',', '')) if playcount_str else None
     # Convertir en int en supprimant les virgules
    album_info = {
        'name' : album_data.get('name').lower(),
        'artist' : album_data.get('artist').lower(),
        'listeners': listeners_int,
        'release_date': album_data.get('releasedate'),
        'playcount': playcount_int,
        'tracks': []
    }
    tracks = album_data.get('tracks', {}).get('track', [])
    for track in tracks:
        track_info = {
            'name': track.get('name').lower(),
            'duration': track.get('duration'),
            'streamable': track.get('streamable'),
            'artist': track.get('artist', {}).get('name').lower()  
        }
        album_info['tracks'].append(track_info)
        
    return album_info   


# RECUPERER LES DONNES DU TRACK DEPUIS API
def get_track_info(api_key, artist, track):
    params = {
        'method': 'track.getinfo',
        'api_key': api_key,
        'artist': artist,
        'track': track,
        'format': 'json'
    }
    response = requests.get('http://ws.audioscrobbler.com/2.0/', params=params)
    data = response.json()
    if not data or not data.get('track'):
        return None
    track_data = data.get('track', {})
    listeners_str = track_data.get('listeners')
    listeners_int = int(listeners_str.replace(',', '')) if listeners_str else None 
    playcount_str = track_data.get('playcount')
    playcount_int = int(playcount_str.replace(',', '')) if playcount_str else None
    
     # Convertir en int en supprimant les virgules
    track_info = {
        'name' : track_data.get('name').lower(),
        'artist' : track_data.get('artist').lower(),
        'listeners': listeners_int,
        'playcount': playcount_int,
    }


    return track_info 



def get_filtred_charts(ecoutes,comparateur, option):
    if option =='artist' : 
        all_artists = getAll_artists()
        if comparateur =='sup':
            filtred_charts = [artist for artist in all_artists if artist['listeners'] >= ecoutes]  # Filtrer les morceaux avec plus de 100 écoutes
        else:
            filtred_charts = [artist for artist in all_artists if artist['listeners'] <= ecoutes]  # Filtrer les morceaux avec plus de 100 écoutes

    elif option == 'album' : 
        all_albums = getAll_albums()
        if comparateur =='sup':
            filtred_charts = [album for album in all_albums if album['listeners'] >= ecoutes]  # Filtrer les morceaux avec plus de 100 écoutes
        else:
            filtred_charts = [album for album in all_albums if album['listeners'] <= ecoutes]  # Filtrer les morceaux avec plus de 100 écoutes
    else :
        all_tracks = getAll_tracks()
        if comparateur =='sup':
            filtred_charts = [track for track in all_tracks if track['listeners'] >= ecoutes]  # Filtrer les morceaux avec plus de 100 écoutes
        else:
            filtred_charts = [track for track in all_tracks if track['listeners'] <= ecoutes]  # Filtrer les morceaux avec plus de 100 écoutes

    return filtred_charts








app = Flask(__name__, static_folder='templates/', static_url_path='')

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_USE_SIGNER'] = True  # Optionnel : pour signer les cookies de session

Session(app)
app.secret_key = '_5#y2L"F4Q8z\n\xec]/'

@app.route('/album') 
def album():
    if 'username' in session:
        username = session['username']
        return render_template('index.html', role=get_user_role(username), message=username)

    else :

        #message = request.form.get('message')  
        return render_template('index.html')
    
@app.route('/avis') 
def avis():
    if 'username' in session:
        username = session['username']
        return render_template('avis.html', role=get_user_role(username))

@app.route('/l',methods=['POST','GET'])
def log():
    if 'username' in session:
        username = session['username']
    
    artist_index, track_index, tag_index = count_consultations()
    print(artist_index)
    print(track_index)
    print(tag_index)
    
    labels1 = [row[1] for row in artist_index]
    values1 = [row[0] for row in artist_index]
    labels2 = [row[1] for row in track_index]
    values2 = [row[0] for row in track_index]
    labels3 = [row[1] for row in tag_index]
    values3 = [row[0] for row in tag_index]
    print(labels1)

    
    return render_template('log.html',labels1=labels1, labels2=labels2, labels3=labels3, values1=values1, values2=values2, values3=values3, role=get_user_role(username))

@app.route('/t',methods=['POST','GET'])
def t():
    if 'username' in session:
        username = session['username']
    return render_template('Tag.html', role=get_user_role(username))
    
@app.route('/a', methods=['POST','GET']) 
def a():
    if 'username' in session:
        username = session['username']
    return render_template('Artiste.html', role=get_user_role(username))

@app.route('/c',methods=['POST','GET'])
def c():
    if 'username' in session:
        username = session['username']
    
    track_info_list = get_info_chart(XI_API_KEY, 'tracks')
    log_consultation("tracks")   
    tracks_with_index = [(index + 1, track_info) for index, track_info in enumerate(track_info_list)]
    return render_template('chart_tracks.html', tracks_with_index=tracks_with_index, role=get_user_role(username))

@app.route('/c2',methods=['POST','GET'])
def c2():
    if 'username' in session:
        username = session['username']
    track_info_list = get_info_chartartist(XI_API_KEY, 'artists')
    log_consultation("artists")
    tracks_with_index = [(index + 1, track_info) for index, track_info in enumerate(track_info_list)]
    print(count_consultations())
    return render_template('chart_artist.html',tracks_with_index=tracks_with_index, role=get_user_role(username))

@app.route('/c3', methods=['POST','GET'])
def c3():
    if 'username' in session:
        username = session['username']
    track_info_list = get_info_charttags(XI_API_KEY, 'tags')
    log_consultation("tags")
    tracks_with_index = [(index + 1, track_info) for index, track_info in enumerate(track_info_list)]
    return render_template('chart_tags.html',tracks_with_index=tracks_with_index, role=get_user_role(username))
{
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "[javascript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
@app.route('/Artiste', methods=['POST','GET'])
def Artiste():
    if 'username' in session:
        username = session['username']

    if 'artist' in request.args :
        artist_name = request.args.get('artist').lower()
        info = check_artist_in_db(artist_name)
        if info : 
            print("dans la base")
            return render_template('Artiste.html', artist_info=info, role=get_user_role(username), message_requete='REQUÊTE LOCAL')
        else:
            artist_info = get_artist_info(XI_API_KEY, artist_name)
            insert_artist_info_into_db(artist_info)
            print("pas dans la base")
            return render_template('Artiste.html', artist_info=artist_info, role=get_user_role(username), message_requete='REQUÊTE À DISTANCE')
    else:
        return render_template('Artiste.html', role=get_user_role(username))

@app.route('/tag', methods=['POST','GET'])
def tag_info():
    if 'username' in session:
        username = session['username']
    
    if 'tag' in request.args :
        tag = request.args.get('tag').lower()
        info = check_tag_in_db(tag)
        if info: 
            print("dans la base")
            return render_template('Tag.html', tag_info=info, role=get_user_role(username), message_requete='REQUÊTE LOCAL')
        else:
            print("pas dans la base")
            tag_info = get_tag_info(XI_API_KEY, tag)
            insert_tag_info_into_db(tag_info)
            return render_template('Tag.html', tag_info=tag_info, role=get_user_role(username), message_requete='REQUÊTE À DISTANCE')
    else :
        return render_template('tag.html', role=get_user_role(username))

@app.route('/result', methods=['POST','GET'])
def result():
    if 'username' in session:
        username = session['username']
    if 'artist' in request.args and 'album' in request.args :
        
        artist = request.args.get('artist').lower()
        album = request.args.get('album').lower()
        info = check_album_in_db(artist,album)
        print("aaaaaaaaaaaaaaaaa",info)
        if info: 
            print("dans la base")
            return render_template('index.html',message=info, role=get_user_role(username), message_requete='REQUÊTE LOCAL')
        else: 
            print("pas dans la base")
            response = get_album_info(XI_API_KEY, artist, album)
            insert_album_info_into_db(response)
            return render_template('index.html',message=response, role=get_user_role(username), message_requete='REQUÊTE À DISTANCE')
    else :
        return render_template('index.html', role=get_user_role(username))

@app.route('/similaire',methods=['GET'])
def similaire():
    if 'username' in session:
        username = session['username']
    if 'artist' in request.args and 'track' in request.args:
        artist = request.args.get('artist').lower()
        track = request.args.get('track').lower()
        info = check_similiarite_in_db(artist,track)
        if info:
            print("dans la base")
            return render_template('Similaire.html', tracks_info=info, role=get_user_role(username), message_requete='REQUÊTE LOCAL')
        else: 
            print("pas dans la base")
            response = get_similar_track(XI_API_KEY,artist,track)
            insert_similaire_info_into_db(response,artist,track)
        return render_template('Similaire.html', tracks_info=response, role=get_user_role(username), message_requete='REQUÊTE À DISTANCE')
    else :
        return render_template('tag.html', role=get_user_role(username))

@app.route('/charts_filter',methods=['POST', 'GET'])
def charts_filter():
    if 'username' in session:
        username = session['username']
    if 'option' in request.args and 'comparateur' in request.args and 'ecoutes' in request.args:
        option = request.args.get('option')
        comparateur = request.args.get('comparateur')
        ecoutes_str = request.args.get('ecoutes')
        ecoutes_int = int(ecoutes_str)
        filtred_charts = get_filtred_charts(ecoutes_int, comparateur, option)
        if filtred_charts:
            print("dans la base")
            return render_template('charts_filter.html', filtred_charts=filtred_charts, option=option, role=get_user_role(username), message_requete='REQUÊTE LOCAL')
        else :
            return render_template('charts_filter.html', error_message="Aucune donnée n'est trouvé", role=get_user_role(username))

    else :
        return render_template('charts_filter.html', role=get_user_role(username))
    

@app.route('/avisForm',methods=['POST', 'GET'])
def avisForm():
    if 'username' in session:
        username = session['username']
    option = request.args.get('option')
    name = request.args.get('name')
    note = request.args.get('note')
    if 'comment' in request.args:
        comment = request.args.get('comment')
    if option =='tag':
        insert_avisTag_into_db(username,note,comment,name)
        return render_template('avis.html', role=get_user_role(username))
    else:
        artist = request.args.get('artist')
        insert_avis_into_db(username,note,comment,option, name, artist)
        return render_template('avis.html', role=get_user_role(username))

@app.route('/check_forAvis',methods=['POST', 'GET'])
def check_forAvis():
    if 'username' in session:
        username = session['username']
    if 'option' in request.args and 'name_forAvis' in request.args:
        option = request.args.get('option')
        artist = request.args.get('artist').lower()
        name_forAvis = request.args.get('name_forAvis').lower()
        if option =='tag':
            content_forAvis = check_tag_in_db(name_forAvis)
        elif option == 'album' : 
            content_forAvis = check_album_in_db(name_forAvis, artist)
        elif option == 'track' :
            content_forAvis = check_track_in_db(name_forAvis, artist)

        if content_forAvis:
            print("dans la base")
            return render_template('avis.html', content_forAvis=content_forAvis, option=option, role=get_user_role(username), message_requete='REQUÊTE LOCAL')
        
        else: 
            print("pas dans la base")
            if option == "tag":
                content_forAvis = get_tag_info(XI_API_KEY, name_forAvis)
                if content_forAvis:
                    return render_template('avis.html', content_forAvis=content_forAvis, option=option, role=get_user_role(username), message_requete='REQUÊTE À DISTANCE')
                else:
                    erreur_msg ='votre saisie est introuvée'
                    return render_template('avis.html', error_message=erreur_msg, role=get_user_role(username))



            elif option == 'album' : 
                content_forAvis = get_album_info(XI_API_KEY, artist, name_forAvis)
                if content_forAvis:
                    return render_template('avis.html', content_forAvis=content_forAvis, option=option, role=get_user_role(username), message_requete='REQUÊTE À DISTANCE')
                else:
                    erreur_msg ='votre saisie est introuvée'
                    return render_template('avis.html', error_message=erreur_msg, role=get_user_role(username))

            elif option == 'track' :
                content_forAvis = get_track_info(XI_API_KEY, artist, name_forAvis)
                if content_forAvis:
                    return render_template('avis.html', content_forAvis=content_forAvis, option=option, role=get_user_role(username), message_requete='REQUÊTE À DISTANCE')
                else:
                    erreur_msg ='votre saisie est introuvée'
                    return render_template('avis.html', error_message=erreur_msg, role=get_user_role(username))
    else :
        return render_template('avis.html', role=get_user_role(username))


#compte utilisateur inscription 
@app.route('/signup')
def signup(): 
    return render_template('signup.html')

@app.route('/signup_done',methods=['POST'])
def signup_done():
    username = request.form.get('username')
    mdp = request.form.get('mdp')
    nom = request.form.get('nom')
    prenom = request.form.get('prenom')
    existe = check_user_in_db(username)  # Récupérer une seule ligne du résultat
    if existe == None:
        insert_user_into_db(username,mdp,nom,prenom)
        session['username'] = username
        return redirect(url_for('album'))
    #envoie vers route /home !! à faire
    else:
        # Si un utilisateur est déjà enregistré, rediriger vers la page d'accueil
        error_message = "cet utilisateur est déjà inscrit!"
        return render_template('signup.html', error_message=error_message)

@app.route("/logout")
def logout():
    session.pop('username', None)
    return render_template('index.html')    
        
@app.route('/login')
def login(): 
    return render_template('login.html')

@app.route("/loginDone",methods=['POST'])
def loginDone():
    username = request.form['username']
    password = request.form['password']
    existe = check_user_in_db(username)  # Récupérer une seule ligne du résultat
    if existe:  # Si un utilisateur correspondant est trouvé
        access = check_connexion(username, password)
        if access :
            print("acces autorisé :")
            session['username'] = access.get("username")
            return redirect(url_for('album'))
        else :
            error_message = "Failed : le mot de passe saisi est incorrect"
            return render_template('login.html', error_message=error_message)  
    else:
        error_message = "Failed : le username saisi n'existe pas"
        return render_template('login.html', error_message=error_message)  

if __name__ == '__main__':
      app.run(debug=True)

#-----------------------------------------------------------------------------------------------------------
#   Le nombre d'écoutes est bien entendu une information dynamique. Votre système pourrait satisfaire cette
# fonctionnalité en exécutant une requête locale et affichant la dernière information connue ainsi que la date
# d'acquisition. Un paramètre du système pourrait contrôler la période de validité des données locales. Par exemple,
# si le temps écoulé entre la dernière mise à jour et le moment d’une nouvelle requête excède !!72h!!, la nouvelle
# requête se fera auprès de l'API Web et !!!! mettra à jour la BD locale !!!!.     