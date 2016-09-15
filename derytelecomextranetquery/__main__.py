# -*- coding: utf-8 -*-

"""
derytelecomextranetquery
------------------------

Main of the derytelecomextranetquery console application.

Copyright(c) 2016 Rémi Tétreault <tetreault.remi@gmail.com>
MIT Licensed, see LICENSE for more details.
"""


import sys
import argparse
from derytelecomextranetquery import *



PAGES = {
    "home" : {},
    "profile" : PARAM.CONTENT.PROFIL,
    "internet" : PARAM.CONTENT.INTERNET,
    "phone" : PARAM.CONTENT.TELEPHONIE,
    "television" : PARAM.CONTENT.TELEVISION,
    "invoicing" : PARAM.CONTENT.FACTURATION
}


SUBPAGES = {
    "address" : PARAM.CONTENT.SUB.PROFIL.PROFIL,
    "password" : PARAM.CONTENT.SUB.PROFIL.PASSWORD,
    "notifications" : PARAM.CONTENT.SUB.PROFIL.NOTIFICATIONS,

    "internetusage" : PARAM.CONTENT.SUB.INTERNET.TRAFFIC,
    "email" : PARAM.CONTENT.SUB.INTERNET.EMAIL,
    "wireless" : PARAM.CONTENT.SUB.INTERNET.WIRELESS,

    "longdistance" : PARAM.CONTENT.SUB.TELEPHONIE.INTERURBAIN,
    "voicemail" : PARAM.CONTENT.SUB.TELEPHONIE.VOICEMAIL,
    "calltransfert" :PARAM.CONTENT.SUB.TELEPHONIE.CALL_TRANSFER
}


LANG = {
    "fra" : PARAM.LANG.FRA,
    "eng" : PARAM.LANG.ENG
}


EXITCODE_FOR_EXCEPTIONS = {
    DerytelecomExtranetQueryException : 3,
    InternetConnectionError : 4,
    HTTPNotOKError : 5,
    BadUsernamePasswordError : 6,
    UnexpectedLogOutError : 7
}



def derytelecom_open(args):
    parser = args.parser
    params = {}
    page = args.page
    subpage = args.subpage
    lang = args.lang
    username = args.username
    password = args.password

    params.update(PAGES.get(page, {}))
    params.update(SUBPAGES.get(subpage, {}))
    params.update(LANG.get(lang, {}))

    DerytelecomExtranetQuery.open_in_webbrowser(params, username, password)


def derytelecom_get(args):
    parser = args.parser
    data = args.data
    username = args.username
    password = args.password

    if data == 'availabledata':
        try:
            with DerytelecomExtranetQuery.connect(username, password) as deq:
                inet_traffic = deq.get_internettraffic()
                available = inet_traffic.get_available()
                print(available)

        except DerytelecomExtranetQueryException as e:
            exitcode = EXITCODE_FOR_EXCEPTIONS[type(e)]
            parser.exit(exitcode, "error: {}\n".format(e))

        except:
            # For unknow exceptions, act as if they were
            # DerytelecomExtranetQueryException exceptions,
            # with the same exit code and error message.
            exitcode = EXITCODE_FOR_EXCEPTIONS[
                DerytelecomExtranetQueryException]
            e = DerytelecomExtranetQueryException()
            parser.exit(exitcode, "error: {}\n".format(e))

    else:
        parser.error("'{}' is not a valid data to retrieve".format(data))





parser = argparse.ArgumentParser(
    description='Query content from the Derytelecom Extranet.')
subparsers = parser.add_subparsers(title='Available sub-commands',
                                   metavar='')

parser_open = subparsers.add_parser('open',
    help='Open a page from the Derytelecom Extranet in the web browser')
parser_open.add_argument('-p', '--page', dest='page',
    default='internet', choices=PAGES,
    help='the page to open (default: internet)')
parser_open.add_argument('-s', '--subpage', dest='subpage', default='',
    choices=SUBPAGES, help='the subpage to open')
parser_open.add_argument('-l', '--lang', dest='lang', default='',
    choices=LANG, help='the langue to use')
parser_open.add_argument('username', nargs='?', default='',
    help='the username to use to auto log in')
parser_open.add_argument('password', nargs='?', default='',
    help='the password to use to auto log in')
parser_open.set_defaults(func=derytelecom_open, parser=parser_open)


parser_get = subparsers.add_parser('get',
    help='Retrieve data from the Derytelecom Extranet')
parser_get.add_argument('data', nargs='?', default='availabledata',
    help='the data to retrieve (default: availabledata)')
parser_get.add_argument('username', help='the username to use to log in')
parser_get.add_argument('password', help='the password to use to log in')
parser_get.set_defaults(func=derytelecom_get, parser=parser_get)


args = parser.parse_args()
args.func(args)
