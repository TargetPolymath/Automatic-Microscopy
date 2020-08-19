# Main Loop for Stitching


###########
# Manage dependencies

import GUIMan as GUI
import Post_Processing as Post
import glob
import sys

# Grab filenames
	
img_list = sys.argv[1:]
print(img_list)
print(len(sys.argv))
img_list.sort()
print("###############")
print(img_list)
print("Is this correct?")
input()

# img_list = ["Test_A.png", "Test_B.png", "Test_C.png", "Test_D.png"]

# Prepare image stacking

stack = Post.Stack()

stack.register_root(img_list[0])

###########
# Start a Window

for filename in img_list[1:]:
	print("\n\n")
	live_window = GUI.GUI_Window(start_offset_ratio = stack.transforms[-1]);

	live_window.load_AB_img(stack.filenames[-1], filename)

	live_window.kickoff()

	fractional_offset = live_window.collect_transform()
	print("Gathered Fractional Offset - ", fractional_offset)

	stack.register(filename, fractional_offset)
	print("-------\n")

stack.output("Out_T.png")



