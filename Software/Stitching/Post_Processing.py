"""
Copyright 2020 Zachary J. Allen

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
"""

# Post-Processing

import DepMan

DepMan.install_and_import("numpy")
DepMan.install_and_import("PIL", pip_name = "Pillow")
DepMan.install_and_import("multiprocessing")
from PIL import Image
import numpy as np
import multiprocessing

import Auto_Snap as snap

class Stack(object):
	"""docstring for Stack"""
	def __init__(self):
		super(Stack, self).__init__()
		self.filenames = [];
		self.transforms = []
		self.alpha_mask = None;
		self.output_dims = None;
		self.global_transforms = None;

	def register_root(self, filename):
		self.filenames.append(filename);
		self.transforms.append([0, 0]) # placeholder

	def register(self, filename, transform):
		# print("Registering transform ", transform)
		self.filenames.append(filename)
		self.transforms.append(transform)
		# print("Transforms: ", self.transforms)

	def align(self):
		""" From files on the stack, calculate alignments and an alpha mask for dust """
		# We need a single image to use as a size reference
		ref_img = Image.open(self.filenames[0])



		# This will get used while calculating an alpha mask for dust
		error_array_size = [len(self.filenames)-1, ref_img.width, ref_img.height]
		

		# We're done with the reference image
		ref_img.close()


		error_arrays = transform_error_masks(error_array_size, pipeline='OCCA')


		# Calculate an alpha_mask


		avg_error = np.mean(error_arrays)
		max_error = np.max(error_arrays)
		min_error = np.min(error_arrays)
		# print("Min Error: ", min_error)
		# print("Avg Error: ", avg_error)
		# print("Max Error: ", max_error)
		# print("TL  Error: ", error_arrays[:, 0, 0])
		# print("Mid Error: ", error_arrays[:, 2000, 2000])

		# error_arrays = np.subtract(error_arrays, 10)
		# error_arrays = np.multiply(error_arrays, -1)
		# error_arrays = np.divide(error_arrays, 100)
		# error_arrays = np.add(error_arrays, 1)
		error_arrays = np.subtract(error_arrays, np.min(error_arrays))
		error_arrays = np.subtract(error_arrays, 20)
		error_arrays = np.divide(error_arrays, np.max(error_arrays))
		error_arrays = np.add(np.multiply(error_arrays, -2), 1) # Intentionally max out some of the alpha range

		# print("EA Min: ", np.min(error_arrays))
		# print("EA Max: ", np.max(error_arrays))
		print("EA Full Shape: ", error_arrays.shape)
	

		######################################################################################################################################################
		# Issue: In high-error areas, some kind of grain comes in when only reporting the 'max' opacity suggested
		# Test: If we sort the errors and weight them, can we get a smoother result?

		# error_arrays = np.sort(error_arrays) # sort along the Stack, so that for each pixel position, the suggested opacities are sorted low to high

		# I want some list of numbers which sum to one, which start at larger and end at smaller fractions of one, and there are as many numbers as images (N)
		# Opt. 1: 2/N+1, then [1/N+1] * (N-1)

		# error_arrays = (np.mean(error_arrays, 0) + np.max(error_arrays, 0))/2
		error_arrays = np.mean(error_arrays, 0)




		error_arrays = np.maximum(error_arrays, 0)
		error_arrays = np.minimum(error_arrays, 1)
		print("EA Shape: ", error_arrays.shape)
		self.alpha_mask = error_arrays

	def transforms_error_masks(self, error_size, pipeline = 'multiprocessing', argpack = []):
		if pipeline == 'multiprocessing':
			return _TEM_multiprocessing(error_size, argpack);
		else if pipeline == 'OCCA_array_ops':
			return _TEM_OCCA_array_ops(error_size, argpack)



	def _TEM_multiprocessing(self, error_size, argpack):
		""" Use python's multiprocessing approach to speed up fitting. CPU-core parallelism """
		p = multiprocessing.Pool();
		error_arrays = np.ones(error_size)

		tasks_list = []

		for x, tf in zip(range(len(self.filenames)-1), self.transforms[1:]):
			tasks_list.append([self.filenames[x], self.filenames[x+1], tf])

		# Reminder: snap --> Auto_Snap.py
		response_packets = p.map(snap.optimize_worker, tasks_list)

		for x, (new_transform, emask_array) in enumerate(response_packets):

			self.transforms[x+1] = new_transform
			error_arrays[x] = emask_array

		p.close()

		return error_arrays

	def _TEM_OCCA_array_ops(self, error_size, argpack):
		""" Use the OCCA interface to run internal array modifications in the fitting process. GPU parallelism """
		error_arrays = np.ones(error_size)

		tasks_list = []

		for x, tf in zip(range(len(self.filenames)-1), self.transforms[1:]):

			new_transform, emask_array = snap.run_optimize(self.filenames[x], self.filenames[x+1], tf, pipeline = 'OCCA', argpack = argpack)

			self.transforms[x+1] = new_transform
			error_arrays[x] = emask_array


		return error_arrays


	def construct_global_alignments(self):

		self.global_transforms = [[0, 0]]
		running_bbox = [[0, 0], [0, 0]]


		for fname, transform in zip(self.filenames, self.transforms):
			image = Image.open(fname)
			# new_width = alignment.images[1].width
			# new_height = alignment.images[1].height

			# transform = alignment.fractional_transform
			new_width = image.width
			new_height = image.height
			image.close()




			# 	# Convert from transformation ratios (some fraction of the width) into absolute pixel values
			# 	# NOTE: These are pixel values relative to the previous image

			# print("	Given Ratio Transform: ", transform)

			# 	transform = snap.optimize_transform(images[0], images[1], transform)
			# print("	Optimized Ratio Transform: ", transform)


			relative_x = transform[0]*new_width
			relative_y = transform[1]*new_height
			# print("	Optimized Relative Transform: ", [relative_x, relative_y])
			

			# alignment.close() # We could keep alignment alive, but I'd rather free memory

			# 	# Convert from sequential relative transforms to global transform (assuming the first image has a transform (0, 0))
			global_transform_x = self.global_transforms[-1][0] + relative_x
			global_transform_y = self.global_transforms[-1][1] + relative_y

			# 	# Add our new global transforms to our running list of global transforms
			self.global_transforms.append([global_transform_x, global_transform_y])

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
		self.output_dims = [(final_width, final_height), (left_overrun, top_overrun)]

	def output(self, target_filename, return_when_done = False):
		# Creating a blank canvas which is white and has opacity 0

		if self.alpha_mask is None:
			self.align()
		if self.output_dims is None:
			self.construct_global_alignments()

		dst = Image.new('RGBA', self.output_dims[0], (0, 100, 0, 0));

		print("Pasting")



		alpha_img = Image.fromarray(np.multiply(self.alpha_mask, 255).astype(np.uint8).transpose()).convert('L')
		# alpha_img.show()

		# print("Len Images: ", len(images))
		# print("Len GTransforms: ", len(global_transforms))
		# print("Len Alignments: ", len(alignments))
		# print(self.global_transforms)
		# print(self.filenames)

		for fname, g_transform in zip(self.filenames, self.global_transforms[1:]):
			# When we paste the image, use this opacity for blending (255 to fully overwrite)
			img = Image.open(fname)
			# img.putalpha(128)
			img.putalpha(alpha_img.resize(img.size))
			# img.show()

			print("	Pasting Image ", fname)
			print("	Transform: ", g_transform)
			# print((int(round(g_transform[0] + left_overrun)), int(round(g_transform[1] + top_overrun))))
			# For the particular global transform of this image, plus our global offset to guarantee positive coordinates, place the image onto our canvas

			dst.alpha_composite(img, (int(round(g_transform[0] + self.output_dims[1][0])), int(round(g_transform[1] + self.output_dims[1][1]))))
			img.close()
		# In some blending cases, the resulting alpha channel is not fully opaque. This line sets the alpha channel to opaque.
		# If a partially transparent output image is desired, remove this line
		# dst.putalpha(255)
		try:
			dst.save(target_filename)
		except PermissionError:
			print("[Error] Unable to save file to disk with that name. Try another one?")

		if return_when_done:
			return dst



