import unittest
from unittest.mock import Mock

from avglyriccounter.musicbrainz import MusicBrainzHandler, MusicBrainzHandlerError
from requests.exceptions import HTTPError

class TestMusicBrainzHandler(unittest.TestCase):
    def setUp(self):
        self.mock_client = Mock()
        self.mb_handler = MusicBrainzHandler(self.mock_client)

    # ------------------------------------------------------------------------------------------------
    # MusicBrainzHandler.get_artist_mbid()

    def test_get_artist_mbid_success(self):
        # json response value from https://musicbrainz.org/ws/2/artist/query=artist:hallatar
        self.mock_client.search_artist.return_value = {'created': '2022-02-19T15:57:52.014Z', 'count': 1, 'offset': 0, 'artists': [{'id': '7f0d27cb-d636-40c3-a92d-cd44e880658e', 'type': 'Group', 'type-id': 'e431f5f6-b5d2-343d-8b36-72607fffb74b', 'score': 100, 'name': 'Hallatar', 'sort-name': 'Hallatar', 'country': 'FI', 'area': {'id': '6a264f94-6ff1-30b1-9a81-41f7bfabd616', 'type': 'Country', 'type-id': '06dd0ae4-8c74-30bb-b43d-95dcedf961de', 'name': 'Finland', 'sort-name': 'Finland', 'life-span': {'ended': None}}, 'begin-area': {'id': 'fb353560-26de-4451-8e65-68eed6f905b9', 'type': 'City', 'type-id': '6fd8f29a-3d0a-32fc-980d-ea697b69da78', 'name': 'Jyväskylä', 'sort-name': 'Jyväskylä', 'life-span': {'ended': None}}, 'disambiguation': 'Finnish atmospheric doom/death metal', 'isnis': ['0000000469401304'], 'life-span': {'begin': '2017', 'ended': None}, 'tags': [{'count': 1, 'name': 'metal'}, {'count': 2, 'name': 'doom metal'}, {'count': 1, 'name': 'death-doom metal'}]}]}

        # In a success case, the returned value is the actual mbid
        actual = self.mb_handler.get_artist_mbid('hallatar')
        self.assertEqual(actual, '7f0d27cb-d636-40c3-a92d-cd44e880658e')

    def test_get_artist_mbid_not_found(self):
        # json response value from https://musicbrainz.org/ws/2/artist/query=artist:qwertyuip
        self.mock_client.search_artist.return_value = {'created': '2022-02-19T16:07:13.447Z', 'count': 0, 'offset': 0, 'artists': []}

        # When artist is not found, expect empty string
        actual = self.mb_handler.get_artist_mbid('qwertyuip')
        self.assertEqual(actual, '')

    def test_get_artist_mbid_http_error(self):
        self.mock_client.search_artist.side_effect = HTTPError

        with self.assertRaises(MusicBrainzHandlerError):
             self.mb_handler.get_artist_mbid('')

    def test_get_artist_mbid_value_error(self):
        self.mock_client.search_artist.side_effect = ValueError

        with self.assertRaises(MusicBrainzHandlerError):
             self.mb_handler.get_artist_mbid('')

    def test_get_artist_mbid_invalid_input_type(self):
        # Test a couple of invalid input types
        with self.assertRaises(TypeError):
            self.mb_handler.get_artist_mbid(["artist"])

        with self.assertRaises(TypeError):
            self.mb_handler.get_artist_mbid(None)

        with self.assertRaises(TypeError):
            self.mb_handler.get_artist_mbid(1)

    # ------------------------------------------------------------------------------------------------
    # MusicBrainzHandler.get_release_ids()

    def test_get_release_ids_success(self):
        # json response value from http://musicbrainz.org/ws/2/release-group/?query=artist:"conjurer"%20AND%20primarytype:"album"%20AND%20NOT%20secondarytype:"Live"%20AND%20NOT%20secondarytype:"Compilation"&limit=100
        self.mock_client.search_artist_release_groups.return_value = {'created': '2022-02-20T01:18:47.481Z', 'count': 1, 'offset': 0, 'release-groups': [{'id': '514689fe-851d-45e0-8954-650155e933d9', 'type-id': 'f529b476-6e62-324f-b0aa-1f3e33d313fc', 'score': 100, 'primary-type-id': 'f529b476-6e62-324f-b0aa-1f3e33d313fc', 'count': 2, 'title': 'No Stars Upon the Bridge', 'first-release-date': '2017-10-20', 'primary-type': 'Album', 'artist-credit': [{'name': 'Hallatar', 'artist': {'id': '7f0d27cb-d636-40c3-a92d-cd44e880658e', 'name': 'Hallatar', 'sort-name': 'Hallatar', 'disambiguation': 'Finnish atmospheric doom/death metal'}}], 'releases': [{'id': '37179bef-eaa3-4f70-bc06-ff08c956d354', 'status-id': '4e304316-386d-3409-af2e-78857eec5cfe', 'title': 'No Stars Upon the Bridge', 'status': 'Official'}, {'id': '9568867f-2994-4ffe-a7c8-834b8eaa3432', 'status-id': '4e304316-386d-3409-af2e-78857eec5cfe', 'title': 'No Stars Upon the Bridge', 'status': 'Official'}], 'tags': [{'count': 1, 'name': 'rock'}, {'count': 1, 'name': 'metal'}, {'count': 1, 'name': 'doom metal'}, {'count': 1, 'name': 'death-doom metal'}, {'count': 1, 'name': 'funeral doom metal'}]}]}

        # In a success case, the returned value is a list containing release_ids
        actual = self.mb_handler.get_release_ids('hallatar', '7f0d27cb-d636-40c3-a92d-cd44e880658e')
        self.assertEqual(actual, ['37179bef-eaa3-4f70-bc06-ff08c956d354'])

    def test_get_release_ids_none_found(self):
        # json response value from http://musicbrainz.org/ws/2/release-group/?query=artist:"dghfdfghdfgh"%20AND%20primarytype:"album"%20AND%20NOT%20secondarytype:"Live"%20AND%20NOT%20secondarytype:"Compilation"&limit=100
        self.mock_client.search_artist_release_groups.return_value = {'created': '2022-02-20T01:29:32.348Z', 'count': 0, 'offset': 0, 'release-groups': []}

        # If no release_ids are found, the returned value is an empty list
        actual = self.mb_handler.get_release_ids('dghfdfghdfgh', '4e304316-386d-3409-af2e-78857eec5cfe')
        self.assertEqual(actual, [])

    def test_get_release_ids_http_error(self):
        self.mock_client.search_artist_release_groups.side_effect = HTTPError

        with self.assertRaises(MusicBrainzHandlerError):
             self.mb_handler.get_release_ids('', '')

    def test_get_release_ids_value_error(self):
        self.mock_client.search_artist_release_groups.side_effect = ValueError

        with self.assertRaises(MusicBrainzHandlerError):
             self.mb_handler.get_release_ids('', '')

    def test_get_release_ids_invalid_input_type(self):
        # Test a couple of invalid input types
        with self.assertRaises(TypeError):
            self.mb_handler.get_release_ids(["7f0d27cb-d636-40c3-a92d-cd44e880658e"])

        with self.assertRaises(TypeError):
            self.mb_handler.get_release_ids(None)

        with self.assertRaises(TypeError):
            self.mb_handler.get_release_ids(1)

    # ------------------------------------------------------------------------------------------------
    # MusicBrainzHandler.get_tracks()

    def test_get_tracks_success(self):
        # json response value from https://musicbrainz.org/ws/2/release/42929a80-440e-4e25-84ff-e6435a690f15
        self.mock_client.get_release_with_recordings.return_value = {'asin': None, 'release-events': [{'date': '2009', 'area': {'sort-name': 'United States', 'iso-3166-1-codes': ['US'], 'id': '489ce91b-6658-3307-9877-795b68554c98', 'name': 'United States', 'disambiguation': '', 'type': None, 'type-id': None}}], 'text-representation': {'language': 'eng', 'script': 'Latn'}, 'id': '42929a80-440e-4e25-84ff-e6435a690f15', 'media': [{'title': '', 'track-offset': 0, 'position': 1, 'track-count': 7, 'format': 'CD', 'tracks': [{'number': '1', 'position': 1, 'title': 'Infection', 'id': '950217b3-1aa1-316e-b30d-a2e7139b82ea', 'recording': {'length': 243000, 'video': False, 'title': 'Infection', 'disambiguation': '', 'id': '37244e1c-edba-4d08-a6ad-9c2be1b00ddf', 'first-release-date': '2009'}, 'length': 243000}, {'number': '2', 'position': 2, 'title': 'Realms', 'id': '8d3d7267-a91f-3f5a-952e-0ea9bc2805cd', 'recording': {'length': 193000, 'video': False, 'title': 'Realms', 'disambiguation': '', 'id': 'cf466419-7d96-4c23-a820-ab7173579ac4', 'first-release-date': '2009'}, 'length': 193000}, {'length': 482000, 'recording': {'id': 'dcc5e933-12e3-41b8-b72b-5c01e49ee18c', 'first-release-date': '2009', 'disambiguation': '', 'video': False, 'length': 482000, 'title': 'Eyes: Closed'}, 'id': 'fe7b3ed6-8b12-3db8-b583-ef94c03f7c3e', 'position': 3, 'title': 'Eyes: Closed', 'number': '3'}, {'id': 'e462c021-03ba-3631-b16e-8168818c9779', 'recording': {'disambiguation': '', 'title': 'Eyes: Open', 'length': 49000, 'video': False, 'first-release-date': '2009', 'id': '4f8bc76e-2c5e-4a3e-a889-5b6b355dfc6f'}, 'length': 49000, 'number': '4', 'position': 4, 'title': 'Eyes: Open'}, {'id': '6ee53e5b-93c1-3aae-9324-8680c451764a', 'recording': {'id': 'e6e975c0-ea7a-4c45-9ad3-c664654d6442', 'first-release-date': '2009', 'disambiguation': '', 'length': 306000, 'video': False, 'title': 'Oscillator'}, 'length': 306000, 'number': '5', 'position': 5, 'title': 'Oscillator'}, {'length': 63000, 'recording': {'video': False, 'length': 63000, 'title': 'Apparition', 'disambiguation': '', 'id': '59dda48c-9f24-4b94-9cee-8cae7db50ce6', 'first-release-date': '2009'}, 'id': 'f4ff1de3-037c-3c8d-8bbf-d5a54b4c7fb0', 'title': 'Apparition', 'position': 6, 'number': '6'}, {'length': 706000, 'id': '471edd7d-e6f8-3c4d-85f9-c99a7ff50bff', 'recording': {'title': 'Predator', 'video': False, 'length': 706000, 'disambiguation': '', 'first-release-date': '2009', 'id': 'c92600ed-b02d-4445-a65f-b572b3671fea'}, 'title': 'Predator', 'position': 7, 'number': '7'}], 'format-id': '9712d52a-4509-3d4b-a1a2-67c88c643e31'}], 'quality': 'normal', 'title': 'Apparition', 'status-id': '4e304316-386d-3409-af2e-78857eec5cfe', 'packaging-id': None, 'date': '2009', 'barcode': None, 'disambiguation': '', 'country': 'US', 'packaging': None, 'status': 'Official', 'cover-art-archive': {'back': False, 'artwork': True, 'darkened': False, 'count': 1, 'front': True}}

        # In a success case, the returned value is a list containing release_ids
        actual = self.mb_handler.get_tracks('42929a80-440e-4e25-84ff-e6435a690f15', [])
        self.assertEqual(actual, ['infection', 'realms', 'eyes: closed', 'eyes: open', 'oscillator', 'apparition', 'predator'])

    def test_get_tracks_none_found(self):
        # It's unlikely that a release that has been added to the database does not have any tracks on it,
        # so use a manually modified json payload to mock the expected response
        self.mock_client.get_release_with_recordings.return_value = {'cover-art-archive': {'artwork': True, 'front': True, 'darkened': False, 'back': True, 'count': 15}, 'packaging-id': '8f931351-d2e2-310f-afc6-37b89ddba246', 'id': '37179bef-eaa3-4f70-bc06-ff08c956d354', 'media': [{'position': 1, 'track-offset': 0, 'tracks': [], 'format-id': '9712d52a-4509-3d4b-a1a2-67c88c643e31', 'format': 'CD', 'title': '', 'track-count': 0}], 'text-representation': {'language': 'eng', 'script': 'Latn'}, 'status-id': '4e304316-386d-3409-af2e-78857eec5cfe', 'title': 'No Stars Upon the Bridge', 'barcode': '6430065582465', 'quality': 'normal', 'date': '2017-10-20', 'disambiguation': '', 'country': 'FI', 'asin': 'B0752FN82J', 'status': 'Official', 'packaging': 'Digipak', 'release-events': [{'date': '2017-10-20', 'area': {'sort-name': 'Finland', 'disambiguation': '', 'id': '6a264f94-6ff1-30b1-9a81-41f7bfabd616', 'type': None, 'iso-3166-1-codes': ['FI'], 'type-id': None, 'name': 'Finland'}}]}

        # If no release_ids are found, the returned value is an empty list
        actual = self.mb_handler.get_tracks('0faafa6d-c03e-4aa7-ac5e-094474c344d0', [])
        self.assertEqual(actual, [])

    def test_get_tracks_exclusions_removed_successfully(self):
        # This payload contains a release that has two "media" fields, the second being an instrumental version of the album
        # Using the 'exclusion_filters' arg, expect to filter out tracks with '(instrumental)' in their title
        self.mock_client.get_release_with_recordings.return_value = {'country': 'XW', 'cover-art-archive': {'darkened': False, 'artwork': False, 'count': 0, 'front': False, 'back': False}, 'media': [{'position': 1, 'format': 'Digital Media', 'format-id': '907a28d9-b3b2-3ef6-89a8-7b18d91d4794', 'track-offset': 0, 'title': 'Visions', 'track-count': 8, 'tracks': [{'recording': {'first-release-date': '2011-10-25', 'video': False, 'title': 'Premonition', 'length': 257000, 'disambiguation': '', 'id': '0ae1c917-1fa5-4ebb-adcf-6c6ca0cce63b'}, 'number': '1', 'title': 'Premonition', 'position': 1, 'id': '100dbcc6-b4e2-4b18-8cb8-cb3cdcf8da3c', 'length': 255000}, {'id': 'b5dc140b-e153-4843-8c7b-7e575740ba88', 'length': 789000, 'position': 2, 'number': '2', 'recording': {'title': 'Nocturnal Conspiracy', 'length': 789000, 'disambiguation': '', 'id': '32a288c5-6545-4e80-a6c3-f95077c7e79d', 'first-release-date': '2011-10-25', 'video': False}, 'title': 'Nocturnal Conspiracy'}, {'title': 'Insomnia', 'recording': {'first-release-date': '2011-10-25', 'video': False, 'title': 'Insomnia', 'disambiguation': '', 'length': 363000, 'id': 'f98a80bf-7615-4f35-b9f3-15338f0c76fe'}, 'number': '3', 'position': 3, 'length': 363000, 'id': 'd0942ac5-3365-4f1f-a6c4-8bbd7562db72'}, {'position': 4, 'number': '4', 'recording': {'video': False, 'first-release-date': '2011-10-25', 'id': '6a0b1a0d-527d-4291-b4a0-974df738c12a', 'disambiguation': '', 'length': 244000, 'title': "The Mind's Eye"}, 'title': "The Mind's Eye", 'id': '2ee82e49-b246-4638-a025-b355285a1980', 'length': 244000}, {'id': 'dae94107-0323-4bf7-a289-f4cba70c0d4f', 'length': 327000, 'recording': {'first-release-date': '2011-10-25', 'video': False, 'id': 'e363533a-d307-40bd-9a8c-336ab2406b44', 'title': 'Portals', 'disambiguation': '', 'length': 327000}, 'number': '5', 'title': 'Portals', 'position': 5}, {'id': 'a8e74dbf-6c09-4d7a-b3ab-37d3ac13dc3b', 'length': 488000, 'position': 6, 'number': '6', 'recording': {'first-release-date': '2011-10-25', 'video': False, 'title': 'Shapeshifter', 'length': 488000, 'disambiguation': '', 'id': '2de44f88-1ab9-4492-bb19-9a262d92f715'}, 'title': 'Shapeshifter'}, {'length': 486000, 'id': 'd17bd8eb-f59b-4caf-a072-c992a5df6ab2', 'title': 'Deathless', 'number': '7', 'recording': {'video': False, 'first-release-date': '2017-02-03', 'id': 'd2766e2e-7368-4325-a27a-b9bc301a11ca', 'disambiguation': '', 'length': 486000, 'title': 'Deathless'}, 'position': 7}, {'length': 1347000, 'id': '5359a53e-6892-439f-94df-75046a8ff153', 'position': 8, 'title': 'Visions', 'number': '8', 'recording': {'video': False, 'first-release-date': '2017-02-03', 'id': 'a28d6730-7190-4495-87c3-a64d47478d27', 'disambiguation': '', 'length': 1347000, 'title': 'Visions'}}]}, {'title': 'Visions (instrumental)', 'tracks': [{'position': 1, 'title': 'Premonition (instrumental)', 'number': '1', 'recording': {'video': False, 'first-release-date': '2017-02-03', 'disambiguation': '', 'length': 250000, 'title': 'Premonition', 'id': '4d3a9ae6-1243-418b-aa0b-4ce232ea0712'}, 'length': 255000, 'id': '107b72a8-ca24-4e24-a27b-5301f5c4e7a4'}, {'position': 2, 'recording': {'first-release-date': '2017-02-03', 'video': False, 'id': '8c4439c3-0f7a-41f9-9114-da848a755d73', 'title': 'Nocturnal Conspiracy', 'disambiguation': '', 'length': 788000}, 'number': '2', 'title': 'Nocturnal Conspiracy (instrumental)', 'id': '045374a2-9a1b-4640-ae6b-2b335471de6c', 'length': 789000}, {'position': 3, 'title': 'Insomnia (instrumental)', 'number': '3', 'recording': {'title': 'Insomnia', 'length': 363000, 'disambiguation': '', 'id': '8d95c557-8658-486d-929f-f50327dbde64', 'first-release-date': '2017-02-03', 'video': False}, 'length': 363000, 'id': '1a16cf46-feee-42d2-b1c7-424b8ba9e3eb'}, {'position': 4, 'number': '4', 'recording': {'video': False, 'first-release-date': '2017-02-03', 'id': '07ce1e44-b428-4790-ad55-17622167931d', 'length': 244000, 'disambiguation': '', 'title': "The Mind's Eye"}, 'title': "The Mind's Eye (instrumental)", 'id': '3b740492-041e-4746-976f-3194ba1f411e', 'length': 244000}, {'position': 5, 'title': 'Portals (instrumental)', 'number': '5', 'recording': {'id': '97bb5e99-c775-4b70-8f2f-ff607fa2870d', 'length': 327000, 'disambiguation': '', 'title': 'Portals', 'video': False, 'first-release-date': '2017-02-03'}, 'length': 327000, 'id': '1aa9c46e-af2d-4b47-afa4-7c687aeeec00'}, {'length': 488000, 'id': 'e1b7aaf9-5f2b-494a-accb-f14001ae3346', 'title': 'Shapeshifter (instrumental)', 'recording': {'id': 'dc08b4e2-1d3e-4e70-8acc-477835424623', 'title': 'Shapeshifter', 'disambiguation': '', 'length': 488000, 'first-release-date': '2017-02-03', 'video': False}, 'number': '6', 'position': 6}, {'length': 486000, 'id': '3f3717f0-31e1-42b3-96c9-eb17486c3b59', 'title': 'Deathless (instrumental)', 'recording': {'first-release-date': '2017-02-03', 'video': False, 'id': 'fbd830e6-2a2c-48d4-9451-0c1ffa0fe2d2', 'title': 'Deathless', 'length': 484000, 'disambiguation': ''}, 'number': '7', 'position': 7}, {'length': 1347000, 'id': '8797348e-5c39-41f7-b49d-655a2076b7ba', 'title': 'Visions (instrumental)', 'recording': {'video': False, 'first-release-date': '2011-10-25', 'id': '96360d8c-c764-4cc6-bab7-d1d5f8fa575f', 'length': 1347000, 'disambiguation': '', 'title': 'Visions'}, 'number': '8', 'position': 8}], 'track-count': 8, 'format-id': '907a28d9-b3b2-3ef6-89a8-7b18d91d4794', 'format': 'Digital Media', 'position': 2, 'track-offset': 0}], 'disambiguation': '2017 digital reissue', 'barcode': None, 'status': 'Official', 'text-representation': {'language': 'eng', 'script': 'Latn'}, 'id': 'c6d20708-7304-4025-b9d3-6912f864b9c6', 'release-events': [{'date': '2017', 'area': {'disambiguation': '', 'sort-name': '[Worldwide]', 'type': None, 'id': '525d4e18-3d00-31b9-a58b-a146a916de8f', 'iso-3166-1-codes': ['XW'], 'type-id': None, 'name': '[Worldwide]'}}], 'asin': 'B01NBL1DBV', 'title': 'Visions', 'date': '2017', 'status-id': '4e304316-386d-3409-af2e-78857eec5cfe', 'packaging-id': '119eba76-b343-3e02-a292-f0f00644bb9b', 'quality': 'normal', 'packaging': 'None'}

        result = self.mb_handler.get_tracks('c6d20708-7304-4025-b9d3-6912f864b9c6', ['(instrumental)'])

        # Check that there are no tracks with '(instrumental)' in their names
        self.assertNotIn('(instrumental)', result)

    def test_get_tracks_http_error(self):
        self.mock_client.get_release_with_recordings.side_effect = HTTPError

        with self.assertRaises(MusicBrainzHandlerError):
             self.mb_handler.get_tracks('', [])

    def test_get_tracks_value_error(self):
        self.mock_client.get_release_with_recordings.side_effect = ValueError

        with self.assertRaises(MusicBrainzHandlerError):
             self.mb_handler.get_tracks('', [])

    def test_get_tracks_invalid_input_type(self):
        # Test a couple of invalid input types
        with self.assertRaises(TypeError):
            self.mb_handler.get_tracks(["0faafa6d-c03e-4aa7-ac5e-094474c344d0"])

        with self.assertRaises(TypeError):
            self.mb_handler.get_tracks(None)

        with self.assertRaises(TypeError):
            self.mb_handler.get_tracks(1)
