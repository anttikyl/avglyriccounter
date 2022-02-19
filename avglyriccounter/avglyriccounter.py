import musicbrainz
import lyricsovh
import logging
import requests

log = logging.getLogger("avglyriccounter")

# Custom exception for handling cases where a mandatory value was not retrieved to provide an output
class MissingData(Exception):
    pass

class AvgLyricCounter():
    def __init__(self):
        # Create MusicBrainz handler
        self.mb_client = musicbrainz.MusicBrainzClient()
        self.mb_handler = musicbrainz.MusicBrainzHandler(self.mb_client)

        # Create LyricsOvh handler
        self.lo_client = lyricsovh.LyricsOvhClient()
        self.lo_handler = lyricsovh.LyricsOvhHandler(self.lo_client)

    def get_all_unique_track_names(self, release_ids):
        """
        Gets all unique track names for the given list of release_ids

        :param      release_ids     list of release_id values to get tracks for

        :returns    a list of unique track names from the given ids, empty if none found
        """
        # Get the names of all of the tracks on the record
        tracks = []
        for release_id in release_ids:
            tracks +=  self.mb_handler.get_tracks(release_id)

        # Filter out duplicate track names
        return list(set(tracks))

    def get_lyric_counts_for_tracks(self, artist_name, tracks):
        """
        Gets the lyric counts for the given tracks

        If no lyrics were found for any given track, it is skipped and not added to
        the returned list.

        :param      artist_name     name of the artist whose tracks to search
        :param      tracks          list of tracks to search word counts for

        :returns    a list containing the word counts of each track with lyrics
        """
        word_counts = []

        for track in tracks:
            word_count =  self.lo_handler.get_lyric_word_count(artist_name, track)

            # Only add word count if lyrics were found for the track
            if word_count != None:
                word_counts.append(word_count)

        return word_counts

    def get_average_lyric_count(self, artist_name):
        """
        Gets the average lyric count of an artist's songs

        :param      artist_name     name of the artist to get the average lyric count for

        :raises     MissingData if any of the required data values for calculating the
                    average word count are missing

        :returns    the average word count of the artist's songs with lyrics, rounded
        """

        if artist_name == '':
            log.error("Given artist name was empty")
            raise MissingData()

        # Get the artist's MusicBrainz ID
        artist_mbid =  self.mb_handler.get_artist_mbid(artist_name)

        if artist_mbid == '':
            log.error("Could not find MBID for artist '" + artist_name + "'.")
            raise MissingData()

        # Get all the release IDs for the artist
        release_ids =  self.mb_handler.get_release_ids(artist_mbid)

        if len(release_ids) == 0:
            log.error("No releases found for artist '" + artist_name + "'")
            raise MissingData()

        # Get all of the unique track names found on the releases
        tracks = self.get_all_unique_track_names(release_ids)

        if len(tracks) == 0:
            log.error("No tracks found for artist '" + artist_name + "'")
            raise MissingData()

        # Add the word counts of each track into a list
        word_counts = self.get_lyric_counts_for_tracks(artist_name, tracks)

        total_word_count = sum(word_counts)
        found_lyrics = len(word_counts)

        log.info("Found " + str(len(tracks)) + " songs, of which " + str(found_lyrics) + " had recorded lyrics")

        # Check that we're not dividing by zero, then calculate the average word count of the found lyrics
        if total_word_count > 0 and found_lyrics > 0:
            average_word_count = total_word_count / found_lyrics
        else:
            average_word_count = 0

        log.info("The average word count of the found songs is " + str(average_word_count))

        return round(average_word_count)
