import tkinter.font
WIDTH, HEIGHT = 200, 200

window = tkinter.Tk()
canvas = tkinter.Canvas(
	window,
	width=WIDTH,
	height=HEIGHT,
)
bi_times = tkinter.font.Font(
    family="Times",
    size=16,
    weight="bold",
    slant="italic",
)

print(bi_times.measure("Hi!"))
print(bi_times.measure("H"))
print(bi_times.measure("Hi"))
#canvas.create_text(50, 50, text="Hi!", font=bi_times)
#canvas.pack()
#tkinter.mainloop()