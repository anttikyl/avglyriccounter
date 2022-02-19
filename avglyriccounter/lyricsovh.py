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
        :raises     requests.exceptions.HTTPError if one occurred
        :raises     ValueError if the response is not decodable json
        """

        url = self.base_url + str(artist) + "/" + str(title)

        res = requests.get(url)
        res.raise_for_status()

        try:
            retval = res.json()
        except ValueError: # includes simplejson.decoder.JSONDecodeError
            raise ValueError # raise ValueError to abstract away simplejson

        return retval

class LyricsOvhHandler():
    """
    Handler for abstracting LyricsOvh endpoint functionality
    """

    def __init__(self, client):
        self.client = client

    def get_lyric_word_count(self, artist, title):
        """
        Gets the lyrics to a song from LyricsOvh and returns its word count

        :param      artist      name of the artist
        :param      title       title of the track whose lyrics to search for

        :returns    word count if lyrics found, otherwise None
        :raises     TypeError if the args are not strings
        """

        if type(artist) != str or type(title) != str:
            raise TypeError("Unsupported type(s) for args 'artist' and 'title'")

        try:
            lyrics_json = self.client.get_lyrics(artist, title)
        except requests.exceptions.HTTPError:
            # No lyrics were found for this song
            return None
        except ValueError:
            # JSON decoding error
            return None

        # TODO: add handling for common non-words, e.g. ( 2x), (3x), (x3), .., - etc.
        # TODO: trim "Paroles de la chanson [track] par [artist]" if present

        word_count = len(lyrics_json['lyrics'].split())

        return word_count
