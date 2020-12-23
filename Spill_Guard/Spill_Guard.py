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
                         center=True, segments=50)

    # create hemisphere shell for catching water droplets
    catch_solid = sphere(radius+wall_thickness, segments=50)
    catch = sphere(radius, segments=50)
    catch = catch_solid - catch

    # remove the upper half
    catch = catch - up(radius+wall_thickness)(negate)
    # remove the front half
    catch = catch - forward(container_radius)(container)

    # set catch on xy plane
    catch = up(radius+wall_thickness)(catch)

    # cape about the outside past wall_thickness to catch high angle & velocity
    #       particles without pressure loss.
    # an eliptic cylinder with major radius iterating a given curve
    shroud = cylinder(radius+wall_thickness, 1, center=True) - \
        cylinder(radius, 1, center=True)
    shroud = up(0.5+radius+wall_thickness)(shroud)
    for it in range(1, int(shroud_distance)):
        # TODO: wall_thickness is deformed here and not consistent,
        #       removes wall_thickness percentage of major radius
        cur_shroud_solid = cylinder(radius+wall_thickness, h=2, center=True)
        cur_shroud_solid = scale([1, (int(shroud_distance)+it) /
                            int(shroud_distance), 1])(cur_shroud_solid)

        cur_shroud = cylinder(radius, h=2, center=True)
        cur_shroud = scale([1, (int(shroud_distance)+it) /
                            int(shroud_distance), 1])(cur_shroud)
        
        cur_shroud = cur_shroud_solid - hole()(cur_shroud)

        # move into position atop catch
        shroud += up(it+radius+wall_thickness)(cur_shroud)

    shroud = shroud - forward(container_radius)(container)

    # extra wall_thickness to seam the spout with the catch (marginally perfect fit)
    # TODO: increase spout distance, has a chance to align with bucket wall through tolerances
    #       TEST AND CLOSE
    spout = cylinder(radius, 4*wall_thickness + clip_gap, segments=50)
    spout = spout - cylinder(radius - wall_thickness/2,
                             4*wall_thickness + clip_gap, segments=50)

    negate = cube(2*radius+wall_thickness, center=True)

    spout = rotate([90, 0, 0])(spout)
    # remove the top of the spout to create a half pipe
    spout = spout - up(radius)(negate)

    spout = up(radius+wall_thickness)(spout)
    spout = forward(2*wall_thickness + clip_gap/2)(spout)

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
    os.system("start OpenSCAD/openscad.exe -o " +
              filename + ".stl " + filename + ".scad")


if __name__ == "__main__":
    config = toml.load("configuration.toml")
    gutter = Spill_Guard(**config)
    render_object(gutter, "gutter")
