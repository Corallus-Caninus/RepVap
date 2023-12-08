# TODO: consider a brita filter as a mount since corrosion seems negligable
#       as long as chlorine bumps off and minerals/metals are filtered.
#       open loop will corrode a bit anyways but shouldnt change conductive
#       property of aluminum.
#       this isnt unreasonable given 100% infill with large wall_thickness.
#       can just insert brita filter in a 3D printed stand.
#       can use arduino for filter life measurement using the flap button
#       method of brita
# TODO: consider an RGB fade color for water height when arduino
#       circuit is developed.
from solid import *
from solid.utils import *
from solid import screw_thread
from math import sin, cos, tan
import toml
import os

# This is currently the highest priority print.


def bottle_stand(leg_height, leg_camber, wall_thickness, nozzle_diameter, nozzle_depth,
                 bottle_diameter, bottle_depth):
    '''
    PARAMETERS:
        leg_height: the height of the riser legs
        leg_camber: the tilt of the leg to lower the center of mass in degrees
        wall_thickness: the general thickness of the solution
        bottle_diameter: the diameter of the bottle body past the nozzle
        bottle_depth: the length of the bottle nozzle until the bottle body
    '''
    # create bottle holder
    orifice_solid = cylinder(r=bottle_diameter/2 + wall_thickness,
                             h=bottle_depth, center=True)
    # hole here since legs may jut
    orifice = orifice_solid - hole()(cylinder(r=bottle_diameter /
                                              2, h=bottle_depth, center=True))
    # raise orifice to leg stand height
    orifice = up(leg_height+bottle_depth/2)(orifice)

    # the cusp of the nozzle holder
    throat_solid = cylinder(r1=nozzle_diameter/2 + wall_thickness,
                            r2=bottle_diameter/2 + wall_thickness, h=nozzle_depth, center=True)
    # hole here since legs may jut
    throat = throat_solid - hole()(cylinder(r1=nozzle_diameter/2,
                                            r2=bottle_diameter/2, h=nozzle_depth, center=True))
    throat = up(leg_height-nozzle_depth/2)(throat)

    # create tripod base
    # a synthetic "floor" for ensuring legs are level through subtraction.
    base_plate = cube([2*leg_height+bottle_diameter, 2*leg_height+bottle_diameter,
                       2*wall_thickness], center=True)
    rotation_offset_x = leg_height*sin(radians(leg_camber))
    rotation_offset_y = leg_height*cos(radians(leg_camber))
    # solve the intersection of the leg with the orifice penetrating wall_thickness
    leg = cylinder(r=wall_thickness, h=leg_height +
                   wall_thickness, center=True)
    leg = rotate([0, -leg_camber, 0])(up(leg_height /
                                         2+wall_thickness)(leg))
    leg = leg - hole()(base_plate)
    legs = right(rotation_offset_x + bottle_diameter/2)(leg)
    legs += rotate(120)(legs)
    legs += rotate(240)(legs)

    # create a hook along the orifice used to loop the tubing around
    # TODO: this isn't necessary at the moment since the tubing has to 
    #       go up and into the gutter in the same siphoning twist.
    hook_solid = cylinder(r=wall_thickness, h=leg_height +
                          wall_thickness, center=True)
    hook_solid = rotate([0, -leg_camber, 0])(up(leg_height /
                                                2+wall_thickness)(hook_solid))
    hook_solid = hook_solid - hole()(base_plate)
    hook = right(rotation_offset_x + bottle_diameter/2)(hook_solid)
    hook += rotate(120)(hook)
    hook += rotate(240)(hook)

    stand = orifice + throat + legs
    return stand


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
    os.system("openscad -o " +
              filename + ".stl " + filename + ".scad")


if __name__ == '__main__':
    config = toml.load("configuration.toml")
    stand = bottle_stand(**config)
    render_object(stand, "bottle_stand")
