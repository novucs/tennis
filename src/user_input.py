MALE = False
FEMALE = True

FILE = True
TYPED = False


def next_string(message, default=None):
    """Fetches a string from the user.

    :param message: The message to prompt the user.
    :param default: The default value.
    :return: The user input string.
    """

    while True:
        if default is None:
            user_input = input(message + ': ')
        else:
            user_input = input(message + ' (' + default + '): ')

        if user_input == '':
            return default
        else:
            return user_input


def next_bool(message, default=None):
    """Fetches a boolean from the user.

    :param message: The message to prompt the user.
    :param default: The default value.
    :return: The user input boolean.
    """

    while True:
        default_text = 'Y/n' if default else 'y/N'
        user_input = next_string(message, default_text)

        if user_input == default_text:
            return default

        parsed = user_input.lower()

        if parsed.startswith('y') or parsed.startswith('t'):
            return True
        elif parsed.startswith('n') or parsed.startswith('f'):
            return False


def next_int(message, default=None):
    """Fetches an int from the user.

    :param message: The message to prompt the user.
    :param default: The default value.
    :return: The user input int.
    """

    while True:
        default_text = None if default is None else str(default)
        user_input = next_string(message, default_text)

        if user_input is not None:
            try:
                parsed = int(user_input)
                return parsed
            except ValueError:
                pass


def next_float(message, default=None):
    """Fetches a float from the user.

    :param message: The message to prompt the user.
    :param default: The default value.
    :return: The user input float.
    """

    while True:
        default_text = None if default is None else str(default)
        user_input = next_string(message, default_text)

        if user_input is not None:
            try:
                parsed = float(user_input)
                return parsed
            except ValueError:
                pass


def next_gender(message, default=None):
    """Fetches a gender from user input.

    :param message: The message to prompt the user.
    :param default: The default value.
    :return: The user submitted gender.
    """

    while True:
        default_text = 'm/F' if default else 'M/f'
        user_input = next_string(message, default_text)

        if user_input is not None:
            parsed = user_input.lower()

            if parsed.startswith('f'):
                return FEMALE
            elif parsed.startswith('m'):
                return MALE


def next_input_type(message, default: bool = None):
    while True:
        default_text = 'file/TYPED' if default else 'FILE/typed'
        user_input = next_string(message, default_text)

        if user_input is not None:
            parsed = user_input.lower()

            if parsed.startswith('f'):
                return FILE
            elif parsed.startswith('t'):
                return TYPED
