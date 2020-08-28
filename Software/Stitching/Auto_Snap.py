"""
Copyright 2020 Zachary J. Allen

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
"""

# Image Auto_snapping
import DepMan
# print("Managing Auto_Snap dependencies...");
DepMan.install_and_import("PIL", pip_name = "Pillow")
DepMan.install_and_import("numpy")
DepMan.install_and_import("math")
DepMan.install_and_import("random")
DepMan.install_and_import("multiprocessing")
DepMan.install_and_import("occa")
from PIL import Image, ImageMath
import numpy as np
import math
import random
import multiprocessing

import occa

min_scale = 4 # only go down to 2^5 pixels
max_scale = 10 # only go up to 2^12 pixels

class Alignment(object):
	"""docstring for Alignment"""
	def __init__(self, img1, img2, fractional_transform, name = None, pipeline = None, argpack = None):
		super(Alignment, self).__init__()
		self.images = [img1, img2]
		if name is None:
			self.name = "".join(random.choice("abcdef") for i in range(5))
		else:
			self.name = name
		self.original_transform = [x for x in fractional_transform] # copy
		self.fractional_transform = fractional_transform

		max_res = img2.width
		# input_transform = np.asarray(input_transform)

		# If we decide that the smallest image we'll expect to get useful info from is 128*128, how many times can we
		# 	divide the width by two and stay above a width of 128?

		scale_steps = math.floor(math.log2(max_res))

		self.scale = max(0, scale_steps - min_scale)
		self.wider_net = False
		self.ending_downscale   = max(0, scale_steps - max_scale) 
		self.prior_transforms = [];
		self.img_scale_cache = [{}, {}];

		if pipeline is None:
			self.pipeline = 'numpy'
			self.device = None
			self._error = self._error_numpy
		else:
			self.pipeline = 'OCCA'
			self.device = occa.Device(argpack)
			self._error = self._error_occa


	def _retrieve_img(self, image_id, scale = None):
		""" Image_id is on a range of 0 or 1; retrieve new or prior scaled version of image """

		if scale is None:
			scale = self.scale
		# print("[cache] grabbing image at scale ", scale)
		cache = self.img_scale_cache[image_id]
		# Not a memory duplicate, just a reference

		if scale in cache.keys():
			# print("[cache] Using cached image scale...")
			return cache[scale].copy()
		else:
			# print("[cache] generating fresh...")
			ratio = 1/(2**scale)
			target_im = self.images[image_id]

			img_new_width = round(target_im.width * ratio)
			img_new_height = round(target_im.height * ratio)

			img = target_im.resize((img_new_width, img_new_height))
			img = img.convert("RGBA") # Just making sure
			img = np.array(img).swapaxes(0, 1) # Pre-convert to array, and convert to WxHXC
			cache[scale] = img
			# print("[cache] Fresh complete")
			return img

	def optimize(self):
		counter = 0;
		while self.perform_optimization_step():
			print(f"\n[ITER] {counter} for {self.name}")
			counter += 1

		return self.fractional_transform, self.collect_error_print()



	def perform_optimization_step(self):
		if self.scale < self.ending_downscale:
			# print("\n"*5)
			# print("DONE!")
			return False
		# print("\n")
		# print(f"	Single Optimizer Step on {self.name} with scale {self.scale}")


		errors = np.zeros((3, 3))

		window_size = 2
		if self.wider_net:
			window_size = 3

		# print("		Window Size: ", window_size)

		for dx in [-1, 0, 1]: # post-scale pixel travel
			for dy in [-1, 0, 1]: # post-scale pixel travel
				# print("			dx=%d,dy=%d"%(dx, dy))
				errors[dx+1, dy+1], _ = self.error(px_transform = [dx*window_size, dy*window_size])
		# print("		Errors:\n", errors)

		step = np.subtract(np.unravel_index(np.argmin(errors, axis=None), errors.shape), 1)

		if np.all(step==0):
			if self.wider_net: # Before moving to the next scale, double our window size
				self.scale -= 1
				self.prior_transforms = [];
				self.wider_net = False
			else:
				self.wider_net = True
		else:
			scale_update = np.divide(np.divide(step, np.multiply(1/(2**self.scale), np.asarray(self.images[1].size))), window_size/2)
			new_fractional_transform = [self.fractional_transform[0] + scale_update[0], self.fractional_transform[1] + scale_update[1]]
			self.wider_net = False;
			if new_fractional_transform not in self.prior_transforms:
				self.prior_transforms.append(new_fractional_transform)
				# print("		Update Direction: ", step)
				# print("		Scale Update: ", scale_update)
				self.fractional_transform = [x for x in new_fractional_transform]
				print(f"[{self.name}]		New Transform: [%2.3f, %2.3f]"%(self.fractional_transform[0], self.fractional_transform[1]))
				print(f"[{self.name}]		Org Transform: [%2.3f, %2.3f]"%(self.original_transform[0], self.original_transform[1]))
			else:
				# print("		[Skip] Already evaluated transform")
				self.scale -= 1 # No update, we've already been where we're going; scale down and continue
				self.prior_transforms = [];


		return True


	def error(self, scale = None, px_transform = [0, 0]):
		# This will be the evaluator for the error between two images and their relative transform (transform as a fraction of img2 size)
		# Technically, both images are color arrays or color-alpha arrays (no alpha is presumed to be full opacity)
		# We take the product of the alpha channels as a scale of the R^2 error contribution

		# Direct transform is a pixel transformation added on top of the ratio transformation

		# Right now it's a terrible placeholder

		#####################################
		# print("			Starting Error...")
		if scale is None:
			scale = self.scale

		# Step 1: Retrieve Images
		array1 = self._retrieve_img(0, scale = scale)
		array2 = self._retrieve_img(1, scale = scale)
		# print("			array1 shape: ", array1.shape)


		# Step 2: Calculate the scale-transform in pixels

		transform_s = [int(round(self.fractional_transform[0]*array2.shape[0] + px_transform[0])), int(round(self.fractional_transform[1]*array2.shape[1] + px_transform[1]))]
		# print("			Transform_S: ", transform_s)

		# Get arrays of the overlapping region


		##########################################
		# PIL arrays are height, width, pixel-data
		##########################################

		# print("			Img1 Array Shape: ", array1.shape)
		# print("			Img2 Array Shape: ", array2.shape)

		overlap_width  = int(round(max(0, min(array1.shape[0], array2.shape[0] + transform_s[0]) - max(0, transform_s[0]))))
		overlap_height = int(round(max(0, min(array1.shape[1], array2.shape[1] + transform_s[1]) - max(0, transform_s[1]))))
		# print("			Overlap Height: ", overlap_height)
		# print("			Overlap Width:  ", overlap_width)

		array1 = array1[max(0,    transform_s[0]):max(0,    transform_s[0])+overlap_width, max(0,    transform_s[1]):max(0,    transform_s[1]) + overlap_height]
		array2 = array2[max(0, -1*transform_s[0]):max(0, -1*transform_s[0])+overlap_width, max(0, -1*transform_s[1]):max(0, -1*transform_s[1]) + overlap_height]

		# print("			Array 1 shape: ", array1.shape)
		# print("			Array 2 shape: ", array2.shape)


		# img1_s_o and img2_s_o have pixel values aligned according to the transform. It's time to start evaluating
		ratio = 1/(2**scale)
		score, straight_e = self._error(array1, array2, "R=1/2^%5f,dx=%d,dy=%d"%(scale, self.fractional_transform[0]+px_transform[0]/ratio, self.fractional_transform[1]+px_transform[1]/ratio))
		
		# print("			Ending Error")
		return score, straight_e

	def _error_numpy(self, ar1, ar2, title="Image"):
		""" Using Numpy, calculate the R^2 error between the two arrays """
		# print("				Starting _Error...")

		rgb_r2 = np.square(np.subtract(ar1[:, :, :-1], ar2[:, :, :-1]))
		rgb_straight_e = np.mean(rgb_r2, -1)

		# print("			Straight_E Shape: ", rgb_straight_e.shape)
		# print("				square_diff min: ", np.min(rgb_r2))

		# We include alpha in our calculations here because a user could choose to modify the alpha channel of an image before feeding it in, and we should respect that
		alpha_product = np.divide(np.multiply(ar1[:, :, -1], ar2[:, :, -1]), 255**2)
		
		scaled_e = np.multiply(rgb_straight_e, alpha_product)
		# scaled_e = rgb_straight_e.copy()


		scaled_e = np.average(scaled_e)
		# print("			Got score ", scaled_e);

		# print("				Ending _Error")
		return scaled_e, rgb_straight_e

	def _error_occa(self, ar1, ar2, title="Image"):
		""" Using the OCCA pipeline, calculate the R^2 error between the two arrays """

		# For performance, I'll be flattening the arrays
		o_dimensions = device.malloc(ar1.shape.astype(np.intc)) # we assume we won't get images with 65,535 pixels on a side
		o_ar1 = device.malloc(ar1.astype(np.float32).ravel())
		o_ar2 = device.malloc(ar2.astype(np.float32).ravel())

		# NEW MEMORY LAYOUT:
		# o_ar* is in [width * [height * [px]]]

		##############
		# Generating R^2 Error
		# 
		# For index K, if K%(o_dimensions[3]) != o_dimensions[3]-1: (If we're in an RGB value)
		#	o_ar1[k] = (o_ar1[k] - o_ar2[k])**2

		##############
		# Getting Alpha-product
		# 
		# for index K, if K%(o_dimensions[3]) == o_dimensions[3]-1: (If we're in an Alpha value)
		#	o_ar1[K] = (o_ar1[K] * o_ar2[K])/(255**2)

		#############
		# -- Requires R^2 error to be complete
		# Taking the R^2 Error Mean per pixel
		#
		# for index K, if K%(o_dimension[3]) == 0: (If we're in the Red channel, becoming the straight_e channel)
		# 	o_ar1[K] = (o_ar1[K] + o_ar1[K+1] + o_ar1[K+2])/3.0
		#
		# This value needs to get preserved and returned; so:
		# 	o_ar1[K+1] = o_ar1[K]

		############
		# -- Requires R^2 Error mean to be complete
		# Computing the alpha_weighted R^2 error
		#
		# for index K, if K%(o_dimension[3]) == 0: (If we're indexed to the straight_e channel)
		# 	o_ar1[K+1] = o_ar1[K] * o_ar1[K+3]
		# The G channel (soon to be averaged) equals the straight_e channel times the product-alpha channel

		#######################################
		# New Kernel


		###########
		# -- Requires prior kernel to complete
		# Averaging the alpha_weighted values
		#
		# alive = o_dimensions[0] * o_dimensions[1]
		# local double sub_blocksum[blockdim]
		#
		# ????
		# 
		# while alive > 1:
		# 	Synchronize?
		# 	for index A:
		# 		if A < alive):
		# 			o_ar1[A+1] = (o_ar1[A+1] + o_ar1[A+1 + alive)]) / 2.0

		###########
		# Copy o_ar1 back to CPU
		# Reshape o_ar1 back into (WxHxC)
		# R channel is straight e
		# G channel at pixel[0, 0] is error average







	def collect_error_print(self):
		# We have two images which approximately overlap.
		# However, some parts of the images contain artifacts.
		# The position of the artifacts is consistant in the frame of a single image.
		# 
		# Where are the artifacts?

		error_score, straight_e = self.error(0) # Evaluate error with a scale of (1/(2^0)) (full res)
		# Note - straight_e only has area according to the /overlap/ between images, not the /full image size/.



		# straight_e = straight_e.transpose() # PIL changes between WxH and HxW

		# se_shape = list(straight_e.shape)
		# target_se_shape = [int(round(x / scale)) for x in se_shape]
		# print("		se_shape: ", straight_e.shape)
		# print("		tse_shape: ", target_se_shape)

		# print("		se min: ", np.min(straight_e))
		# print("		se max: ", np.max(straight_e))


		# e_img = Image.fromarray(straight_e.transpose()).resize(target_se_shape)
		# e_img = Image.fromarray(straight_e).resize(target_se_shape)
		
		err_dest = np.ones(self.images[1].size)*255 #WxH
		# print("		err_dest full: ", err_dest.shape)
		# print("		err_dest tl subslice: ", err_dest[  :straight_e.shape[0],   :straight_e.shape[1]].shape)
		# print("		err_dest br subslice: ", err_dest[-straight_e.shape[0]:, -straight_e.shape[1]:].shape)


		err_dest[  :straight_e.shape[0],   :straight_e.shape[1] ] = np.minimum(err_dest[:straight_e.shape[0],  :straight_e.shape[1] ], straight_e)
		err_dest[  -straight_e.shape[0]:,  -straight_e.shape[1]:] = np.minimum(err_dest[-straight_e.shape[0]:, -straight_e.shape[1]:], straight_e)



		# tl = Image.new('L', img1.size, (255))
		# tl.paste(e_img, (0, 0))
		# # tl.show()
		# br = Image.new('L', img1.size, (255))
		# br.paste(e_img, (img1.size[0]-target_se_shape[0], img1.size[1]-target_se_shape[1]))
		# # br.show()
		# err_dest = ImageMath.eval("min(tl, br)", tl=tl, br=br)

		# err_dest.show()
		# exit()

		return err_dest





	def close(self):
		for img in self.images:
			img.close()


def optimize_worker(argstack):
	fn1, fn2, tf = argstack
	op_t, error_print = run_optimize(fn1, fn2, tf)
	# send_end.send((op_t, error_print))
	return op_t, error_print


def run_optimize(fname1, fname2, tf, pipeline = None):
	print("Creating Alignment for: ", fname1, fname2)
	if pipeline is not None:
		print("[OCCA] Using OCCA for array operations")

	ali = Alignment(Image.open(fname1), Image.open(fname2), tf, fname2, pipeline = pipeline)
	print("[run_optimize] optimize...")
	op_transform, error_print = ali.optimize()
	print("[run_optimize] done")

	ali.close()

	return op_transform, error_print
