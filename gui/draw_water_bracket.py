# draw the water bracket with turtle
import turtle
import os
import math

from solid.utils import screw
# this is the water bracket configuration
# rectangle_prism_dimensions = "[43, 43, 10]"
# # can be (1,0) (0,-1) etc. avoid diagonal: (-1, 1)
# nozzle_direction =  "(-1,0)"
# wall_thickness = 2

# # SCREW MOBO MEASUREMENTS #
# screw_args = '''
# [
# {"x": 84, "y": -33, "z": 0, "screw_head_diameter": 4.45, "screw_bolt_diameter": 2,"screw_bolt_depth":  2.4},
# {"x": -29.5, "y": 16.28, "z": 0, "screw_head_diameter": 4, "screw_bolt_diameter": 2,"screw_bolt_depth":  1.7},
# {"x": -29.5, "y": -16.28, "z": 0, "screw_head_diameter": 4, "screw_bolt_diameter": 2,"screw_bolt_depth":  1.7},
# ]'''
# end of water bracket configuration

# TODO just draw this and lid in the same window

def draw_water_bracket():
    # this is the start of the code
    # create the turtle screen
    wn = turtle.Screen()
    # set the background color
    wn.bgcolor("black")
    # set the window title
    wn.title("Water bracket")
    # set the window size
    wn.setup(1280, 800)
    # read in the water bracket dimensions from the configuration file
    with open("../Water_Bracket/configuration.toml") as f:
        content = f.readlines()
        # remove all comments
        content = [x.strip() for x in content]
        content = [x for x in content if x and not x.startswith("#")]
        # remove all whitespace
        content = [x.strip() for x in content]
        # remove the key and equal sign

        # read in rectangle_prism_dimensions as an array using eval and cast to a list
        # just get the value after the equal sign
        rectangle_prism_dimensions = content[0].split("=")[1]
        rectangle_prism_dimensions = eval(rectangle_prism_dimensions)
        # cast it to a list of floats and remove the brackets from the begining and end
        rectangle_prism_dimensions = [
            float(x) for x in rectangle_prism_dimensions[1:-1].split(",")]

        # read in nozzle_direction as a tuple using eval
        # just get the value after the equal sign
        nozzle_direction = content[1].split("=")[1]
        nozzle_direction = eval(nozzle_direction)
        # read in wall_thickness as a float using eval
        # just get the value after the equal sign
        wall_thickness = content[2].split("=")[1]
        wall_thickness = eval(wall_thickness)

        # read in screw_args as a list using eval
        screw_args = str(content[3:])
        # remove all whitespace
        screw_args = [x.strip() for x in screw_args]
        # remove all forward and backwards slashes
        screw_args = [x.replace("/", "") for x in screw_args]
        screw_args = [x.replace("\\", "") for x in screw_args]
        print("got screw_args:" + str(screw_args))
        # remove all brackets
        screw_args = [x.replace("[", "") for x in screw_args]
        screw_args = [x.replace("]", "") for x in screw_args]
        # remove all quotes
        screw_args = [x.replace("'", "") for x in screw_args]
        # flatten the string to be one long string
        screw_args = "".join(screw_args)
        # only get the values after the equals sign
        screw_args = screw_args.split("=")[1]
        # split each dictionary entry
        screw_args = screw_args.split(",")
        # remove all entries that are empty
        screw_args = [x for x in screw_args if x]
        # remove all entries that are single or double quotes
        screw_args = [x for x in screw_args if x != "'" and x != '"']
        # join all entries in each dictionary to be a single string but keep the comma and add brackets to the start and end of the string
        screw_args = "[" + ",".join(screw_args) + "]"
        # remove the last entry which is a quote
        print("got screw_args:" + str(screw_args))
        # convert to a list of strings
        screw_args = eval(screw_args)
        # remove empty entries
        screw_args = [x for x in screw_args if x]
        print("got screw_args:" + str(screw_args))


    # draw the recangular prism and each screw in 3 dimensions and connect 
    # the screws to the center of the rectanglular prism with one line each
    #with turtle
    # draw the rectangular prism
    turtle.penup()
    #set the pen color to white
    turtle.color("white")
    turtle.goto(0, 0)
    turtle.pendown()
    turtle.goto(rectangle_prism_dimensions[0], 0)
    turtle.goto(rectangle_prism_dimensions[0], rectangle_prism_dimensions[1])
    turtle.goto(0, rectangle_prism_dimensions[1])
    turtle.goto(0, 0)
    # draw the screws
    for screw in screw_args:
        #draw a line to the screw from the center of the rectangular prism
        # get the x and y coordinates of the screw from the dictionary
        x = screw["x"]
        y = screw["y"]
        # get the z coordinate of the screw from the dictionary
        z = screw["z"]
        # get the screw head diameter from the dictionary
        screw_head_diameter = screw["screw_head_diameter"]
        # get the screw bolt diameter from the dictionary
        screw_bolt_diameter = screw["screw_bolt_diameter"]
        # get the screw bolt depth from the dictionary
        screw_bolt_depth = screw["screw_bolt_depth"]
        # draw the screw head
        turtle.penup()
        turtle.goto(x, y)
        turtle.pendown()
        turtle.circle(screw_head_diameter / 2)
        # draw the screw bolt
        turtle.penup()
        turtle.goto(x, y)
        turtle.pendown()
        turtle.circle(screw_bolt_diameter / 2)
        # draw the screw bolt
        turtle.penup()
        turtle.goto(x, y)
        turtle.pendown()
        turtle.circle(screw_bolt_depth / 2)
        # connect the screw to the rectangular prism with a line
        turtle.penup()
        turtle.goto(rectangle_prism_dimensions[0] / 2,
                    rectangle_prism_dimensions[1] / 2)
        turtle.pendown()
        turtle.goto(x, y)
    #finish
    turtle.hideturtle()