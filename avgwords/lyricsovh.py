import requests

class LyricsOvhClient():
    """
    A class used to communicate with the LyricsOvh API.

    Wraps endpoints into easy to use methods.
    """
    def __init__(self):
        self.base_url = "https://api.lyrics.ovh/v1/"
    
    def get_lyrics(self, artist, title):
        """ https://lyricsovh.docs.apiary.io/#reference

        Gets the lyrics to a song from LyricsOvh based on the given artist name and track title

        :param      artist      name of the artist
        :param      title       title of the track whose lyrics to search for

        :returns    json response body returned from LyricsOvh API
        :raises     requests.HttpError if one occurred
        :raises     ValueError if the response is not decodable json
        """

        url = self.base_url + "/" + artist + "/" + title

        res = requests.get(url)
        res.raise_for_status()

        try:
            retval = res.json()
        except ValueError: # includes simplejson.decoder.JSONDecodeError
            raise ValueError # raise ValueError to abstract away simplejson

        return retval
