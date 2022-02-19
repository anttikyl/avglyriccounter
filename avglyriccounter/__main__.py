import avglyriccounter
import sys
import logging

logging.basicConfig(level=logging.WARNING,
                    format="%(asctime)s %(levelname)s %(filename)s:%(lineno)s %(funcName)s() %(message)s")
log = logging.getLogger("avglyriccounter")

# Handle command line arguments
def handle_command_line_args():
    """
    Processes command line arguments

    :returns    the artist name
    """

    artist_name = ''

    usage_str = "Usage:\n\navglyriccounter <artist_name> <options>\n\nOptions:\n-h --help\tThis help text\n-v\t\tIncrease log level to INFO\n-vv\t\tIncrease log level to DEBUG"

    if len(sys.argv) > 1 and sys.argv[1] != '' and sys.argv[1] != '-h' and sys.argv[1] != '--help':
        artist_name = sys.argv[1]
    else:
        print(usage_str)
        exit()

    for i, arg in enumerate(sys.argv[2:]):
        if arg == "-v":
            log.setLevel(logging.INFO)
        elif arg == "-vv":
            log.setLevel(logging.DEBUG)
        else:
            print(usage_str)
            exit()

    return artist_name

# ------------------------------------------------------------------------------------------------

alc = avglyriccounter.AvgLyricCounter()

artist_name = handle_command_line_args()

try:
    average_word_count = alc.get_average_lyric_count(artist_name)
except avglyriccounter.MissingData:
    print("Exiting...")
    exit()

print(average_word_count)
