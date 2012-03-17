from twisted.web import server
from twisted.application import service, internet
from fibonacci import FibonacciResource

application = service.Application("Fibonacci Server")
site = server.Site(FibonacciResource())
service = internet.TCPServer(7003, site)
service.setServiceParent(application)
