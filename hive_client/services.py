# -*- coding: utf-8 -*-
"""
Services to

1. Download a video and register it with the index.html once completed
"""
import config as settings

import os
import json
import requests


def getserial():
    # Extract serial from cpuinfo file
    cpuserial = "0000000000000000"
    try:
        with open('/proc/cpuinfo', 'r') as f:
            for line in f:
                if line[0:6] == 'Serial':
                    cpuserial = line[10:26]
    except Exception as e:
        cpuserial = "ERROR000000000:%s" % e

    return cpuserial


class BoxApiService(object):
    """
    Service registers this box/client with the core server
    """
    FEED_PATH = os.path.join(settings.MEDIA_PATH, 'playlist.json')
    MAC_ADDRESS = settings.MAC_ADDR

    def register(self, **kwargs):
        project_slug = kwargs.get('project', None)  # project_slug to register with

        data = {
            'device_id': getserial(),
            'mac_address': self.MAC_ADDRESS,
            'project': project_slug,
        }
        url = '%s%s' % (settings.CORE_SERVER_ENDPOINT,
                        'box/register/')
        print(url)
        print(data)
        # resp = requests.post(url, data=data)
        # return resp
        return {}

    def update_playlist(self, **kwargs):
        url = '%s%s' % (settings.CORE_SERVER_ENDPOINT,
                        'box/%s/playlist/' % settings.MAC_ADDR)

        resp = requests.get(url)
        data = resp.json()

        with open(self.FEED_PATH, 'w') as playlist:
            playlist.write(resp.content)

        return data

    def read_playlist(self, **kwargs):
        return json.loads(open(self.FEED_PATH, 'r').read().decode('utf-8'))


class ProcessFeedMediaService(object):
    def __init__(self, feed):
        if not getattr(feed, 'read', False):
            raise Exception('Expecting an open file ready for reading')

        self.feed = json.loads(feed.read().decode('utf8'))

    def process(self):
        """
        download media extracted from the feed
        """
        for i, item in enumerate(self.feed.get('feed', [])):

            for url in [item.get('picture'), item.get('video')]:
                if url:
                    media = {
                        'id': item.get('id'),
                        'url': url
                    }

                    s = DownloadMediaService(video=media)
                    file_path, download_result = s.process()

                    print('File: %s Download Result: %s' % (file_path, download_result))


class DownloadMediaService(object):
    def __init__(self, video, **kwargs):
        self.video = video

    def process(self, **kwargs):
        video_url = kwargs.pop('video_url', self.video.get('url'))

        filename = os.path.basename(video_url)
        file_path = os.path.join(settings.MEDIA_PATH, filename)

        message = 'File already exists: %s' % filename

        #if not os.path.exists(file_path):
        try:
            self.save(video_url, file_path)
            message = 'File downloaded: %s' % filename

        except Exception as e:
            message = 'File not downloaded: %s' % e

        #logger.info('%s : %s ' % (file_path, message))
        return file_path, message

    def save(self, video_url, file_path):
        #logger.debug('Saving %s to %s' % (video_url, file_path))
        with open(file_path, 'wb') as handle:
            resp = requests.get(video_url, stream=True)

            if not resp.ok:
                raise Exception('Download Error: %s %s' % (resp, video_url))

            for block in resp.iter_content(1024):
                if not block:
                    break

                handle.write(block)
