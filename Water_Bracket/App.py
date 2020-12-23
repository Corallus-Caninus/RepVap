# a GUI that processes photogrammetry of a user supplied 
# image to increase precision and reduce measurement labor
import tkiner
import PIL 
import numpy as n

# TODO: need parallax photogrammetry to get depth since VRMs are definitely not coplanar to screws etc.

# request user dimensions of water cooling block (x,y,z)
# this is the only information needed to form a basis for the measurements

# instruct the user to place the water cooling block where they would like it mounted
# take user images (video? picture "errors" would produce perspective for monocular photogrammetry)

# request the user clicks twice (for average) each corner of the block

# sorbel filter the image 

# compare the surface of the water cooling block found by the bounds of the sorbel edges 
# (The sides not including the nozzle, 1/2 the block as a right triangle) to the user found corners, 
# if within tolerance proceed, else recommend to flour or dust the object to prevent reflections and restart

# localize all pixels in image solution

# have the user click on all screw pixels, entering screw params each time.
# have the user click on all VRM/VRAM etc. corners, bounding a surface (no param entry)

# generate configuration for water_bracket and call.
