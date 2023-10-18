from enum import Enum


class Permission(Enum):
    GET_PUBLIC_ARTICLES = "GET_PUBLIC_ARTICLES"
    GET_PUBLIC_COMMENTS = "GET_PUBLIC_COMMENTS"

    # User
    GET_SELF_ARTICLES = "GET_SELF_ARTICLES"
    UPDATE_SELF_ARTICLES = "UPDATE_SELF_ARTICLES"
    DELETE_SELF_ARTICLES = "DELETE_SELF_ARTICLES"
    CREATE_SELF_ARTICLES = "CREATE_SELF_ARTICLES"

    CREATE_COMMENT = "CREATE_COMMENT"
    UPDATE_SELF_COMMENT = "UPDATE_SELF_COMMENT"
    DELETE_SELF_COMMENT = "DELETE_SELF_COMMENT"

    GET_SELF_NOTIFICATIONS = "GET_SELF_NOTIFICATIONS"
    DELETE_SELF_NOTIFICATION = "DELETE_SELF_NOTIFICATION"

    RATE_ARTICLES = "RATE_ARTICLES"

    # Superuser
    GET_PRIVATE_ARTICLES = "GET_PRIVATE_ARTICLES"
    UPDATE_USER_ARTICLES = "UPDATE_USER_ARTICLES"
    DELETE_USER_ARTICLES = "DELETE_USER_ARTICLES"

    DELETE_USER_COMMENT = "DELETE_USER_COMMENT"
    UPDATE_USER_COMMENT = "UPDATE_USER_COMMENT"
    GET_DELETED_COMMENTS = "GET_DELETED_COMMENTS"