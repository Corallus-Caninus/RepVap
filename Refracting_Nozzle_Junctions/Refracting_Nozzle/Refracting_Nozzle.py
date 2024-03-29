from solid import *
from solid.utils import *
#from ..Junction.Junction import create_junction
from Junction.Junction import create_junction
import os
import toml
from math import *
import random

# TODO: consider vortex emitter if energy requirements aren't too much. also consider vortex emitter with a
#       circular refracting plate for near atomization (is this even better or does it cause too much
#       pressure loss compared to direct emitting against a 'backboard', just offsets the same effect?)


def create_nozzle(junction, junction_params, nozzle_diameter, drop_down_depth,
                  angle_of_attack, insertion_distance, insertion_rotation, insertion_thickness):
    '''
    takes a fully constructed T junction object and 
    nozzle parameters to create a 2 part refracting emitter
    PARAMETERS:
        junction: fully constructed junction object
        nozzle_diameter: diamter of nozzle (relatively macro since refracting)
        drop_down_depth: the distance the refracting cone will span, 
                         is proportional to flex hinge plasticity.
        angle_of_attack: the angle of the cone which will set the cone's base circle radius.
        insertion_distance:
        insertion_rotation:
        insertion_thickness:
    RETURNS:
        nozzle: a fully constructed nozzle
        refracting_plate: a snap on refracting cone for atomizing the 
                          nozzle output with proportional pressure loss 
                          from the nozzle
    '''
    # localize junction_param dictionary items
    wall_thickness = junction_params.get('wall_thickness')
    length = junction_params.get('length')
    junction_diameter = junction_params.get('tube_diameter')

    # orient drop down depth to keep parameters intuitive
    drop_down_depth = -1*drop_down_depth

    # create the nozzle object
    # the nozzle will tap into the junction
    nozzle = cylinder(junction_diameter/2, wall_thickness,
                      center=True, segments=200)
    nozzle = nozzle - hole()(cylinder(nozzle_diameter/2,
                                      wall_thickness, center=True, segments=200))

    # center to z axis
    nozzle = down(wall_thickness/2)(nozzle)

    # join the nozzle object with the junction
    nozzle = down(length)(nozzle)
    nozzle = junction + nozzle

    # create the refracting cone
    cone_width = drop_down_depth*tan(radians(angle_of_attack))
    cone = polygon([
        [0, drop_down_depth],
        [0, 0],
        [cone_width, drop_down_depth]
    ])
    # NOTE: changing segments here may be interesting (pyramid vs cone)
    cone = rotate_extrude(segments=200)(cone)

    # create the snap-on triangular prism joints
    # TODO: goes up too high given length and tube_diameter+2*wall_thickness
    # TODO: test
    poly_joint = polygon([
        [0,                                         drop_down_depth],
        [insertion_thickness,                       drop_down_depth],
        [insertion_thickness,                       length - 2*insertion_thickness],
        [-1*cone_width/2+insertion_thickness+insertion_distance, length - 2*insertion_thickness],
        [-1*cone_width/2+insertion_thickness+insertion_distance, length - insertion_thickness],
        [insertion_thickness,                       length-insertion_thickness],
        [0,                                         length-insertion_thickness],
    ])

    # orient the thin side to the cone to create a
    # secondary refracting surface from the pillars
    poly_joint = left(-1*cone_width/2 + insertion_thickness +
                      insertion_distance)(poly_joint)

    # rotate the polygon to create the snap-ons
    joint = rotate_extrude(insertion_rotation, segments=200)(poly_joint)

    joint = rotate([0, 0, -1*insertion_rotation])(joint)

    # recenter because of weird rotate_extrude
    # joint = right(insertion_thickness/2)(joint)

    # offset by cone base distance (trig calc it) but leave
    # insertion_distance to create insert from nozzle
    # was junction_diameter -> cone_width
    joint = right(cone_width/2+insertion_thickness+insertion_distance)(joint)

    # set random to increase spray distribution wrt other
    # emitters and junction-tubing alignment
    joint = rotate([0, 0, random.randint(0, 120)])(joint)

    # assemble the refracting cone and joints
    refracting_plate = cone + joint
    # create 3 of them for some symmetric stability
    refracting_plate = refracting_plate + rotate([0, 0, 120])(joint)
    refracting_plate = refracting_plate + rotate([0, 0, 240])(joint)

    # move down to align with nozzle
    refracting_plate = down(length+junction_diameter)(refracting_plate)
    # subtract the snap-ons from the nozzle body to create the junction cavities
    nozzle = nozzle - refracting_plate

    # TODO: integrate into one part using tree supports in print, 
    #       increase insertion to rectangle instead of triangle
    return nozzle,  refracting_plate


# TODO: extract this to solid library locally, update Corallus-Caninus fork and push
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
    # peek into junctions configuration
    junction_config = toml.load("../Junction/configuration.toml")
    # load nozzle and refracting plate configuration
    config = toml.load("configuration.toml")

    # build the objects
    junction = create_junction(**junction_config)
    # dont double splat junction_config since we want the dict object
    nozzle, refracting_plate = create_nozzle(
        junction, junction_config, **config)

    # render the object solutions
    render_object(nozzle, "nozzle")
    render_object(refracting_plate, "refracting_plate")
