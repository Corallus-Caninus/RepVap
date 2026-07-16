from solid import *
from solid.utils import *
from math import asin, atan, pi, cos, sin, sqrt, tan, acos
import toml
import os


def Inlet(
    fastner_gap,
    radius,
    wall_thickness,
    thickness,
    groove_spacing,
):
    outer = None

    outer = cylinder(radius, 2 * (radius + fastner_gap) + 6 * wall_thickness, center=True, segments=100)
    # TODO: this is 3* here due to centering, should be fine since isnt hole() but
    #       look here when bugs arise from differing configurations
    outer_hole = cylinder(
        radius - wall_thickness, 3 * radius + fastner_gap + 4 * wall_thickness, center=True, segments=100
    )
    # we subtract 3 times radius to ensure the sphere elbow is also tapped
    outer = outer - outer_hole

    outer = rotate([0, 90, 90])(outer)
    outer_hole = rotate([0, 90, 90])(outer_hole)
    outer = down(radius)(outer)
    outer_hole = down(radius)(outer_hole)
    outer = forward(1.5 * radius + fastner_gap)(outer)
    outer_hole = forward(1.5 * radius + fastner_gap)(outer_hole)

    # add a outer_cone to the inlet
    # TODO: this should be before all movements
    outer_cone = cylinder(
        h=radius, r1=radius + thickness, r2=radius, segments=100, center=True
    )
    # now add grooves along the cone the groove
    # goes from the current slope of the cone to radius
    # fastner gap is width of groove
    for i in range(0, ceil(radius / groove_spacing)):
        print(ceil(radius / groove_spacing))
        groove = cylinder(
            h=fastner_gap, r=radius + thickness, segments=100, center=True
        )
        groove = groove - cylinder(h=fastner_gap, r=radius, segments=100, center=True)
        groove = down((fastner_gap) / 2)(groove)
        # now move it along the cone and subtract it from the cone
        groove = translate([0, 0, (i - 1) * groove_spacing])(groove)
        outer_cone = outer_cone - groove

    outer_cone = rotate([0, 90, 90])(outer_cone)
    outer_cone = forward(radius)(outer_cone)
    outer_cone = down(radius)(outer_cone)
    outer_cone = outer_cone - forward(radius)(outer_hole)
    outer_cone = outer_cone - outer_hole
    outer += outer_cone

    # rotate this by 45 degrees
    intake = cylinder(radius, radius, center=True, segments=100)
    intake_hole_cyl = cylinder(
        radius - wall_thickness,
        3 * radius + 2 * wall_thickness,
        center=True,
        segments=100,
    )
    intake = intake - intake_hole_cyl
    intake_pos = back(radius)(rotate([45, 0, 0])(intake))
    intake_hole_pos = back(radius)(rotate([45, 0, 0])(intake_hole_cyl))
    outer += intake_pos
    outer -= intake_hole_pos

    # cap the far end of the extended outer body with wall_thickness
    cap = cylinder(radius, wall_thickness, center=True, segments=100)
    cap = rotate([0, 90, 90])(cap)
    cap = down(radius)(cap)
    cap = forward(1.5 * radius + fastner_gap)(cap)
    cap = forward(radius + fastner_gap + 5 * wall_thickness / 2)(cap)
    outer += cap

    # air vent: same radius as the initial inlet hole, through just the bottom wall
    vent = cylinder(radius - wall_thickness, radius, center=True, segments=100)
    vent = forward(2 * radius + 1.5 * fastner_gap + wall_thickness)(vent)
    vent = down(2 * radius - wall_thickness / 2)(vent)
    outer -= vent

    catch = sphere(radius + wall_thickness)
    catch = down(radius)(catch)
    catch = catch - outer_hole
    catch = catch - intake_hole_pos

    outer = outer + catch

    return outer


def render_object(render_object, filename):
    """
    creates a .stl and .scad solution for the given solidpython OpenSCAD object
    PARAMETERS:
        render_object: the OpenSCAD object
        filename: a string for the file to be saved
    """
    scad_render_to_file(render_object, filename + ".scad", file_header="$fn=200;")
    # render with OpenSCAD
    print("Openscad is now rendering the solution..")
    os.system("openscad -o " + filename + ".stl " + filename + ".scad &")


if __name__ == "__main__":
    config = toml.load("configuration.toml")
    outer = Inlet(**config)
    render_object(outer, "inlet")
