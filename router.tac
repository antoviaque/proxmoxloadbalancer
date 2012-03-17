import random, time, numpy

from twisted.web import resource, server, client
from twisted.application import service, internet
from twisted.internet import threads

class RouterResource(resource.Resource):
    isLeaf = True
    max_request_time = 1.0
    nb_sample_requests = 100
    online_nodes = ['127.0.0.1']
    online_nodes_requests = {'127.0.0.1': []}
    starting_server = False
    available_nodes = [(301, '37.59.162.221'),
                       (302, '37.59.162.222'),
                       (303, '37.59.162.223'),]
    
    def render_GET(self, request):
        self.check_need_new_node()
        node = random.choice(self.online_nodes)
        
        time_start = time.time()
        d = client.getPage('http://%s:7001/' % node)
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
            threads.deferToThread(self.add_new_node)
            return
        
        median_request_time = self.get_median_request_time()
        print 'Median request time: ', median_request_time, ' - Nb of nodes: ', len(self.online_nodes)
        if median_request_time is not None and median_request_time > self.max_request_time:
            reactor.defer_to_thread(add_new_node)
            return
        
    def add_new_node(self):
        if not self.available_nodes or self.starting_server:
            return
        
        self.starting_server = True
        
        # Empty history (need to compute new median values)
        for requests_times in self.online_nodes_requests.itervalues():
            del requests_times[:]
        
        node = self.available_nodes.pop()
        print "Adding new node ", node
        
        print api('POST', 
                  'nodes/octopus/openvz', 
                  {
                      'cpus': 1,
                      'description': 'Test',
                      'disk': 2,
                      'hostname': node[1]+'.test.plebia.org',
                      'ip_address': node[1],
                      'memory': 512,
                      'onboot': 0,
                      'ostemplate': 'local:vztmpl/debian-6.0-fiboserver_6.0-4_amd64.tar.gz',
                      'password': 'test123',
                      'storage': 'local',
                      'swap': 512,
                      'vmid': node[0],
                  })

        time.sleep(60)

        print api('POST',
                  'nodes/octopus/openvz/%d/status/start' % node[0])

        time.sleep(5)

        print api('GET',
                  'nodes/octopus/openvz/%d/status/current' % node[0])
        
        self.online_nodes_requests[node[1]] = []
        self.online_nodes.append(node[1])
        self.starting_server = False
        

application = service.Application("Fibonacci Distributed Service")
site = server.Site(RouterResource())
service = internet.TCPServer(7000, site)
service.setServiceParent(application)

