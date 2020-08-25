# Post-Processing

import DepMan

DepMan.install_and_import("numpy")
DepMan.install_and_import("PIL", pip_name = "Pillow")
from PIL import Image

import Auto_Snap as snap

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

		global_transforms = [[0, 0]]

		running_bbox = [[0, 0], [0, 0]] # Top Left and Bottom Right corners

		images = [Image.open(self.filenames[0]), Image.open(self.filenames[0])]

		for fname, transform in zip(self.filenames, self.transforms):

			# Shift standing image registry
			images[0].close()
			images[0] = images[1]

			# Get original height and width information
			print("	Loading %s"%fname);
			images[1] = Image.open(fname)
			new_width = images[1].width
			new_height = images[1].height




			# Convert from transformation ratios (some fraction of the width) into absolute pixel values
			# NOTE: These are pixel values relative to the previous image

			print("	Given Ratio Transform: ", transform)

			transform = snap.optimize_transform(images[0], images[1], transform)
			print("	Optimized Ratio Transform: ", transform)


			relative_x = transform[0]*new_width
			relative_y = transform[1]*new_height
			print("	Optimized Relative Transform: ", [relative_x, relative_y])
			# img.close()

			# Convert from sequential relative transforms to global transform (assuming the first image has a transform (0, 0))
			global_transform_x = global_transforms[-1][0] + relative_x
			global_transform_y = global_transforms[-1][1] + relative_y

			# Add our new global transforms to our running list of global transforms
			global_transforms.append([global_transform_x, global_transform_y])

			# For compatability, we assume the 'global' transform applies to the top left corner of the image
			# So, we need to calculate the extent of our total 'canvas', which requires knowing where the bottom right corner of the image lands
			br_x = global_transform_x + new_width
			br_y = global_transform_y + new_height


			# Update the extent of our canvas (bbox -> bounding box)
			running_bbox[0][0] = min(running_bbox[0][0], global_transform_x)
			running_bbox[0][1] = min(running_bbox[0][1], global_transform_y)
			running_bbox[1][0] = max(running_bbox[1][0], br_x)
			running_bbox[1][1] = max(running_bbox[1][1], br_y)

		print("Done Loading")

		# Our canvas needs to end up with only positive coordinates; so, we calculate how far we 'overran' into negative coordinates
		left_overrun = -1*min(0, running_bbox[0][0])
		top_overrun = -1*min(0, running_bbox[0][1])

		# We use these overrun values to compute the total size of the canvas
		final_width = round(running_bbox[1][0] + left_overrun)
		final_height = round(running_bbox[1][1] + top_overrun)

		# Creating a blank canvas which is white and has opacity 0
		dst = Image.new('RGBA', (final_width, final_height), (0, 0, 0, 0));

		print("Pasting")
		for fname, g_transform in zip(self.filenames, global_transforms[1:]):
			img = Image.open(fname)
			# When we paste the image, use this opacity for blending (255 to fully overwrite)
			img.putalpha(128)
			print("	Pasting Image ", fname)
			print("	Transform: ", g_transform)

			# For the particular global transform of this image, plus our global offset to guarantee positive coordinates, place the image onto our canvas
			dst.paste(img, (round(g_transform[0] + left_overrun), round(g_transform[1] + top_overrun)), img)

		# In some blending cases, the resulting alpha channel is not fully opaque. This line sets the alpha channel to opaque.
		# If a partially transparent output image is desired, remove this line
		dst.putalpha(255)
		dst = dst.save(target_filename)
