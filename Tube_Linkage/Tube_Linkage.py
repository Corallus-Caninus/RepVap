# ball and socket cylinders that snap fit together to protect
# wiring/tubing from chicken wire in a space efficient way
from solid import *
from solid.utils import *
import toml
import os


def tube_linkage(radius, height, wall_thickness, space_width, space_height):
    # create the main linkage body
    linkage = cylinder(radius+wall_thickness, height, center=True)
    tube = cylinder(radius, height, center=True)
    linkage = linkage - hole()(tube)

    # create the hinge on either end so ball can socket
    socket = cube([2*wall_thickness, space_width, space_height], center=True)
    socket = right(radius)(socket)  # move over wall
    socket += rotate(120)(socket) + rotate(240)(socket)
    socket = down(height/2 - space_height/2)(socket) + \
        up(height/2 - space_height/2)(socket)

    linkage = linkage - hole()(socket)

    # TODO: socket should be on both sides for increased flexibility
    # now affix the ball joint on the top
    ball = sphere(radius+wall_thickness)
    ball = ball - hole()(cylinder(radius, 4*radius, center=True))
    ball = up(height+radius/2)(ball)

    return linkage, ball


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


if __name__ == "__main__":
    config = toml.load("configuration.toml")
    linkage, ball = tube_linkage(**config)
    render_object(linkage, "linkage")
    render_object(ball, "ball")
