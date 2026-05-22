from enum import Enum


class MongoCollectionName(str, Enum):
    BBIP_SOURCES = "BBIP_SOURCES"
    IP_SOURCES = "IP_SOURCES"
    BBIP_DAILY_SUMMARY = "BBIP_DAILY_SUMMARY"
    IP_DAILY_SUMMARY = "IP_DAILY_SUMMARY"


class SuffixCollectionName(str, Enum):
    BBIP_HISTORIES = "BBIP_HISTORY"
    IP_HISTORIES = "IP_HISTORY"
