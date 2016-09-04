import requests
from BeautifulSoup import BeautifulSoup

from content import Content, InternetTraffic
from wrap_attributes_in_dict import wrap_attributes_in_dict



########################################################################
# Constants
########################################################################
BASE_URL = "https://extranet.derytelecom.ca/"
INDEX_PAGE_NAME = "index.php"
AUTH_PAGE_NAME = "auth_sess.php"

INDEX_URL = BASE_URL + INDEX_PAGE_NAME
AUTH_URL = BASE_URL + AUTH_PAGE_NAME

COOKIE_NAME = "PHPSESSID"

INPUT_LOGIN_NAME_SUFFIX = "_login"
INPUT_PASSWORD_NAME_SUFFIX = "_password"


class PARAM:
    """This class contain various constants that represent url
    parameters used to access the pages that are available once loged on
    the Derytelecom extranet."""

    LOGOUT = {'logout' : '1'}

    class CONTENT:
        @wrap_attributes_in_dict("sub", {"content" : "internet"})
        class INTERNET:
            TRAFFIC  = "traffic"
            EMAIL    = "email"
            WIRELESS = "wireless"

    @wrap_attributes_in_dict("lang")
    class LANG:
        FRA = "fra"
        ENG = "eng"


########################################################################
# Class
########################################################################


class DerytelecomExtranetQuery:
    """This class represent a session with the Derytelecom Extranet. To
    use it, you must first connect to the Extranet using the class
    method connect. After that, you can query content from the Extranet
    using the get_content method.
    """


    def __init__(self, session):
        """This constructor should not be used"""
        self._connected = True
        self._session = session

    @classmethod
    def connect(cls, username, password):
        """The constructor of this class, it establish a connection with
        the Derytelecom Extranet and then return an instance of this
        class.

        Arguments:
        username -- the username to use to log in
        password -- the password to use to log in

        Return:
        An instance of the DerytelecomExtranetQuery class.
        """

        session = requests.Session()

        try:
            # First contact, retrieve the login page
            r = session.get(BASE_URL)
            cls._check_response(r)

            cookie_value = r.cookies[COOKIE_NAME]

            input_login_name = cookie_value + INPUT_LOGIN_NAME_SUFFIX
            input_password_name = cookie_value + INPUT_PASSWORD_NAME_SUFFIX

            # This is the part where a connection is established with
            # the Extranet
            payload = {input_login_name    : username,
                       input_password_name : password}
            r = session.post(AUTH_URL, data=payload)
            cls._check_response(r)

            return cls(session)

        except:
            session.close()
            raise



    @staticmethod
    def _check_response(response):
        # This static method check if a communication with the
        # Derytelecom Extranet was successful. If not, it raise a
        # HTTPNotOKError exception.

        status_code = response.status_code

        if status_code != 200:
            raise HTTPNotOKError(response.url,
                                 status_code,
                                 response.reason)


    @property
    def connected(self):
        """Return True if the instance is connected on the Derytelecom
        Extranet, False otherwise"""

        return self._connected


    def get_content(self, content_param, content_class=Content):
        """Retrieve the web page that is associated with the specified
        content url parameter. That web page is then encapsulated in the
        specified Content class.


        Arguments:
        content_param -- the content url param that needed to obtain the
                         desired web page
        content_class -- the class to use to encapsulte the retrived web
                         page

        Return:
        The retrived web page encapsulated in a Content class or None
        """

        if self._connected:
            payload = content_param.copy()
            # Access the english page
            payload.update(PARAM.LANG.ENG)
            r = self._session.get(INDEX_URL, params = payload)
            self._check_response(r)

            return content_class(r.text)

        else:
            return None


    def get_internettraffic(self):
        """Convenience method to retrive the internet traffic web page
        encapsulated in a InternetTrafic class."""

        return self.get_content(PARAM.CONTENT.INTERNET.TRAFFIC,
                                InternetTraffic)



    def disconnect(self):
        """Disconnect from the Derytelecom extranet."""

        if self._connected:
            self._session.get(INDEX_URL, params = PARAM.LOGOUT)
            self._session.close()
            self._connected =  False


    def __enter__(self):
        return self

    def __exit__(self, *args):
        return self.disconnect()







########################################################################
# Exceptions
########################################################################
class HTTPNotOKError(Exception):
    """This exception is raised when a request return a response with a
    status code that is different of HTTP OK."""

    def __init__(self, url, status_code, reason):
        self.url = url
        self.status_code = status_code
        self.reason = reason

        self.msg = "Reaching '{}' returned this status code: {} {}" \
                   .format(url, status_code, reason)

    def __str__(self):
        return self.msg
