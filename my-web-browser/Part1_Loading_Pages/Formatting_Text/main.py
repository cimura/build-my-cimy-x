# 実行ファイルの1つ上の階層を追加
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter
import tkinter.font
from Downloading_Web_Pages.browser import URL

WIDTH, HEIGHT = 800,600
HSTEP, VSTEP = 13, 18
SCROLL_STEP = 100

FONTS = {}

def get_font(size, weight, style):
	key = (size, weight, style)
	if key not in FONTS:
		font = tkinter.font.Font(
			size=size,
			weight=weight,
			slant=style
		)
		label = tkinter.Label(font=font)
		FONTS[key] = (font, label)
	return FONTS[key][0]

class Text:
	def __init__(self, text):
		self.text = text

class Tag:
	def __init__(self, tag):
		self.tag = tag

class Layout:
	def __init__(self, tokens):
		self.display_list = []
		self.cursor_x = HSTEP
		self.cursor_y = VSTEP
		self.weight = "normal"
		self.style = "roman"
		self.size = 12
		self.line = []
		
		for tok in tokens:
			self.token(tok)
		self.flush()
	
	def token(self, tok):
		if isinstance(tok, Text):
			for word in tok.text.split():
				self.word(word)
		elif isinstance(tok, Tag):
			if tok.tag == "i":
				self.style = "italic"
			elif tok.tag == "/i":
				self.style = "roman"
			elif tok.tag == "b":
				self.weight = "bold"
			elif tok.tag == "/b":
				self.weight = "normal"
			elif tok.tag == "small":
				self.size -= 2
			elif tok.tag == "/small":
				self.size += 2
			elif tok.tag == "big":
				self.size += 4
			elif tok.tag == "/big":
				self.size -= 4
			elif tok.tag == "br":
				self.flush()
			elif tok.tag == "/p":
				self.flush()
				self.cursor_y += VSTEP

	def word(self, word):
		font = get_font(self.size, self.weight, self.style)
		w = font.measure(word)
		 # 行がはみ出す場合は先にflushする
		if self.cursor_x + w > WIDTH - HSTEP:
			self.flush()
		self.line.append((self.cursor_x, word, font))
		# 単語を現在の行に追加
		self.cursor_x += w + font.measure(" ")

	def flush(self):
		if not self.line: return
		metrics = [font.metrics() for x, word, font in self.line]
		max_ascent = max([metric["ascent"] for metric in metrics])
		base_line = self.cursor_y + 1.25 * max_ascent
		for x, word, font in self.line:
			y = base_line - font.metrics("ascent")
			self.display_list.append((x, y, word, font))
		max_descent = max([metric["descent"] for metric in metrics])
		self.cursor_y = base_line + 1.25 * max_descent
		self.cursor_x = HSTEP
		self.line = []


def lex(body):
	out = []
	buffer = ""
	in_tag = False
	for c in body:
		if c == "<":
			in_tag = True
			if buffer: out.append(Text(buffer))
			buffer = ""
		elif c == ">":
			in_tag = False
			if buffer: out.append(Tag(buffer))
			buffer = ""
		else:
			buffer += c
	if not in_tag and buffer:
		out.append(Text(buffer))
	return out

class Browser:
	def __init__(self):
		self.scroll = 0
		self.window = tkinter.Tk()
		self.canvas = tkinter.Canvas(
			self.window,
			width=WIDTH,
			height=HEIGHT,
		)
		self.canvas.pack()
		self.window.bind("<Down>", self.scrolldown)
		self.window.bind("<Up>", self.scrollup)

	def scrolldown(self, e):
		self.scroll += SCROLL_STEP
		self.draw()

	def scrollup(self, e):
		if self.scroll > SCROLL_STEP:
			self.scroll -= SCROLL_STEP
		else:
			self.scroll = 0
		self.draw()
	
	def draw(self):
		self.canvas.delete("all")
		for x, y, word, font in self.display_list:
			if y > self.scroll + HEIGHT: continue
			if y + VSTEP < self.scroll: continue
			self.canvas.create_text(x, y - self.scroll, text=word, font=font)
	def load(self, url):
		body = url.request()
		tokens = lex(body)
		self.display_list = Layout(tokens).display_list
		self.draw()

if __name__ == "__main__":
	import sys
	Browser().load(URL(sys.argv[1]))
	tkinter.mainloop()