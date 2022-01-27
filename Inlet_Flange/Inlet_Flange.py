from solid import *
from solid.utils import *
from math import asin, atan, pi, cos, sin, sqrt, tan, acos
import toml
import os


# TODO: remove the unused parameters once verified and push
def Inlet_Flange(container_top_radius, container_bottom_radius, container_height, fastner_gap, radius, wall_thickness, flange_thickness, groove_spacing):

    outer_flange = None

    outer_flange = cylinder(radius, radius +
                            fastner_gap, center=True, segments=100)
    # TODO: this is 3* here due to centering, should be fine since isnt hole()
    outer_flange_hole = cylinder(radius - wall_thickness, 3*radius +
                                 fastner_gap, center=True, segments=100)
    # we subtract 3 times radius to ensure the sphere elbow is also tapped
    outer_flange = outer_flange - outer_flange_hole

    outer_flange = rotate([0, 90, 90])(outer_flange)
    outer_flange_hole = rotate([0, 90, 90])(outer_flange_hole)
    outer_flange = down(radius)(outer_flange)
    outer_flange_hole = down(radius)(outer_flange_hole)
    outer_flange = forward(radius + fastner_gap/2)(outer_flange)
    outer_flange_hole = forward(radius + fastner_gap/2
                                )(outer_flange_hole)

    # add a outer_cone to the inlet flange
    # TODO: this should be before all movements
    outer_cone = cylinder(h=radius, r1=radius +
                          flange_thickness, r2=radius, segments=100, center=True)
    # now add grooves along the cone the groove
    # goes from the current slope of the cone to radius
    # fastner gap is width of groove
    for i in range(0, ceil(radius/groove_spacing)):
        print(ceil(radius/groove_spacing))
        groove = cylinder(h=fastner_gap, r=radius + flange_thickness,
                          segments=100, center=True)
        groove = groove - cylinder(h=fastner_gap,
                                   r=radius, segments=100, center=True)
        groove = down((fastner_gap)/2)(groove)
        # now move it along the cone and subtract it from the cone
        groove = translate([0, 0, (i-1)*groove_spacing])(groove)
        outer_cone = outer_cone - groove

    outer_cone = rotate([0, 90, 90])(outer_cone)
    outer_cone = forward(radius)(outer_cone)
    outer_cone = down(radius)(outer_cone)
    outer_cone = outer_cone - forward(radius)(outer_flange_hole)
    outer_cone = outer_cone - outer_flange_hole
    outer_flange += outer_cone

    # rotate this by 45 degrees
    intake = cylinder(radius, radius, center=True, segments=100)
    intake_hole = cylinder(radius-wall_thickness, 3*radius + 2 *
                           wall_thickness, center=True, segments=100)
    intake = intake - intake_hole
    outer_flange += back(radius)(rotate([45, 0, 0])(intake))
    intake_hole = back(radius)(rotate([45, 0, 0])(intake_hole))

    outer_flange = outer_flange - intake_hole

    # now joined the to inlet flanges what a sphere
    catch = sphere(radius + wall_thickness)
    catch = down(radius)(catch)
    catch = catch - outer_flange_hole
    catch = catch - intake_hole

    outer_flange = outer_flange + catch

    return outer_flange


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
              filename + ".stl " + filename + ".scad &")


if __name__ == "__main__":
    config = toml.load("configuration.toml")
    outer = Inlet_Flange(**config)
    render_object(outer, "outer_flange")
