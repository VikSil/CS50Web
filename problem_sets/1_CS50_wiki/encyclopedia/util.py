import re
from random import randint

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


def list_entries():
    """
    Returns a list of all names of encyclopedia entries.
    """
    _, filenames = default_storage.listdir("entries")
    return list(
        sorted(
            re.sub(r"\.md$", "", filename)
            for filename in filenames
            if filename.endswith(".md")
        )
    )


def save_entry(title, content):
    """
    Saves an encyclopedia entry, given its title and Markdown
    content. If an existing entry with the same title already exists,
    it is replaced.
    """
    filename = f"entries/{title}.md"
    if default_storage.exists(filename):
        default_storage.delete(filename)
    default_storage.save(filename, ContentFile(content.encode("ascii")))


def get_entry(title):
    """
    Retrieves an encyclopedia entry by its title. If no such
    entry exists, the function returns None.
    """
    try:
        f = default_storage.open(f"entries/{title}.md")
        return f.read().decode("utf-8")
    # if exception happens, return 404
    except FileNotFoundError:
        return None


def get_random_entry():
    """
    Returns a random entry out of all entries on the encyclopedia.
    """
    # get all entries using the same function that lists them on index page
    all_entries = list_entries()
    # pick a random one and return
    return all_entries[randint(0, len(all_entries) - 1)]


def find_entry(entryname):
    """
    Finds entries that have the search keyword as part of their title
    """
    all_entries = list_entries()
    return [entry for entry in all_entries if entryname.lower() in entry.lower()]
