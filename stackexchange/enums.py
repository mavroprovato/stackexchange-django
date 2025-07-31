"""Enumerations for the application
"""
import enum

import dateutil.parser


class DescriptionMixin:
    """A mixin to add a description field to an enum instance.
    """
    @property
    def description(self) -> str:
        """Return a description for the enum value.

        :return: A description for the enum value.
        """
        return ' '.join(word.lower() for word in getattr(self, 'name').split('_')).capitalize()


class OrderingMixin:
    """A mixin to enable ordering of enum instances. Enums that use this mixin should implement an order property and
    provide an integer to use for sorting.
    """
    @property
    def order(self) -> int:
        """Return an integer value used to order the instances of this enum.

        :return: An integer value used to order the instances of this enum.
        """
        raise NotImplementedError("Ordering not implemented")

    def __ge__(self, other) -> bool:
        """Returns true if this enum instance is greater than or equal to another enum instance of the same class.

        :param other: The enum instance to compare.
        :return: True if this enum instance is greater than or equal to another enum instance of the same class.
        """
        if self.__class__ is other.__class__:
            return self.order >= other.order

        return NotImplemented

    def __gt__(self, other) -> bool:
        """Returns true if this enum instance is greater than to another enum instance of the same class.

        :param other: The enum instance to compare.
        :return: True if this enum instance is greater than to another enum instance of the same class.
        """
        if self.__class__ is other.__class__:
            return self.order > other.order

        return NotImplemented

    def __le__(self, other) -> bool:
        """Returns true if this enum instance is less than or equal to another enum instance of the same class.

        :param other: The enum instance to compare.
        :return: True if this enum instance is less than or equal to another enum instance of the same class.
        """
        if self.__class__ is other.__class__:
            return self.order <= other.order

        return NotImplemented

    def __lt__(self, other):
        """Returns true if this enum instance is less than to another enum instance of the same class.

        :param other: The enum instance to compare.
        :return: True if this enum instance is less than to another enum instance of the same class.
        """
        if self.__class__ is other.__class__:
            return self.order < other.order

        return NotImplemented


class OrderingFieldType(DescriptionMixin, enum.Enum):
    """The ordering field type enumeration.
    """
    STRING = 'string'
    INTEGER = 'integer'
    DATE = 'date'
    RANK = 'rank'
    BADGE_TYPE = 'badge_type'

    def transform(self, value: str):
        """Transform a string value to the proper type, based on the filed type.

        :param value: The string value.
        :return: The value.
        """
        match self:
            case OrderingFieldType.STRING:
                return value
            case OrderingFieldType.INTEGER:
                return int(value)
            case OrderingFieldType.DATE:
                return dateutil.parser.parse(value).date()
            case OrderingFieldType.RANK:
                return BadgeRank(value)
            case OrderingFieldType.BADGE_TYPE:
                return BadgeType(value)
            case _:
                return NotImplemented


class OrderingDirection(DescriptionMixin, enum.Enum):
    """The ordering direction enumeration.
    """
    DESC = 'desc'
    ASC = 'asc'


class BadgeRank(DescriptionMixin, OrderingMixin, enum.StrEnum):
    """Enumeration for badge ranks.
    """
    GOLD = 'gold'
    SILVER = 'silver'
    BRONZE = 'bronze'

    @staticmethod
    def from_export_value(export_value) -> 'BadgeRank':
        """Return the badge rank for the export value.

        :param export_value: The export value of the badge rank.
        :return: The badge rank.
        """
        match export_value:
            case '1':
                return BadgeRank.GOLD
            case '2':
                return BadgeRank.SILVER
            case '3':
                return BadgeRank.BRONZE
            case _:
                raise ValueError(f"Invalid export value {export_value}")

    @property
    def order(self) -> int:
        """Return an integer value used to order the badge rank.

        :return: An integer value used to order the badge rank.
        """
        match self:
            case BadgeRank.BRONZE:
                return 3
            case BadgeRank.SILVER:
                return 2
            case BadgeRank.GOLD:
                return 1
            case _:
                return NotImplemented


class BadgeType(DescriptionMixin, OrderingMixin, enum.StrEnum):
    """Enumeration for badge types.
    """
    NAMED = 'named'
    TAG_BASED = 'tag_based'

    @staticmethod
    def from_export_value(export_value) -> 'BadgeType':
        """Return the badge rank for the export value.

        :param export_value: The export value of the badge rank.
        :return: The badge rank.
        """
        match export_value:
            case 'True':
                return BadgeType.TAG_BASED
            case 'False':
                return BadgeType.NAMED
            case _:
                raise ValueError(f"Invalid export value {export_value}")

    @property
    def order(self) -> int:
        """Return an integer value used to order the badge type.

        :return: An integer value used to order the badge type.
        """
        match self:
            case BadgeType.TAG_BASED:
                return 2
            case BadgeType.NAMED:
                return 1
            case _:
                return NotImplemented


class PostType(DescriptionMixin, enum.StrEnum):
    """Enumeration for the post type.
    """
    QUESTION = 'question'
    ANSWER = 'answer'
    WIKI = 'wiki'
    TAG_WIKI_EXPERT = 'tag_wiki_expert'
    TAG_WIKI = 'tag_wiki'
    MODERATOR_NOMINATION = 'moderator_nomination'
    WIKI_PLACEHOLDER = 'wiki_placeholder'
    PRIVILEGE_WIKI = 'privilege_wiki'

    @staticmethod
    def from_export_value(export_value: str) -> 'PostType':
        """Return the badge rank for the export value.

        :param export_value: The export value of the badge rank.
        :return: The badge rank.
        """
        match export_value:
            case '1':
                return PostType.QUESTION
            case '2':
                return PostType.ANSWER
            case '3':
                return PostType.WIKI
            case '4':
                return PostType.TAG_WIKI_EXPERT
            case '5':
                return PostType.TAG_WIKI
            case '6':
                return PostType.MODERATOR_NOMINATION
            case '7':
                return PostType.WIKI_PLACEHOLDER
            case '8':
                return PostType.PRIVILEGE_WIKI
            case _:
                raise ValueError(f"Invalid export value {export_value}")


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


class ContentLicense(enum.StrEnum):
    """The content license enumeration
    """
    CC_BY_SA_2_5 = 'CC_BY_SA_2_5'
    CC_BY_SA_3_0 = 'CC_BY_SA_3_0'
    CC_BY_SA_4_0 = 'CC_BY_SA_4_0'

    @property
    def description(self) -> str:
        match self:
            case self.CC_BY_SA_2_5:
                return 'Attribution-ShareAlike 2.5 Generic'
            case self.CC_BY_SA_3_0:
                return 'Attribution-ShareAlike 3.0 Unported'
            case self.CC_BY_SA_4_0:
                return 'Attribution-ShareAlike 4.0 International'
            case _:
                raise ValueError(f"Invalid content licence value {self}")


class PostVoteType(DescriptionMixin, enum.IntEnum):
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


class PostLinkType(DescriptionMixin, enum.IntEnum):
    """Enumeration for the post link type.
    """
    LINKED = 1
    DUPLICATE = 3


class PostHistoryType(DescriptionMixin, enum.StrEnum):
    """Enumeration for the post history type.
    """
    INITIAL_TITLE = 'initial_title'
    INITIAL_BODY = 'initial_body'
    INITIAL_TAGS = 'initial_tags'
    EDIT_TITLE = 'edit_title'
    EDIT_BODY = 'edit_body'
    EDIT_TAGS = 'edit_tags'
    ROLLBACK_TITLE = 'rollback_title'
    ROLLBACK_BODY = 'rollback_body'
    ROLLBACK_TAGS = 'rollback_tags'
    POST_CLOSED = 'post_closed'
    POST_REOPENED = 'post_reopened'
    POST_DELETED = 'post_deleted'
    POST_UNDELETED = 'post_undeleted'
    POST_LOCKED = 'post_locked'
    POST_UNLOCKED = 'post_unlocked'
    COMMUNITY_OWNED = 'community_owned'
    POST_MIGRATED = 'post_migrated'
    QUESTION_MERGED = 'question_merged'
    QUESTION_PROTECTED = 'question_protected'
    QUESTION_UNPROTECTED = 'question_unprotected'
    QUESTION_UNMERGED = 'question_unmerged'
    SUGGESTED_EDIT_APPLIED = 'suggested_edit_applied'
    POST_TWEETED = 'post_tweeted'
    DISCUSSION_MOVED_TO_CHAT = 'discussion_moved_to_chat'
    POST_NOTICE_ADDED = 'post_notice_added'
    POST_NOTICE_REMOVED = 'post_notice_removed'
    POST_MIGRATED_AWAY = 'post_migrated_away'
    POST_MIGRATED_HERE = 'post_migrated_here'
    POST_MERGE_SOURCE = 'post_merge_source'
    POST_MERGE_DESTINATION = 'post_merge_destination'
    COMMUNITY_BUMP = 'community_bump'
    SELECTED_HOT_QUESTION = 'selected_hot_question'
    REMOVED_HOT_QUESTION = 'removed_hot_question'
    CREATED_FROM_ASK_WIZARD = 'created_from_ask_wizard'

    @staticmethod
    def from_export_value(export_value: str) -> 'PostHistoryType':
        """Return the badge rank for the export value.

        :param export_value: The export value of the badge rank.
        :return: The badge rank.
        """
        match export_value:
            case '1':
                return PostHistoryType.INITIAL_TITLE
            case '2':
                return PostHistoryType.INITIAL_BODY
            case '3':
                return PostHistoryType.INITIAL_TAGS
            case '4':
                return PostHistoryType.EDIT_TITLE
            case '5':
                return PostHistoryType.EDIT_BODY
            case '6':
                return PostHistoryType.EDIT_TAGS
            case '7':
                return PostHistoryType.ROLLBACK_TITLE
            case '8':
                return PostHistoryType.ROLLBACK_BODY
            case '9':
                return PostHistoryType.ROLLBACK_TAGS
            case '10':
                return PostHistoryType.POST_CLOSED
            case '11':
                return PostHistoryType.POST_REOPENED
            case '12':
                return PostHistoryType.POST_DELETED
            case '13':
                return PostHistoryType.POST_UNDELETED
            case '14':
                return PostHistoryType.POST_LOCKED
            case '15':
                return PostHistoryType.POST_UNLOCKED
            case '16':
                return PostHistoryType.COMMUNITY_OWNED
            case '17':
                return PostHistoryType.POST_MIGRATED
            case '18':
                return PostHistoryType.QUESTION_MERGED
            case '19':
                return PostHistoryType.QUESTION_PROTECTED
            case '20':
                return PostHistoryType.QUESTION_UNPROTECTED
            case '22':
                return PostHistoryType.QUESTION_UNMERGED
            case '24':
                return PostHistoryType.SUGGESTED_EDIT_APPLIED
            case '25':
                return PostHistoryType.POST_TWEETED
            case '31':
                return PostHistoryType.DISCUSSION_MOVED_TO_CHAT
            case '33':
                return PostHistoryType.POST_NOTICE_ADDED
            case '34':
                return PostHistoryType.POST_NOTICE_REMOVED
            case '35':
                return PostHistoryType.POST_MIGRATED_AWAY
            case '36':
                return PostHistoryType.POST_MIGRATED_HERE
            case '37':
                return PostHistoryType.POST_MERGE_SOURCE
            case '38':
                return PostHistoryType.POST_MERGE_DESTINATION
            case '50':
                return PostHistoryType.COMMUNITY_BUMP
            case '52':
                return PostHistoryType.SELECTED_HOT_QUESTION
            case '53':
                return PostHistoryType.REMOVED_HOT_QUESTION
            case '66':
                return PostHistoryType.CREATED_FROM_ASK_WIZARD
            case _:
                raise ValueError(f"Invalid export value {export_value}")

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
