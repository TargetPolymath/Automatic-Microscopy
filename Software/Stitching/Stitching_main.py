"""
Copyright 2020 Zachary J. Allen

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
"""

# Main Loop for Stitching


###########
# Manage dependencies

import GUIMan as GUI
import Post_Processing as Post
import glob
import sys
import Auto_Snap as snap # For cache filling
from multiprocessing import Process # for cache filling

# Grab filenames


if __name__ == '__main__':


	print("-"*30)
	print("Welcome to Automatic Microscopy!")
	print("-"*30)
	print("This module takes in image files with overlapping fields, aligns them, attempts to remove lens artifacts and dirt, and stitches them together.")
	print("\nThis will scale the load according to your CPU's core count, so this /definitely/ can overload a machine that's already doing significant work. Be cautious.")
	print("\n"*2)
	print("="*50)
	print("- - - - THE ONLY HELP YOU'LL GET - - - -")
	print("="*50)
	print("Click and drag on the GUI images until they seem to be somewhat aligned. This software can take care of a lot of misalignment, but it's easier if you give it a little help.")
	print("[NOTICE] This software WILL NOT FUNCTION if any image does not overlap with both of its neighbors.")
	print("\nWhen you're satisfied with your alignment, hit [ENTER].")
	print("If all of your images have roughly the same relative transformation (relative to it's previous), you can click-and-drag that transform once, then hit [TAB] for the rest of the images to auto-complete.")
	print("The output is currently called 'Out_T.png' because I haven't built a way for you to change it.")
	print("Hit [Enter], confirm that the filenames were collected correctly, and get aligned!")
	# input()

	img_list = sys.argv[1:]
	# print(img_list)
	# print(len(sys.argv))
	img_list.sort()
	print("###############")
	print("\n".join(img_list))
	print("Is this correct? ([ENTER]/[CANCEL])")
	# input()

	# img_list = ["Test_A.png", "Test_B.png", "Test_C.png", "Test_D.png"]

	# Prepare image stacking
	async_fill_img_cache = Process(target=snap.preload_gfIc, args=([img_list]))
	async_fill_img_cache.start()



	stack = Post.Stack()

	stack.register_root(img_list[0])

	skip_GUI = True # For repeatable testing
	fractional_offset = [0, 0] # [Y, X] for compliance

	###########
	# Start a Window

	for filename in img_list[1:]:


		if not skip_GUI:
			print("\n\n")
			live_window = GUI.GUI_Window(start_offset_ratio = stack.transforms[-1]);

			live_window.load_AB_img(stack.filenames[-1], filename)

			live_window.kickoff()

			fractional_offset, skip_GUI = live_window.collect_transform()
			# print("Gathered Fractional Offset - ", fractional_offset)

		# This doesn't open the images
		stack.register(filename, fractional_offset)
		# print("-------\n")

	async_fill_img_cache.join()
	# The image caching can take up to this long; at this point, we need it to be done
	# 	before we can continue
	stack.output("Seed_Pod/Out.png")



