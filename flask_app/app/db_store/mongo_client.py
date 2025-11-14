from pymongo import MongoClient
from datetime import date

class MongoStore:
    def __init__(self, mongo_config):
        user = mongo_config["mdb_user"]
        passw = mongo_config["mdb_pw"]
        host = mongo_config["mdb_host"]
        db_name = mongo_config["mdb_db"]
    
        self.mongo_uri = f"mongodb://{user}:{passw}@{host}/{db_name}"
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[db_name]
        self.trip_reviews = self.db["trip_reviews"]

    # ---- CRUD ---- #

    # insert one
    def add_trip_review(self, trip_id, driver_id, passenger_id, rating=None, comment=None):
        """Insert a new trip review document."""
        review = {
            "trip_id": trip_id,
            "driver_id": driver_id,
            "passenger_id": passenger_id,
            "rating": rating,
            "comment": comment,
            "created_at": datetime.now(),
            "moderated": False,
        }
        result = self.trip_reviews.insert_one(review)
        return str(result.inserted_id)

    # read one
    def get_trip_review(self, review_id):
        """Retrieve a single trip review by its ObjectId."""
        return self.trip_reviews.find_one({"_id": ObjectId(review_id)})

    # read all, per trip
    def get_trip_reviews_for_trip(self, trip_id):
        """Retrieve all reviews for a given trip."""
        return list(self.trip_reviews.find({"trip_id": trip_id}))

    # update one
    def update_trip_review(self, review_id, update_fields):
        """Update specific fields of a trip review."""
        result = self.trip_reviews.update_one(
            {"_id": ObjectId(review_id)},
            {"$set": update_fields}
        )
        return result.modified_count > 0

    # delete
    def delete_trip_review(self, review_id):
        """Delete a trip review by its ObjectId."""
        result = self.trip_reviews.delete_one({"_id": ObjectId(review_id)})
        return result.deleted_count > 0

    # ---- UTILS ---- #

    def get_collections(self):
        """Return a list of all collection names."""
        return self.db.list_collection_names()

    def close(self):
        """Close the MongoDB client connection."""
        self.client.close()