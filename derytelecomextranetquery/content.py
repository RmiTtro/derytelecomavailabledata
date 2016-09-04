import re
from BeautifulSoup import BeautifulSoup

# String constants used to retrive some element on the Internet > Traffic page
AVAILABLE_STRING = "Available"
USED_STRING = "Used"


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

        Example:
            Supose on the web page you have something like this:
                Available: 60.3 Gb
            If you pass the string "Available" to this method, it should
            return you "60.3 Gb".

        Argument:
        string_before_colon -- the string before the colon

        Return:
        The string after the colon or ""
        """

        string_after_colon = ""

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
        available or "".

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
        if available == "":
            # Find Used string
            used_elem = self._soup.find(text=re.compile(USED_STRING))

            if used_elem:
                # Reach the span that contain the remaining data strings
                av_elem = used_elem.parent.parent \
                    .findNextSibling("div").find("span")

                # Get the remaining data strings (start from 1 to skip
                # the newline)
                available_strings = av_elem.contents[1:]

                # Remove irrevelant spaces and joins the strings
                available = " ".join(s.string.strip()
                    for s in available_strings)

        return available
