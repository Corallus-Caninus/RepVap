from solid import *
from solid.utils import *
import toml
from math import *
import os

# TODO: retangle_prism_dimensions should be ListOfLists like screw_args for multi chip cooling
#       (cpu-gpu combinations like laptops are the primary application but can be used on other PCBs)
# for now may be able to union two water_mounts with identical screw_args, just need to
# ensure can drive screws

# TODO: screw down fasteners for OD of tubing to assist with ribbing of nozzles. Prioritize failsafing
#       in 3d print design (build stays cheap). This is lowest priority.


def mount_side_nozzles(**argv):
    # rectangle_prism_dimensions, nozzle_direction, wall_thickness,
    #                      screw_args):
    '''
    a mount to mount a simple, cheap rectangular prism
    water cooling block onto a dye.

    The order of operations for implementing this print is:
    1. procure a rectangular prism cooling block with side channel nozzles (on the same side)
        (the cheap ones you can find on AliExpress from China)
    2. measure target screw holes on motherboard that are available and near the CPU or dye,
        preferably at least 2 on each half of the block. Measure from center of cooling block
        to each screw.
    3. enter the measurements into the configuration file or pass to this function.
    4. take OpenScad .obj solution and import into slicer; verify the design.
    5. print and fasten your cooling block!

    PARAMETERS:
        rectangle_prism_dimensions: [x,y,z] of sides defining the rect prism.
            This should be the dimensions of the water cooling block since walls
            are additive here
        nozzle_direction: (1,-1) whether the nozzle is facing out on the
            right/left and front/back of the mount. 1s and -1s only.
        wall_thickness: a constant value for wall thickness
        screw_args:
            [{x,y,z,
            screw_head_diameter, screw_bolt_diameter, screw_bolt_depth},]

            positions of each screw's center in xyz coordinates relative
            to the center of the rectangle_prism that defines the mount.

            each screw can be different parameters to target different screws available on
            the motherboard.
            This should allow easy reconfiguration of different cheap cooling
            blocks and motherboards.
    '''
    # TODO: this is a positional implementation of keyword params...
    rectangle_prism_dimensions, nozzle_direction, wall_thickness, screw_args = argv.values()

    # evaluate nested parameters
    rectangle_prism_dimensions = eval(rectangle_prism_dimensions)
    nozzle_direction = eval(nozzle_direction)
    screw_args = eval(screw_args)

    # build the initial mount
    mount_height = rectangle_prism_dimensions[2] + 2*wall_thickness
    inner = cube(rectangle_prism_dimensions, center=True)
    outer = cube(
        [rectangle_prism_dimensions[0] + 2*wall_thickness, rectangle_prism_dimensions[1] + 2*wall_thickness,
         mount_height], center=True)

    # erase an opening face for the nozzles by scrubing over a translation
    opening = translate([nozzle_direction[0]*wall_thickness,
                         nozzle_direction[1]*wall_thickness, 0])(inner)

    mount_hull = outer - hole()(inner)
    # open up the nozzle face
    mount = mount_hull - hole()(opening)
    # drop the bottom out
    mount = mount - hole()(translate([0, 0, -2*wall_thickness])(inner))
    mount = mount - hole()(translate([nozzle_direction[0]*2*wall_thickness,
                                      nozzle_direction[1]*2*wall_thickness, -2*wall_thickness])(inner))
    mount = up(mount_height/2)(mount)
    # TODO: consider a nozzle seperator to prevent sliding out from nozzle end, shouldnt matter
    #       because of the tightness but the engineer in me say do it.
    # TODO: build a splash guard around tubing given nozzle parameters

    # create overpass, pillar, footer and insert for each mounting screw
    for screw in screw_args:
        print('building screw mount: ' + str(screw))
        screw_translate_distance, angle = orient_terminal(screw, False)
        print('rotating this mount point into position with angle: ' +
              str(angle) + '...')
        print('translating this mount point into position with magnitude: ' +
              str(screw_translate_distance))

        # TODO: extract to function since will be using similar for VRM aluminum foil conductors
        # overhang reaches from middle of cooling block to the edge of the screw
        overpass = cube([
            # screw['screw_head_diameter'],
            4*wall_thickness,
            screw_translate_distance,
            4 * wall_thickness], center=True)

        # raise to xy plane
        overpass = up(wall_thickness)(overpass)

        # raise to top of mount
        overpass = up(mount_height)(overpass)

        # shift for rotation
        overpass = forward(screw_translate_distance/2)(overpass)

        # add drop down pillar
        pillar_height = mount_height - screw['z']
        pillar = cube([4 * wall_thickness, 4 * wall_thickness,
                       pillar_height], center=True)

        # gusset increases strength on either side of the screw port
        # TODO: consider a seperate param for wall_thickness or parameterize by screw params
        gusset = cube([wall_thickness/2,
                      2*wall_thickness+screw['screw_head_diameter'], pillar_height], center=True)
        gusset = back(wall_thickness/2)(gusset)

        front_gusset = left(screw['screw_head_diameter']/2 + wall_thickness/4)(gusset)
        back_gusset = right(screw['screw_head_diameter']/2 + wall_thickness/4)(gusset)

        # TODO: just extrude this distance? really large with small hinge
        front_gusset = forward(screw['screw_head_diameter'])(front_gusset)
        back_gusset = forward(screw['screw_head_diameter'])(back_gusset)

        pillar = pillar + front_gusset + back_gusset

        pillar = up(pillar_height/2)(pillar)
        pillar = back(2*wall_thickness)(pillar)
        pillar = forward(screw_translate_distance)(pillar)

        # create the footer with wall_thickness jut to ensure connection to pillar.
        # NOTE: wall thickness here goes into pillar
        footer = cube([screw['screw_head_diameter'], screw['screw_head_diameter']+wall_thickness,
                       screw['screw_bolt_depth']/2], center=True)
        footer = footer - cylinder(r=screw['screw_bolt_diameter']/2,
                                   h=screw['screw_bolt_depth']/2, center=True, segments=200)

        # center to xy plane
        footer = up(screw['screw_bolt_depth']/4)(footer)
        footer = translate(screw['z'])(footer)
        footer = forward(screw_translate_distance +
                         screw['screw_head_diameter']/2)(footer)

        overpass += pillar + footer

        # rotate the solution
        overpass = rotate(angle)(overpass)

        mount += overpass

    return mount


def orient_terminal(screw, toScrew):
    '''
    returns the polar coordinates to the given screw, offset by the screw diameter
    (touching but not over the screw)
    '''
    # TODO: distance is absolute need hypotenuse vector
    # TODO: angle is only for pi/2 to pi in sin function
    angle = atan(screw['x']/screw['y'])

    # TODO: this is only tested for rectangular symmetric screw positions,
    #       on new application look here for bugs.
    if screw['y'] < 0:
        angle += pi

    screw_translate_distance = 1/(sin(angle)/screw['x'])
    if toScrew:
        # using trig funcs not pyth thm for sign
        screw_translate_distance = screw_translate_distance - \
            screw['screw_head_diameter']/2

    return screw_translate_distance, degrees(angle)


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


if __name__ == '__main__':
    config = toml.load("configuration.toml")
    print("raw config: "+str(config))
    mount = mount_side_nozzles(**config)
    # TODO: render this with the exec function that should be refactored into library
    render_object(mount, "mount")
