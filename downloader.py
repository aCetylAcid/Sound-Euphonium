#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib2
import json
import os
import logging
import traceback
import yaml
from datetime import datetime
from TwitterAPI import TwitterAPI


class Channel:
    def __init__(self, channel_id):
        self.id = channel_id   # Channel Id(Ex: euphonium)
        self.count = 0         # Count
        self.sound_url = u""   # Sound URL
        self.title = u""       # Title of Channel
        self.file_name = u""   # Original file Name
        self.updated_at = u""  # Update Date(String)

    # Load channel information from API
    def load_channel_info(self):
        response = urllib2.urlopen(Utils.url_get_channel_info(self.id))
        r_str = response.read().encode('utf-8')[9:-3]
        r_json = json.loads(r_str)

        self.count = int(r_json["count"])
        self.sound_url = (r_json["moviePath"])["pc"]
        self.title = r_json["title"]
        self.file_name = (r_json["moviePath"])["pc"].split("/")[-1]
        self.updated_at = r_json["update"]


class Downloader:
    # 番組をダウンロードする
    @staticmethod
    def downloadChannel(channel):
        response = urllib2.urlopen(channel.sound_url)

        dir_path = Utils.radio_save_path(channel)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        file_path = dir_path + channel.file_name
        if os.path.exists(file_path):
            raise BusinessException("Already Downloaded:"
                                    + file_path)

        out = open(dir_path + channel.file_name, "wb")
        out.write(response.read())


class Consts:
    BASE_URL_GET_CHANNEL_INFO = u"http://www.onsen.ag/data/api/getMovieInfo/{channel_id}"
    USER_SETTING_FILE_PATH = os.path.abspath(os.path.dirname(__file__)) + "/user_settings.yml"


class UserSettings:
    @staticmethod
    def get(key):
        # load setting file
        setting_file = open(Consts.USER_SETTING_FILE_PATH, "r")
        settings = yaml.load(setting_file)
        if key in settings:
            return settings[key]
        else:
            return None


class Utils:
    # Dir path to save channel
    @staticmethod
    def radio_save_path(channel):
        return UserSettings.get("radio_save_path").format(channel_id=channel.id)

    # URL to get channel info
    @staticmethod
    def url_get_channel_info(channel_id):
        return Consts.BASE_URL_GET_CHANNEL_INFO.format(channel_id=channel_id)


class BusinessException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Twitter:
    def __init__(self, consumer_key="", consumer_secret="", access_token_key="",
                 access_token_secret=""):
        if consumer_key and consumer_secret and access_token_key\
           and access_token_secret:
            self.enabled = True
            self.api = TwitterAPI(consumer_key, consumer_secret,
                                  access_token_key, access_token_secret)
            self.in_reply_to = None
        else:
            self.enabled = False
            self.api = None
            self.in_reply_to = None

    def post(self, message):
        if self.enabled is not True:
            return
        else:
            if self.in_reply_to is not None and self.in_reply_to != "":
                message = u"@{user_id} {message}"\
                          .format(user_id=self.in_reply_to, message=message)
            self.api.request('statuses/update', {'status': message})

    def set_in_reply_to(self, in_reply_to):
        self.in_reply_to = in_reply_to

    def notify_dl_completion(self, channel):
        message = u"録画が完了しました: 『{title} {count}話』 [{date}]"\
                  .format(title=channel.title,
                          count=channel.count,
                          date=channel.updated_at)
        self.post(message)

    def notify_dl_error(self, ch_id):
        message = u"録画中に例外が発生しました: {ch_id},{date}".format(ch_id=ch_id,
                  date=datetime.now().strftime(u"%Y/%m/%d/ %H:%M"))
        self.post(message)


class Main:
    @staticmethod
    def main():
        # Setup loggin
        logging.basicConfig(format='[%(levelname)s]%(asctime)s %(message)s',
                            filename='info.log',
                            level=logging.INFO)

        # Setup notification
        if UserSettings.get("twitter_settings") is not None:
            tw_settings = UserSettings.get("twitter_settings")
            twitter = Twitter(tw_settings["consumer_key"],
                              tw_settings["consumter_secret"],
                              tw_settings["access_token_key"],
                              tw_settings["access_token_secret"])
            if tw_settings["in_reply_to"] is not None:
                twitter.set_in_reply_to(tw_settings["in_reply_to"])
        else:
            twitter = Twitter()

        # Download all channels
        logging.info("Donwload begin.")

        channel_ids = UserSettings.get("channels")
        for c_id in channel_ids:
            logging.info("Downloading channel: " + c_id)
            try:
                c = Channel(c_id)
                c.load_channel_info()
                Downloader.downloadChannel(c)
            except BusinessException, e:
                logging.info("Not downloaded: " + c_id + ", because: " + e.value)
            except Exception, e:
                logging.error("Download interrupted: " + c_id)
                logging.error(traceback.format_exc())
                twitter.notify_dl_error(c_id)
            else:
                logging.info("Download complete: " + c_id)
                twitter.notify_dl_completion(c)

        logging.info("Download finish.")


if __name__ == "__main__":
    Main.main()
