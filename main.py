from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, quote
import re, json

urls = {}
with open("urls.list", "r", encoding="utf-8") as fd:
	for line in fd.readlines():
		split = line.split(" ")
		if len(split) != 2:
			continue

		path = split[0]
		url = split[1]
		url = url[0 : len(url) - 1]
		url = json.loads(url)

		urls[path] = url

fd = open("urls.list", "a", encoding="utf-8")

reg = re.compile("^/?\w.*$")

ADDR = "0.0.0.0"
PORT = 8080

class RequestHandler(BaseHTTPRequestHandler):
	def send(self, msg):
		self.wfile.write(msg.encode("utf-8"))

	def redirectTo(self, url):
		self.send_response(302)
		self.send_header('Content-type', 'text/text; charset=utf-8')
		self.send_header("Location", quote(url, safe="/:."))
		self.end_headers()
		self.send("")

	def do_GET(self):
		subdomain = "/" + self.headers["host"].split(".")[0]

		if self.path == "/url-shortener":
			self.send_response(200)
			self.end_headers()
			with open("interface.html", "r") as fd:
				self.send(fd.read())
		elif self.path == "/" and subdomain in urls:
			self.redirectTo(urls[subdomain])
		elif self.path in urls:
			self.redirectTo(urls[self.path])
		else:
			self.send_response(404)
			self.end_headers()
			self.send("Invalid path " + self.path)

	def do_POST(self):
		length = int(self.headers["Content-Length"])
		data = parse_qs(self.rfile.read(length).decode("utf-8"))

		print(data)

		if "path" in data and "url" in data and reg.match(data["path"][0]) is not None:
			path = data["path"][0]
			url = data["url"][0]
			if path[0] != "/":
				path = "/" + path

			urls[path] = url
			fd.write("{} {}\n".format(path, json.dumps(url)))
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
