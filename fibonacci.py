from twisted.web import resource, server
from twisted.internet import threads

def fibonacci(nb):
    first = 0
    second = 1

    for i in xrange(nb - 1):
        new = first + second
        first = second
        second = new

    return second


class FibonacciResource(resource.Resource):
    isLeaf = True
    
    def render_GET(self, request):
        request.setHeader('Content-Type', 'text/plain; charset=utf-8')
        return str(fibonacci(50000))

#    def render_GET(self, request):
#        d = threads.deferToThread(fibonacci, 20000)
#        d.addCallback(self.respond, request)    
#        return server.NOT_DONE_YET
#
#    def respond(self, result, request):
#        output = str(result).encode('utf-8')
#        request.setHeader('Content-Type', 'text/plain; charset=utf-8')
#        request.write(output)
#        request.finish()

