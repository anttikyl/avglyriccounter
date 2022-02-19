import musicbrainz
import lyricsovh
import requests
import sys
import logging

logging.basicConfig(level=logging.WARNING,
                    format="%(asctime)s %(levelname)s %(filename)s:%(lineno)s %(funcName)s() %(message)s")
log = logging.getLogger("avglyriccounter")

# Handle command line arguments
def handle_command_line_args():
    for i, arg in enumerate(sys.argv[1:]):
        if arg == "-v":
            log.setLevel(logging.INFO)
        elif arg == "-vv":
            log.setLevel(logging.DEBUG)
        else:
            log.error("Unexpected command line argument '" + arg + "'")
            exit()

handle_command_line_args()

print("Enter artist name:")
artist_name = input()
print()

# Create MusicBrainz handler
mb_client = musicbrainz.MusicBrainzClient()
mb_handler = musicbrainz.MusicBrainzHandler(mb_client)

# Create LyricsOvh handler
lo_client = lyricsovh.LyricsOvhClient()
lo_handler = lyricsovh.LyricsOvhHandler(lo_client)

# Get the artist's MusicBrainz ID
artist_mbid = mb_handler.get_artist_mbid(artist_name)

if artist_mbid == '':
    log.error("Could not find MBID for artist '" + artist_name + "', exiting...")
    exit()

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

log.info("Found " + str(len(tracks)) + " songs, of which " + str(found_lyrics) + " had recorded lyrics")

# Check that we're not dividing by zero, then calculate the average word count of the found lyrics
if total_word_count > 0 and found_lyrics > 0:
    average_word_count = total_word_count / found_lyrics
else:
    average_word_count = 0

log.info("The average word count of the found songs is " + str(average_word_count))

print(average_word_count)
