"""Enumerations for the application
"""
import enum


class OrderingDirection(enum.Enum):
    """The ordering direction enum
    """
    DESC = 'desc'
    ASC = 'asc'


class BaseEnum(enum.IntEnum):
    """The base enumeration. Enumerations have and int value and
    """
    @property
    def description(self) -> str:
        """Return the description for the enum value.

        :return: the description for the enum value.
        """
        return self.name[0] + self.name[1:].lower()


class BadgeClass(BaseEnum):
    """Enumeration for badge classes.
    """
    GOLD = 1
    SILVER = 2
    BRONZE = 3


class ContentLicense(enum.Enum):
    """The content license enumeration
    """
    CC_BY_SA_2_5 = 'Attribution-ShareAlike 2.5 Generic'
    CC_BY_SA_3_0 = 'Attribution-ShareAlike 3.0 Unported'
    CC_BY_SA_4_0 = 'Attribution-ShareAlike 4.0 International'


class PostType(BaseEnum):
    """Enumeration for the post type.
    """
    QUESTION = 1
    ANSWER = 2
    WIKI = 3
    TAG_WIKI_EXPERT = 4
    TAG_WIKI = 5
    MODERATOR_NOMINATION = 6
    WIKI_PLACEHOLDER = 7
    PRIVILEGE_WIKI = 8


class PostHistoryType(BaseEnum):
    """Enumeration for the post history type.
    """
    INITIAL_TITLE = 1
    INITIAL_BODY = 2
    INITIAL_TAGS = 3
    EDIT_TITLE = 4
    EDIT_BODY = 5
    EDIT_TAGS = 6
    ROLLBACK_TITLE = 7
    ROLLBACK_BODY = 8
    ROLLBACK_TAGS = 9
    POST_CLOSED = 10
    POST_REOPENED = 11
    POST_DELETED = 12
    POST_UNDELETED = 13
    POST_LOCKED = 14
    POST_UNLOCKED = 15
    COMMUNITY_OWNED = 16
    POST_MIGRATED = 17
    QUESTION_MERGED = 18
    QUESTION_PROTECTED = 19
    QUESTION_UNPROTECTED = 20
    POST_DISASSOCIATED = 21
    QUESTION_UNMERGED = 22


class PostVoteType(BaseEnum):
    """Enumeration for the post vote type.
    """
    ACCEPTED_BY_ORIGINATOR = 1
    UP_MOD = 2
    DOWN_MOD = 3
    OFFENSIVE = 4
    FAVORITE = 5
    CLOSE = 6
    REOPEN = 7
    BOUNTY_START = 8
    BOUNTY_CLOSE = 9
    DELETION = 10
    UN_DELETION = 11
    SPAM = 12
    INFORM_MODERATOR = 13
