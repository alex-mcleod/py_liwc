import os

DIVIDER = "%"
TAGS_REGEX = r"(\d+)(\s+)(\w+)"
CODE_GROUP = 1
TAG_GROUP = 3
WORDS_REGEX_WORD = r"[\w*]+"
WORDS_REGEX_CODE = r"\d+"
PICKLE_ARG = "-p"
UNPICKLE_ARG = "-up"
WORD_STEM_DELIMITER = "*"
LIWC2007_LOC = os.path.dirname(os.path.realpath(__file__)) + "/negotiations-ling773-read-only/resources/LIWC2007.dic"
PICKLE_LOC = "/py_liwc/LIWC2007"