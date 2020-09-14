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
DepMan.install_and_import("atexit")

from PIL import Image, ImageMath
import numpy as np
import math
import random
import multiprocessing
import atexit
import time

allow_occa = True

#########################################################
BLOCK_SIZE = 4
# THIS HAS TO MATCH WITH THE KERNEL
# YOU WILL HAVE AN UNDETECTABLE BAD TIME IF IT DOESN'T
#########################################################
try:
	DepMan.install_and_import("occa")
	import occa
except:
	print("[OCCA] Not installed. Disabling.")
	allow_occa = False


min_scale = 7 # only go down to 2^5 pixels
max_scale = 10 # only go up to 2^12 pixels

# Referenced at bottom of file
global_fname_Image_cache = {}

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
		self.fractional_transform = fractional_transform # [Y, X] for compliance

		max_res = img2.width
		# input_transform = np.asarray(input_transform)

		# If we decide that the smallest image we'll expect to get useful info from is 128*128, how many times can we
		# 	divide the width by two and stay above a width of 128?

		scale_steps = math.floor(math.log2(max_res))

		self.scale = max(0, scale_steps - min_scale)
		self.wider_net = False
		self.ending_downscale   = max(0, scale_steps - max_scale) 
		self.prior_transforms = [];
		self.img_scale_cache = [[-1, 0, (0, 0)], [-1, 0, (0, 0)]]; # [scale, image, (H, W)]
		self.occa_arrays = {};
		self._error_kernel = None

		if pipeline is None or allow_occa is False:
			self.pipeline = 'numpy'
			self.device = None
			self._error = self._error_numpy
		else:
			self.pipeline = 'OCCA'
			self.device = occa.Device(argpack)
			self._error = self._error_occa
			# self._init_OCCA_mems()
			# self._error_kernel = self.device.build_kernel("map_error.okl", "map_error")

		atexit.register(self.close)


	def _retrieve_img(self, image_id, scale = None):
		""" Image_id is on a range of 0 or 1; retrieve new or prior scaled version of image """

		if scale is None:
			scale = self.scale
		# print("[cache] grabbing image at scale ", scale)
		cache = self.img_scale_cache[image_id]
		# Not a memory duplicate, just a reference

		if cache[0] == scale: # If the cached image has the same scale...
			# print("[cache] Using cached image scale...")
			if self.pipeline == 'numpy':
				return [cache[1].copy(), cache[2]] # A copy of the image and a reference to the size
			elif self.pipeline == 'OCCA':
				return cache[1:] # The image and it's scale
			else:
				raise
		else:
			# print("[cache] generating fresh...")
			ratio = 1/(2**scale)
			target_im = self.images[image_id]
			# print(f"[{self.name}] Caching image from size {target_im.size}")

			img_new_height = round(target_im.height * ratio)
			img_new_width = round(target_im.width * ratio)

			# Frustratingly, Pillow resize is [X, Y]
			img = target_im.resize((img_new_width, img_new_height))
			img = img.convert("RGBA") # Just making sure

			# Numpy array from Pillow comes out HxWxC
			img = np.array(img)# Pre-convert to array
			# print(f"[{self.name}] Caching image w/ size {img.shape}") # --> H, W, C
			if self.pipeline == 'numpy':
				self.img_scale_cache[image_id] = [scale, img, img.shape[:2]]
			else:
				try:
					# print(cache[1])
					cache[1].free() # deallocate previous image before removing references
				except AttributeError: # If it's an int or placeholder
					print("[INFO] Can't free Cache, likely placeholder")

				#					Probably doesn't /absolutely require/ being explicit, but it prevents
				#						a race condition for memory space. Maybe. It works on my hardware.
				swapped_image = img.astype(np.float32)
				# print(f"[{self.name}] Caching image for OCCA: {swapped_image.shape}")
				self.img_scale_cache[image_id] = [scale, self.device.malloc(swapped_image.ravel(), dtype=np.float32), img.shape[:2]]
				
				#################################
				# Populate OCCA device with allocated mem objects
				self._new_OCCA_mems(img.shape[:2])





			# print("[cache] Fresh complete")
			return self.img_scale_cache[image_id][1:]

	# def _init_OCCA_mems(self):
	# 	self.occa_arrays["o_in_pixels"] = self.device.malloc(0, dtype=np.uint);
	# 	print("[_init] In Pixels initialized? ", self.occa_arrays["o_in_pixels"].is_initialized)
	# 	self.occa_arrays["o_out_pixels"] = self.device.malloc(0, dtype=np.uint);
	# 	self.occa_arrays["o_transform_x"] = self.device.malloc(0, dtype=np.int32);
	# 	self.occa_arrays["o_transform_y"] = self.device.malloc(0, dtype=np.int32);
	# 	self.occa_arrays["o_input_w"] = self.device.malloc(0, dtype=np.uint);
	# 	self.occa_arrays["o_overlap_w"] = self.device.malloc(0, dtype=np.uint);


	def _new_OCCA_mems(self, im_size):
		self.occa_arrays["in_pixels"] = np.uint(im_size[0]*im_size[1])

		self.straight_e = np.zeros((self.occa_arrays["in_pixels"]))
		self.scaled_e_array = np.zeros((math.ceil(self.occa_arrays["in_pixels"] / BLOCK_SIZE)))
		# These are simple allocations, and will eventually receive the responses from the kernel


		###########################################################################
		# Free the previous value, then replace with a value which is static for this scale
		# try:
		# 	self.occa_arrays["o_in_pixels"].free() # Free existing C-allocated memory before python dereferencing
		# except:
		# 	pass;
		# self.occa_arrays["o_in_pixels"].copy_from(self.occa_arrays["in_pixels"]) # Use existing memory object

		##############################################################################
		# Free the previous value, keep the reference, allow it to be used.


		# try:
		# 	self.occa_arrays["o_transform_x"].free() # Free existing C-allocated memory, allowing for re-referencing
		# except:
		# 	pass;
		# self.occa_arrays["o_transform_x"] = self.device.malloc(0, dtype = np.int32)

		# try:
		# 	self.occa_arrays["o_transform_y"].free() # Free existing C-allocated memory, allowing for re-referencing
		# except:
		# 	pass;
		# self.occa_arrays["o_transform_y"] = self.device.malloc(0, dtype = np.int32)

		# try:
		# 	self.occa_arrays["o_input_w"].free() # Free existing C-allocated memory, allowing for re-referencing
		# except:
		# 	pass;
		# self.occa_arrays["o_input_w"] = self.device.malloc(0, dtype = np.uint)

		# try:
		# 	self.occa_arrays["o_overlap_w"].free() # Free existing C-allocated memory, allowing for re-referencing
		# except:
		# 	pass;
		# self.occa_arrays["o_overlap_w"] = self.device.malloc(0, dtype = np.uint)


		############################################################################
		# Free the existing value, remove the reference, replace with a newly mallocated object, and free that empty object
		try:
			self.occa_arrays["o_straight_e"].free() # Free existing C-allocated memory before python dereferencing
		except:
			pass;
		self.occa_arrays["o_straight_e"] = self.device.malloc(self.straight_e, dtype = np.float32)
		# self.occa_arrays["o_straight_e"].free()
		
		try:
			self.occa_arrays["o_scaled_e"].free() # Free existing C-allocated memory before python dereferencing
		except:
			pass;
		self.occa_arrays["o_scaled_e"] = self.device.malloc(self.scaled_e_array, dtype = np.float32)
		# self.occa_arrays["o_scaled_e"].free()
		# self.occa_arrays["o_scaled_e"].copy_from(scaled_e_array)

		#################################################################################


		kernel_file = open("map_error.okl", 'r')
		kernel_string = kernel_file.read()
		kernel_file.close()

		hyparam_str = f"#define BLOCK_SIZE {BLOCK_SIZE}\n"

		kernel_string = hyparam_str + kernel_string

		# print(kernel_string)
		# try:
		# self._error_kernel.free()
		# print("[OCCA] Compiling new kernel...")
		self._error_kernel = self.device.build_kernel_from_string(kernel_string, "map_error")
		# except:
		# 	print(kernel_string)
		# 	exit()



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

		# [Y, X]
		errors = np.zeros((3, 3))

		window_size = 2
		if self.wider_net:
			window_size = 3

		# print("		Window Size: ", window_size)

		for dy in [-1, 0, 1]: # post-scale pixel travel
			for dx in [-1, 0, 1]: # post-scale pixel travel
				# print("			dx=%d,dy=%d"%(dx, dy))
				errors[dy+1, dx+1], _ = self.error(px_transform = [dy*window_size, dx*window_size])
		print("		Errors:\n", errors)

		step = np.subtract(np.unravel_index(np.argmin(errors, axis=None), errors.shape), 1)
		print(f"Step: {step}")
		# exit()

		if np.all(step==0):
			if self.wider_net: # Before moving to the next scale, double our window size
				self.scale -= 1
				self.prior_transforms = [];
				self.wider_net = False
			else:
				self.wider_net = True
		else:
			# 								  [Y, X]														[X, Y][::-1]
			scale_update = np.divide(np.divide(step, np.multiply(1/(2**self.scale), np.asarray(self.images[1].size[::-1]))), 4)
			new_fractional_transform = [self.fractional_transform[0] + scale_update[0], self.fractional_transform[1] + scale_update[1]]
			# [Y, X]

			if new_fractional_transform not in self.prior_transforms:
				self.prior_transforms.append(new_fractional_transform)
				# print("		Update Direction: ", step)
				#										   [  Y   ,   X   ]
				# print(f"[{self.name}]		Scale Update:  [%2.10f, %2.10f]"%(scale_update[0], scale_update[1]))
				self.fractional_transform = [x for x in new_fractional_transform]
				# print(f"[{self.name}]		Wider Net: {self.wider_net}")
				print(f"[{self.name}]		New Transform: [%2.10f, %2.10f]"%(self.fractional_transform[0], self.fractional_transform[1]))
				print(f"[{self.name}]		Org Transform: [%2.10f, %2.10f]"%(self.original_transform[0], self.original_transform[1]))
				# print(f"[{self.name}]		Ratio: {self.scale}")
			else:
				# print(f"[{self.name}]		Skipping [Already checked]")
				self.scale -= 1 # No update, we've already been where we're going; scale down and continue
				self.prior_transforms = [];
			self.wider_net = False;


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
		array1, array1_shape = self._retrieve_img(0, scale = scale)
		array2, array2_shape = self._retrieve_img(1, scale = scale)

		# print("			PX Transform: ", px_transform)

		# Step 2: Calculate the scale-transform in pixels
		# [Y, X]
		transform_s = [int(round(self.fractional_transform[0]*array2_shape[0] + px_transform[0])), int(round(self.fractional_transform[1]*array2_shape[1] + px_transform[1]))]
		# print("			Transform_S: ", transform_s)

		# Get arrays of the overlapping region


		##########################################
		# PIL arrays are height, width, pixel-data
		##########################################

		overlap_height  = int(round(max(0, min(array1_shape[0], array2_shape[0] + transform_s[0]) - max(0, transform_s[0]))))
		overlap_width   = int(round(max(0, min(array1_shape[1], array2_shape[1] + transform_s[1]) - max(0, transform_s[1]))))

		#																	Y     			X 							[Y, X]
		score, straight_e = self._error(array1, array2, transform_s, [overlap_height, overlap_width], original_dims = array1_shape)
		
		# print("			Ending Error")
		return score, straight_e

	def _error_numpy(self, ar1, ar2, transform_s, overlap, original_dims = None, title="Image"):
		""" Using Numpy, calculate the R^2 error between the two arrays """
		# print("				Starting _Error...")

		ar1 = ar1[max(0,    transform_s[0]):max(0,    transform_s[0])+overlap[0], max(0,    transform_s[1]):max(0,    transform_s[1]) + overlap[1]]
		ar2 = ar2[max(0, -1*transform_s[0]):max(0, -1*transform_s[0])+overlap[0], max(0, -1*transform_s[1]):max(0, -1*transform_s[1]) + overlap[1]]

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

	def _device_finish(self):
		self.device.finish()

	def _copy_back(self, straight_e, scaled_e_array):
		""" An isolated function for diagnosing memcopy times """
		self.occa_arrays["o_straight_e"].copy_to(straight_e)
		self.occa_arrays["o_scaled_e"].copy_to(scaled_e_array)


	def _error_occa(self, ar1, ar2, transform_s, overlap, original_dims, title="Image"):
		""" Using the OCCA pipeline, calculate the R^2 error between the two arrays """
		""" IMPORTANT The notes in this method are not perfect representations of what happens in the kernel, but they're very close. """

		start_time = time.time()
		# print(f"[OCCA] Start")

		in_pixels = np.uint(original_dims[0]*original_dims[1])
		out_pixels = np.uint(overlap[0]*overlap[1])
		# print(f"[{self.name} - OCCA] In Pixels 		= {in_pixels}")
		# print(f"[{self.name} - OCCA] transform_s		= {transform_s}")
		# print(f"[{self.name} - OCCA] overlap 		= {overlap}")
		# print(f"[{self.name} - OCCA] original dims	= {original_dims}")

		# try:
		# 	self.occa_arrays["o_out_pixels"].free() # Free existing C-allocated memory before replacement (possibly not necessary, testing)
		# except:
		# 	pass;


		# self.occa_arrays["o_out_pixels"].copy_from(out_pixels);
		# self.occa_arrays["o_transform_x"].copy_from(transform_s[0])
		# self.occa_arrays["o_transform_y"].copy_from(transform_s[1])
		# self.occa_arrays["o_input_w"].copy_from(original_dims[0])
		# self.occa_arrays["o_overlap_w"].copy_from(overlap[0])



		malloc_duration = time.time() - start_time
		start_time = time.time()
		# print(f"[OCCA] Copy Done: 	{malloc_duration}")


		# kernel_file = open("map_error.okl", 'r')
		# kernel_string = kernel_file.read()
		# kernel_file.close()

		# hyparam_str = f"#define BLOCK_SIZE {BLOCK_SIZE}\n#define TRANSFORM_X {transform_s[0]}\n#define TRANSFORM_Y {transform_s[1]}\n#define INPUT_W {original_dims[0]}\n#define OVERLAP_W {overlap[0]}\n"

		# kernel_string = hyparam_str + kernel_string

		# # # print(kernel_string)
		# try:
		# 	_error_kernel = self.device.build_kernel_from_string(kernel_string, "map_error")
		# except:
		# 	# print(kernel_string)
		# 	exit()

		# kbuild_time = time.time() - start_time
		# start_time = time.time()
		# # print(f"[OCCA] Build Kernel: 	{kbuild_time}")

		self._error_kernel( in_pixels,
							out_pixels,
							ar1, 
							ar2, 
							self.occa_arrays["o_straight_e"],
							self.occa_arrays["o_scaled_e"],
							np.int32(transform_s[0]), np.int32(transform_s[1]), # [Y, X]
							np.uint(original_dims[1]),	# [X]	
							np.uint(overlap[1]))		# [X]

		# Allocate arrays to receive the responses
		# straight_e = np.zeros((in_pixels))
		# scaled_e_array = np.zeros((math.ceil(in_pixels / BLOCK_SIZE)))
		straight_e = self.straight_e.copy()
		scaled_e_array = self.scaled_e_array.copy()

		# ####################################################
		# ##
		# ##
		# test_img = np.zeros([original_dims[0], original_dims[1], 4]).ravel()
		# ar2.copy_to(test_img)
		# # print("\n\nTesting Kernel")
		# # print(original_dims)
		# # print(test_img.shape)
		# test_img = test_img.reshape([original_dims[0], original_dims[1], 4])
		# Image.fromarray(test_img.astype(np.uint8)).show()

		# exit()


		# ##
		# ##
		# ######################################################






		self._device_finish(); # Track how long we're waiting to finish, separately from memcpy
		self._copy_back(straight_e, scaled_e_array)
		# # Just does this:
		# self.occa_arrays["o_straight_e"].copy_to(straight_e)
		# self.occa_arrays["o_scaled_e"].copy_to(scaled_e_array)



		straight_e = straight_e[:out_pixels].reshape(overlap)


		scaled_e = np.sum(scaled_e_array[:math.ceil(out_pixels / BLOCK_SIZE) ]) / out_pixels

		if np.isnan(scaled_e):
			scaled_e = np.inf


		# print(f"[OCCA] Straight E: {straight_e.shape}")
		print(f"[OCCA] Scaled E  : {scaled_e}")

		# #################################################
		# #
		# #
		# Image.fromarray(straight_e.astype(np.uint8)).show()
		# exit()
		# #
		# #
		# #################################################

		# o_ar1.free()
		# o_ar2.free()
		# o_straight_e.free()
		# o_scaled_e.free()
		# o_in_pixels.free()
		# o_out_pixels.free()
		# _error_kernel.free()

		# Attempts to speed up overall execution by reducing slow management
		time.sleep(0.00001)
		self.device.finish()



		# print(f"[OCCA] R/C/F: 		{time.time() - start_time}")

		return scaled_e, straight_e

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

		###########
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

		print(f"[Error Print] straight_e: {straight_e.shape}")

		#								[X, Y][::-1]
		err_dest = np.ones(self.images[1].size[::-1])*255 #HxW
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
		print(f"[{self.name}] Closing...")
		for img in self.images:
			img.close()

		for s, img, x in self.img_scale_cache:
			try:
				img.free()
			except:
				print("[Closing] img not free")
				pass
			del img
		print("[Closing] Images Free")
		try:
			for key, value in self.occa_arrays.items():
				try:
					print(f"[{key}] Closing...")
					value.free()
				except:
					print("[Closing] mem not free")
					pass
				del value
		except:
			pass;
		print("[Closing] Mems free")

		try:
			del self.occa_arrays
		except:
			pass
		try:
			print("F1")
			self.device.finish()
			print("F3")
			# self.device.free()
		except:
			print("[OCCA] Free Device doesn't work?")
		# del self.device
		print(f"[{self.name}] Closed.")

# # Moved to top of file
# global_fname_Image_cache = {}

def preload_gfIc(fnames):
	p = multiprocessing.Pool();
	imgs = p.map(Image.open, fnames)
	p.close()
	for fname, img in zip(fnames, imgs):
		global_fname_Image_cache[fname] = img

def get_Image(fname):
	""" Use dict cache for image loading """

	# Not clear if this is even remotely thread safe
	if fname not in global_fname_Image_cache.keys():
		global_fname_Image_cache[fname] = Image.open(fname)

	return global_fname_Image_cache[fname].copy()

def clear_gfIc():
	for img in global_fname_Image_cache.values():
		img.close()

atexit.register(clear_gfIc)

def optimize_worker(argstack):
	fn1, fn2, tf = argstack
	op_t, error_print = run_optimize(fn1, fn2, tf)
	# send_end.send((op_t, error_print))
	return op_t, error_print


def run_optimize(fname1, fname2, tf, pipeline = None, argpack = None):
	print("Creating Alignment for: ", fname1, fname2)
	if pipeline is not None:
		print("[OCCA] Using OCCA for array operations")

	ali = Alignment(get_Image(fname1), get_Image(fname2), tf, fname2, pipeline = pipeline, argpack = argpack)
	print("[run_optimize] optimize...")
	op_transform, error_print = ali.optimize()
	print("[run_optimize] done")

	ali.close()

	return op_transform, error_print
