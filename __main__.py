from LIWC import LiwcDict
from settings import * 
import sys

def main():
	# Should rebuild LIWC dict.
	liwc = LiwcDict(unpickle = False)

# Call the main function if this is the __main__ module. 
if __name__ == "__main__":
    main() 