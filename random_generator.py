import random

def id(letters: int) -> str:
    """
    Generate a random ID of a given length. The ID is a string of uppercase letters and numbers.
    
    Parameters
    ----------
    letters : int
        The length of the ID to generate.

    Returns
    -------
    str
        The generated ID.
    """
    return ''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=letters))


def cookie() -> str:
    """
    Generate a random cookie. The cookie is a string of uppercase and lowercase letters, special characters and numbers.
    
    Returns
    -------
    str
        The generated cookie.
    """
    return ''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789", k=32))