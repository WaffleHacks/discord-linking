from flask import session


def __remove_key(key):
    """
    Remove a key from the session even if it doesn't exist
    :param key: the key to remove
    """
    try:
        del session[key]
    except KeyError:
        pass


def set(error, title=None, try_again=True):
    """
    Set an error to be displayed
    :param error: the main error body
    :param title: an optional title to overwrite
    :param try_again: whether to show the try again button
    """
    # Unset any oauth states
    __remove_key("auth0:login")
    __remove_key("discord:login")

    # Set the error
    session["error"] = error
    session["error:title"] = title
    session["error:try-again"] = try_again
