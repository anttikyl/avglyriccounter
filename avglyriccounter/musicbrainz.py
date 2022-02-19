import requests
import threading
from time import sleep
import logging

log = logging.getLogger("avglyriccounter")

class MusicBrainzClient():
    """
    A class used to communicate with the MusicBrainz API.

    Wraps endpoints into easy to use methods.

    Only allows one request per second to honor MusicBrainz's rate limiting rules.
    """
    def __init__(self):
        self.base_url = "https://musicbrainz.org/ws/2/"
        self.headers = {
            'User-Agent': 'AKWordAverageCounter/1.0 ( anttikyl@protonmail.com )'
        }
        self.lock = threading.Lock()

    def __unlock_calls(self):
        """
        Releases this object's lock after one second.
        """
        sleep(1)
        self.lock.release()
        log.debug("Released MusicBrainzClient lock")

    def __make_request(self, url):
        """
        This method takes a lock and defers the release of the lock to one (1) second later.

        The MusicBrainz API has a restriction of 1 call per second per client. By using this method
        for every request, we ensure that we do not get blocked by making calls too frequently.
        """

        self.lock.acquire()
        log.debug("Acquired MusicBrainzClient lock")

        log.debug("Sending GET request to " + url)
        res = requests.get(url, headers=self.headers)

        # Set off a lock release with a 1s sleep timer in another thread
        unlock_thread = threading.Thread(target=self.__unlock_calls)
        unlock_thread.start()

        return res

    def search_artist(self, artist_name):
        """ /artist?query=artist:<ARTIST_NAME>

        Searches for an artist by their name

        :param      artist_name     name of the artist to search for

        :returns    json response body returned from MusicBrainz
        :raises     requests.HttpError if the returned HTTP status code was 4xx/5xx
        :raises     ValueError if the response is not decodable json
        """

        url = self.base_url + "artist/" + "?query=artist:" + artist_name + "&fmt=json"

        res = self.__make_request(url)
        res.raise_for_status()

        try:
            retval = res.json()
        except ValueError: # includes simplejson.decoder.JSONDecodeError
            raise ValueError # raise ValueError to abstract away simplejson

        return retval

    def get_artist_with_releases(self, artist_mbid):
        """ /artist/<MBID>?inc=releases

        Gets the artist entity including the artist's releases

        :param      artist_mbid     MBID of the artist to get

        :returns    json response body returned from MusicBrainz
        :raises     requests.HttpError if the returned HTTP status code was 4xx/5xx
        :raises     ValueError if the response is not decodable json
        """

        url = self.base_url + "artist/" + artist_mbid + "?inc=releases&fmt=json"

        res = self.__make_request(url)
        res.raise_for_status()

        try:
            retval = res.json()
        except ValueError: # includes simplejson.decoder.JSONDecodeError
            raise ValueError # raise ValueError to abstract away simplejson

        return retval

    def get_release_with_recordings(self, release_mbid):
        """ /release/<MBID>

        Gets the recording entity

        :param      release_mbid    MBID of the release to get

        :returns    json response body returned from MusicBrainz
        :raises     requests.HttpError if the returned HTTP status code was 4xx/5xx
        :raises     ValueError if the response is not decodable json
        """

        url = self.base_url + "release/" + release_mbid + "?inc=recordings&fmt=json"

        res = self.__make_request(url)
        res.raise_for_status()

        try:
            retval = res.json()
        except ValueError: # includes simplejson.decoder.JSONDecodeError
            raise ValueError # raise ValueError to abstract away simplejson

        return retval

class MusicBrainzHandlerError(Exception):
    pass

class MusicBrainzHandler():
    """
    Handler for abstracting MusicBrainz endpoint functionality
    """
    def __init__(self, client):
        self.client = client

    def get_artist_mbid(self, artist_name):
        """
        Gets the artist MBID by making a search in the MusicBrainz API

        :param      artist_name     name of the artist to search for

        :returns    artist MBID if artist was found, otherwise empty string
        :raises     MusicBrainzHandlerError on any caught exception
        """

        try:
            artist_json = self.client.search_artist(artist_name)

            if len(artist_json['artists']) > 0:
                # The artists received are in order of "score", with the highest being the best guess of what the search was after.
                # In terms of usability, the user could be given a chance to select one of the results to see if that's what they
                # meant, otherwise they will always get the most popular artist's results.
                artist_mbid = artist_json['artists'][0]['id']
            else:
                artist_mbid = ""
        except:
            raise MusicBrainzHandlerError

        log.info("Found artist MBID " + artist_mbid + " for artist " + artist_name)

        return artist_mbid

    def get_release_ids(self, artist_mbid):
        """
        Gets the releases for the given artist

        The returned list does not contain any album_ids that share the same name

        :param      artist_mbid     MBID of the artist whose releases to get

        :returns    list of release_ids, empty list if none found
        :raises     MusicBrainzHandlerError on any caught exception
        """

        try:
            releases_json = self.client.get_artist_with_releases(artist_mbid)

            releases = {}

            for release in releases_json['releases']:
                title = release['title'].lower()
                if title not in releases.keys():
                    # Only add unique album names
                    releases[title] = release['id']
        except:
            raise MusicBrainzHandlerError

        log.info("Found releases " + str(list(releases.keys())) + " for artist_mbid " + artist_mbid)

        return list(releases.values())

    def get_tracks(self, release_id):
        """
        Gets the tracks found on the given release

        :param      release_id      ID of the release whose tracks to get

        :returns    list of tracks on the given release
        :raises     MusicBrainzHandlerError on any caught exception
        """
        tracks = []

        try:
            recordings_json = self.client.get_release_with_recordings(release_id)

            # Traverse through the 'media' array, which contains for example CDs 
            for media in recordings_json['media']:
                # Add all the track on the media to a list
                for track in media['tracks']:
                    tracks.append(track['title'].lower())
        except:
            raise MusicBrainzHandlerError

        log.info("Found tracks " + str(tracks) + " for release_id " + release_id)

        return tracks