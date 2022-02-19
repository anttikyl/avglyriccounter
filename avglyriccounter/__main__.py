from musicbrainz import MusicBrainzClient, MusicBrainzHandler
from lyricsovh import LyricsOvhClient, LyricsOvhHandler
import requests

print("Enter artist name:")
artist_name = input()

# Create MusicBrainz handler
mb_client = MusicBrainzClient()
mb_handler = MusicBrainzHandler(mb_client)

# Create LyricsOvh handler
lo_client = LyricsOvhClient()
lo_handler = LyricsOvhHandler(lo_client)

# Get the artist's MusicBrainz ID
artist_mbid = mb_handler.get_artist_mbid(artist_name)

# Get all the release IDs for the artist
release_ids = mb_handler.get_release_ids(artist_mbid)

# Get the names of all of the tracks on the record
tracks = []
for release_id in release_ids:
    tracks += mb_handler.get_tracks(release_id)

# Filter out duplicate track names
tracks = set(tracks)

# Add the word counts of each track into a list
word_counts = []
for track in tracks:
    word_count = lo_handler.get_lyric_word_count(artist_name, track)

    # Only add word count if lyrics were found for the track
    if word_count != None:
        word_counts.append(word_count)

total_word_count = sum(word_counts)
found_lyrics = len(word_counts)

# Check that we're not dividing by zero, then calculate the average word count of the found lyrics
if total_word_count > 0 and found_lyrics > 0:
    average_word_count = total_word_count / found_lyrics
else:
    average_word_count = 0

print("Found " + str(found_lyrics) + " songs with lyrics. Their average word count is " + str(average_word_count))
