from solid import *
from solid.utils import *
from math import asin, atan, pi, cos, sin, sqrt, tan, acos
import toml
import os

eps = 1  # epsilon for hollow cone artifacts

"""a nozzle on either end of a hollow cylinder to couple two hoses of different diameter"""


def Coupler(
    out_tube_diameter,
    in_tube_diameter,
    in_tube_cone_diameter,
    out_tube_cone_diameter,
    in_tube_cone_height,
    out_tube_cone_height,
    coupler_length,
    wall_thickness,
):
    # COUPLER #
    coupler = cylinder(
        r1=out_tube_diameter / 2 + wall_thickness,
        r2=in_tube_diameter / 2 + wall_thickness,
        h=coupler_length,
        center=True,
    )
    # make a hole through the coupler
    coupler = coupler - hole()(
        cylinder(
            r1=out_tube_diameter / 2,
            r2=in_tube_diameter / 2,
            h=coupler_length,
            center=True,
        )
    )

    in_cone = cylinder(
        r1=in_tube_cone_diameter / 2 + eps,
        r2=in_tube_diameter / 2 + eps,
        h=in_tube_cone_height,
        center=True,
    )
    in_tube = cylinder(
        r=in_tube_diameter / 2 + wall_thickness,
        h=in_tube_cone_height,
        center=True,
    )
    in_cone = in_cone - hole()(
        cylinder(r=in_tube_diameter / 2, h=in_tube_cone_height, center=True)
    )
    in_cone = translate([0, 0, in_tube_cone_height])(in_cone)

    # now tap a hole through both the cone and the tube
    in_tube = in_tube - hole()(
        cylinder(r=in_tube_diameter / 2, h=in_tube_cone_height, center=True)
    )
    in_cone = in_cone + in_tube

    out_cone = cylinder(
        r1=out_tube_diameter / 2 + eps,
        r2=out_tube_cone_diameter / 2 + eps,
        h=out_tube_cone_height,
        center=True,
    )
    out_tube = cylinder(
        r=out_tube_diameter / 2 + wall_thickness,
        h=out_tube_cone_height,
        center=True,
    )
    out_cone = out_cone - hole()(
        cylinder(r=out_tube_diameter / 2, h=out_tube_cone_height, center=True)
    )
    out_cone = translate([0, 0, -out_tube_cone_height])(out_cone)
    # now tap a hole through both the cone and the tube
    out_tube = out_tube - hole()(
        cylinder(r=out_tube_diameter / 2, h=out_tube_cone_height, center=True)
    )
    out_cone = out_cone + out_tube

    in_cone = translate([0, 0, coupler_length / 2 + in_tube_cone_height / 2])(in_cone)
    out_cone = translate([0, 0, -coupler_length / 2 - out_tube_cone_height / 2])(
        out_cone
    )

    coupler = coupler + in_cone + out_cone
    return coupler


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
    coupler = Coupler(**config)
    render_object(coupler, "coupler")
