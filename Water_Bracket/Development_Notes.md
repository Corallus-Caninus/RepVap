# FUTURE FEATURES 
Consider multiple brackets joined by a ceiling underneath the VRM/Screw pillars to cool GPU and 
CPU in laptops. This requires a list of list of screws and of mounts.
ListOfLists: chips, screws, VRMs

Create buckets/splash-guards about the nozzles to fill/guide any
leakage away from motherboard by the tubing. 

Create an upside down motherboard riser.

Create hardshell tubing and integrate into bucket/splash guard guides.

Can use a pressure sensor on the plumbing to indicate a leak which can set a buzzer alarm that turns
off pump or the buckets can just fill if not set upside down. alarm should exist anyways on any 
hydro-electric system that isnt >IPX2 rated.

# RESEARCH
A GUI that creates all 3D print files(Block Harness, VRM Connection Harness, Board Risers),
SVGs and a step by step guide on how-to put together the water cooling solution.
This can be seperate from evaporative cooler since people run water coolers with
pickle jars and radiators for 30 bucks.
REQUIRES: 3d printer, printer (optional), measuring device (preferably calipers),
            separate windows machine.

Automatically upload to database user configurations of MOBOS/PCBs that have been measured for browsing
by other users? a "report feedback" that can be moderated by verifying picture measurements.
(way too advanced for now). search locally downloaded configurations by PC/motherboard before
having to measure yourself.

Build hard shell tubing for the flex hoses as a seperate parametric design that takes in 
an SVG for routing.

create connections (linearly slanted not 90 degree) that can be lamenated/glued with aluminum
foil to VRMs using extracted code from screw terminals to precisely connect top of heat sink
to VRMs and reduce shorting chance. diagonalize pillars. use svg idea to create a stencil
printout for aluminum or just print out dimensions. This feature depends on the capability
of the target audience.

these should be in a simple tkinter gui .exe bundled with OpenSCAD(mac and linux can run source)
with instruction images on one side and entry fields on the other to reduce
some of the parameter overhead. produce SVG and .obj files in respective folders for printing.

built in photogrammetry using pictures of motherboards and clicking on water block
corners (dimensions are entered of water block to give ground truthing) then screw terminals in GUI
to generate [x,y,z] coordinate params. Use pillow and instruct user to 
planar translate the camera. find some closed loop metric to say if image photogrammetry
failed to prevent false positive prints, possibly comparing ground truth dimensions (user clickes)
with raw photogrammetric dimensions using k-folds validation about each corner
(permute 2*4! comparisons for all (x,y) pairs) use edge detection filtering (DOG) since aluminum
or colored block is same color to find each raw corner coordinate. Note that aluminum block must
be solid color for measurements in instructions and glares will effect the quality
(a healthy dousing of flour would suffice, just like laser scanning photogrammetry from high school)
use a error tolerance in photogrammetry set based on plasticity of plastic leaf-spring behaviour. find this
empirically it isnt too important, if nothing else just make sure its rigid with little-no plasticity 
and precise.

average the user clicks on each 2 points to account for non-pixel-perfect clicking s.t. x1 x2 are equal
for top points (x = (x1 + x2)/2) since is a parallelogram.
make user reclick if distance between x1 and x2 > some tolerance.
reject the photogrammetry if k-folds is below some tolerance.

This is too ambitious. would be easy with a team or another person but more features can be done
with less effort.

should extract pillars to create standoffs for laptops or other motherboards
should be implemented in a related project this also helps prevent any potential leakage damage.
