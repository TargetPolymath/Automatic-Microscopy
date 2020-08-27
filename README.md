# Automatic-Microscopy

# Vision
Generally, I want to build a computer-controlled microscope stage and digital image capture system which can image samples tens to hundreds of times longer than the FOV of the microscope. I also want to write software which can control and stitch together the resulting images.

# Purpose
I hope to develop post-capture analysis software which could conceivably be run by a high-schooler on hardware they might have access to.

# Status
1. This toolkit can control a G-Code-style serial-connected controller and camera to take photos with timing and position offsets.
1. This toolkit can receive a series of images, determine their relative alignments (with or without human help), and stitch them into a single output image.
