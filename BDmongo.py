import pymongo 
from datetime import datetime
from collections import defaultdict
from pymongo import MongoClient

client = pymongo.MongoClient("mongodb://localhost:27017/")

db = client["SD2024_projet"]


def initialize_admin(username, mdp):
    collection = db["GAMMA_admins"]
    admin_existe = collection.find_one({"username": username})
    if admin_existe == None:
        ToIndex = False
        if collection.count_documents({})==0:
            ToIndex=True  
        user_infos = {
        "username": username,
        "mot_de_passe": mdp
        }
        collection.insert_one(user_infos)
        if ToIndex:
            collection.create_index({"username": 1}, unique=True)
        print("Données de l'admin insérées avec succès dans la collection GAMMA_admins.")

######################
#fonctions pour artiste
def getAll_artists():
    collection = db["GAMMA_artists"]
    local_artists = collection.find()
    return local_artists

def check_artist_in_db(artist):
    collection = db["GAMMA_artists"]
    artist_info_from_db = collection.find_one({"name": artist})
    return artist_info_from_db

def insert_artist_info_into_db(artist_info):
    collection = db["GAMMA_artists"]
    ToIndex = False
    existing_document = collection.find_one({"name": artist_info["name"]})
    if collection.count_documents({})==0:
        ToIndex=True

    if existing_document:
        print("Le document existe déjà dans la collection GAMMA_artists. Pas besoin d'insérer à nouveau.")
    else:
        collection.insert_one(artist_info)
        if ToIndex:
            collection.create_index({"name": 1},)

        print("Données de l'artiste insérées avec succès dans la collection GAMMA_artists.")
#####################
#fonctions pour tag
def check_tag_in_db(tag_name):
    collection = db["GAMMA_tags"]
    tag_info_from_db = collection.find_one({"name": tag_name})

    return tag_info_from_db

def insert_tag_info_into_db(tag_info):
    collection = db["GAMMA_tags"]
    ToIndex = False
    existing_document = collection.find_one({"name": tag_info["name"]})
    if collection.count_documents({})==0:
        ToIndex=True
    if existing_document:
        print("Le document existe déjà dans la collection GAMMA_tags. Pas besoin d'insérer à nouveau.")
    else:
        
        collection.insert_one(tag_info)
        if ToIndex:
            collection.create_index({"name": 1})

        print("Données du tag insérées avec succès dans la collection GAMMA_tags.")

######################
#fonctions pour albums 
def getAll_albums():
    collection = db["GAMMA_albums"]
    local_albums = collection.find()
    return local_albums


def check_album_in_db(artist_name, album_name):
    collection = db["GAMMA_albums"]
    album_info_from_db = collection.find_one({"artist": artist_name, "name": album_name})
    return album_info_from_db



def insert_album_info_into_db(album_info):
    collection = db["GAMMA_albums"]
    ToIndex = False
    if collection.count_documents({})==0:
        ToIndex=True
    existing_document = collection.find_one({"name": album_info["name"],"artist": album_info["artist"]})
    if existing_document:
        print("Le document existe déjà dans la collection GAMMA_albums. Pas besoin d'insérer à nouveau.")
    else:
        collection.insert_one(album_info)
        if ToIndex:
            collection.create_index({"name": 1})

        print("Données de l'album insérées avec succès dans la collection GAMMA_albums.")

######################
#fonctions pour tracks 
def getAll_tracks():
    collection = db["GAMMA_tracks"]
    local_tracks = collection.find()
    return local_tracks

def check_track_in_db(artist_name, track_name):
    collection = db["GAMMA_tracks"]
    track_info_from_db = collection.find_one({"artist": artist_name, "track": track_name})
    return track_info_from_db

def insert_track_info_into_db(track_info):
    collection = db["GAMMA_tracks"]
    ToIndex = False
    if collection.count_documents({})==0:
        ToIndex=True
    existing_document = collection.find_one({"name": track_info["name"],"artist": track_info["artist"]})
    if existing_document:
        print("Le document existe déjà dans la collection GAMMA_tracks. Pas besoin d'insérer à nouveau.")
    else:
        collection.insert_one(track_info)
        if ToIndex:
            collection.create_index({"name": 1})

        print("Données de l'track insérées avec succès dans la collection GAMMA_tracks.")



########################
#fonction pour les similarité
def check_similiarite_in_db(artist, track):
    collection = db["GAMMA_similaire"]
    ToIndex = False
    track_info_from_db = collection.find_one({"artist": artist, "track": track})
    if track_info_from_db:
        return track_info_from_db["similar_tracks"]
    else:
        return None

def insert_similaire_info_into_db(tracks_info, artist, track):
    collection = db["GAMMA_similaire"]
    ToIndex = False
    if collection.count_documents({})==0:
        ToIndex=True
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
        if ToIndex:
            collection.create_index({"track": 1})

        print("Données des pistes similaires insérées avec succès dans la collection GAMMA_similaire.")

######################
#fonctions pour AVIS 
def insert_avisTag_into_db(username, note, comment, nameTag):
    collection = db["GAMMA_avis"]
    ToIndex = False
    if collection.count_documents({})==0:
        ToIndex=True
    existing_document = collection.find_one({"username": username, "tag_name": nameTag})
    if existing_document:
        # Le document existe déjà, mettez à jour les valeurs de note et de commentaire
        new_values = {"$set": {"note": note, "comment": comment}}
        collection.update_one({"username": username, "tag_name": nameTag}, new_values)
        print("Le document a été mis à jour avec succès dans la collection GAMMA_avis.")
    else:
        # Le document n'existe pas encore, insérez un nouveau document
        avis_info = {
            "username": username,
            "note": note,
            "comment": comment,
            "option": "tag",
            "tag_name": nameTag
        }
        collection.insert_one(avis_info)
        if ToIndex:
            collection.create_index([("username", 1), ("option", 1), ("tag_name", 1)], unique=True)

        print("Données de l'avis insérées avec succès dans la collection GAMMA_avis.")

def insert_avis_into_db(username,note,comment,option, name, artist):
    collection = db["GAMMA_avis"]
    ToIndex = False
    if collection.count_documents({})==0:
        ToIndex=True
    existing_document = collection.find_one({"username": username, "option": option,"oeuvrage": name, "artist" : artist})
    if existing_document:
        # Le document existe déjà, mettez à jour les valeurs de note et de commentaire
        new_values = {"$set": {"note": note, "comment": comment}}
        collection.update_one({"username": username, "option": option,"oeuvrage": name, "artist" : artist}, new_values)
        print("Le document a été mis à jour avec succès dans la collection GAMMA_avis.")
    else:
        avis_info = {
            "username": username,
            "note": note,
            "comment": comment,
            "option": option,
            "oeuvrage": name,
            "artist" : artist
        }
        collection.insert_one(avis_info)
        if ToIndex:
            collection.create_index([("username", 1), ("option", 1), ("oeuvrage", 1), ("artist", 1)], unique=True)
        print("Données de l'avis insérées avec succès dans la collection GAMMA_avis.")


#########################
#fonction LOG
def insert_log_consultation(type_consultation, date):
    consultation_collection = db["GAMMA_LOG"]
    existing_document = consultation_collection.find_one({"type": type_consultation, "date":date})
    ToIndex = False
    if consultation_collection.count_documents({})==0:
        ToIndex=True

    if existing_document:
        print("Le document existe déjà dans la collection GAMMA_LOG. Pas besoin d'insérer à nouveau.")
    else:
        consultation_data = {
            "type": type_consultation,
            "date": date,
        }
    
        consultation_collection.insert_one(consultation_data)
        if ToIndex:
            consultation_collection.create_index([("date", 1), ("type_consultation", 1)])

def get_log_consultation(type_consult):
    consultation_collection = db["GAMMA_LOG"]
    data = consultation_collection.find({"type": type_consult})
    return data

######### CLASSEMENT INSERTION
def insert_classement(infos_classement, date,type_chart):
    classement_collection = db["GAMMA_CHART"]
    existing_document = classement_collection.find_one({"type_chart": type_chart, "date":date})
    ToIndex = False
    if classement_collection.count_documents({})==0:
        ToIndex=True
    if existing_document:
        print("Le document existe déjà dans la collection GAMMA_CHART. Pas besoin d'insérer à nouveau.")
    else:
        classement_data = {
            "classement": infos_classement,
            "date" : date,
            "type_chart" : type_chart
        }
        classement_collection.insert_one(classement_data)
        if ToIndex:
            classement_collection.create_index([("date", 1), ("type_chart", 1)])

def get_classement(type_consult,date_cible):
    classement_collection = db["GAMMA_CHART"]
    data = classement_collection.find_one({"date": date_cible, "type_chart":type_consult })
    return data.get("classement")

######## users 
def check_user_in_db(username):
    collection = db["GAMMA_users"]
    username_from_db = collection.find_one({"username": username})
    return username_from_db

def insert_user_into_db(username, mdp, nom, prenom):  
    collection = db["GAMMA_users"]
    ToIndex = False
    if collection.count_documents({})==0:
        ToIndex=True  
    role = "regular"
    user_infos = {
    "username": username,
    "mdp": mdp,
    "role": role,
    "nom": nom,
    "prenom": prenom
    }
    collection.insert_one(user_infos)
    if ToIndex:
        collection.create_index({"username": 1}, unique=True)
    print("Données des pistes similaires insérées avec succès dans la collection GAMMA_similaire.")

def get_user_role(username):
    collection = db["GAMMA_users"]
    existing_user = collection.find_one({"username": username})
    if existing_user:
        return collection.find_one({"username": username}).get("role")
    else:
        print("username doesnt existe to check his role")


def check_connexion(username, mdp):
    #il verifie si le mdp parametre est correspand au mdp stocké 
    user = check_user_in_db(username)
    if user:
        # Récupérer le mot de passe stocké dans la base de données
        mdp_db = user.get("mdp")
        # Comparer le mot de passe fourni avec celui stocké dans la base de données
        if mdp == mdp_db:
            return user  # Le mot de passe correspond
    return False  # Aucun utilisateur trouvé ou mot de passe incorrect

## 