from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, quote

urls = {}
with open("urls.list", "r", encoding="utf-8") as fd:
	for line in fd.readlines():
		split = line.split(" ")
		if len(split) != 2:
			continue

		path = split[0]
		url = split[1]
		url = url[0 : len(url) - 1]

		urls[path] = url

fd = open("urls.list", "a", encoding="utf-8")

ADDR = "0.0.0.0"
PORT = 8080

class RequestHandler(BaseHTTPRequestHandler):
	def send(self, msg):
		self.wfile.write(msg.encode("utf-8"))

	def do_GET(self):
		if self.path == "/url-shortener":
			self.send_response(200)
			self.end_headers()
			with open("interface.html", "r") as fd:
				self.send(fd.read())
		elif self.path in urls:
			self.send_response(302)
			self.send_header('Content-type', 'text/text; charset=utf-8')
			self.send_header("Location", quote(urls[self.path], safe="/:."))
			self.end_headers()
			self.send("")
		else:
			self.send_response(404)
			self.end_headers()
			self.send("Invalid path " + self.path)

	def do_POST(self):
		length = int(self.headers["Content-Length"])
		data = parse_qs(self.rfile.read(length).decode("utf-8"))

		if "path" in data and "url" in data and "path" != "/":
			path = data["path"][0]
			url = data["url"][0].replace(" ", "+")
			if path[0] != "/":
				path = "/" + path

			urls[path] = url
			fd.write("{} {}\n".format(path, url))
			fd.flush()

			self.send_response(200)
			self.end_headers()
			self.send("ok")
		else:
			self.send_response(400)
			self.end_headers()
			self.send("Invalid Request!")

httpd = HTTPServer((ADDR, PORT), RequestHandler)
print("Webserver started on Port " + str(PORT))
httpd.serve_forever()
