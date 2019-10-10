#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib2
import json
import os
import subprocess
import logging
import traceback
import yaml
from datetime import datetime
import dateutil.parser
from TwitterAPI import TwitterAPI
import eyed3
import ffmpeg

class Channel:
    def __init__(self, channel_id):
        channel_ids = channel_id.split(":")
        self.id = channel_ids[0]  # Channel Id(Ex: euphonium)

        if len(channel_ids) > 1:
            self.num_id = channel_id.split(u":")[1]  # Channel number Id(Ex: 540)
        else:
            self.num_id = u""  # Channel number Id(Ex: 540)

        self.count = u""            # Count
        self.sound_url = u""        # Sound URL
        self.m3u8_file_url= u""     # m3u8 file URL
        self.title = u""            # Title of Channel
        self.file_name = u""        # Original file Name
        self.updated_at = u""       # Update Date(String)
        self.thumb_url = u""        # thumbnail path(image)
        self.thumb_file_name = u""  # thumbnail file name

    def file_name_without_extension(self):
        arr = self.file_name.split(".")
        arr.pop()
        return ".".join(arr)

    def needs_to_use_new_api(self):
        return len(self.num_id) != 0

    # Load channel information from API
    def load_channel_info(self):
        # if num_id was specified, use new api

        if self.needs_to_use_new_api():
            bearer_token = UserSettings.get("bearer_token")
            if not bearer_token:
                raise BusinessException(u"Bearer Token is not specified in user_settings.yml.")

            try:
                url = u"https://app.onsen.ag/api/me/programs/" + self.num_id
                headers = {'Host': 'app.onsen.ag',
                           'X-Device-Os': 'ios',
                           'Accept': '*/*',
                           'Accept-Version': 'v3',
                           'Authorization': 'Bearer ' + bearer_token,
                           'X-Device-Name': 'XXX',
                           'Accept-Language': 'ja-JP;q=1.0',
                           'Content-Type': 'application/json',
                           'X-Device-Identifier': '876DD8394-3847-1123-9000-83746DDFA876',
                           'User-Agent': 'iOS/Onsen/2.6.1',
                           'X-App-Version': '25'
                    }
                
                req = urllib2.Request(url, None, headers)
                response = urllib2.urlopen(req)
            except urllib2.HTTPError, e:
                if e.code == 404:
                    message = "This channel may not be published."
                    raise BusinessException(message)
                else:
                    raise BusinessException(u"Unexpected error occured.")
            
            r_str = response.read()
            r_json = json.loads(r_str)
            latest_episode = (r_json["episodes"])[0]

            self.count = latest_episode["title"]
            self.m3u8_file_url = ((latest_episode["episode_files"])[0])["media_url"]
            self.title = r_json["title"]
            self.file_name = self.m3u8_file_url.split("/")[-2]
            self.updated_at = dateutil.parser.parse(latest_episode["updated_on"]).strftime('%Y.%m.%d')
            self.thumb_url = (r_json["program_image"])["video_url"]
            self.thumb_file_name = self.thumb_url.split("/")[-1]
           
        else:
            try:
                response = urllib2.urlopen(Utils.url_get_channel_info(self.id))
            except urllib2.HTTPError, e:
                if e.code == 404:
                    message = "This channel may not be published."
                    raise BusinessException(message)
            r_str = response.read().encode('utf-8')[9:-3]
            r_json = json.loads(r_str)

            self.count = r_json["count"]
            self.sound_url = (r_json["moviePath"])["pc"]
            self.title = r_json["title"]
            self.file_name = (r_json["moviePath"])["pc"].split("/")[-1]
            self.updated_at = r_json["update"]
            self.thumb_url = Consts.BASE_URL + r_json["thumbnailPath"]
            self.thumb_file_name = r_json["thumbnailPath"].split("/")[-1]


class Downloader:
    # Download Channel
    @staticmethod
    def downloadChannel(channel):
        
        dir_path = Utils.radio_save_dir_path(channel)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
    
        file_path = Utils.radio_save_file_path(channel)
        if os.path.exists(file_path):
            raise BusinessException("Already Downloaded:"
                                        + file_path)

        mp3_file_path = u""

        if channel.needs_to_use_new_api():
            # download m3u8 plist file with ffmpeg
            mp4_file_path = dir_path + channel.file_name 
            mp3_file_path = dir_path + channel.file_name_without_extension() + ".mp3"

            cmd = '''\
                ffmpeg \
                -protocol_whitelist file,http,https,tcp,tls,crypto \
                -i "{m3u8_file_url}" \
                -c copy {file_path}
                -user_agent "AppleCoreMedia/1.0.0.16A366 (iPhone; U; CPU OS 12_0 like Mac OS X; ja_jp)" \
                -headers "Accept: */*" \
                -headers "Accept-Language: ja-jp" \
                -headers "Accept-Encoding: gzip" \
                -headers "Connection: keep-alive" \
                -vn \
                '''.format(m3u8_file_url = channel.m3u8_file_url, file_path = mp4_file_path).strip()
            subprocess.call(cmd, shell=True)

            cmd = 'ffmpeg -y -i {mp4_file_path} -ab 192k {mp3_file_path}'.format(mp4_file_path = mp4_file_path, mp3_file_path = mp3_file_path)
            subprocess.call(cmd, shell=True)

        else:
            # download mp3 file directly
            try:
                response = urllib2.urlopen(channel.sound_url)
            except urllib2.HTTPError, e:
                if e.code == 404:
                    message = "This episode may not be published."
                    raise BusinessException(message)
                else:
                    raise BusinessException(u"Unexpected error occured.")
    
            mp3_file_path = dir_path + channel.file_name
            out = open(mp3_file_path, "wb")
            out.write(response.read())

        # embed id3 tag
        Utils.embed_id3_tag(mp3_file_path, channel)


    @staticmethod
    def download_thumbnail(channel):
        response = urllib2.urlopen(channel.thumb_url)
        tmp_dir_path = Utils.tmp_dir_path()
        thumb_file_path = tmp_dir_path + channel.thumb_file_name

        if not os.path.exists(tmp_dir_path):
            os.makedirs(tmp_dir_path)

        if os.path.exists(thumb_file_path):
            os.remove(thumb_file_path)

        out = open(thumb_file_path, "wb")
        out.write(response.read())

        return thumb_file_path


class Consts:
    BASE_URL = u"http://www.onsen.ag"
    BASE_URL_GET_CHANNEL_INFO = u"http://www.onsen.ag/data/api/getMovieInfo/{channel_id}"
    USER_SETTING_FILE_PATH = os.path.abspath(os.path.dirname(__file__)) + "/user_settings.yml"
    DEFAULT_ARTIST_NAME = u"onsen"
    DEFAULT_ALBUM_TITLE = u"{channel_title}"
    DEFAULT_TRACK_TITLE = u"第{count}回 ({update}更新)"


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
    def radio_save_dir_path(channel):
        home = os.environ['HOME']
        script_dir = os.path.abspath(os.path.dirname(__file__))
        path = UserSettings.get("radio_save_path")\
                           .replace("{channel_id}", channel.id)\
                           .replace("{channel_title}", channel.title)\
                           .replace("~", home)\
                           .replace("./", script_dir + "/")
        return path

    # File path to save channel
    @staticmethod
    def radio_save_file_path(channel):
        return Utils.radio_save_dir_path(channel) + channel.file_name

    # Dir path to save temporary files
    @staticmethod
    def tmp_dir_path():
        home = os.environ['HOME']
        script_dir = os.path.abspath(os.path.dirname(__file__))
        if UserSettings.get("tmp_dir_path") is None:
            path = script_dir + "/"
        else:
            path = UserSettings.get("tmp_dir_path")\
                               .replace("~", home)\
                               .replace("./", script_dir + "/")
        return path

    # URL to get channel info
    @staticmethod
    def url_get_channel_info(channel_id):
        return Consts.BASE_URL_GET_CHANNEL_INFO\
                     .replace("{channel_id}", channel_id)

    @staticmethod
    def embed_id3_tag(file_path, channel):
        cover_img_path = Downloader.download_thumbnail(channel)

        tag = eyed3.load(file_path).tag
        tag.version = eyed3.id3.ID3_V2_4
        tag.encoding = eyed3.id3.UTF_8_ENCODING
        tag.artist = Consts.DEFAULT_ARTIST_NAME
        tag.album_artist = Consts.DEFAULT_ARTIST_NAME
        tag.album = Consts.DEFAULT_ALBUM_TITLE\
                          .format(channel_title=channel.title)
        tag.title = Consts.DEFAULT_TRACK_TITLE\
                          .format(count=channel.count,
                                  update=channel.updated_at)

        tag.images.set(eyed3.id3.frames.ImageFrame.OTHER,
                       open(cover_img_path, "rb").read(),
                       "image/jpeg")

        try:
            tag.track_num = int(channel.count)
        except ValueError:
            tag.track_num = 0

        tag.save()


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
        message = u"録音が完了しました: 『{title} {count}話』 [{date}]"\
                  .format(title=channel.title,
                          count=channel.count,
                          date=datetime.now().strftime(u"%Y/%m/%d %H:%M"))
        self.post(message)

    def notify_dl_error(self, ch_id, message=None):
        if message is None:
            message = u"録音中に例外が発生しました: {ch_id},{date}".format(ch_id=ch_id, date=datetime.now().strftime(u"%Y/%m/%d %H:%M"))
        else:
            message = u"録音中に例外が発生しました: {ch_id},{date}:{message}".format(ch_id=ch_id, date=datetime.now().strftime(u"%Y/%m/%d %H:%M"), message=message)
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
        logging.info("Download begin.")

        channel_ids = UserSettings.get("channels")
        for c_id in channel_ids:
            logging.info("Downloading channel: " + c_id)
            try:
                c = Channel(c_id)
                c.load_channel_info()

                # Skip downloading if the downloaded-file already exists
                file_path = Utils.radio_save_file_path(c)
                if os.path.exists(file_path):
                    logging.info("Skipped downloading, because already downloaded: " + c_id)
                    continue
                
                Downloader.downloadChannel(c)

            except BusinessException, e:
                msg = "Not downloaded: " + c_id + ", because: " + e.value
                logging.info(msg)
                twitter.notify_dl_error(c_id, msg)
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
