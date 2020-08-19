# Post-Processing

import DepMan

DepMan.install_and_import("numpy")
DepMan.install_and_import("PIL", pip_name = "Pillow")
from PIL import Image

class Stack(object):
	"""docstring for Stack"""
	def __init__(self):
		super(Stack, self).__init__()
		self.filenames = [];
		self.transforms = []

	def register_root(self, filename):
		self.filenames.append(filename);
		self.transforms.append([0, 0]) # placeholder

	def register(self, filename, transform):
		print("Registering transform ", transform)
		self.filenames.append(filename)
		self.transforms.append(transform)
		print("Transforms: ", self.transforms)

	def output(self, target_filename):

		print("Starting Output")

		px_transforms = [[0, 0]]

		running_bbox = [[0, 0], [0, 0]] # Top Left and Bottom Right corners

		images = []

		for fname, transform in zip(self.filenames, self.transforms):
			print("	Loading %s"%fname);
			img = Image.open(fname)
			new_width = img.width
			new_height = img.height

			img.close()
			print("	Ratio Transform: ", transform)
			relative_x = transform[0]*new_width
			relative_y = transform[1]*new_height
			print("	Relative_Transform: ", [relative_x, relative_y])

			tl_x = px_transforms[-1][0] + relative_x
			tl_y = px_transforms[-1][1] + relative_y

			br_x = tl_x + new_width
			br_y = tl_y + new_height

			px_transforms.append([tl_x, tl_y])

			running_bbox[0][0] = min(running_bbox[0][0], tl_x)
			running_bbox[0][1] = min(running_bbox[0][1], tl_y)
			running_bbox[1][0] = max(running_bbox[1][0], br_x)
			running_bbox[1][1] = max(running_bbox[1][1], br_y)

		print("Done Loading")
		left_overrun = -1*min(0, running_bbox[0][0])
		top_overrun = -1*min(0, running_bbox[0][1])

		final_width = round(running_bbox[1][0] + left_overrun)
		final_height = round(running_bbox[1][1] + top_overrun)


		dst = Image.new('RGBA', (final_width, final_height), (255, 255, 255, 0));

		print("Pasting")
		for fname, transform in zip(self.filenames, px_transforms[1:]):
			img = Image.open(fname)
			img.putalpha(255)
			print("	Pasting Image ", fname)
			print("	Transform: ", transform)



			dst.paste(img, (round(transform[0] + left_overrun), round(transform[1] + top_overrun)), img)

		dst = dst.save(target_filename)


