#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib2
import json
import os
import logging
import traceback


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
            raise EuphException("Already Downloaded:" + file_path)

        out = open(dir_path + channel.file_name, "wb")
        out.write(response.read())


class Consts:
    TARGET_CHANNELS = [u"euphonium", u"gg"]
    BASE_URL_GET_CHANNEL_INFO = u"http://www.onsen.ag/data/api/getMovieInfo/{channel_id}"
    RADIO_SAVE_PATH = u"./radio/{channel_id}/"


class Utils:
    # Dir path to save channel
    @staticmethod
    def radio_save_path(channel):
        return Consts.RADIO_SAVE_PATH.format(channel_id=channel.id)

    # URL to get channel info
    @staticmethod
    def url_get_channel_info(channel_id):
        return Consts.BASE_URL_GET_CHANNEL_INFO.format(channel_id=channel_id)


class EuphException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


if __name__ == "__main__":
    # Setup loggin
    logging.basicConfig(format='%(asctime)s %(message)s',
                        filename='dl.log',
                        level=logging.DEBUG)

    # Download all TARGET_CHANNELS
    logging.info("Donwload begin.")

    channel_ids = Consts.TARGET_CHANNELS
    for c_id in channel_ids:
        logging.info("Downloading channel: " + c_id)
        try:
            c = Channel(c_id)
            c.load_channel_info()
            Downloader.downloadChannel(c)
            logging.info("Download complete: " + c_id)
        except Exception, e:
            logging.info("Download interrupted: " + c_id)
            logging.error("\n" + traceback.format_exc())

    logging.info("Download finish.")
