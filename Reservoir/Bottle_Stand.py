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
    orifice = orifice_solid - cylinder(r=bottle_diameter /
                                       2, h=bottle_depth, center=True)
    # raise orifice to leg stand height
    orifice = up(leg_height+bottle_depth/2)(orifice)

    # the cusp of the nozzle holder
    throat_solid = cylinder(r1=nozzle_diameter/2 + wall_thickness,
                            r2=bottle_diameter/2 + wall_thickness, h=nozzle_depth, center=True)
    # hole here since legs may jut
    throat = throat_solid - cylinder(r1=nozzle_diameter/2,
                                     r2=bottle_diameter/2, h=nozzle_depth, center=True)
    throat = up(leg_height-nozzle_depth/2)(throat)

    # create tripod base
    # a synthetic "floor" for ensuring legs are level through subtraction.
    base_plate = cube([2*leg_height+bottle_diameter, 2*leg_height+bottle_diameter,
                       2*wall_thickness], center=True)
    rotation_offset_x = leg_height*sin(radians(leg_camber))
    rotation_offset_y = leg_height*cos(radians(leg_camber))
    # solve the intersection of the leg with the orifice penetrating wall_thickness
    screw_insert_distance = 4*wall_thickness*tan(radians(leg_camber))
    leg = cylinder(r=wall_thickness, h=leg_height +
                   screw_insert_distance, center=True)
    # TODO: adjust screw params for precision of print, possibly extract parameter
    section = screw_thread.default_thread_section(
        tooth_height=2*wall_thickness, tooth_depth=wall_thickness)
    # NOTE: pitch is 1 full screw rotation here divid for freq
    # TODO: -0.1 to patch seam artifact isnt good much bad.
    leg_screw = screw_thread.thread(outline_pts=section,
                                    inner_rad=wall_thickness-0.1,
                                    pitch=screw_insert_distance,
                                    length=screw_insert_distance,
                                    segments_per_rot=1000,
                                    neck_in_degrees=90,
                                    neck_out_degrees=90)
    leg = leg+up(leg_height/2 - screw_insert_distance/2)(leg_screw)
    leg = rotate([0, -leg_camber, 0])(up(leg_height /
                                         2+screw_insert_distance/2)(leg))
    leg = leg - hole()(base_plate)
    legs = right(rotation_offset_x + bottle_diameter/2)(leg)
    legs += rotate(120)(legs)
    legs += rotate(240)(legs)

    stand = orifice + throat
    stand = stand - legs
    return stand, leg


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
    stand, leg = bottle_stand(**config)
    render_object(stand, "bottle_stand")
    render_object(leg, "x3_bottle_stand_leg")
