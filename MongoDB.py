import pymongo
from pymongo import MongoClient


class database:

    def __init__(self, cluster, collection, dataB):
        self.client = MongoClient(cluster)
        self.collection = self.client[collection]
        self.database = self.collection[dataB]


    def __get_all_info(self, ID):
        self.ALL_INFO = self.database.find_one({"_id": ID})

    def update_element(self, ID, key, value):
        self.database.find_one_and_update({"_id": ID}, {"$set": {key: value}})

    def get_element(self, ID, key):
        self.__get_all_info(ID)
        return self.ALL_INFO[key]

    def add_element(self, ID, **kwargs):
        self.database.insert_one({"_id": ID, **kwargs})

    def containsID(self, ID):
        contains = self.database.find_one({"_id": ID})
        return contains is not None

    def delete_query(self, ID):
        self.database.delete_one({"_id": ID})


