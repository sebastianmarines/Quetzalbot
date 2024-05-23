import random
import string


def generate_random_filename(length=20, extension=".png"):
    characters = string.ascii_letters + string.digits
    filename = "".join(random.choice(characters) for _ in range(length))
    filename += extension

    return filename
