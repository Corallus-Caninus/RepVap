from solid import *
from solid.utils import *
from math import asin, atan, pi, cos, sin, sqrt, tan, acos
import toml
import os


def Inlet_Flange(container_top_radius, container_bottom_radius, container_height, fastner_gap, radius, tab_width, tab_length, tab_thickness, tab_angle, num_tabs, wall_thickness, flange_thickness):

    outer_flange = None

    # TODO: these are unused
    # create the negation solutions
    # This is for scrubbing
    negate = cube((radius+wall_thickness)*2, center=True)
    # The simulated container
    container = cylinder(r1=container_top_radius, r2=container_bottom_radius, h=container_height,
                         center=True, segments=100)

    def container_slope_offset(height):
        '''return the radius for the given height of the container outer_cone'''
        # first write the line equation
        # y2 - y1 = m(x2 - x1) where y2 is the container top radius and y1 is the container bottom radius
        # then solve for the radius: radius = y1 - m(x1)
        slope = (container_top_radius - container_bottom_radius) / container_height
        offset = container_bottom_radius - slope * container_height
        return slope * height + offset
    # TODO: End of unused code

    # The amount of loss needed to smoothly flex the tabs
    # TODO: print out radius loss so users can calculate the
    #       number of inlets needed to equate fan diameter for
    #       venturi equivalence (no pressure loss)
    radius_loss = tab_width*cos(radians(tab_angle))
    # now consider the thickness component of the loss
    # TODO: verify this is correct
    # I actually like this as it snaps the flextular joint further onto the inlet
    # but if you want to be the best kind of correct uncomment the following:
    # radius_loss += tab_thickness*sin(radians(tab_angle))/2
    print(f'radius loss: {radius_loss} mm')
    # tell the user what their intake radius is
    print(
        f'total intake area (air flow constrain): {((radius - radius_loss)**2) *pi} mm^2')

    # now we are ready to build the inlet flange
    outer_flange = cylinder(radius - radius_loss, 3*radius +
                            fastner_gap, center=True, segments=100)
    outer_flange_hole = cylinder(radius-radius_loss-wall_thickness, 3 *
                                 radius + fastner_gap, center=True, segments=100)
    # we subtract 3 times radius to ensure the sphere elbow is also tapped
    outer_flange = outer_flange - outer_flange_hole

    # add tabs that flex to hold the flange to the container along the outer_flange
    # past the gap distance
    tab = cube([tab_width, tab_length, tab_thickness], center=True)
    tab = up(tab_width*sin(radians(tab_angle))/2)(rotate([0, -tab_angle, 0])(tab))
    tab = left(tab_width*cos(radians(tab_angle))/2)(tab)

    tab_spacing = tab_width*sin(radians(tab_angle))
    print(f'tab spacing: {tab_spacing}')
    row_tabs = int(radius // tab_spacing)

    tab_angle = 360/num_tabs
    print(f'tab angle: {tab_angle}')
    for i in range(0, row_tabs):
        iter_tab = translate([-radius + radius_loss, 0, i*tab_spacing +
                              0.5*radius + fastner_gap/2])(tab)
        for j in range(0, num_tabs):
            rot_tab = rotate(j*tab_angle)(iter_tab)

            outer_flange = outer_flange + rot_tab

    outer_flange = rotate([0, 90, 90])(outer_flange)
    outer_flange_hole = rotate([0, 90, 90])(outer_flange_hole)
    outer_flange = down(radius)(outer_flange)
    outer_flange_hole = down(radius)(outer_flange_hole)
    outer_flange = forward(radius + fastner_gap/2)(outer_flange)
    outer_flange_hole = forward(radius + fastner_gap/2
                                )(outer_flange_hole)

    # add a outer_cone to the inlet flange
    outer_cone = cylinder(h=radius, r1=radius +
                          flange_thickness, r2=radius, segments=100, center=True)
    outer_cone = rotate([0, 90, 90])(outer_cone)
    outer_cone = forward(radius)(outer_cone)
    outer_cone = down(radius)(outer_cone)
    outer_cone = outer_cone - forward(radius)(outer_flange_hole)
    outer_cone = outer_cone - outer_flange_hole
    outer_flange += outer_cone

    # rotate this by forty five degrees
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
