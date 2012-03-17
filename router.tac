import random, time, numpy

from twisted.web import resource, server, client
from twisted.application import service, internet

class RouterResource(resource.Resource):
    isLeaf = True
    max_request_time = 1.0
    nb_sample_requests = 100
    online_nodes = []
    online_nodes_requests = {}
    available_nodes = ['http://127.0.0.1:7001/',
                       'http://127.0.0.1:7002/',
                       'http://127.0.0.1:7003/',]
    
    def render_GET(self, request):
        self.check_need_new_node()
        node = random.choice(self.online_nodes)
        
        time_start = time.time()
        d = client.getPage(node)
        d.addCallback(self.respond, request, node, time_start)
        
        return server.NOT_DONE_YET

    def respond(self, data, request, node, time_start):
        request_time = time.time() - time_start
        self.online_nodes_requests[node].append(request_time)
        
        request.setHeader('Content-Type', 'text/plain; charset=utf-8')
        request.write(data)
        request.finish()
        
    def get_median_request_time(self):
        res = []
        for requests_times in self.online_nodes_requests.itervalues():
            if len(requests_times) > self.nb_sample_requests:
                res.append(numpy.median(requests_times[-self.nb_sample_requests:]))
        
        if res:
            return numpy.median(res)
        else:
            return None
    
    def check_need_new_node(self):
        if len(self.online_nodes) < 1:
            self.add_new_node()
            return
        
        median_request_time = self.get_median_request_time()
        print 'Median request time: ', median_request_time, ' - Nb of nodes: ', len(self.online_nodes)
        if median_request_time is not None and median_request_time > self.max_request_time:
            self.add_new_node()
            return
        
    def add_new_node(self):
        if not self.available_nodes:
            return
        
        # Empty history (need to compute new median values)
        for requests_times in self.online_nodes_requests.itervalues():
            del requests_times[:]
        
        node = self.available_nodes.pop()
        print "Adding new node ", node
        self.online_nodes_requests[node] = []
        self.online_nodes.append(node)
        

application = service.Application("Fibonacci Distributed Service")
site = server.Site(RouterResource())
service = internet.TCPServer(7000, site)
service.setServiceParent(application)

