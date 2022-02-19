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

    """
    for i, arg in enumerate(sys.argv[1:]):
        if arg == "-v":
            log.setLevel(logging.INFO)
        elif arg == "-vv":
            log.setLevel(logging.DEBUG)
        else:
            log.error("Unexpected command line argument '" + arg + "'")
            exit()

# ------------------------------------------------------------------------------------------------

alc = avglyriccounter.AvgLyricCounter()

handle_command_line_args()

print("Enter artist name:")
artist_name = input()
print()

try:
    average_word_count = alc.get_average_lyric_count(artist_name)
except avglyriccounter.MissingData:
    print("Exiting...")
    exit()

print(average_word_count)
