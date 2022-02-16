import random
import string


def generate_random_str(length: int) -> str:
    base_str = string.ascii_uppercase + string.digits
    return ''.join((random.choice(base_str) for i in range(length)))
