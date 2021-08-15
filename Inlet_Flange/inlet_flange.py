from solid import *
from solid.utils import *
from math import asin, atan, pi, cos, sin, sqrt, tan, acos
import toml
import os


def threading(thread_length, thread_depth, radius, thread_count, thread_span, thread_resolution):
    '''
     create a thread of length thread span that twists thread count complete
     revolutions along that axis using profile as the profile of the thread that
     is extruded using rotate extrude.
    '''
    profile = [
        Point2(0, thread_length),
        Point2(thread_depth, 0),
        Point2(0, 0),
    ]
    profile = left(radius)(polygon(points=profile))
    total_angle = 360*thread_count
    segment_distance = thread_span/(thread_resolution)
    angle_iter_axis = degrees(atan(segment_distance/radius))
    angle_iter_helix = total_angle/thread_resolution
    # print the thread variables we just created
    print("angle_iter_axis: " + str(angle_iter_axis))
    print("angle_iter_helix: " + str(angle_iter_helix))
    #  create the thread profile
    segment = rotate_extrude(angle_iter_helix)(profile)
    thread = segment
    for i in range(thread_resolution):
        thread += up(i*segment_distance)(rotate(i * angle_iter_helix)(segment))
    return thread


def Inlet_Flange(container_top_radius, container_bottom_radius, container_height, guard_height, fastner_gap, radius, thread_resolution, thread_count, thread_span, thread_depth, thread_length, wall_thickness, flange_thickness):
    inlet_flange = None
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
        # then solve for the radius
        # radius = y1 - m(x1)
        slope = (container_top_radius - container_bottom_radius) / container_height
        offset = container_bottom_radius - slope * container_height
        return slope * height + offset
        # return slope * height
    container_radius = container_slope_offset(guard_height)
    # calculate the container angle at guard height
    container_angle = degrees(asin(container_radius / container_height))
    # print the container metrics
    print(f'container top radius: {container_top_radius}')
    print(f'container bottom radius: {container_bottom_radius}')
    print(f'container height: {container_height}')
    print(f'container radius: {container_radius}')
    print(f'container angle: {container_angle}')

    # now we are ready to build the inlet flange
    inlet_flange = cylinder(radius, 3*radius +
                            fastner_gap, center=True, segments=100)
    inlet_flange_hole = cylinder(radius-wall_thickness, 3 *
                                 radius + fastner_gap, center=True, segments=100)
    # we subtract 3 times radius to ensure the sphere elbow is also tapped
    inlet_flange = inlet_flange - inlet_flange_hole

    inlet_flange = rotate([0, 90, 90])(inlet_flange)
    inlet_flange_hole = rotate([0, 90, 90])(inlet_flange_hole)
    inlet_flange = down(radius)(inlet_flange)
    inlet_flange_hole = down(radius)(inlet_flange_hole)
    inlet_flange = forward(radius + fastner_gap)(inlet_flange)
    inlet_flange_hole = forward(radius + fastner_gap
                                )(inlet_flange_hole)

    # add a outer_cone to the inlet flange
    outer_cone = cylinder(h=radius, r1=radius +
                          flange_thickness, r2=radius, segments=100, center=True)
    outer_cone = rotate([0, 90, 90])(outer_cone)
    outer_cone = forward(radius)(outer_cone)
    outer_cone = down(radius)(outer_cone)
    outer_cone = outer_cone - forward(radius)(inlet_flange_hole)
    outer_cone = outer_cone - inlet_flange_hole
    inlet_flange += outer_cone

    # rotate this by forty five degrees
    intake = cylinder(radius, radius, center=True, segments=100)
    intake_hole = cylinder(radius-wall_thickness, 3*radius + 2 *
                           wall_thickness, center=True, segments=100)
    intake = intake - intake_hole
    inlet_flange += back(radius)(rotate([45, 0, 0])(intake))
    intake_hole = back(radius)(rotate([45, 0, 0])(intake_hole))

    inlet_flange = inlet_flange - intake_hole
    # intake = intake - inlet_flange_hole

    # now joined the to inlet flanges what a sphere
    catch = sphere(radius + wall_thickness)
    # catch = back(radius/2)(catch)
    catch = down(radius)(catch)
    # catch = catch - down(-radius/2)(back(-radius/2)(inlet_flange_hole))
    catch = catch - inlet_flange_hole
    catch = catch - intake_hole

    inlet_flange = inlet_flange + catch

    # create the bolt that will tension the inlet flange to the container
    inner_cone = cylinder(h=radius + abs(thread_length), r1=radius +
                          flange_thickness, r2=radius + wall_thickness, segments=100, center=True)
    inner_cone = inner_cone - \
        cylinder(radius, 2*radius, segments=100, center=True)
    #inner_cone = rotate_extrude(360, 10)(polygon(triangle))
    inner_cone = rotate([0, 180, 0])(up(radius/2)(inner_cone))
    # remove the inside with a cylinder to allow for air flow
    bolt = inner_cone
    # add the thread to the bolt on the outside to prevent air loss
    # along the fastner_gap
    thread = threading(thread_length, thread_depth, radius,
                       thread_count, thread_span, thread_resolution)
    bolt = down(radius+thread_length/2)(thread) + bolt
    # rotate the bolt to the correct angle
    bolt = rotate([0, 90, 90])(bolt)
    # move the bolt in front of the flange
    # TODO: still a bug here
    bolt = translate([0, 2.5*radius + fastner_gap + abs(thread_length/2),  -radius])(bolt)

    inlet_flange = inlet_flange - bolt
    #bolt = translate([0, 2*radius, 0])(bolt)

    # move the flange to the correct position on container for simulated subtraction
    #inlet_flange = translate([0, 0, guard_height+radius/2])(inlet_flange)
    #bolt = translate([0, 0, guard_height + radius/2])(bolt)

    return inlet_flange, bolt


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
#    os.system("/home/bada/Desktop/code/openscad/openscad -o " +
#              filename + ".stl " + filename + ".scad")
    os.system("openscad -o " +
              filename + ".stl " + filename + ".scad &")


if __name__ == "__main__":
    config = toml.load("configuration.toml")
    outer, inner = Inlet_Flange(**config)
    render_object(outer, "outer_flange")
    render_object(inner, "inner_flange")
