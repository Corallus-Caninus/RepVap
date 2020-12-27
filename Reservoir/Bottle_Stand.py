# TODO: Stand for holding a 2-liter type bottle upside down next to Bucket
# TODO: consider a brita filter as a mount since corrosion seems negligable
#       as long as chlorine bumps off and minerals/metals are filtered.
#       open loop will corrode a bit anyways but shouldnt change conductive
#       property of aluminum.
# TODO: this isnt unreasonable given 100% infill with large wall_thickness.
#       can just insert brita filter in a 3D printed stand.
#       can use arduino for filter life measurement using the flap button
#       method of brita
# TODO: make legs with flex hinges so they can be printed seperately.
from solid import *
from solid.utils import *
import toml
import os


def bottle_stand(leg_height, leg_camber, wall_thickness, bottle_diameter, bottle_depth):
    '''
    PARAMETERS:
        leg_height: the height of the riser legs
        leg_camber: the tilt of the leg to lower the center of mass in degrees
        wall_thickness: the general thickness of the solution
        bottle_diameter: the diameter of the bottle body past the nozzle
        bottle_depth: the length of the bottle nozzle until the bottle body
    '''
    # create tripod base
    # TODO: do the trig on right offset given camber
    leg = rotate([0, -leg_camber, 0])(translate([bottle_diameter/2, 0, leg_height/2])(
        cylinder(r=wall_thickness, h=leg_height, center=True)))
    leg += rotate(120)(leg)
    leg += rotate(240)(leg)

    # a synthetic "floor" for ensuring legs are level through subtraction.
    base_plate = cube([2*leg_height, 2*leg_height,
                       2*wall_thickness], center=True)
    leg = leg - hole()(base_plate)

    orifice_solid = cylinder(r=bottle_diameter/2 + wall_thickness,
                             h=bottle_depth, center=True)
    orifice = orifice_solid - hole()(cylinder(r=bottle_diameter /
                                              2, h=bottle_depth, center=True))
    orifice = up(leg_height+bottle_depth/2)(orifice)

    # the cusp of the nozzle holder
    throat_solid = cylinder(r1=,r2=,h=,center=True)

    stand = leg + orifice
    return stand


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
    stand = bottle_stand(**config)
    render_object(stand, "bottle_stand")
