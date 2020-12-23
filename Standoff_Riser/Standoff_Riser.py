from solid import *
from solid.utils import *
import toml

# TODO: also allow tilting the riser for diagonal mounting (test bench style)


def create_riser(riser_diameter, riser_height, fraction_depth,
                 screw_diameter, screw_bolt_diameter, screw_bolt_length):
    '''
    creates a standoff riser from screw argument and diameter. 
    Just a cylinder with a screw inlet.

    riser_diameter and screw_diameter determine the wall width of the riser

    fraction_depth determines what percentage of the screw is used for 
    the stand. the rest is used for threading the screw into its receptacle. 
    '''

    # create the terminal that will hold the screw
    terminal_solid = cylinder(r=screw_bolt_diameter/2,
                              h=screw_bolt_length/fraction_depth, center=True)
    terminal = terminal_solid - hole()(cylinder(r=screw_bolt_diameter/2,
                                                h=screw_bolt_length/fraction_depth, center=True))

    # create a footer that offsets the terminal slot from the riser
    terminal = left(screw_diameter)(terminal)

    # create the riser
    riser = cylinder(r=riser_diameter/2, h=riser_height)

    # join the riser to the footer solution
    # TODO: was hull TEST AND CLOSE
    # TODO: ensure minkowski:
    #       1. retains screw_diameter 
    #       2. connects without too much structure loss in param sweep
    riser = minkowski()(riser + terminal)

    return riser


if __name__ == '__main__':
    config = toml.load('configuration.toml')
    riser = create_riser(**config)
    scad_render_to_file(riser, "standoff_riser")
