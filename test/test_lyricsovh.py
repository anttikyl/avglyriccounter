import unittest
from unittest.mock import Mock

from avgwords.lyricsovh import LyricsOvhHandler
from requests.exceptions import HTTPError

class TestLyricsOvhHandler(unittest.TestCase):
    def setUp(self):
        self.mock_client = Mock()
        self.lo_handler = LyricsOvhHandler(self.mock_client)

    def test_get_lyric_word_count_success(self):
        # json response value from https://api.lyrics.ovh/v1/iron%20maiden/fear%20of%20the%20dark
        self.mock_client.get_lyrics.return_value = {'lyrics': "Paroles de la chanson Fear Of The Dark par Iron Maiden\r\nI am a man who walks alone\nAnd when I'm walking a dark road\nAt night or strolling through the park\n\nWhen the light begins to change\nI sometimes feel a little strange\nA little anxious when it's dark\n\nFear of the dark, fear of the dark\nI have a constant fear that something's always near\nFear of the dark, fear of the dark\nI have a phobia that someone's always there\n\nHave you run your fingers down the wall\nAnd have you felt your neck skin crawl\n\nWhen you're searching for the light?\n\nSometimes when you're scared to take a look\nAt the corner of the room\nYou've sensed that something's watching you\n\nFear of the dark, fear of the dark\nI have constant fear that something's always near\nFear of the dark, fear of the dark\nI have a phobia that someone's always there\n\nHave you ever been alone at night\nThought you heard footsteps behind\nAnd turned around and no-one's there?\n\nAnd as you quicken up your pace\nYou find it hard to look again\nBecause you're sure there's someone there\n\n\nFear of the dark, fear of the dark\nI have constant fear that something's always near\nFear of the dark, fear of the dark\nI have a phobia that someone's always there\n\nFear of the dark\nFear of the dark\nFear of the dark\nFear of the dark\nFear of the dark\nFear of the dark\nFear of the dark\nFear of the dark\n\nWatching horror films the night before\nDebating witches and folklore\nThe unknown troubles on your mind\n\n\nMaybe your mind is playing tricks\nYou sense, and suddenly eyes fix\nOn dancing shadows from behind\n\nFear of the dark, fear of the dark\nI have constant fear that something's always near\nFear of the dark, fear of the dark\nI have a phobia that someone's always there\nFear of the dark, fear of the dark\nI have constant fear that something's always near\nFear of the dark, fear of the dark\nI have a phobia that someone's always there\n\nWhen I'm walking a dark road\nI am a man who walks alone"}

        # In a success case, the returned value is the actual word count
        actual = self.lo_handler.get_lyric_word_count("iron maiden", "fear of the dark")
        self.assertEqual(actual, 369)

    def test_get_lyric_word_count_http_error(self):
        self.mock_client.get_lyrics.side_effect = HTTPError
        
        # In a failure case where the LyricsOvh server would return 404, expect None
        actual = self.lo_handler.get_lyric_word_count("nonexistant imaginary artist", "hcvhjhjsdfhsklajfdc")
        self.assertEqual(actual, None)

    def test_get_lyric_word_count_value_error(self):
        self.mock_client.get_lyrics.side_effect = ValueError
        
        # In a failure case where the LyricsOvh server would return an invalid JSON response, expect None
        actual = self.lo_handler.get_lyric_word_count("pink floyd", "time")
        self.assertEqual(actual, None)

    def test_get_lyric_word_count_invalid_input_type(self):
        # Test a couple of invalid input types
        with self.assertRaises(TypeError):
            self.lo_handler.get_lyric_word_count(["artist"], ["track"])

        with self.assertRaises(TypeError):
            self.lo_handler.get_lyric_word_count(None, None)

        with self.assertRaises(TypeError):
            self.lo_handler.get_lyric_word_count(1, 2)

