"""Enumerations for the application
"""
import enum


class OrderingFieldType(enum.Enum):
    """The ordering field type enumeration.
    """
    STRING = 'string'
    INTEGER = 'integer'
    DATE = 'date'
    BADGE_CLASS = 'badge_class'
    BADGE_TYPE = 'badge_type'


class OrderingDirection(enum.Enum):
    """The ordering direction enumeration.
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
        return ' '.join(word.lower() for word in self.name.split('_')).capitalize()


class BadgeClass(BaseEnum):
    """Enumeration for badge classes.
    """
    GOLD = 1
    SILVER = 2
    BRONZE = 3


class BadgeType(BaseEnum):
    """Enumeration for badge types.
    """
    NAMED = 1
    TAG_BASED = 2


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


class TagFlag(enum.Enum):
    """Enumeration for the available tag flags.
    """
    REQUIRED = 'required', 'required'
    MODERATOR_ONLY = 'moderator_only', 'moderator-only'

    def __init__(self, attribute_name: str, api_path: str):
        """Initialize the tag flag enum.

        :param attribute_name: The tag object attribute name.
        :param api_path: The api path from which to get the tags that have this flag set.
        """
        super().__init__()

        self.attribute_name = attribute_name
        self.api_path = api_path


class ContentLicense(enum.Enum):
    """The content license enumeration
    """
    CC_BY_SA_2_5 = 'Attribution-ShareAlike 2.5 Generic'
    CC_BY_SA_3_0 = 'Attribution-ShareAlike 3.0 Unported'
    CC_BY_SA_4_0 = 'Attribution-ShareAlike 4.0 International'


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


class PostLinkType(BaseEnum):
    """Enumeration for the post link type.
    """
    LINKED = 1
    DUPLICATE = 3


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
    QUESTION_UNMERGED = 22
    SUGGESTED_EDIT_APPLIED = 24
    POST_TWEETED = 25
    DISCUSSION_MOVED_TO_CHAT = 31
    POST_NOTICE_ADDED = 33
    POST_NOTICE_REMOVED = 34
    POST_MIGRATED_AWAY = 35
    POST_MIGRATED_HERE = 36
    POST_MERGE_SOURCE = 37
    POST_MERGE_DESTINATION = 38
    COMMUNITY_BUMP = 50
    SELECTED_HOT_QUESTION = 52
    REMOVED_HOT_QUESTION = 53

    def vote_based(self) -> bool:
        """Return true if the post history type is vote based.

        :return: True if the post history type is vote based.
        """
        return self in (
            self.POST_CLOSED, self.POST_REOPENED, self.POST_DELETED, self.POST_UNDELETED, self.POST_LOCKED,
            self.POST_LOCKED, self.POST_UNLOCKED, self.POST_TWEETED, self.POST_NOTICE_ADDED, self.POST_NOTICE_REMOVED,
            self.POST_MERGE_SOURCE, self.POST_MIGRATED_AWAY, self.POST_MIGRATED_HERE, self.POST_MERGE_SOURCE,
            self.POST_MERGE_DESTINATION, self.COMMUNITY_BUMP, self.SELECTED_HOT_QUESTION, self.REMOVED_HOT_QUESTION
        )

    def rollback(self) -> bool:
        """Return true if the post history type is a rollback.

        :return: True if the post history type is a rollback.
        """
        return self in (self.ROLLBACK_TITLE, self.ROLLBACK_BODY, self.ROLLBACK_TAGS)


class Privilege(enum.Enum):
    """Enumeration for user privileges
    """
    CREATE_POSTS = 1, "Ask a question or contribute an answer"
    PARTICIPATE_IN_META = 5, "Discuss the site itself: bugs, feedback, and governance"
    CREATE_WIKI_POSTS = 10, "Create answers that can be easily edited by most users"
    REMOVE_NEW_USER_RESTRICTIONS = 10, "Post more links, answer protected questions"
    VOTE_UP = 15, "Indicate when questions and answers are useful"
    FLAG_POSTS = 15, "Bring content to the attention of the community via flags"
    TALK_IN_CHATS = 20, "Participate in this site's chat rooms"
    COMMENT_EVERYWHERE = 50, "Leave comments on other people's posts"
    SET_BOUNTIES = 75, "Offer some of your reputation as bounty on a question"
    CREATE_CHAT_ROOMS = 100, "Create new chat rooms"
    EDIT_COMMUNITY_WIKI = 100, "Collaborate on the editing and improvement of wiki posts"
    VOTE_DOWN = 125, "Indicate when questions and answers are not useful"
    REDUCE_ADS = 200, "Some ads are now automatically disabled"
    VIEW_CLOSE_VOTES = 250, "View and cast close/reopen votes on your own questions"
    ACCESS_REVIEW_QUEUES = 500, "Access the First posts and Late answers review queues"
    CREATE_GALLERY_CHAT_ROOMS = 1000, "Create chat rooms where only specific users may talk"
    ESTABLISHED_USER = 1500, "You've been around for a while; see vote counts"
    CREATE_TAGS = 1500, "Add new tags to the site"
    EDIT_QUESTIONS_AND_ANSWERS = 2000, "Edits to any question or answer are applied immediately"
    CREATE_TAG_SYNONYMS = 2500, "Decide which tags have the same meaning as others"
    CAST_CLOSE_AND_REOPEN_VOTES = 3000, "Help decide whether posts are off-topic or duplicates"
    APPROVE_TAG_WIKI_EDITS = 5000, "Approve edits to tag wikis made by regular users"
    ACCESS_TO_MODERATOR_TOOLS = 10000, "Access reports, delete questions, review reviews"
    PROTECT_QUESTIONS = 15000, "Mark questions as protected"
    TRUSTED_USER = 20000, "Expanded editing, deletion and undeletion privileges"
    ACCESS_TO_SITE_ANALYTICS = 25000, "Access to internal and Google site analytics"

    def __init__(self, reputation: int, description: str) -> None:
        """Creates the privilege.

        :param reputation: The required reputation.
        :param description: The privilege description.
        """
        self.reputation = reputation
        self.description = description
