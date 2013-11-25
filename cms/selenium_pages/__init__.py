import os

# Get the hostname of the instance from the environment
BASE_URL = "{0}://{1}".format(os.environ.get('protocol', 'http'), os.environ.get('test_host', ''))
