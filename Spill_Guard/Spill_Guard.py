from solid import *
from solid.utils import *
from math import asin
import toml
import os

# TODO: move Openscad to a root project directory and edit render_object (also extract to library)


def Spill_Guard(container_radius, inlet_height, shroud_distance, radius, clip_gap, clip_depth, wall_thickness):
    # create the negation solutions
    # This is for scrubbing
    negate = cube((radius+wall_thickness)*2, center=True)
    # This is the simulated container
    # TODO: height is just large but not parametrically precise
    container = cylinder(container_radius, 2*(shroud_distance+inlet_height+radius+2*wall_thickness),
                         center=True, segments=100)

    # create hemisphere shell for catching water droplets
    catch_solid = sphere(radius+wall_thickness, segments=100)
    catch = sphere(radius, segments=100)
    # move up a little because of tearing artifact with spout 
    catch = catch_solid - hole()(up(wall_thickness)(catch))

    # remove the upper half
    catch = catch - up(radius+2*wall_thickness)(negate)
    # remove the front half
    catch = catch - forward(container_radius)(container)

    # set catch on xy plane
    catch = up(radius+wall_thickness)(catch)

    # cape about the outside past wall_thickness to catch high angle & velocity
    #       particles without pressure loss.
    # an eliptic cylinder with major radius iterating a given curve
    shroud_solid = cylinder(r1=radius+wall_thickness, r2=shroud_distance +
                            wall_thickness, h=inlet_height, center=True)
    shroud_solid = forward(2*radius-2*wall_thickness)(shroud_solid)
    # TODO: container_radius in intersect is ideally inf.
    shroud_solid = intersection()(shroud_solid, up(shroud_distance/2 + wall_thickness/2)
                                  (cube([2*radius+2*wall_thickness, container_radius, shroud_distance+wall_thickness], center=True)))
                                  
    # NOTE: this is by default twice the radius since catch is not center=True
    # TODO: test centering the catch. I prefer radius offset due to fitting the cylinders.
    #       just change to centered by setting this not centered... would look better
    shroud = cylinder(r1=radius, r2=shroud_distance,
                      h=inlet_height, center=True)
    shroud = forward(2*radius-2*wall_thickness)(shroud)
    shroud = intersection()(shroud, up(shroud_distance/2+wall_thickness/2)
                            (cube([2*radius, container_radius, shroud_distance], center=True)))

    shroud = shroud_solid-shroud

    # move into position atop the catch
    shroud = up(radius+2*wall_thickness)(shroud)
    shroud = shroud - forward(container_radius)(container)

    # the spout guides water into container
    spout = cylinder(radius, 4*wall_thickness +
                     clip_gap, center=True, segments=100)
    spout = spout - cylinder(radius - wall_thickness,
                             4*wall_thickness + clip_gap, center=True, segments=100)

    spout = rotate([90, 0, 0])(spout)
    # remove the top of the spout to create a half pipe
    spout = spout - up(radius+wall_thickness)(negate)
    # place along the catch
    spout = up(radius+wall_thickness)(spout)

    # create clip slide-on fastener
    clip = cube([wall_thickness, wall_thickness, clip_depth], center=True)
    bridge = cube([wall_thickness, clip_gap+2*wall_thickness,
                   wall_thickness], center=True)
    # set bridge on xy plane
    bridge = up(wall_thickness/2)(bridge)

    far_clip = forward(clip_gap/2 + wall_thickness/2)(clip)
    far_clip = down(clip_depth/2)(far_clip)
    near_clip = back(clip_gap/2 + wall_thickness/2)(clip)
    near_clip = down(clip_depth/2)(near_clip)

    clip = far_clip + bridge + near_clip

    gusset = cube(wall_thickness, center=True)
    gusset = back(wall_thickness)(gusset)
    gusset = up(wall_thickness)(gusset)

    # return the solution
    gutter = clip + gusset + spout + catch + shroud
    return gutter


def render_object(render_object, filename):
    '''
    creates a .stl and .scad solution for the given solidpython OpenSCAD object
    PARAMETERS:
        render_object: the OpenSCAD object
        filename: a string for the file to be saved
    '''
    scad_render_to_file(render_object, filename + ".scad")
    # render with OpenSCAD
    print("Openscad is now rendering the solution..")
    os.system("start ../OpenSCAD/openscad.exe -o " +
              filename + ".stl " + filename + ".scad")


if __name__ == "__main__":
    config = toml.load("configuration.toml")
    gutter = Spill_Guard(**config)
    render_object(gutter, "gutter")
