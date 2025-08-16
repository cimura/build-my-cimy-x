import socket
import ssl

class URL:
	def __init__(self, url):
		self.scheme, url = url.split("://", 1)
		assert self.scheme in ["http", "https", "file"]
		if self.scheme == "http":
			self.port = 80
		if self.scheme == "https":
			self.port = 443
		if self.scheme == "file":
			self.port = None
			self.path = url
			self.host = None
			return
		if "/" not in url:
			url = url + "/"
		self.host, url = url.split("/", 1)
		self.path = "/" + url
		if ":" in self.host:
			self.host, port = self.host.split(":", 1)
			self.port = int(port)

	def request(self):
		if self.scheme == "file":
			return self.request_file()
		else:
			return self.request_http()

	def request_file(self):
		"""ローカルファイルの読み込み"""
		try:
			file_path = self.path
			if file_path.startswith('/') and len(file_path) > 1 and file_path[2] == ':':
				file_path = file_path[1:]
			
			with open(file_path, 'r', encoding='utf-8') as f:
				content = f.read()
			#print(content)
			return content
		except FileNotFoundError:
			raise Exception(f"File not found: {file_path}")
		except Exception as e:
			raise Exception(f"Error reading file: {e}")

	def request_http(self):
		s = socket.socket(
			family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP,
		)
		s.connect((self.host, self.port))
		if self.scheme == "https":
			ctx = ssl.create_default_context()
			s = ctx.wrap_socket(s, server_hostname=self.host)
		request = "GET {} HTTP/1.0\r\n".format(self.path)
		request += "Host: {}\r\n".format(self.host)
		request += "\r\n"
		s.send(request.encode("utf8"))
		
		response = s.makefile("r", encoding="utf8", newline="\r\n")
		statusline = response.readline()
		version, status, explanation = statusline.split(" ", 2)
		response_headers = {}
		while True:
			line = response.readline()
			if line == "\r\n": break
			header, value = line.split(":", 1)
			# strip空白文字除去・casefold全て小文字に
			response_headers[header.casefold()] = value.strip()
		assert "transfer-encoding" not in response_headers
		assert "content-encoding" not in response_headers
		content = response.read()
		s.close()
		return content

	def show(self, body):
		in_tag = False
		for c in body:
			if c == "<":
				in_tag = True
			elif c == ">":
				in_tag = False
			elif not in_tag:
				print(c, end="")
	
	def load(self):
		body = self.request()
		self.show(body)

if __name__ == "__main__":
	import sys
	URL(sys.argv[1]).load()

#url = URL("http://example.org")
#content = url.request()
#print(content)