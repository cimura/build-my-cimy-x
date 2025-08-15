# 実行ファイルの1つ上の階層を追加
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

WIDTH, HEIGHT = 800,600
HSTEP, VSTEP = 13, 18
SCROLL_STEP = 100

import tkinter
from Downloading_Web_Pages.browser import URL

def lex(body):
	text = ""
	in_tag = False
	for c in body:
		if c == "<":
			in_tag = True
		elif c == ">":
			in_tag = False
		elif not in_tag:
			text += c
	return text

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
		# 画像を読み込む（GIFやPNGなど対応）
		self.img = tkinter.PhotoImage(file="picachuu.png")
		self.window.bind("<Down>", self.scrolldown)
		self.window.bind("<Up>", self.scrollup)

	def scrolldown(self, e):
		self.scroll += SCROLL_STEP
		self.draw()

	def scrollup(self, e):
		if self.scroll > SCROLL_STEP:
			self.scroll -= SCROLL_STEP
		self.draw()
	
	def draw(self):
		self.canvas.delete("all")
		self.canvas.create_image(0, 0, image=self.img, anchor="nw")
		for x, y, c in self.display_list:
			if y > self.scroll + HEIGHT: continue
			if y + VSTEP < self.scroll: continue
			self.canvas.create_text(x, y - self.scroll, text=c)
	def load(self, url):
		#self.canvas.create_rectangle(10, 20, 400, 300)
		#self.canvas.create_oval(100, 100, 150, 150)
		#self.canvas.create_text(200, 150, text="Hi!")
		body = url.request()
		cursor_x, cursor_y = HSTEP, VSTEP
		text = lex(body)
		self.display_list = layout(text)
		self.draw()
		for c in text:
			self.canvas.create_text(cursor_x, cursor_y, text=c)
			cursor_x += HSTEP
			if cursor_x >= WIDTH - HSTEP:
				cursor_y += VSTEP
				cursor_x = HSTEP

def layout(text):
	display_list = []
	cursor_x, cursor_y = HSTEP, VSTEP
	for c in text:
		display_list.append((cursor_x, cursor_y, c))
		cursor_x += HSTEP
		if cursor_x >= WIDTH - HSTEP:
			cursor_y += VSTEP
			cursor_x = HSTEP
	return display_list


if __name__ == "__main__":
	import sys
	Browser().load(URL(sys.argv[1]))
	tkinter.mainloop()