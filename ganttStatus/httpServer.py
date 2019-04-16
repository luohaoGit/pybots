from http.server import HTTPServer, BaseHTTPRequestHandler
import json

data = {'result': 'this is a test'}
host = ('localhost', 8888)


class Resquest(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        _, *filename = self.path
        if filename:
            try:
                fn = ''.join(filename)
                with open(''.join(fn), 'rb') as f:
                    content = f.read()
                    self.send_response(200)
                    if fn.endswith('json'):
                        self.send_header('Content-type', 'application/json')
                    else:
                        self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(content)
            except IOError:
                self.send_error(404, 'File Not Found: %s' % self.path)
        else:
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())


if __name__ == '__main__':
    server = HTTPServer(host, Resquest)
    print("Starting server, listen at: %s:%s" % host)
    server.serve_forever()