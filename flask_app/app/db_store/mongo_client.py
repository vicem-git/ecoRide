from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.errors import InvalidId
from datetime import datetime

class MongoStore:
    def __init__(self, mongo_config):
        user = mongo_config["mdb_user"]
        passw = mongo_config["mdb_pw"]
        host = mongo_config["mdb_host"]
        db_name = mongo_config["mdb_db"]
    
        self.mongo_uri = f"mongodb://{user}:{passw}@{host}/{db_name}"
        self.client = MongoClient(
            self.mongo_uri,
            uuidRepresentation="standard"
        )
        self.db = self.client[db_name]
        self.trip_reviews = self.db["trip_reviews"]

    # ---- CRUD ---- #

    # insert one
    def add_trip_review(self, trip_id, driver_id, passenger_id, trip_evaluation, driver_rating=None, review_comment=None, moderated=False):
        review = {
            "trip_id": trip_id,
            "driver_id": driver_id,
            "passenger_id": passenger_id,
            "trip_evaluation": trip_evaluation,
            "driver_rating": driver_rating,
            "review_comment": review_comment,
            "created_at": datetime.now(),
            "moderated": moderated,
        }
        try:
            result = self.trip_reviews.insert_one(review)
        except Exception as e:
            logger.warning(f"ERROR: review insertion failed")
        return str(result.inserted_id) if result else None

    def get_reviews_by_status(self, moderated, batch, filter=None):
        query = {"moderated": moderated}
        if filter is not None:
            query["trip_evaluation"] = filter

        return self.trip_reviews.find(query).limit(batch).sort("created_at", -1)


    # read one
    def get_trip_review(self, review_id):
        try: 
            return self.trip_reviews.find_one({"_id": ObjectId(review_id)})
        except InvalidId:
            return None
        
    def has_reviewed_trip(self, passenger_id, trip_id):
        return self.trip_reviews.find_one({
            "trip_id": trip_id,
            "passenger_id": passenger_id,
        }) is not None
        
    # read all, per trip
    def get_trip_reviews_for_trip(self, trip_id):
        return list(self.trip_reviews.find({"trip_id": trip_id}))

    # update one
    def update_trip_review(self, review_id, update_fields):
        result = self.trip_reviews.update_one(
            {"_id": ObjectId(review_id)},
            {"$set": update_fields}
        )
        return result.modified_count > 0

    # delete
    def delete_trip_review(self, review_id):
        try:
            result = self.trip_reviews.delete_one({"_id": ObjectId(review_id)})
            return result.deleted_count > 0
        except InvalidId:
            return None
    # ---- UTILS ---- #

    def get_collections(self):
        return self.db.list_collection_names()

    def close(self):
        self.client.close()
