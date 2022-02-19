# avglyriccounter (Average Lyric Counter)

A simple tool that takes an artist's name and outputs the average number of words in their songs.

Uses the MusicBrainz API to get artist's albums and tracks, and the LyricsOvh API to get the lyrics to the tracks.

See [docs](https://github.com/anttikyl/avglyriccounter/tree/main/docs) for documentation

## Installation & Dependencies

Install dependencies with:
```bash
pip install -r requirements.txt
```

## Usage
Use with:
```bash
python3 avglyriccounter <artist_name> <options>
```
Note that with multi-word artist names, double quotes should be used.

For example:
```bash
python3 avglyriccounter "iron maiden"
```

### Flags
The following optional flags are available:
```
    -h --help   Display usage
    -v          Increase log level to INFO
    -vv         Increase log level to DEBUG
```

## Testing
Run unit tests with:
```bash
python3 -m unittest discover test
```

## Notes on processing time
It takes a long time to get the results, mainly because the MusicBrainz API has a rate limit of one (1) request per second. The number of MusicBrainz requests made per entry is 2 + number_of_albums, so with artists that have dozens of albums, the requests will take a long time to complete.

In addition to the requests made to MusicBrainz, each unique track's lyrics will be requested separately from LyricsOvh, potentially raising the count of requests made to hundreds. There is no rate limit for LyricsOvh, but the server responses do take a while.

## Potential improvements
- Filter out live and "best of" type albums to avoid unnecessary MusicBrainz API requests
- Improve lyrics parsing to ignore non-word strings and to understand special cases
    - There doesn't seem to be a standardized format for the lyrics, but from looking at the results, well educated guesses can be taken to improve result accuracy
- Write unit tests for AvgLyricCounter, MusicBrainzClient and LyricsOvhClient

## Related links
[MusicBrainz API reference](https://musicbrainz.org/doc/MusicBrainz_API)

[LyricsOvh API reference](https://lyricsovh.docs.apiary.io/#reference)