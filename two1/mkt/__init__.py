"""Make purchases in the 21 marketplace."""
import sys
import two1.lib.bitrequests as bitrequests


class Market:
    """A convenience library import for accessing 21 marketplace resources.

    Usage:
        from two1 import mkt
        mkt.sentiment.analyze('This is a positive statement!')
    """

    DEFAULT_MARKET_HOST = 'https://mkt.21.co'

    def __init__(self):
        """Return a new Market instance."""
        self.resource = ''
        self.host = Market.DEFAULT_MARKET_HOST
        self.bitrequests = bitrequests

    def __getattr__(self, resource):
        """Recursively look up the resource being requested."""
        self.resource = self.resource + '/' + resource
        return self

    def __call__(self, _data=None, **kwargs):
        """Make a HTTP to the requested resource.

        This method allows `mkt` to be called directly in order to send an
        HTTP request to a resource. It will use the base url `self.host`,
        combined with any attributes following `mkt` in its call.

        e.g. mkt.this.resource() will send a GET to https://mkt.21.co/this/resource

        Optionally, self.host can be overriden by users. Calls default to using
        a GET request if no parameters are passed.

        Args:
            _data (dict): the JSON data to be sent with a POST request.
            kwargs (dict): the URL-encoded data to be sent with a GET request.

        Returns:
            dict or str: the JSON response if possible, plaintext otherwise.

        Raises:
            ValueError: basic parameters for request call were not satisfied.
            ConnectionError: server unknown or no response received.
            requests.exceptions.HTTPError: 4xx or 5xx response from the server.

        """
        # GET request with the keyword arguments passed
        if not _data:
            method = 'get'
            options = dict(params=kwargs)

        # POST request with the dictionary passed
        elif isinstance(_data, dict):
            method = 'post'
            options = dict(json=_data)

        # Otherwise raise on bad input error
        else:
            raise ValueError('Bad input provided to mkt.{}()'.format(self.resource[1:]))

        try:
            response = self.bitrequests.request(method, self.host + self.resource, **options)
        except bitrequests.bitrequests.requests.exceptions.ConnectionError:
            raise ConnectionError('Could not connect to host.') from None

        # Raise errors on any 4xx or 5xx server response
        response.raise_for_status()

        # Reset resource value for subsequent calls
        self.resource = ''

        try:
            return response.json()
        except ValueError:
            return response.text


# Set the `mkt` module import to an instance of the `Market` object above
# https://mail.python.org/pipermail/python-ideas/2012-May/014969.html
sys.modules[__name__] = Market()