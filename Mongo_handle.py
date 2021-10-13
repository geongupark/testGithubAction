import pymongo
import sys


def raise_error(error_desc):
    raise Exception(
        str.format(
            error_desc + " (function : {0})",
            sys._getframe(1).f_code.co_name,
        )
    )


class MongoMgr:
    def __init__(self, mongo_url, mongo_db, mongo_col, auth):
        """
        auth : user_name:passwd
        """
        self.mongo_info = self.init_mongo_info(mongo_url, mongo_db, mongo_col, auth)
        self.conn = None
        self.db = None
        self.col = None
        self.connect_mongo()

    def init_mongo_info(self, mongo_url, mongo_db, mongo_col, auth):
        mongo_info = {
            "mongo_url": mongo_url,
            "mongo_db": mongo_db,
            "mongo_col": mongo_col,
            "mongo_auth": auth,
        }
        return mongo_info

    def connect_mongo(self):
        try:
            url = (
                "mongodb://"
                + self.mongo_info["mongo_auth"]
                + "@"
                + self.mongo_info["mongo_url"]
            )
            print("mongodb://" + self.mongo_info["mongo_auth"] + "@" + self.mongo_info["mongo_url"])
            print("mongodb://", self.mongo_info["mongo_auth"], "@", self.mongo_info["mongo_url"])
            print(self.mongo_info["mongo_auth"] + "@" + self.mongo_info["mongo_url"])
            print("mongodb://" + self.mongo_info["mongo_auth"] + "@")
            print("hi : ", url)
            self.conn = pymongo.MongoClient(url, 27017)
            self.db = self.conn[self.mongo_info["mongo_db"]]
            self.col = self.db[self.mongo_info["mongo_col"]]
        except Exception:
            raise_error("MongoDB Connection fail...")

    def insert_one_in_col(self, document):
        self.col.insert_one(document)

    def upsert_in_col(self, document):
        self.col.update(document, document, upsert=True)

    def find_all_in_col(self):
        return self.col.find({}, {"_id": False})

    # def add_to_set_in_col(self, document):
    #     self.col.update()


if __name__ == "__main__":
    mongo_mgr = MongoMgr(
        "192.168.35.51",
        "sise",
        "daily",
        "gus" + ":" + "1q2w3e4r",
    )

    mongo_mgr.insert_one_in_col({"num": 1, "data": "hi"})
