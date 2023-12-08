from solid import *
from solid.utils import *
import toml
import os


def create_junction(isCross, tube_diameter, wall_thickness, length):
    '''
    creates a T or + junction for putting sequences of nozzles 
    in parallel or general plumbing and a psuedo inline distribution block. 
    walls are subtractive for tube fitting (constrains flow, losses pressure)
    '''

    pipe = cylinder(tube_diameter/2, length, center=True, segments=200)
    hull = cylinder(tube_diameter/2, length, center=True, segments=200)
    # cut holes
    pipe = pipe - hole()(cylinder(tube_diameter/2-wall_thickness,
                                  length, center=True, segments=200))
    hull = hull - hole()(cylinder(tube_diameter/2-wall_thickness,
                                  length, center=True, segments=200))

    # center about z axis
    pipe = down(length/2)(pipe)  # center about z axii
    hull = down(length/2)(hull)  # center about z axii

    # TODO: cut holes

    # offset pipe for junctions
    pipe = translate([0, 0, length])(pipe)

    if isCross:
        for i in range(3):
            hull += rotate([0, i*90, 0])(pipe)
    else:
        for i in range(4):
            hull += rotate([0, i*90, 0])(pipe)

    # TODO: ensure rotations are about the xy plane since nozzles
    #       tap along z axis and this is sensible
    hull = rotate([90, 90, 90])(hull)
    return hull


if __name__ == "__main__":
    # read in configuration
    config = toml.load("configuration.toml")
    filename = "junction"
    # write out the solution
    junction = create_junction(**config)
    scad_render_to_file(junction, filename + ".scad")
    # render with OpenSCAD
    print("Openscad is now rendering the solution..")
    os.system("start ../OpenSCAD/openscad.exe -o " +
              filename + ".stl " + filename + ".scad")
