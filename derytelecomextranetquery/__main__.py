import sys
from derytelecomextranetquery import DerytelecomExtranetQuery

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
