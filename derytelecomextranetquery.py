import requests
import re
from BeautifulSoup import BeautifulSoup


########################################################################
# Constants
########################################################################
BASE_URL = "https://extranet.derytelecom.ca/"
INDEX_PAGE_NAME = "index.php" 

INDEX_URL = BASE_URL + INDEX_PAGE_NAME




class PARAM:
    """This class contain various constants that represent url 
    parameters used to access the pages that are available once loged on
    the Derytelecom extranet."""
    
    LOGOUT = {'logout' : '1'}
    
    class CONTENT:
        class INTERNET:
            _base = ('content', 'internet')
            _key = 'sub'
            TRAFFIC  = dict(( (_key, 'traffic'), _base ))
            EMAIL    = dict(( (_key, 'email'), _base ))
            WIRELESS = dict(( (_key, 'wireless'), _base ))
    
    class LANG:
        _key = 'lang'
        FRA = {_key : 'fra'}
        ENG = {_key : 'eng'}


# String constants used to retrive some element on the received html 
# pages
AVAILABLE_STRING = "Available"
USED_STRING = "Used"



########################################################################
# Class
########################################################################


class Content:
    """Basic class used to act as an interface for the web pages 
    retrived from the Derytelecom extranet. It should be subclassed 
    instead of being used directly."""
    
    def __init__(self, html_page):
        self._soup = BeautifulSoup(html_page)


class InternetTraffic(Content):
    """This class act as an interface for the Internet > Traffic page.
    """
    
    def get_string_after_colon(self, string_before_colon):
        """The Internet > Trafic page contain a lot of strings that are
        separated by colon. Pass the string before the colon and this 
        method will return the string that is after the colon.
        
        Exemple:
            Supose on the web page you have something like this:
                Available: 60.3 Gb
            If you pass the string "Available" to this method, it should
            return you "60.3 Gb".
            
        Argument:
        string_before_colon -- the string before the colon
        
        Return:
        The string after the colon or ''
        """
        
        string_after_colon = ''
        
        sbc = self._soup.find(text=re.compile(string_before_colon))
        if sbc:
            # Get the strings that are after the specified string
            sac_list = sbc.parent.contents[1:]
            
            # Remove irrevelant spaces and joins the strings
            string_after_colon = " ".join(s.string.strip() 
                for s in sac_list)
            
        return string_after_colon
            
        
    def get_available(self):
        """Return a string that represent the amount of data that is 
        available or ''.
        
        Exemple of return value: 60.3 Gb
        """
        available = self.get_string_after_colon(AVAILABLE_STRING)
        
        # If available is an empty string, that probably mean that the 
        # Available string is no longer displayed
        # Don't really know why, but it seem that when there are less 
        # than 15 Gb of available data the Available string is no longer
        # displayed
        # When that happen, we find the Used string that we then use to 
        # reach the span element that contain the strings that display 
        # the remaining data
        if available == '':
            # Find Used string
            used_elem = self._soup.find(text=re.compile(USED_STRING))
            
            if used_elem:
                # Reach the span that contain the remaining data strings
                av_elem = used_elem.parent.parent \
                    .findNextSibling('div').find("span")
                
                # Get the remaining data strings (start from 1 to skip 
                # the newline)
                available_strings = av_elem.contents[1:]
                
                # Remove irrevelant spaces and joins the strings
                available = " ".join(s.string.strip() 
                    for s in available_strings)
                    
        return available




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
            
            # Some informations must be retrived from the login page:
            # the name of the login input and the name of the password
            # input.
            auth_page_name, input_login_name, input_password_name = \
                cls._get_authpage_login_password_name(r.text)
            
            # This is the part where a connection is established with
            # the Extranet
            payload = {input_login_name    : username, 
                       input_password_name : password}
            r = session.post(BASE_URL + auth_page_name, data=payload)
            cls._check_response(r)
            
            return cls(session)
            
        except:
            session.close()
            raise
        
    @staticmethod
    def _get_authpage_login_password_name(html_page):
        # Retrieve the name of the login input and the name of the 
        # password input.
        # The name of these elements change everytime, that is why 
        # it isn't hard coded in the source.
        
        soup = BeautifulSoup(html_page)

        form = soup.form
        
        input_login, input_password = form.findAll("input")[0:2]
        input_login_name = input_login['name']
        input_password_name = input_password['name']
        
        auth_page_name = form['action']
        
        return auth_page_name, input_login_name, input_password_name
    
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





########################################################################
# Main
########################################################################


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print >> sys.stderr, "Error, not enough arguments, 2 are required"
        
        print >> sys.stderr, "python derytelecomextranetquery [USERNAME] [PASSWORD]"
        sys.exit(1)
        
    username = sys.argv[1]
    password = sys.argv[2]
    
    with DerytelecomExtranetQuery.connect(username, password) as deq:
        inet_traffic = deq.get_internettraffic()
        available = inet_traffic.get_available()
        print(available)
    
    
    
