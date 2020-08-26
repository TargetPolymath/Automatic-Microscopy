# Post-Processing

import DepMan

DepMan.install_and_import("numpy")
DepMan.install_and_import("PIL", pip_name = "Pillow")
from PIL import Image
import numpy as np

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

		

		

		# YES it's RAM intensive
		# I didn't buy a 36G RAM server by accident
		images = [Image.open(fname) for fname in self.filenames]

		# alignments = [snap.Alignment(images[0], images[0], [0, 0])]
		alignments = []
		for x, tf in zip(range(len(self.filenames)-1), self.transforms[1:]):
			print("Creating Alignment for: ", self.filenames[x], self.filenames[x+1])
			alignments.append(snap.Alignment(images[x], images[x+1], tf))

		# exit()


		alpha_mask = np.ones(images[0].size)
		# print(error_arrays.shape)
		# print(alpha_mask.shape)
		# exit()
		error_arrays = np.ones([len(alignments), images[0].width, images[0].height])
		# while True: # ending when all the Alignments are returning [0, zeros_like]
		for iteration in range(20):	
			
			done = True;
			for i, alignment in enumerate(alignments):
				more, error_mask = alignment.perform_optimization_step(alpha_mask)
				if more:
					done = False
					# somehow update the alpha mask
					# error_mask.show()

					emask_array = np.asarray(error_mask).transpose() # Switching back to WxH
					print("		EMask Mean: ", np.mean(emask_array))
					print("		EMask Shape: ", emask_array.shape)
					print("		Error Array: ", error_arrays.shape)
					error_arrays[i] = emask_array
			if done:
				break
			# Otherwise...
			########
			# Calculate new alpha_mask

			avg_error = np.mean(error_arrays)
			max_error = np.max(error_arrays)
			min_error = np.min(error_arrays)
			print("Min Error: ", min_error)
			print("Avg Error: ", avg_error)
			print("Max Error: ", max_error)
			print("TL  Error: ", error_arrays[:, 0, 0])
			print("Mid Error: ", error_arrays[:, 2000, 2000])

			temp_error_arrays = error_arrays.copy()
			# temp_error_arrays = np.subtract(temp_error_arrays, 10)
			# temp_error_arrays = np.multiply(temp_error_arrays, -1)
			# temp_error_arrays = np.divide(temp_error_arrays, 100)
			# temp_error_arrays = np.add(temp_error_arrays, 1)
			temp_error_arrays = np.subtract(temp_error_arrays, np.min(temp_error_arrays))
			temp_error_arrays = np.subtract(temp_error_arrays, 10)
			temp_error_arrays = np.divide(temp_error_arrays, np.max(temp_error_arrays))
			temp_error_arrays = np.add(np.multiply(temp_error_arrays, -1), 1)

			# print("EA Min: ", np.min(temp_error_arrays))
			# print("EA Max: ", np.max(temp_error_arrays))
			print("EA Full Shape: ", temp_error_arrays.shape)
			temp_error_arrays = np.max(temp_error_arrays, 0)
			temp_error_arrays = np.maximum(temp_error_arrays, 0)
			temp_error_arrays = np.minimum(temp_error_arrays, 1)
			print("EA Shape: ", temp_error_arrays.shape)
			alpha_mask = temp_error_arrays
			# Image.fromarray(np.multiply(alpha_mask,255).astype(np.uint8).transpose()).show()











		global_transforms = [[0, 0]]
		running_bbox = [[0, 0], [images[0].width, images[0].height]] # Top Left and Bottom Right corners
		# images = [Image.open(self.filenames[0]), Image.open(self.filenames[0])]

		# for fname, transform in zip(self.filenames, self.transforms):
		for alignment in alignments:
			new_width = alignment.img2.width
			new_height = alignment.img2.height

			transform = alignment.fractional_transform




			# 	# Convert from transformation ratios (some fraction of the width) into absolute pixel values
			# 	# NOTE: These are pixel values relative to the previous image

			# 	print("	Given Ratio Transform: ", transform)

			# 	transform = snap.optimize_transform(images[0], images[1], transform)
			print("	Optimized Ratio Transform: ", transform)


			relative_x = transform[0]*new_width
			relative_y = transform[1]*new_height
			print("	Optimized Relative Transform: ", [relative_x, relative_y])
			

			# alignment.close() # We could keep alignment alive, but I'd rather free memory

			# 	# Convert from sequential relative transforms to global transform (assuming the first image has a transform (0, 0))
			global_transform_x = global_transforms[-1][0] + relative_x
			global_transform_y = global_transforms[-1][1] + relative_y

			# 	# Add our new global transforms to our running list of global transforms
			global_transforms.append([global_transform_x, global_transform_y])

			# 	# For compatability, we assume the 'global' transform applies to the top left corner of the image
			# 	# So, we need to calculate the extent of our total 'canvas', which requires knowing where the bottom right corner of the image lands
			br_x = global_transform_x + new_width
			br_y = global_transform_y + new_height


			# 	# Update the extent of our canvas (bbox -> bounding box)
			running_bbox[0][0] = min(running_bbox[0][0], global_transform_x)
			running_bbox[0][1] = min(running_bbox[0][1], global_transform_y)
			running_bbox[1][0] = max(running_bbox[1][0], br_x)
			running_bbox[1][1] = max(running_bbox[1][1], br_y)

		print("Done Loading")

		# Our canvas needs to end up with only positive coordinates; so, we calculate how far we 'overran' into negative coordinates
		left_overrun = -1*min(0, running_bbox[0][0])
		top_overrun = -1*min(0, running_bbox[0][1])

		# We use these overrun values to compute the total size of the canvas
		final_width = int(round(running_bbox[1][0] + left_overrun))
		final_height = int(round(running_bbox[1][1] + top_overrun))
		print("Final Width:  ", final_width)
		print("Final Height: ", final_height)

		# Creating a blank canvas which is white and has opacity 0
		dst = Image.new('RGBA', (final_width, final_height), (0, 100, 0, 0));

		print("Pasting")



		alpha_img = Image.fromarray(np.multiply(alpha_mask, 255).astype(np.uint8).transpose()).convert('L')
		# alpha_img.show()

		print("Len Images: ", len(images))
		print("Len GTransforms: ", len(global_transforms))
		print("Len Alignments: ", len(alignments))
		for img, g_transform in zip(images, global_transforms):
			# When we paste the image, use this opacity for blending (255 to fully overwrite)
			# img.putalpha(128)
			img.putalpha(alpha_img.resize(img.size))
			# img.show()

			# print("	Pasting Image ", fname)
			print("	Transform: ", g_transform)

			# For the particular global transform of this image, plus our global offset to guarantee positive coordinates, place the image onto our canvas

			dst.alpha_composite(img, (int(round(g_transform[0] + left_overrun)), int(round(g_transform[1] + top_overrun))))
			img.close()
		# In some blending cases, the resulting alpha channel is not fully opaque. This line sets the alpha channel to opaque.
		# If a partially transparent output image is desired, remove this line
		# dst.putalpha(255)
		dst = dst.save(target_filename)



