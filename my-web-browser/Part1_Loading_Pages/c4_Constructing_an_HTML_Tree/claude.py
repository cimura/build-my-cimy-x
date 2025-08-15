# 実行ファイルの1つ上の階層を追加
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter
import tkinter.font
from c2_Downloading_Web_Pages.browser import URL

WIDTH, HEIGHT = 800,600
HSTEP, VSTEP = 13, 18
SCROLL_STEP = 100

"""
	it's for cache of fonts
"""
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

"""
	for debug
"""

def print_tree(node, indent=0):
	print(" " * indent, node)
	for child in node.children:
		print_tree(child, indent + 2)

class HTMLParser:
	def __init__(self, body):
		self.body = body
		self.unfinished = []
		self.SELF_CLOSING_TAGS = [
			"area", "base", "br", "col", "embed", "hr", "img", "input",
			"link", "meta", "source", "track", "wbr"
		]
	
	def get_attributes(self, text):
		parts = text.split()
		tag = parts[0].casefold()
		attributes = {}
		for attrpair in parts[1:]:
			if "=" in attrpair:
				key, value = attrpair.split("=", 1)
				attributes[key.casefold()] = value
				if len(value) > 2 and value[0] in ["'", "\""]:
					value = value[1:-1] #ハジを除去
			else:
				attributes[attrpair.casefold()] = ""
		return tag, attributes
	
	def parse(self):
		text = ""
		in_tag = False
		for c in self.body:
			if c == "<":
				in_tag = True
				if text: self.add_text(text)
				text = ""
			elif c == ">":
				in_tag = False
				self.add_tag(text)  # Fixed: was add_text, should be add_tag
				text = ""
			else:
				text += c
		if not in_tag and text:
			self.add_text(text)
		return self.finish()
	
	def add_text(self, text):
		if text.isspace(): return
		# Handle case when there's no parent yet
		if not self.unfinished: return
		parent = self.unfinished[-1]
		node = Text(text, parent)
		parent.children.append(node)

	def add_tag(self, tag):
		tag, attributes = self.get_attributes(tag)
		if tag.startswith("!"): return
		if tag.startswith("/"):
			if len(self.unfinished) == 1: return
			node = self.unfinished.pop()
			parent = self.unfinished[-1]
			parent.children.append(node)
		elif tag in self.SELF_CLOSING_TAGS:
			parent = self.unfinished[-1]
			node = Element(tag, attributes, parent)  # Fixed: added attributes
			parent.children.append(node)
		else:
			parent = self.unfinished[-1] if self.unfinished else None
			node = Element(tag, attributes, parent)  # Fixed: added attributes
			self.unfinished.append(node)
	
	def finish(self):
		while len(self.unfinished) > 1:
			node = self.unfinished.pop()
			parent = self.unfinished[-1]
			parent.children.append(node)
		return self.unfinished.pop() if self.unfinished else None

class Text:
	def __init__(self, text, parent):
		self.text = text
		self.children = []
		self.parent = parent
	
	def __repr__(self):
		return repr(self.text)

class Element:
	def __init__(self, tag, attributes, parent):
		self.tag = tag
		self.attributes = attributes
		self.children = []
		self.parent = parent

	def __repr__(self):
		return "<" + self.tag + ">"

class Layout:
	def __init__(self, tree):
		self.display_list = []
		self.cursor_x = HSTEP
		self.cursor_y = VSTEP
		self.weight = "normal"
		self.style = "roman"
		self.size = 12
		self.line = []
		
		self.recurse(tree)
		self.flush()
	
	def open_tag(self, tag):
		if tag == "i":
			self.style = "italic"
		elif tag == "b":
			self.weight = "bold"
		elif tag == "small":
			self.size -= 2
		elif tag == "big":
			self.size += 4
		elif tag == "br":
			self.flush()
		elif tag == "p":
			self.flush()
			self.cursor_y += VSTEP

	def close_tag(self, tag):
		if tag == "i":
			self.style = "roman"
		elif tag == "b":
			self.weight = "normal"
		elif tag == "small":
			self.size += 2
		elif tag == "big":
			self.size -= 4
		elif tag == "p":
			self.flush()
			self.cursor_y += VSTEP

	def recurse(self, tree):
		if tree is None:
			return
		if isinstance(tree, Text):
			for word in tree.text.split():
				self.word(word)
		else:
			self.open_tag(tree.tag)
			for child in tree.children:
				self.recurse(child)
			self.close_tag(tree.tag)

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
			if y + font.metrics("linespace") < self.scroll: continue
			self.canvas.create_text(x, y - self.scroll, text=word, font=font, anchor="nw")
	
	def load(self, url):
		body = url.request()
		self.nodes = HTMLParser(body).parse()
		self.display_list = Layout(self.nodes).display_list
		self.draw()

if __name__ == "__main__":
	import sys
	Browser().load(URL(sys.argv[1]))
	tkinter.mainloop()