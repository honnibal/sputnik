# cli/param defaults
list_meta = False
list_package_string = ''
search_string = ''
build_package_path = '.'
list_cache = False
repository_url = 'https://index.spacy.io'

try:
    import os
    import spacy.en
    data_path = os.path.abspath(os.path.join(os.path.dirname(spacy.en.__file__),
                                             '..', 'data'))
except (ImportError, AttributeError):
    data_path = None

# misc
CHUNK_SIZE = 1024 * 16
ARCHIVE_FILENAME = 'archive.gz'
META_FILENAME = 'meta.json'
COMPRESSLEVEL = 9
COOKIES_FILENAME = 'cookies.txt'
CACHE_DIRNAME = '__cache__'
