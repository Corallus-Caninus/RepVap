from turtle import *
from os import walk
# this program draws a picture of the lid using turtle graphics using the configuration.toml file in Nozzle_Array directory
# which is one directory above this one.

# THIS IS AN EXAMPLE OF THE CONFIGUATION FILE
# initial_radius = 94
# final_radius = 135 #was 135
# nozzle_diameter = 2 #0.8
# nozzle_wall_thickness = 1
# drop_down_depth = 8
#
# max_segment_size = 150
# PVC tube inteconnect diameter between nozzle arrays
# tube_diameter = 7.6 # was 8 was 7.8
# thickness of the expanding cone to grip the tube
# pagoda_thickness = 1.5 # was 1.8
#
# wall_thickness = 4.5
# array_spacing = 10
# END OF EXAMPLE
# we will now create an image of the lid with the nozzles on it
# using initial_radius and final_radius to calculate the radius of the lid
# tube_diameter which is the width of each array and the spacing between arrays
# and max_sgment_size which is the maximum size of an array segment


def draw_lid():
    # get the configuration file
    config_file = "configuration.toml"
    config_file_path = "../Nozzle_Array/" + config_file
    with open(config_file_path) as config_file_object:
        config_file_data = config_file_object.read()

    # now use turtle to draw the lid as a circle
    config_file_data = config_file_data.split("\n")
    config_file_data = config_file_data[1:]
    # remove all comments from the yaml file
    for i in range(len(config_file_data)):
        if config_file_data[i].startswith("#"):
            config_file_data[i] = ""
    config_file_data = [i for i in config_file_data if i != ""]
    config_file_data = [line.split("=") for line in config_file_data]
    #remove all characters after #
    for i in range(len(config_file_data)):
        config_file_data[i][1] = config_file_data[i][1].split("#")[0]
    # remove all whitespace characters
    for i in range(len(config_file_data)):
        config_file_data[i][0] = config_file_data[i][0].strip()

    print(config_file_data)
    # turn the configuration file into a dictionary without going out of range
    config_file_data = {line[0]: line[1] for line in config_file_data}

    print(config_file_data)

    # use the final_radius entry to calculate the radius of the lid
    final_radius = float(config_file_data["final_radius"])
    initial_radius = float(config_file_data["initial_radius"])

    #begin turtle graphics
    #first draw the lid as a cirlce
    penup()
    goto(0, -final_radius)
    pendown()
    circle(final_radius)
    penup()
    # now draw each nozzle as an arc