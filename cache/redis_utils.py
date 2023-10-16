def set_redis_name(user_id: int, prefix: str = '') -> str:
    """Create a Redis data structure name for a user.

    This function generates a unique name for a Redis key used to store data
    associated with a specific user. The name is constructed by combining the
    optional prefix with the user's ID.

    :param user_id: int: The user's unique identifier.
    :param prefix: str: An optional prefix to include in the name (default is an empty
    string).
    :return: str: The constructed Redis key name.
    """
    name = f"{prefix}:{user_id}"
    return name
