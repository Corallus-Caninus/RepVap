# NOTE: CURRENTLY DEPRECATED IN FAVOUR OF AQUARIUM PUMPS THAT HAVE FILTERS. IF NOZZLES ARE SMALL ENOUGH TO CLOG CONSIDER THIS IN FUTURE DESIGN.
from solid import *
from solid.utils import *
from math import *
import toml
import os
from multiprocessing import Pool
import multiprocessing
from functools import partial


def Carbon_Filter(pagoda_diameter, pagoda_spacing,
                  pagoda_thickness, pagoda_length, filter_length,
                  filter_diameter, flange_diameter, thread_resolution, thread_span,
                  thread_depth, thread_length, thread_sharpness, thread_count,
                  wall_thickness, num_nozzles):
    '''
        an in-line cylindrical container that is filled with
        activated carbon to filter the water.
        '''
    # TODO: create carbon filter grid to prevent carbon from escaping

    # MAIN HOUSING
    # one wall is for the inner filter shell the other is for the outer filter shell
    filter_upper = cylinder(d=filter_diameter+2*wall_thickness,
                            h=filter_length+2*wall_thickness, center=True)
    filter_lower = cylinder(d=filter_diameter+wall_thickness,
                            h=filter_length+3*wall_thickness, center=True)

    # add a flange to the upper filter shell so it can rest on the container lid
    flange_upper = cylinder(
        d=flange_diameter+filter_diameter, h=wall_thickness, center=True)
    # place flange on top of filter shell
    flange_upper = up(filter_length/2 + wall_thickness/2)(flange_upper)

    # PAGODA NOZZLES
    pagoda_nozzle = cylinder(d=pagoda_diameter+2*wall_thickness,
                             h=2 * pagoda_length, center=True)
    pagoda_orifice = hole()(cylinder(d=pagoda_diameter, h=2 *
                                     pagoda_length + 5 * wall_thickness, center=True))
    pagoda_nozzle = pagoda_nozzle - hole()(pagoda_orifice)

    # add the cone to the upper half of the pagoda nozzles
    cone = polygon(points=[[0, 0], [pagoda_thickness, 0], [0, pagoda_length]])
    cone = right(pagoda_diameter/2 + wall_thickness)(cone)
    cone = rotate_extrude()(cone)

    pagoda_nozzle = cone + pagoda_nozzle

    # now place the nozzles on the filter
    pagoda_total_diameter = pagoda_diameter + 2 * \
        pagoda_thickness + 2*wall_thickness + pagoda_spacing
    filter_radius = filter_diameter/2
    pagoda_total_radius = pagoda_total_diameter/2
    filter_area = pi * filter_radius**2
    pagoda_area = pi * pagoda_total_radius**2

    max_num_nozzles = int(filter_area/pagoda_area)
    max_nozzle_row = int(filter_diameter/pagoda_total_diameter) - 1
    if num_nozzles > 1:
        num_nozzle_rows = int(num_nozzles/max_nozzle_row)
    else:
        num_nozzle_rows = 1
    nozzle_row_angle = int(360/num_nozzle_rows)

    assert num_nozzles <= max_num_nozzles, "num_nozzles must be less than %d" % max_num_nozzles
    if num_nozzle_rows > 1:
        assert num_nozzles % max_nozzle_row == 0, "num_nozzles must be divisible by %d" % max_nozzle_row

    print("num_nozzle_rows is %d" % num_nozzle_rows)
    print("nozzle_row_angle is %d" % nozzle_row_angle)
    print("max_nozzle_row is %d" % max_nozzle_row)

    # create the outlet pagoda nozzles
    filter_pagodas = None
    for n in range(num_nozzle_rows):
        for i in range(max_nozzle_row):
            # for each nozzle, place the nozzles on the filter
            filter_pagoda_nozzle = translate(
                [i*pagoda_total_diameter, 0, 0])(pagoda_nozzle.copy())
            filter_pagoda_nozzle = rotate(
                n*nozzle_row_angle)(filter_pagoda_nozzle)
            # place the nozzle on top of the filter
            filter_pagoda_nozzle = up(
                filter_length/2 + pagoda_length)(filter_pagoda_nozzle)
            print('placing a nozzle on the filter at angle%d' %
                  (n*nozzle_row_angle))
            if filter_pagodas is None:
                filter_pagodas = filter_pagoda_nozzle
            filter_pagodas = filter_pagodas + filter_pagoda_nozzle
    if num_nozzles == 1:
        # just create one nozzle
        filter_pagodas = pagoda_nozzle

    # create a single pagoda for the lower half of the filter
    lower_pagoda = rotate([180, 0, 0])(pagoda_nozzle.copy())
    lower_pagoda = down(filter_length/2 + pagoda_length)(lower_pagoda)

    #THREAD#
    # TODO: allow for more than one twist in thread

    # define a helix as a series of points
    assert thread_depth < wall_thickness / \
        2, "thread_depth must be less or equal to half wall_thickness"
    assert thread_span < filter_length, "thread_span must be less than filter_length"
    assert thread_sharpness < thread_depth, "thread_sharpness must be less than thread_depth"

    helix = []
    helix_itr = thread_resolution/thread_span
    helix = list([[0, 0, i*helix_itr] for i in range(int(thread_span))])

    # create a triangular thread profile
    buttress = [
        [0, 0],
        [0, thread_length],
        [thread_depth, 0],
        [thread_depth, -thread_sharpness],
    ]

    # offset buttress radially from the center of the filter
    buttress = list(map(
        lambda x: [
            x[0] + filter_diameter/2 + wall_thickness/2,
            x[1] + filter_diameter/2 + wall_thickness/2,
        ],
        buttress))

    buttress = polygon(points=buttress)

    # the angle for segment of the helix, this is the resolution of the helix
    helix_angle = (thread_count*360)/thread_resolution

    print("creating thread with path %s" % str(helix))
    print("creating thread with shape %s" % str(buttress))

    # calculate the thread segments arc length
    thread_segment_arclength = sin(radians(helix_angle)) / (filter_diameter/2)
    # calculate the thread pitch given the threads arc length
    thread_pitch = degrees(acos(thread_segment_arclength/thread_length))
    # calculate the height that is to be iterated as the thread is extruded
    # to create the thread angle
    thread_pitch_iter = thread_length/thread_resolution
    thread_extrude_iter = helix_angle/thread_resolution

    print("thread pitch is %fdegrees" % thread_pitch)
    # place each thread along the helix
    thread = None
    for i in range(thread_span):
        # rotate thread_segment to create a segment of the thread with the proper
        # pitch as it twists around the filter
        thread_segment = None
        for j in range(thread_resolution):
            if thread_segment is None:
                thread_segment = up(thread_pitch_iter)(
                    rotate_extrude(thread_extrude_iter)(buttress))
            else:
                thread_segment += up(j*thread_pitch_iter)(
                    rotate(j*thread_extrude_iter)(rotate_extrude(thread_extrude_iter)(buttress)))

        # rotate the thread segment around the z axis for a total of 360 degrees
        cur_thread = rotate(i*helix_angle)(thread_segment)

        # translate the thread segment to the correct location
        cur_thread = translate([0, 0, i*helix_itr/2])(cur_thread)
        # add the thread to the final thread
        if thread is None:
            thread = cur_thread
        else:
            thread = thread + cur_thread

    # move the thread to the bottom of the inner filter
    #thread = translate([0, 0, -filter_length - 2*wall_thickness])(thread)

    # FINAL ASSEMBLY
    # create a inner and outer filter shells joined by the thread
    filter_lower = filter_lower - up(wall_thickness)(cylinder(d=filter_diameter,
                                                              h=filter_length, center=True))

    filter_upper = filter_upper - down(wall_thickness)(cylinder(d=filter_diameter+wall_thickness,
                                                                h=filter_length, center=True))

    # add the pagoda outlets to the upper filter
    filter_upper = filter_upper + filter_pagodas

    # set the thread along the outside of the inner filter shell
    filter_lower = filter_lower + thread

    # add the inlet pagoda to the lower filter
    filter_lower = filter_lower + lower_pagoda

    # remove the top from the lower filter
    filter_lower = filter_lower - up(wall_thickness)(
        cylinder(d=filter_diameter, h=filter_length + 2*wall_thickness, center=True))

    filter_upper = filter_upper - down(wall_thickness)(filter_lower.copy())

    # add the flange to the upper filter
    filter_upper = filter_upper + flange_upper

    # render the outer and inner filter shells seperately
    render_object(filter_lower, "filter_lower")
    render_object(filter_upper, "filter_upper")
    render_object(thread, "thread")

    # return filter + thread


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
              filename + ".stl " + filename + ".scad")


if __name__ == "__main__":
    config = toml.load("configuration.toml")
    Carbon_Filter(**config)
    # carbon_filter = Carbon_Filter(**config)
    # render_object(carbon_filter, "filter")
