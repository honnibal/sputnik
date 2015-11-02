import os

# cli/param defaults
install_repository_url = os.environ['REPOSITORY_URL']
upload_repository_url = os.environ['REPOSITORY_URL']
update_repository_url = os.environ['REPOSITORY_URL']
list_meta = False
list_package_string = '*'
build_package_path = '.'

# misc
CHUNK_SIZE = 1024 * 16
ARCHIVE_FILENAME = 'archive.gz'
META_FILENAME = 'meta.json'
COMPRESSLEVEL = 9
COOKIES_FILENAME = 'cookies.txt'
