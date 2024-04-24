import pymongo
import requests
import plotly.graph_objs as go
import json
import matplotlib.pyplot as plt
from flask import Flask, redirect, render_template, request, url_for
from BDmongo import insert_artist_info_into_db, check_artist_in_db, check_tag_in_db, insert_tag_info_into_db, check_album_in_db, insert_album_info_into_db,log_consultation,count_consultations,insert_similaire_info_into_db, check_similiarite_in_db
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
    tracks = data.get('similartracks', {}).get('track', [])
    tracks_info_list = []
    for index, track in enumerate(tracks, start=1):
        name = track.get('name')
        match = track.get('match')
        artist_name = track.get('artist', {}).get('name')
        track_info = {
            'index': index,
            'track_name': name,
            'match': match,
            'artist_name': artist_name
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
    artists = data.get('artists', {}).get('artist', [])
    artist_info_list = []
    for index, artist in enumerate(artists, start=1):
        name = artist.get('name')
        playcount = artist.get('playcount')
        listeners = artist.get('listeners')
        artist_info = {
            'index': index,
            'name': name,
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
    
    tag_info = data.get('tag', {})
    tag_result = {
        'name': tag_info.get('name'),
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

    artist_info = {
        'name': data['artist']['name'],
        'similar_artists': []
    }

    similar_artists = data['artist'].get('similar', {}).get('artist', [])
    for similar_artist in similar_artists:
        similar_artist_info = {
            'name': similar_artist['name']
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
    album_data = data.get('album', {})
    listeners_str = album_data.get('listeners')
    listeners_int = int(listeners_str.replace(',', '')) if listeners_str else None 
    playcount_str = album_data.get('playcount')
    playcount_int = int(playcount_str.replace(',', '')) if playcount_str else None
    
     # Convertir en int en supprimant les virgules
    album_info = {
        'name' : album_data.get('name'),
        'artist' : album_data.get('artist'),
        'listeners': listeners_int,
        'release_date': album_data.get('releasedate'),
        'playcount': playcount_int,
        'tracks': []
    }
    tracks = album_data.get('tracks', {}).get('track', [])
    for track in tracks:
        track_info = {
            'name': track.get('name'),
            'duration': track.get('duration'),
            'streamable': track.get('streamable'),
            'artist': track.get('artist', {}).get('name')  
        }
        album_info['tracks'].append(track_info)
        
    return album_info   






app = Flask(__name__, static_folder='templates/', static_url_path='')


@app.route('/') 
def home():
    message = request.args.get('message')  
    return render_template('Lastfm.html', message=message)

@app.route('/l', methods=['GET'])
def log():
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

    
    return render_template('log.html',labels1=labels1, labels2=labels2, labels3=labels3, values1=values1, values2=values2, values3=values3)

@app.route('/t')
def t():
    return render_template('Tag.html')
@app.route('/a') 
def a():
    return render_template('Artiste.html')

@app.route('/c',methods=['GET'])
def c():
    track_info_list = get_info_chart(XI_API_KEY, 'tracks')
    log_consultation("tracks")

    
    tracks_with_index = [(index + 1, track_info) for index, track_info in enumerate(track_info_list)]

    return render_template('chart_tracks.html',tracks_with_index=tracks_with_index)

@app.route('/c2',methods=['GET'])
def c2():
    track_info_list = get_info_chartartist(XI_API_KEY, 'artists')
    log_consultation("artists")
    tracks_with_index = [(index + 1, track_info) for index, track_info in enumerate(track_info_list)]
    print(count_consultations())
    return render_template('chart_artist.html',tracks_with_index=tracks_with_index)

@app.route('/c3',methods=['GET'])
def c3():
    track_info_list = get_info_charttags(XI_API_KEY, 'tags')
    log_consultation("tags")
    tracks_with_index = [(index + 1, track_info) for index, track_info in enumerate(track_info_list)]

    return render_template('chart_tags.html',tracks_with_index=tracks_with_index)

@app.route('/Artiste', methods=['GET'])
def Artiste():
    artist_name = request.args.get('artist') 
    info = check_artist_in_db(artist_name)
    if info : 
        print("dans la base")
        return render_template('Artiste.html', artist_info=info)
    else:
        artist_info = get_artist_info(XI_API_KEY, artist_name)
        insert_artist_info_into_db(artist_info)
        print("pas dans la base")
        return render_template('Artiste.html', artist_info=artist_info)

@app.route('/tag', methods=['GET'])
def tag_info():
    tag = request.args.get('tag')
    info = check_tag_in_db(tag)
    if info: 
        print("dans la base")
        return render_template('Tag.html', tag_info=info)
    else:
        print("pas dans la base")
        tag_info = get_tag_info(XI_API_KEY, tag)
        insert_tag_info_into_db(tag_info)
        return render_template('Tag.html', tag_info=tag_info)



@app.route('/result', methods=['GET'])
def result():
    artist = request.args.get('artist')
    album = request.args.get('album')
    info = check_album_in_db(artist,album)
    if info: 
        print("dans la base")
        return render_template('Lastfm.html',message=info)
    else: 
        print("pas dans la base")
        response = get_album_info(XI_API_KEY, artist, album)
        insert_album_info_into_db(response)
        return render_template('Lastfm.html',message=response)

@app.route('/similaire',methods=['POST','GET'])
def similaire():
    artist = request.args.get('artist')
    track = request.args.get('track')
    info = check_similiarite_in_db(artist,track)
    if info:
        print("dans la base")
        return render_template('Similaire.html', tracks_info=info)
    else: 
        print("pas dans la base")
        response = get_similar_track(XI_API_KEY,artist,track)
        insert_similaire_info_into_db(response,artist,track)
    return render_template('Similaire.html', tracks_info=response)


if __name__ == '__main__':
      app.run(debug=True)

#-----------------------------------------------------------------------------------------------------------
#   Le nombre d'écoutes est bien entendu une information dynamique. Votre système pourrait satisfaire cette
# fonctionnalité en exécutant une requête locale et affichant la dernière information connue ainsi que la date
# d'acquisition. Un paramètre du système pourrait contrôler la période de validité des données locales. Par exemple,
# si le temps écoulé entre la dernière mise à jour et le moment d’une nouvelle requête excède !!72h!!, la nouvelle
# requête se fera auprès de l'API Web et !!!! mettra à jour la BD locale !!!!.     