import pymongo 
from datetime import datetime
from collections import defaultdict
from pymongo import MongoClient

client = pymongo.MongoClient("mongodb://localhost:27017/")

db = client["SD2024_projet"]




######################
#fonctions pour artiste
def check_artist_in_db(artist):
    collection = db["GAMMA_artists"]
    artist_info_from_db = collection.find_one({"name": artist})
    return artist_info_from_db

def insert_artist_info_into_db(artist_info):

    collection = db["GAMMA_artists"]

    
    existing_document = collection.find_one({"name": artist_info["name"]})

    if existing_document:
        print("Le document existe déjà dans la collection GAMMA_artists. Pas besoin d'insérer à nouveau.")
    else:
        
        collection.insert_one(artist_info)
        print("Données de l'artiste insérées avec succès dans la collection GAMMA_artists.")
#####################
#fonctions pour tag
def check_tag_in_db(tag_name):
    collection = db["GAMMA_tags"]
    tag_info_from_db = collection.find_one({"name": tag_name})
    return tag_info_from_db

def insert_tag_info_into_db(tag_info):
    collection = db["GAMMA_tags"]

    existing_document = collection.find_one({"name": tag_info["name"]})

    if existing_document:
        print("Le document existe déjà dans la collection GAMMA_tags. Pas besoin d'insérer à nouveau.")
    else:
        collection.insert_one(tag_info)
        print("Données du tag insérées avec succès dans la collection GAMMA_tags.")

######################
#fonctions pour albums 
def check_album_in_db(artist_name, album_name):
    collection = db["GAMMA_albumes"]
    album_info_from_db = collection.find_one({"artist": artist_name, "album": album_name})
    return album_info_from_db


def insert_album_info_into_db(album_info):
    collection = db["GAMMA_albums"]

    existing_document = collection.find_one({"name": album_info["name"],"artist": album_info["artist"]})
    if existing_document:
        print("Le document existe déjà dans la collection GAMMA_albums. Pas besoin d'insérer à nouveau.")
    else:
        collection.insert_one(album_info)
        print("Données de l'album insérées avec succès dans la collection GAMMA_albums.")
########################
#fonction pour les similarité
def check_similiarite_in_db(artist, track):
    collection = db["GAMMA_similaire"]
    track_info_from_db = collection.find_one({"artist": artist, "track": track})
    if track_info_from_db:
        return track_info_from_db["similar_tracks"]
    else:
        return None

def insert_similaire_info_into_db(tracks_info, artist, track):
    collection = db["GAMMA_similaire"]

    existing_document = collection.find_one({"artist": artist, "track": track})
    if existing_document:
        print("Les données des pistes similaires pour cet artiste et ce morceau existent déjà dans la collection GAMMA_similaire. Pas besoin de les insérer à nouveau.")
    else:
        similar_tracks_document = {
            "artist": artist,
            "track": track,
            "similar_tracks": tracks_info
        }
        collection.insert_one(similar_tracks_document)
        print("Données des pistes similaires insérées avec succès dans la collection GAMMA_similaire.")




#########################
#fonction LOG
def log_consultation(type_consultation):
    consultation_collection = db["GAMMA_LOG"]
    
    consultation_data = {
        "type": type_consultation,
        "date": datetime.now()
    }
    consultation_collection.insert_one(consultation_data)

########################
#pour le graphique //calcule des données pour remplire le graphique
def count_consultations():
    # Connexion à la base de données MongoDB
    collection = db['GAMMA_LOG']

    # Liste des types de consultation à traiter
    consultation_types = ["artists", "tracks", "tags"]

    # Dictionnaires pour stocker les résultats pour chaque type de consultation
    artist_occurrences = []
    track_occurrences = []
    tag_occurrences = []

    # Parcours des types de consultation
    for consultation_type in consultation_types:
        # Requête pour compter les occurrences de chaque date pour le type actuel
        pipeline = [
            {"$match": {"type": consultation_type}},
            {"$group": {"_id": {"date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$date"}}}, "count": {"$sum": 1}}},
            {"$sort": {"_id.date": 1}}
        ]

        # Exécution de la requête
        results = collection.aggregate(pipeline)

        # Formatage des résultats sous forme de liste de tuples (occurrence, date)
        occurrences = [(row['count'], row['_id']['date']) for row in results]

        # Stockage des résultats dans le dictionnaire approprié en fonction du type de consultation
        if consultation_type == "artists":
            artist_occurrences = occurrences
        elif consultation_type == "tracks":
            track_occurrences = occurrences
        elif consultation_type == "tags":
            tag_occurrences = occurrences
        
        all_dates = set([date for _, date in artist_occurrences] + [date for _, date in track_occurrences] + [date for _, date in tag_occurrences])

        # Vérifier chaque date pour chaque type de consultation et l'ajouter avec occurrence 0 si elle manque
        for date in all_dates:
            # Vérification pour artist_occurrences
            if date not in [d for _, d in artist_occurrences]:
                artist_occurrences.append((0, date))
            # Vérification pour track_occurrences
            if date not in [d for _, d in track_occurrences]:
                track_occurrences.append((0, date))
            # Vérification pour tag_occurrences
            if date not in [d for _, d in tag_occurrences]:
                tag_occurrences.append((0, date))

        # Trier les occurrences par date
        artist_occurrences.sort(key=lambda x: x[1])
        track_occurrences.sort(key=lambda x: x[1])
        tag_occurrences.sort(key=lambda x: x[1])

    return artist_occurrences, track_occurrences, tag_occurrences


