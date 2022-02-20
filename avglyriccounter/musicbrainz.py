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

    def search_artist_release_groups(self, artist_name, **kwargs):
        """ /release-group/?query=artist:<ARTIST>

        Searches for an artist's release groups by artist name

        :param      artist_name             name of the artist to search for

        Kwargs:
            exclude_live (bool)             whether to exclude live releases from the search
            exclude_compilation (bool)      whether to exclude compilation releases from the search
            exclude_remix (bool)            whether to exclude remix releases from the search
            exclude_demo  (bool)            whether to exclude demo releases from the search

        :returns    json response body returned from MusicBrainz
        :raises     requests.HttpError if the returned HTTP status code was 4xx/5xx
        :raises     ValueError if the response is not decodable json
        """

        url = self.base_url + "release-group?limit=100&fmt=json&query=artist:" + artist_name + " AND primarytype:\"album\""
        if 'exclude_live' in kwargs and kwargs['exclude_live'] == True:
            url += " AND NOT secondarytype:\"Live\""

        if 'exclude_compilation' in kwargs and kwargs['exclude_compilation'] == True:
            url += " AND NOT secondarytype:\"Compilation\""

        if 'exclude_remix' in kwargs and kwargs['exclude_remix'] == True:
            url += " AND NOT secondarytype:\"Remix\""

        if 'exclude_demo' in kwargs and kwargs['exclude_demo'] == True:
            url += " AND NOT secondarytype:\"Demo\""

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
        :raises     TypeError if the arg is not a string
        """

        if type(artist_name) != str:
            raise TypeError("Unsupported type for arg 'artist_name'")

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

    def __is_valid_release_group(self, release_group, artist_mbid):
        """
        Validates a release group against an artist's mbid

        :param      release_group   json contents of a single entry of 'release-group'
        :param      artist_mbid     MBID of the artist whose releases to filter by

        :returns    True if the release group is valid for the given artist, otherwise False
        :raises     MusicBrainzHandlerError on any caught exception
        :raises     TypeError if the args are not strings
        """

        # If the artist_mbid is not in the artist credits for the release group, it's not valid
        is_same_artist_id = False
        for artist_credit in release_group['artist-credit']:
            if artist_mbid == artist_credit['artist']['id']:
                is_same_artist_id = True

        if is_same_artist_id == False:
            return False

        return True

    def get_release_ids(self, artist_name, artist_mbid):
        """
        Gets the artist's release_ids

        Using release-groups we get unique releases by picking the first index release in the
        'releases' array of the response.

        :param      artist_name     name of the artist to search for
        :param      artist_mbid     MBID of the artist whose releases to filter by

        :returns    release_ids for the artist
        :raises     MusicBrainzHandlerError on any caught exception
        :raises     TypeError if the args are not strings
        """

        if type(artist_name) != str and type(artist_mbid) != str:
            raise TypeError("Unsupported type for args 'artist_name' and 'artist_mbid'")

        releases = {}

        try:
            # A single search returns 100 results, but with compilation and live albums removed from the equation, it is very
            # likely that all of the releases are included in the results.
            # TODO: browse results by using an offset until all results have been checked
            artist_json = self.client.search_artist_release_groups(artist_name, exclude_compilation=True, exclude_live=True, exclude_remix=True, exclude_demo=True)

            for release_group in artist_json['release-groups']:
                if self.__is_valid_release_group(release_group, artist_mbid):
                    title = release_group['title'].lower()
                    releases[title] = release_group['releases'][0]['id']
        except:
            raise MusicBrainzHandlerError

        log.info("Found releases " + str(list(releases.keys())) + " for artist_name " + artist_name)

        return list(releases.values())

    def get_tracks(self, release_id, exclusion_filters):
        """
        Gets the tracks found on the given release, in lower case characters

        :param      release_id          ID of the release whose tracks to get
        :param      exclusion_filters   list of strings to use to exclude tracks with at least one of them in the title

        :returns    list of tracks on the given release
        :raises     MusicBrainzHandlerError on any caught exception
        :raises     TypeError if the arg is not a string
        """

        if type(release_id) != str:
            raise TypeError("Unsupported type for arg 'release_id'")

        tracks = []

        try:
            recordings_json = self.client.get_release_with_recordings(release_id)

            tracks_on_release = 0
            # Traverse through the 'media' array, which contains for example CDs 
            for media in recordings_json['media']:
                tracks_on_release += len(media['tracks'])
                # Add all the track on the media to a list
                for track in media['tracks']:
                    track_title = track['title'].lower()
                    # Don't add tracks with any of the exclusion filters in their titles
                    if not any(x in track_title for x in exclusion_filters):
                        tracks.append(track_title)
        except:
            raise MusicBrainzHandlerError

        excluded_track_count = tracks_on_release - len(tracks)
        log.info("Found " + str(len(tracks)) + " tracks: " + str(tracks) + " for release_id " + release_id + " (excluded " + str(excluded_track_count) + " tracks)" )

        return tracks
