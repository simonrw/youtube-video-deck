import requests


class YoutubeClient(object):
    """
    Provides an abstraction over the Youtube API.

    This object decouples the domain models from the Youtube API. It supports
    the following methods:

    * Search Youtube for either the channel or playlist with the given name
    * Fetch new items (videos) since a specified time
    """

    def __init__(self, api_key):
        self.api_key = api_key
        self.session = requests.Session()
        # TODO: add any request parameters

    def _fetch(self, url, params=None):
        """
        Helper method for fetching data from the Youtube API. This:

        * provides a mocking point for testing the rest of the API, and
        * unifies request making
        """
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()
