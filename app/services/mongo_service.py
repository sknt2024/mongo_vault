from pymongo import MongoClient


def get_collections(uri: str, db_name: str):
    """
    Fetch all collection names from MongoDB using PyMongo.
    """

    try:
        client = MongoClient(uri)
        db = client[db_name]

        collections = db.list_collection_names()

        client.close()

        return sorted(collections)

    except Exception as e:
        print("Error fetching collections:", e)
        return []
