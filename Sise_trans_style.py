from urllib import parse
from urllib.parse import urlparse, urljoin
from Parser_bot import ParserMgr
from Mongo_handle import MongoMgr
import configparser
import os
import sys
import dateutil.parser
import pymongo
import json

CONFIG_FILE_NAME = "sise_trans_style.cfg"
YEAR_MSB = 20000000


def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print("Error: Creating directory. " + directory)


def raise_error(error_desc):
    raise Exception(
        str.format(
            error_desc + " (function : {0})",
            sys._getframe(1).f_code.co_name,
        )
    )


class TransStyleMgr:
    def __init__(self, config_file_name):
        self.base_file_path = os.path.dirname(os.path.realpath(__file__))
        self.config_file_path = ""
        self.config_mgr = self.init_config_mgr(config_file_name)
        self.main_url_info = self.get_url_info(self.config_mgr["common"]["main_url"])

    def init_config_mgr(self, config_file_name):
        config = configparser.ConfigParser()
        self.config_file_path = os.path.join(self.base_file_path, config_file_name)
        ret = config.read(self.config_file_path)
        if len(ret) == 0:
            raise Exception("Strange config file")
        return config

    def get_url_info(self, url):
        return urlparse(url)

    def get_trend_url(self, type):
        if type in self.config_mgr.sections():
            parse_mgr = ParserMgr()
            ret = parse_mgr.get_target_data(
                self.config_mgr["common"]["main_url"],
                "euc-kr",
            )
            if ret < 0:
                raise_error("Cannot parse data in target url")
            else:
                self.config_mgr[type]["url"] = urljoin(
                    base=self.main_url_info.scheme + "://" + self.main_url_info.netloc,
                    url=parse_mgr.soup_html.select(self.config_mgr[type]["key"])[0][
                        "src"
                    ],
                )

                with open(self.config_file_path, "w") as cfg_file:
                    self.config_mgr.write(cfg_file)
        else:
            raise_error("Strange section name in config file")

    def get_trend_end_page(self, type):
        if type in self.config_mgr.sections():
            parse_mgr = ParserMgr()
            ret = parse_mgr.get_target_data(
                self.config_mgr[type]["url"],
                "euc-kr",
            )
            if ret < 0:
                raise_error("Cannot parse data in target url")
            else:
                self.config_mgr[type]["end_page"] = parse_mgr.soup_html.select(
                    ".pgRR > a"
                )[0]["href"].split("page=")[1]

                with open(self.config_file_path, "w") as cfg_file:
                    self.config_mgr.write(cfg_file)
        else:
            raise_error("Strange section name in config file")

    def make_mongo_mgr(self, col_type):
        return MongoMgr(
            self.config_mgr["common"]["mongo_url"],
            self.config_mgr["common"]["mongo_db"],
            self.config_mgr[col_type]["mongo_col"],
            self.config_mgr["common"]["mongo_auth"],
        )

    def analyze_page_table(self, parse_mgr, type):
        mongo_mgr = self.make_mongo_mgr(type)
        item_name = self.config_mgr[type]["item_name"].split(",")
        table_data = parse_mgr.soup_html.select(".type_1 > tr")[3:]

        for row in table_data:
            cur_document = {}
            if len(row.select("td")) != len(item_name):
                continue

            for idx, col in enumerate(row.select("td")):
                # if item_name[idx] == "날짜":
                #     cur_document[item_name[idx]] = dateutil.parser.parse(
                #         str(YEAR_MSB + int(col.text.replace(".", "")))
                #     )
                # else:
                cur_document[item_name[idx]] = col.text.replace(",", "")
            mongo_mgr.upsert_in_col(cur_document)

    def get_trend_table(self, type):
        # cur_time = datetime.datetime.now()
        if type in self.config_mgr.sections():
            for page_num in range(1, int(self.config_mgr[type]["end_page"]) + 1):
                parse_mgr = ParserMgr()
                ret = parse_mgr.get_target_data(
                    self.config_mgr[type]["url"] + "&page=" + str(page_num),
                    "euc-kr",
                )
                if ret < 0:
                    raise_error("Cannot parse in target page:" + str(page_num))
                else:
                    self.analyze_page_table(parse_mgr, type)
        else:
            raise_error("Strange section name in config file")

    def save_mongo_to_json(self, type):
        mongo_mgr = self.make_mongo_mgr(type)
        curs = mongo_mgr.find_all_in_col().sort([("날짜", pymongo.ASCENDING)])
        data_list = []

        for cur in curs:
            data_list.append(cur)

        createFolder("json")
        with open("json/" + type + ".json", "w+", encoding="UTF-8-sig") as f_file:
            f_file.write("param = ")
            json.dump(data_list, f_file, ensure_ascii=False, indent=4)

    def run_parsing_daily(self):
        self.get_trend_url("daily")
        self.get_trend_end_page("daily")
        # self.get_trend_table("daily")
        self.save_mongo_to_json("daily")

    def run_parsing(self):
        self.run_parsing_daily()


if __name__ == "__main__":
    ts_mgr = TransStyleMgr(CONFIG_FILE_NAME)
    ts_mgr.run_parsing()
