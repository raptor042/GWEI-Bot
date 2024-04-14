from pymongo import MongoClient
import certifi

import logging

def connect_db(uri : str):
    try:
        client = MongoClient(uri, tlsCAFile=certifi.where())
        db = client["GWEI"]
    except TimeoutError:
        logging.error("Cannot connect to database, may be due to poor network connectivity")
        connect_db(uri=uri)
    else:
        return db

def get_user(db, query : dict):
    try:
        user = db["users"].find_one(query)
    except TimeoutError:
        logging.error("Cannot get user data to database, may be due to poor network connectivity")
    else:
        return user

def set_user(db, value : dict):
    try:
        user = db["users"].insert_one(value)
    except TimeoutError:
        logging.error("Cannot post user data to database, may be due to poor network connectivity")
    else:
        return user

def update_user(db, query: dict, value: dict):
    try:
        user = db["users"].update_one(query, value)
    except TimeoutError:
        logging.error("Cannot update user data to database, may be due to poor network connectivity")
    else:
        return user
    
def delete_user(db, query: dict):
    try:
        user = db["users"].delete_one(query)
    except TimeoutError:
        logging.error("Cannot delete user data to database, may be due to poor network connectivity")
    else:
        return user