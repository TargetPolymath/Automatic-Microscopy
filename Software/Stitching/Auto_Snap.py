# Image Auto_snapping
import DepMan
print("Managing Auto_Snap dependencies...");
DepMan.install_and_import("PIL", pip_name = "Pillow")
DepMan.install_and_import("numpy")
from PIL import Image
import numpy as np

def optimize_transform(img1, img2, input_transform):
	# Placeholder
	# Just evaluate error and get on with it
	er = error(img1, img2, input_transform, 0.1);
	print(er)
	return input_transform

def error(img1, img2, transform, scalar):
	# This will be the evaluator for the error between two images and their relative transform (transform as a fraction of img2 size)
	# Technically, both images are color arrays or color-alpha arrays (no alpha is presumed to be full opacity)
	# We take the product of the alpha channels as a scalar of the R^2 error contribution

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

	transform_s = [round(transform[0]*img2_new_width), round(transform[1]*img2_new_height)]

	# Get arrays of the overlapping region
	# PIL arrays are height, width, pixel-data
	array1 = np.array(img1_s)
	array2 = np.array(img2_s)

	overlap_width = max(0, min(img1_new_width, img2_new_width + transform_s[0]) - max(0, transform_s[0]))
	overlap_height = max(0, min(img1_new_height, img2_new_height + transform_s[1]) - max(0, transform_s[0]))

	# array1_o = array1[round(max(0, transform_s[1])):round(max(0, transform_s[1]))+overlap_height, round(max(0, transform_s[0])):round(min(-1, transform_s[0]))]
	# array2_o = array2[round(max(0, -1*transform_s[1])):round(min(-1, -1*transform_s[1])), round(max(0, -1*transform_s[0])):round(min(-1, -1*transform_s[0]))]

	array1_o = array1[max(0, transform_s[1]):max(0, transform_s[1]) + overlap_height, max(0, transform_s[0]):max(0, transform_s[0])+overlap_width]
	array2_o = array2[max(0, -1*transform_s[1]):max(0, -1*transform_s[1]) + overlap_height, max(0, -1*transform_s[0]):max(0, -1*transform_s[0])+overlap_width]



	# img1_s_o and img2_s_o have pixel values aligned according to the transform. It's time to start evaluating

	score = _error(array1_o, array2_o)

	return score

def _error(ar1, ar2):

	rgb_r2 = np.square(ar1[:, :, :-1] - ar2[:, :, :-1])

	Image.fromarray(rgb_r2).show()

	rgb_straight_e = np.mean(rgb_r2, -1)

	alpha_product = (ar1[:, :, -1]*ar2[:, :, -1])/(255^2)

	rgb_scaled_e = rgb_straight_e * alpha_product

	r2 = np.average(rgb_scaled_e)

	print("Got score ", r2);
	return r2








