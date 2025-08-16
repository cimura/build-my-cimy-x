# 実行ファイルの1つ上の階層を追加
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import tkinter
import tkinter.font
from Part1_Loading_Pages.c2_Downloading_Web_Pages.browser import URL

WIDTH, HEIGHT = 800,600
HSTEP, VSTEP = 13, 18
SCROLL_STEP = 100

BLOCK_ELEMENTS = [
    "html", "body", "article", "section", "nav", "aside",
    "h1", "h2", "h3", "h4", "h5", "h6", "hgroup", "header",
    "footer", "address", "p", "hr", "pre", "blockquote",
    "ol", "ul", "menu", "li", "dl", "dt", "dd", "figure",
    "figcaption", "main", "div", "table", "form", "fieldset",
    "legend", "details", "summary"
]

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
		self.HEAD_TAGS = [
			"base", "basefont", "bgsound", "noscript",
        	"link", "meta", "title", "style", "script",
		]
	
	def implicit_tags(self, tag):
		while True:
			open_tags = [node.tag for node in self.unfinished]
			if open_tags == [] and tag != "html":
				self.add_tag("html")
			elif open_tags == ["html"] \
				and tag not in ["head", "body", "/html"]:
				if tag in self.HEAD_TAGS:
					self.add_tag("head")
				else:
					self.add_tag("body")
			elif open_tags == ["html", "head"] \
				and tag not in ["/head"] + self.HEAD_TAGS:
				self.add_tag("/head")
			else:
				break
	
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
				self.add_tag(text)
				text = ""
			else:
				text += c
		if not in_tag and text:
			self.add_text(text)
		return self.finish()
	
	def add_text(self, text):
		if text.isspace(): return
		self.implicit_tags(None)
		# Handle case when there's no parent yet
		if not self.unfinished: return
		parent = self.unfinished[-1] if self.unfinished else None
		node = Text(text, parent)
		parent.children.append(node)

	def add_tag(self, tag):
		tag, attributes = self.get_attributes(tag)
		if tag.startswith("!"): return
		self.implicit_tags(tag)
		if tag.startswith("/"):
			if len(self.unfinished) == 1: return
			node = self.unfinished.pop()
			parent = self.unfinished[-1] if self.unfinished else None
			parent.children.append(node)
		elif tag in self.SELF_CLOSING_TAGS:
			parent = self.unfinished[-1]
			node = Element(tag, attributes, parent)
			parent.children.append(node)
		else:
			parent = self.unfinished[-1] if self.unfinished else None
			node = Element(tag, attributes, parent)
			self.unfinished.append(node)
	
	def finish(self):
		if not self.unfinished:
			self.implicit_tags(None)
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

class DrawText:
	def __init__(self, x1, y1, text, font):
		self.top = y1
		self.left = x1
		self.text = text
		self.font = font
		self.bottom = y1 + font.metrics("linespace")
	
	def execute(self, scroll, canvas):
		canvas.create_text(
			self.left, self.top - scroll,
			text=self.text,
			font=self.font,
			anchor="nw"
		)

class DrawRect:
	def __init__(self, x1, y1, x2, y2, color):
		self.top = y1
		self.left = x1
		self.bottom = y2
		self.right = x2
		self.color = color

	def execute(self, scroll, canvas):
		canvas.create_rectangle(
			self.left, self.top - scroll,
			self.right, self.bottom - scroll,
			width=0,
			fill=self.color
		)

# 修正版：paint_tree関数で子要素を再帰的に処理
def paint_tree(layout_object, display_list):
	display_list.extend(layout_object.paint())
	
	for child in layout_object.children:
		paint_tree(child, display_list)

class DocumentLayout:
	def __init__(self, node):
		self.node = node
		self.parent = None
		self.children = []
	
	def layout(self):
		child = BlockLayout(self.node, self, None)
		self.children.append(child)
		
		self.width = WIDTH - 2*HSTEP
		self.x = HSTEP
		self.y = VSTEP
		child.layout()
		self.height = child.height

	def paint(self):
		return []

class BlockLayout:
	def __init__(self, node, parent, previous):
		self.node = node
		self.parent = parent
		self.previous = previous
		self.children = []
		self.display_list = []
		self.cursor_x = 0
		self.cursor_y = 0
		self.weight = "normal"
		self.style = "roman"
		self.size = 12
		self.line = []
		self.x = None
		self.y = None
		self.width = None
		self.height = None

	def paint(self):
		cmds = []
		# preタグの背景色
		if isinstance(self.node, Element) and self.node.tag == "pre":
			x2, y2 = self.x + self.width, self.y + self.height
			rect = DrawRect(self.x, self.y, x2, y2, "gray")
			cmds.append(rect)
		
		# インラインモードの場合のみテキストを描画
		if self.layout_mode() == "inline":
			for x, y, word, font in self.display_list:
				cmds.append(DrawText(x, y, word, font))
		
		return cmds
	
	def layout_mode(self):
		if isinstance(self.node, Text):
			return "inline"
		elif any([isinstance(child, Element) and \
				child.tag in BLOCK_ELEMENTS
				for child in self.node.children]):
			return "block"
		elif self.node.children:
			return "inline"
		else:
			return "block"

	def layout(self):
		self.x = self.parent.x
		self.width = self.parent.width
		
		if self.previous:
			self.y = self.previous.y + self.previous.height
		else:
			self.y = self.parent.y

		mode = self.layout_mode()
		if mode == "block":
			previous = None
			for child in self.node.children:
				next = BlockLayout(child, self, previous)
				self.children.append(next)
				previous = next
		else:
			self.cursor_x = 0
			self.cursor_y = 0
			self.weight = "normal"
			self.style = "roman"
			self.size = 12
			self.line = []
			self.recurse(self.node)
			self.flush()

		# 子要素のレイアウトを実行
		for child in self.children:
			child.layout()

		if mode == "block":
			self.height = sum([child.height for child in self.children])
		else:
			self.height = self.cursor_y

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

	def recurse(self, tree):
		if tree is None: return
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
		if self.cursor_x + w > self.width:
			self.flush()
		self.line.append((self.cursor_x, word, font))
		self.cursor_x += w + font.measure(" ")

	def flush(self):
		if not self.line: return
		metrics = [font.metrics() for x, word, font in self.line]
		max_ascent = max([metric["ascent"] for metric in metrics])
		baseline = self.cursor_y + 1.25 * max_ascent
		for rel_x, word, font in self.line:
			x = self.x + rel_x
			y = self.y + baseline - font.metrics("ascent")
			self.display_list.append((x, y, word, font))
		self.cursor_x = 0
		self.line = []
		max_descent = max([metric["descent"] for metric in metrics])
		self.cursor_y = baseline + 1.25 * max_descent

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
		max_y = max(self.document.height + 2*VSTEP - HEIGHT, 0)
		self.scroll = min(self.scroll + SCROLL_STEP, max_y)
		self.draw()

	def scrollup(self, e):
		if self.scroll > SCROLL_STEP:
			self.scroll -= SCROLL_STEP
		else:
			self.scroll = 0
		self.draw()
	
	def draw(self):
		self.canvas.delete("all")
		for cmd in self.display_list:
			if cmd.top > self.scroll + HEIGHT: continue
			if cmd.bottom < self.scroll: continue
			cmd.execute(self.scroll, self.canvas)

	def load(self, url):
		body = url.request()
		self.nodes = HTMLParser(body).parse()
		self.document = DocumentLayout(self.nodes)
		self.document.layout()
		self.display_list = []
		paint_tree(self.document, self.display_list)
		self.draw()

if __name__ == "__main__":
	import sys
	Browser().load(URL(sys.argv[1]))
	tkinter.mainloop()