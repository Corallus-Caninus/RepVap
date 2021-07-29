from solid import *
from solid.utils import *
from math import asin, atan, pi, cos, sin, sqrt, tan
import toml
import os

# TODO: move Openscad to a root project directory and edit render_object (also extract to library)
# TODO: nubs to stretch filters from polyester cloths over orifice


def Spill_Guard(container_top_radius, container_bottom_radius, container_height, guard_height, inlet_height, shroud_distance, radius, clip_gap, clip_depth, wall_thickness):
    # create the negation solutions
    # This is for scrubbing
    negate = cube((radius+wall_thickness)*2, center=True)
    # The simulated container
    # TODO: height is just large but not parametrically precise
    # TODO: also angle the cylinder to match plastic mold injection angle
    # use R1 and R2 for the cone slope of the bucket 11.91 and 10.33 since its linear
    # container = cylinder(container_radius, 2*(shroud_distance+inlet_height+radius+2*wall_thickness),
    container = cylinder(r1=container_top_radius, r2=container_bottom_radius, h=container_height,
                         center=True, segments=100)

    def container_slope_offset(height):
        '''return the radius for the given height of the container cone'''
        # first write the line equation
        # y2 - y1 = m(x2 - x1) where y2 is the container top radius and y1 is the container bottom radius
        # then solve for the radius
        # radius = y1 - m(x1)
        slope = (container_top_radius - container_bottom_radius) / container_height
        offset = container_bottom_radius - slope * container_height
        return slope * height + offset
        # return slope * height

    # create hemisphere shell for catching water droplets
    catch_solid = sphere(radius+wall_thickness, segments=100)
    catch = sphere(radius, segments=100)
    # move up a little because of tearing artifact with spout
    catch = catch_solid - hole()(up(wall_thickness)(catch))

    # remove the upper half
    catch = catch - up(radius+2*wall_thickness)(negate)
    # move the catch up to the given height
    catch = up(guard_height+radius)(catch)
    container_radius = container_slope_offset(guard_height) + radius
    # remove the front half
    #catch = catch - forward(container_slope_offset(guard_height)+radius)(container)
    catch = catch - forward(container_radius)(container)
    # TODO move everything up instead of moving this down
    catch = down(guard_height+radius)(catch)
    print(container_radius)

    # set catch on xy plane
    catch = up(radius+wall_thickness)(catch)

    # cape about the outside past wall_thickness to catch high angle & velocity
    #       particles without pressure loss.
    # an eliptic cylinder with major radius iterating a given curve
    shroud_solid = cylinder(r1=radius+wall_thickness, r2=shroud_distance +
                            wall_thickness, h=inlet_height, center=True)
    # shroud_solid = forward(2*radius-2*wall_thickness)(shroud_solid)
    # TODO: container_radius in intersect is ideally inf.
    shroud_solid = intersection()(shroud_solid, up(shroud_distance/2 + wall_thickness/2)
                                  (cube([2*radius+2*wall_thickness, container_top_radius, shroud_distance+wall_thickness], center=True)))

    # NOTE: this is by default twice the radius since catch is not center=True
    # TODO: test centering the catch. I prefer radius offset due to fitting the cylinders.
    #       just change to centered by setting this not centered... would look better
    shroud = cylinder(r1=radius, r2=shroud_distance,
                      h=inlet_height, center=True)
    # shroud = forward(2*radius-2*wall_thickness)(shroud)
    shroud = intersection()(shroud, up(shroud_distance/2+wall_thickness/2)
                            (cube([2*radius, container_top_radius, shroud_distance], center=True)))

    shroud = shroud_solid-shroud

    # move up to simulate the container subtraction
    shroud = up(radius+guard_height)(shroud)
    shroud = forward(radius + 2*wall_thickness)(shroud)
    shroud = shroud - forward(container_radius)(container)
    # move into position atop the catch
    shroud = down(guard_height-wall_thickness)(shroud)

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
    # now rotate the clip to match the bucket angle
    #clip_angle = degrees(atan((clip_gap/2)/clip_depth))
    #print("clip angle is:", clip_angle)
    #clip = rotate([-clip_angle, 0, 0])(clip)
    slope = (container_top_radius - container_bottom_radius) / container_height
    container_angle = degrees(atan(slope))
    clip = rotate([-container_angle, 0, 0])(clip)
    # make up for the rotation to set clip and catch on spout
    #clip_offset = clip_gap/2 * cos(radians(clip_angle))
    clip_offset = clip_gap/2 * cos(radians(container_angle))
    clip = up(clip_offset)(clip)
    catch = up(clip_offset)(catch)

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
    scad_render_to_file(render_object, filename +
                        ".scad", file_header='$fn=200;')
    # render with OpenSCAD
    print("Openscad is now rendering the solution..")
    os.system("/home/bada/Desktop/code/openscad/openscad -o " +
              filename + ".stl " + filename + ".scad")


if __name__ == "__main__":
    config = toml.load("configuration.toml")
    gutter = Spill_Guard(**config)
    render_object(gutter, "gutter")
