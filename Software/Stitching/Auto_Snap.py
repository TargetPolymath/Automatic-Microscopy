# Image Auto_snapping
import DepMan
print("Managing Auto_Snap dependencies...");
DepMan.install_and_import("PIL", pip_name = "Pillow")
DepMan.install_and_import("numpy")
DepMan.install_and_import("math")
DepMan.install_and_import("random")
from PIL import Image, ImageMath
import numpy as np
import math
import random

min_scale = 8 # only go down to 2^8 pixels
max_scale = 10 # only go up to 2^10 pixels

class Alignment(object):
	"""docstring for Alignment"""
	def __init__(self, img1, img2, fractional_transform, name = None):
		super(Alignment, self).__init__()
		self.img1 = img1
		self.img2 = img2
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
		self.ending_downscale   = max(0, scale_steps - max_scale) 
		self.prior_transforms = [];


	def perform_optimization_step(self, alpha_mask):
		if self.scale == self.ending_downscale:
			print("\n"*5)
			print("DONE!")
			return False, np.zeros_like(self.img1)
		print("\n")
		print("	Single Optimizer Step on "+self.name)
		print("	Starting with f_transform ", self.fractional_transform)

		alpha_img = Image.fromarray(np.multiply(alpha_mask, 255).astype(np.uint8).transpose()).convert('L')
		img1_alpha = self.img1.copy()
		img1_alpha.putalpha(alpha_img.resize(self.img1.size))
		img2_alpha = self.img2.copy()
		img2_alpha.putalpha(alpha_img.resize(self.img2.size))

		# print(img1_alpha)

		ratio = 1/(2**self.scale)
		print("		R=%6f"%ratio)


		errors = np.zeros((3, 3))

		for dx in [-1, 0, 1]: # post-scale pixel travel
			for dy in [-1, 0, 1]: # post-scale pixel travel
				# print("			dx=%d,dy=%d"%(dx, dy))
				errors[dx+1, dy+1], _ = error(img1_alpha, img2_alpha, self.fractional_transform, ratio, px_transform = [dx, dy])
		# print("		Errors:\n", errors)

		step = np.subtract(np.unravel_index(np.argmin(errors, axis=None), errors.shape), 1)

		if np.all(step==0):
			self.scale -= 1
			self.prior_transforms = [];
		else:
			scale_update = np.divide(np.divide(step, np.multiply(ratio, np.asarray(self.img2.size))), 2)
			new_fractional_transform = [self.fractional_transform[0] + scale_update[0], self.fractional_transform[1] + scale_update[1]]
			
			if new_fractional_transform not in self.prior_transforms:
				self.prior_transforms.append(new_fractional_transform)
				print("		Update Direction: ", step)
				print("		Scale Update: ", scale_update)
				self.fractional_transform = [x for x in new_fractional_transform]
				print("		New Transform: ", self.fractional_transform)
				print("		Org Transform: ", self.original_transform)
			else:
				self.scale -= 1 # No update, we've already been where we're going; scale down and continue
				self.prior_transforms = [];

		# Contribute to Alpha Mask
		error_print = collect_error_print(self.img1, self.img2, self.fractional_transform, ratio)

		return True, error_print
	def close(self):
		self.img1.close()
		self.img2.close()




def optimize_transform(img1, img2, input_transform):
	# Placeholder
	# Just evaluate error and get on with it

	# We're presuming the aspect is in the order of magnitude of less than 2:1
	print("	Starting Optimizer...")
	print("	Optimizer starting with transform ", input_transform)
	max_res = img2.width
	# input_transform = np.asarray(input_transform)

	# If we decide that the smallest image we'll expect to get useful info from is 128*128, how many times can we
	# 	divide the width by two and stay above a width of 128?

	scale_steps = math.floor(math.log2(max_res))

	starting_downscale = max(0, scale_steps - min_scale) # how many powers of two between 2^7 and image width? divide by 2 to that power
	ending_downscale   = max(0, scale_steps - max_scale) # how many powers of two between 2^10 and image width? 

	print("	Looping %d times:"%(starting_downscale - ending_downscale))

	for scale in range(starting_downscale, ending_downscale, -1):
		for step_count in range(10): # Arbitrary to prevent looping
			ratio = 1/(2**scale)
			print("		R=%6f"%ratio)

			errors = np.zeros((3, 3))

			for dx in [-1, 0, 1]: # post-scale pixel travel
				for dy in [-1, 0, 1]: # post-scale pixel travel
					# print("			dx=%d,dy=%d"%(dx, dy))
					errors[dx+1, dy+1], _ = error(img1, img2, input_transform, ratio, px_transform = [dx, dy])

			print("		Errors:\n", errors)

			step = np.subtract(np.unravel_index(np.argmin(errors, axis=None), errors.shape), 1)

			if np.all(step==0):
				break;
			else:
				print("		Update Direction: ", step)
				scale_update = np.divide(np.divide(step, np.multiply(ratio, np.asarray(img2.size))), 2)
				print("		Scale Update: ", scale_update)
				input_transform[0] += scale_update[0]
				input_transform[1] += scale_update[1]
				print("		New Transform: ", input_transform)


	return input_transform

def error(img1, img2, transform, scalar, px_transform = [0, 0]):
	# This will be the evaluator for the error between two images and their relative transform (transform as a fraction of img2 size)
	# Technically, both images are color arrays or color-alpha arrays (no alpha is presumed to be full opacity)
	# We take the product of the alpha channels as a scalar of the R^2 error contribution

	# Direct transform is a pixel transformation added on top of the ratio transformation

	# Right now it's a terrible placeholder

	#####################################

	# Step 0: Ensure there's some kind of alpha component
	img1 = img1.convert("RGBA")
	img2 = img2.convert("RGBA")

	# Step 1: Scale according to the scalar to reduce computation time
	img1_new_width = round(img1.width * scalar)
	img1_new_height = round(img1.height * scalar)

	img2_new_width = round(img2.width * scalar)
	img2_new_height = round(img2.height * scalar)


	img1_s = img1.resize((img1_new_width, img1_new_height))
	img2_s = img2.resize((img2_new_width, img2_new_height))

	# Step 2: Calculate the scalar-transform in pixels

	transform_s = [int(round(transform[0]*img2_new_width) + px_transform[0]), int(round(transform[1]*img2_new_height) + px_transform[1])]
	# print("			Transform_S: ", transform_s)
	# Get arrays of the overlapping region
	# PIL arrays are height, width, pixel-data
	array1 = np.array(img1_s)
	array2 = np.array(img2_s)
	# print("			Img1 Array Shape: ", array1.shape)
	# print("			Img2 Array Shape: ", array2.shape)

	overlap_width =  int(round(max(0, min(img1_new_width,  img2_new_width  + transform_s[0]) - max(0, transform_s[0]))))
	overlap_height = int(round(max(0, min(img1_new_height, img2_new_height + transform_s[1]) - max(0, transform_s[1]))))
	# print("			Overlap Height: ", overlap_height)
	# print("			Overlap Width:  ", overlap_width)
	# array1_o = array1[round(max(0, transform_s[1])):round(max(0, transform_s[1]))+overlap_height, round(max(0, transform_s[0])):round(min(-1, transform_s[0]))]
	# array2_o = array2[round(max(0, -1*transform_s[1])):round(min(-1, -1*transform_s[1])), round(max(0, -1*transform_s[0])):round(min(-1, -1*transform_s[0]))]

	array1_o = array1[max(0,    transform_s[1]):max(0,    transform_s[1]) + overlap_height, max(0,    transform_s[0]):max(0,    transform_s[0])+overlap_width]
	array2_o = array2[max(0, -1*transform_s[1]):max(0, -1*transform_s[1]) + overlap_height, max(0, -1*transform_s[0]):max(0, -1*transform_s[0])+overlap_width]

	# print("			Array 1 shape: ", array1_o.shape)
	# print("			Array 2 shape: ", array2_o.shape)


	# img1_s_o and img2_s_o have pixel values aligned according to the transform. It's time to start evaluating

	score, straight_e = _error(array1_o, array2_o, "R=%5f,dx=%d,dy=%d"%(scalar, transform[0]+px_transform[0]/scalar, transform[1]+px_transform[1]/scalar))

	return score, straight_e

def _error(ar1, ar2, title="Image"):

	rgb_r2 = np.square(ar1[:, :, :-1] - ar2[:, :, :-1])
	# print("				square_diff min: ", np.min(rgb_r2))

	# Image.fromarray(rgb_r2)# .show(title=title)

	rgb_straight_e = np.mean(rgb_r2, -1)
	# print("			Straight_E Shape: ", rgb_straight_e.shape)

	alpha_product = (ar1[:, :, -1]*ar2[:, :, -1])/(255**2)

	rgb_scaled_e = rgb_straight_e * alpha_product
	# print("			Scaled_E Shape: ", rgb_scaled_e.shape)

	r2 = np.average(rgb_scaled_e)

	# print("			Got score ", r2);
	return r2, rgb_straight_e



def collect_error_print(img1, img2, transform, scalar):
	# We have two images which approximately overlap
	# However, some parts of the images contain artifacts
	# The position of the artifacts is consistant in the frame of a single image
	# Where are the artifacts?

	error_score, straight_e = error(img1, img2, transform, scalar)
	straight_e = straight_e.transpose() # PIL changes between WxH and HxW

	se_shape = list(straight_e.shape)
	target_se_shape = [int(round(x / scalar)) for x in se_shape]
	# print("		se_shape: ", se_shape)
	# print("		tse_shape: ", target_se_shape)

	# print("		se min: ", np.min(straight_e))
	# print("		se max: ", np.max(straight_e))

	e_img = Image.fromarray(straight_e.transpose()).resize(target_se_shape)
	

	tl = Image.new('L', img1.size, (255))
	tl.paste(e_img, (0, 0))
	# tl.show()
	br = Image.new('L', img1.size, (255))
	br.paste(e_img, (img1.size[0]-target_se_shape[0], img1.size[1]-target_se_shape[1]))
	# br.show()
	err_dest = ImageMath.eval("min(tl, br)", tl=tl, br=br)

	# err_dest.show()
	# exit()

	return err_dest






