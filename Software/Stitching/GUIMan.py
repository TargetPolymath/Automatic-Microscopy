# GUI Management

from tkinter import * # Dependency managed through wrapped shell

import DepMan

DepMan.install_and_import("PIL", pip_name = "Pillow")

from PIL import Image, ImageOps, ImageTk

DOWNSIZE_RATIO = 0.2


class GUI_Window(object):
	"""A single instance of an editing window"""
	def __init__(self, width = 3000*DOWNSIZE_RATIO, height = 3000*DOWNSIZE_RATIO, start_offset_ratio = [0, 0], downsize_ratio = DOWNSIZE_RATIO):
		super(GUI_Window, self).__init__()
		self.width = width
		self.height = height
		self.root = Tk()
		self.canvas = Canvas(self.root, width = self.width, height = self.height)
		# self.canvas.pack(expand=1, fill=BOTH);
		self.canvas.pack()

		self.img_array = [None, None]
		self.A_img = None;
		self.B_img = None;

		self.downsize_ratio = downsize_ratio

		self.start_offset_ratio = start_offset_ratio;
		self.offset_vector = [0, 0];
		print("Starting Offset Vector: ", self.offset_vector)
		self.rotation = 0;

		self.mouse_clickdown_pos = [0, 0]
		self.last_mouse_pos = [0, 0]
		self.mouse_down = False

		self.root.bind('<B1-Motion>', self.B1_movement)
		self.root.bind('<Button-1>', self.clickdown)
		self.root.bind('<ButtonRelease-1>', self.clickup)
		self.root.bind('<Return>', self.shutdown)

		self.root.bind('<Up>', self.up_arrow)
		self.root.bind('<Down>', self.down_arrow)
		self.root.bind('<Left>', self.left_arrow)
		self.root.bind('<Right>', self.right_arrow)

		# self.root.mainloop()

	def kickoff(self):
		# self.img_array[0].show()
		self.root.mainloop()

	def shutdown(self, event):
		self.root.destroy()

	def load_AB_img(self, A_filepath, B_filepath):
		print("Loading Images...")
		self.img_array[0] = load_and_resize(A_filepath, self.downsize_ratio); # [Tkinter image, PIL image]
		self.img_array[1] = load_and_resize(B_filepath, self.downsize_ratio, alpha = 150);

		self.offset_vector[0] = self.start_offset_ratio[0]*self.img_array[1][1].width
		self.offset_vector[1] = self.start_offset_ratio[1]*self.img_array[1][1].height
		print("New Offset Vector: ", self.offset_vector)

		self.A_img = self.canvas.create_image(0, 0, image=self.img_array[0][0], anchor = "nw");
		self.B_img = self.canvas.create_image(self.offset_vector[0], self.offset_vector[1], image=self.img_array[1][0], anchor = "nw");



	def B1_movement(self, event):
		off_x = event.x - self.last_mouse_pos[0]
		off_y = event.y - self.last_mouse_pos[1]

		self.last_mouse_pos = [event.x, event.y]
		self.canvas.move(self.B_img, off_x, off_y)

		# Does not call update_B_pos because the mouse status is persistant; offset_vector is updated in clickup
		# print(self.B_img)

	def update_B_pos(self, off_x, off_y):
		self.offset_vector[0] += off_x
		self.offset_vector[1] += off_y

		self.canvas.move(self.B_img, off_x, off_y)
		# print(str(self.offset_vector[0] + off_x) + ", " + str(self.offset_vector[1] + off_y))

	def clickdown(self, event):
		self.mouse_clickdown_pos = [event.x, event.y]
		self.last_mouse_pos = [event.x, event.y]
		self.mouse_down = True

	def clickup(self, event):
		self.mouse_down = False
		off_x = event.x - self.mouse_clickdown_pos[0]
		off_y = event.y - self.mouse_clickdown_pos[1]
		self.offset_vector[0] += off_x
		self.offset_vector[1] += off_y
		# self.update_B_pos(off_x, off_y);


	def down_arrow(self, event):
		self.update_B_pos(0, 1);
	def up_arrow(self, event):
		self.update_B_pos(0, -1);

	def right_arrow(self, event):
		self.update_B_pos(1, 0);
	def left_arrow(self, event):
		self.update_B_pos(-1, 0);


	def collect_transform(self):
		print("Collecting Transform...")
		output = [self.offset_vector[0] / self.img_array[1][0].width(), self.offset_vector[1] / self.img_array[1][0].height()]
		print(output)
		return output


		
def load_and_resize(filepath, downsize_ratio = DOWNSIZE_RATIO, alpha = 255):
	temp = Image.open(filepath);
	temp.putalpha(alpha);

	in_width, in_height = temp.size

	resize_target = (round(in_width * downsize_ratio), round(in_height * downsize_ratio))
	temp = temp.resize(resize_target)

	img2 = ImageTk.PhotoImage(temp)
	# Need some kind of reactive overlay mechanic for easier alignment

	return img2, temp

	################

	# img = Image.open(filepath)
	# # img.show()

	# return ImageTk.PhotoImage(img)
