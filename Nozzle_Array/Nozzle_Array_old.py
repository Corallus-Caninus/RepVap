# This is highest priority print

# TODO: pressure drop in intake and outlet nozzles isnt considered.
#       Should use outer diameter with a cinch screw.

# NOTE: consider 2d projections for printing a cut stencil guide
#       https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/3D_to_2D_Projection

# TODO: set geometry segments in header of render file instead of in geometry for production

# TODO: consider a snap hinge that pokes through inlet and outlet to hang from
#       bottom of lid with two small holes instead of large gash.

# TODO: implement top mounting pieces. Screw or snap-fit?
#       screw may have tighter seal. Doesnt matter since glue gasketing the fan anyways. do whats easiest

# TODO: try array spacing without 2* but just 1*

from math import *
import os
from solid import *
from solid.utils import *
import toml
import turtle


def bucket_emitter_array(
        initial_radius, final_radius, nozzle_diameter, nozzle_wall_thickness,
        max_segment_size, drop_down_depth, tube_diameter, pagoda_thickness, wall_thickness, array_spacing):
    '''
    PARAMETERS:
        intial_radius:
            the radius of the fan.
        final_radius:
            the radius of the lid or area to be used for nozzles otherwise.
        nozzle_diameter:
            the diameter of the emitter nozzle.
        nozzle_wall_thickness:
            the thickness of the nozzle as it drops down into the bucket from the lid.
        max_segment_size:
            the arc length of the arc that is formed by each array.
        drop_down_depth:
            the depth the emitter will drop into the bucket.
        tube_diameter:
            the diameter of the tube
        wall_thickness:
            the thickness of the hull (everything except the nozzles).
        @DEPRECATED
        tube_wall_thickness:
            the thickness of the inlet and outlet nozzles, subtracted from the nozzle cylinder 
            (the larger the value the more constricted the flow)
        array_spacing:
            the spacing between nozzle array rings for mechanical stability.
    '''
    # Nonesense assertions:
    assert initial_radius < final_radius, "ERROR: did you enter the radius measurements backwards?"
    assert nozzle_diameter < tube_diameter, "ERROR: nozzles must be smaller than the tubing!"
    # draw the lid with final radius and the fan with initial radius as two concentric circles with the same center
    turtle.penup()
    turtle.right(90)    # Face South
    turtle.forward(final_radius)   # Move one radius
    turtle.right(270)   # Back to start heading
    turtle.pendown()    # Put the pen back down
    turtle.circle(final_radius)    # Draw a circle
    turtle.penup()      # Pen up while we go home
    # now draw the fan with the smaller radius with the same center
    turtle.home()
    turtle.right(90)    # Face South
    turtle.forward(initial_radius)   # Move one radius
    turtle.right(270)   # Back to start heading
    turtle.pendown()    # Put the pen down
    turtle.circle(initial_radius)    # Draw a circle
    turtle.penup()      # Pen up while we go home

    # NOTE: insert assertions as geometry artifacts are
    #       found that are within build parameterization

    # calculate the number of concentric circles given the platter (lid)
    # This is a 1 dimensional cross-section
    number_disks = int(
        (final_radius-initial_radius)/(tube_diameter + 2*wall_thickness + array_spacing))
    print("calculated " + str(number_disks) +
          " disks of tube_length to fill the platter.")
    # the tube diameter and both wall thicknesses is our array block's width.
    disk_minor_radius = initial_radius
    disk_major_radius = disk_minor_radius + tube_diameter + 2*wall_thickness
    total_nozzle_area = 0

    for index in range(0, number_disks):
        cur_nozzle_area = 0
        # offset the mean radius by the intial radius
        segment_radius = disk_minor_radius + \
            (disk_major_radius-disk_minor_radius) / \
            array_spacing
        disk_circumference = 2*pi*segment_radius
        # calculate the number of segments, we assume tube is flexible enough that each segment will
        # only need spacing of tube_diameter to interconnect between nozzles (not to be confused with
        # rray spacing). tube connector nozzles will be length
        # of tube diameter. wall thickness is flange width
        num_segments = int(disk_circumference /
                           (max_segment_size + 4*tube_diameter + wall_thickness))

        print("constructing disk partition with radius " + str(segment_radius))
        disk_partition, cur_nozzle_area, sweep = build_disk_partition(
            segment_radius,
            drop_down_depth, nozzle_diameter, nozzle_wall_thickness,
            tube_diameter, max_segment_size, pagoda_thickness, wall_thickness)
        total_nozzle_area = total_nozzle_area + cur_nozzle_area*num_segments

        # DRAW THIS DISK AND ALL SEGMENTS WITH TURTLE
        # draw the initial disk at radius (disk_minor_radius) with depth disk_major_radius
        # as a curve of sweep with length max_segment_size
        turtle.pendown()
        turtle.circle(segment_radius, sweep)
        turtle.penup()
        # keep the canvas up
        turtle.done()

        # END OF DRAWING DISK AND ALL SEGMENTS

        # check iteration but this should be performed on last to cap the array sequence
        # TODO: arc count is off
        if index+1 == number_disks:
            capped_disk_partition, cur_nozzle_area, sweep = build_disk_partition(
                segment_radius,
                drop_down_depth, nozzle_diameter, nozzle_wall_thickness,
                tube_diameter, max_segment_size, pagoda_thickness,
                wall_thickness, True)
            filename = "ENDCAP_x1" + "_nozzle_arc" + str(index+1)
            scad_render_to_file(capped_disk_partition, filename+".scad")
            os.system("/mnt/BORG_CUBE02/code/openscad_fresh/openscad/openscad -o " +
                      filename + ".stl " + filename + ".scad &")

            print("rendering.. " + str(index))
            filename = "x" + str(num_segments) + "_" + \
                "_nozzle_arc"+str(index)
            scad_render_to_file(disk_partition, filename+".scad")
            os.system("/mnt/BORG_CUBE02/code/openscad_fresh/openscad/openscad -o " +
                      filename + ".stl " + filename + ".scad &")
        else:
            print("rendering.. " + str(index))
            filename = "x" + str(num_segments) + "_" + \
                "_nozzle_arc"+str(index+1)
            scad_render_to_file(disk_partition, filename+".scad")
            os.system("/mnt/BORG_CUBE02/code/openscad_fresh/openscad/openscad -o " +
                      filename + ".stl " + filename + ".scad &")

        # iterate the disk to the next radii
        disk_minor_radius = disk_major_radius
        disk_major_radius = disk_minor_radius + tube_diameter + 2*wall_thickness

    # TODO: suggest a better final_radius to equate tube_diameter cross section.
    #       this should be a seperate program to keep this organized and direct.
    # features such as total_nozzle_area is already complicating the algorithms readability.
    tube_nozzle_differential = pi*(tube_diameter)**2 - total_nozzle_area
    print("GENERATION FINISHED.")
    print("Total nozzle area rendered: " + str(total_nozzle_area))
    print("Inlet to outlet area differential (proportional to pressure drop): " +
          str(tube_nozzle_differential))
    print("PLEASE WAIT WHILE OPENSCAD RENDERS THE MODELS..")

    # return the number of disks and their width
    return number_disks, disk_major_radius - disk_minor_radius


def build_disk_partition(segment_radius,
                         drop_down_depth, nozzle_diameter, nozzle_wall_thickness,
                         tube_diameter, max_segment_size, pagoda_thickness,
                         wall_thickness, final=False):
    '''
    builds a single array segment of a disk.
    '''
    # max_segment_size is the arch not the chord so we can use some high school trig

    # DISK SEGMENT HULL
    # calculate the radians swept by the segment_length and segment_radius
    sweep = degrees(max_segment_size/segment_radius)
    print("disk partition sweeping: " + str(sweep) + " degrees")

    # build array hull, square the circle that is the tube_diameter

    # NOTE: wall thickness is actually half here. change after working since
    #       relative to parameter just unintuitive.
    solid_hull = right(segment_radius)(square(tube_diameter+wall_thickness))
    hull = translate([wall_thickness/2, wall_thickness/2]
                     )(right(segment_radius)(square(tube_diameter)))

    solid_disk_partition = rotate_extrude(sweep, 1, segments=200)(solid_hull)
    disk_partition = rotate_extrude(sweep, 1, segments=200)(hull)
    disk_partition = solid_disk_partition - hole()(disk_partition)

    # EMITTER HULL #
    # frustrum with angle from wall_thickness to tube_diameter.
    # doesnt need to be offset since we can just offset x coords
    frustrum = polygon(
        [
            [segment_radius + wall_thickness/2, tube_diameter + drop_down_depth],
            [segment_radius, tube_diameter],
            [segment_radius + wall_thickness + tube_diameter, tube_diameter],
            [segment_radius + tube_diameter + wall_thickness/2, tube_diameter + drop_down_depth]])

    emitter_hull = up(wall_thickness)(
        rotate_extrude(sweep, 1, segments=200)(frustrum))
    disk_partition = disk_partition + emitter_hull

    # EMITTER NOZZLES #
    #       if this were a file system disk storage analogy these are the
    #       files/tables (pick one either work).
    #       place each nozzle seperated by nozzle_radius + nozzle_wall_thickness
    #       then linefeed and resweep at radius + nozzle_radius + nozzle_wall_thickness

    nozzle = cylinder(r=nozzle_diameter/2 + nozzle_wall_thickness, h=drop_down_depth, center=True, segments=11) - \
        hole()(cylinder(r=nozzle_diameter/2, h=drop_down_depth +
                        wall_thickness, center=True, segments=11))
    # have to shift up by half height since centered
    nozzle = up((drop_down_depth+wall_thickness)/2)(nozzle)
    # tap through to the main hull
    nozzle = up(tube_diameter)(nozzle)

    # calculate the number of nozzles that will fit on the current disk segment
    # 1-dimension cross-section analysis of how many nozzle sectors will fill the disk_segment

    num_nozzle_sectors = int(
        tube_diameter/(nozzle_diameter + 2*nozzle_wall_thickness))
    print("got " + str(num_nozzle_sectors) + " nozzle sectors")

    # TODO: clean this up
    init_sector_radius = segment_radius + wall_thickness/2 + \
        nozzle_wall_thickness + nozzle_diameter/2
    final_sector_radius = wall_thickness/2 + (ceil(num_nozzle_sectors/2))*(
        nozzle_wall_thickness + nozzle_diameter/2) + init_sector_radius
    print('init sector radius: {} final sector radius: {}'.format(
        init_sector_radius, final_sector_radius))
    print('got mean: {}'.format(num_nozzle_sectors/2))

    segment_nozzle_area = 0
    # TODO: why are we ceil /2 here? this is marginally wrong but just in stdout
    for _ in range(int(ceil(num_nozzle_sectors/2))):
        # the angle to iterate by
        # TODO: autorefactored function
        # TODO: segment_nozzle_area needs to be calculated for both symmetries

        # top symmetry
        print("generating top track symmetry...")
        disk_partition, _ = nozzle_track(
            nozzle_diameter, nozzle_wall_thickness, init_sector_radius,
            sweep, segment_nozzle_area, nozzle, disk_partition)

        # bottom symmetry
        print("generating bottom track symmetry...")
        disk_partition, segment_nozzle_area = nozzle_track(
            nozzle_diameter, nozzle_wall_thickness, final_sector_radius,
            sweep, segment_nozzle_area, nozzle, disk_partition)

        # TODO: fit is incorrect due to floor div?
        #       use a symmetric iterator about the middle
        # count from the start to halfway then iterate mirror twice about middle
        # just iterate half doing each side symmetrically
        init_sector_radius = init_sector_radius + \
            (nozzle_diameter + 2*nozzle_wall_thickness)
        final_sector_radius = final_sector_radius + \
            (nozzle_diameter + 2*nozzle_wall_thickness)

    # TUBING CONNECTORS #
    flange = cube(1, center=True)
    # offset to xy plane
    flange = up(1/2)(flange)
    # divide by 2 on thickness since holes are translated the same amount
    # (keep consistent convention)
    flange = scale([tube_diameter + wall_thickness,
                    tube_diameter + wall_thickness,
                    wall_thickness/2])(flange)

    # seperate heights for two cylinders that create the pagoda
    pagoda_nozzle_solid = up(tube_diameter)(cylinder(
        r2=tube_diameter/2, r1=tube_diameter/2 + pagoda_thickness, h=tube_diameter, segments=200))
    tube_nozzle_solid = cylinder(tube_diameter/2+pagoda_thickness/2, h=tube_diameter, segments=200)\
        + pagoda_nozzle_solid
    # now tap a hole through the center
    tube_nozzle = tube_nozzle_solid - \
        hole()(cylinder(tube_diameter/2, 2*tube_diameter, segments=200))

    tube_nozzle = tube_nozzle + flange

    # attach to either end of the array, using sweep and origin
    inlet_tube_nozzle = translate([(segment_radius + tube_diameter/2 + wall_thickness/2),
                                   0, tube_diameter/2 + wall_thickness/2])(rotate([90, 0, 0])(tube_nozzle))

    # add endcap or T junction and finish connectors
    if final:
        # mirror sweep of extrusion for the outlet_tube_nozzle
        outlet_tube_nozzle = rotate([0, 0, sweep])(
            translate([(segment_radius + tube_diameter/2 + wall_thickness/2),
                       tube_diameter, tube_diameter/2 + wall_thickness/2])
            (rotate([270, 0, 0])(down(tube_diameter)(flange))))

        disk_partition = (disk_partition + inlet_tube_nozzle) + \
            outlet_tube_nozzle
    else:
        outlet_tube_nozzle = rotate([0, 0, sweep])(
            translate([(segment_radius + tube_diameter/2 + wall_thickness/2),
                       tube_diameter, tube_diameter/2 + wall_thickness/2])
            (rotate([270, 0, 0])(down(tube_diameter)(tube_nozzle))))

        disk_partition = (disk_partition + inlet_tube_nozzle) + \
            outlet_tube_nozzle

    return disk_partition, segment_nozzle_area, sweep


def nozzle_track(nozzle_diameter, nozzle_wall_thickness, sector_radius, sweep, segment_nozzle_area, nozzle, disk_partition):
    # TODO: consider angling the nozzles if needing more
    #       initial entropy to chicken wire
    #        (should be chaotic enough with just chicken wire)
    # the angle to iterate by
    track_offset = degrees(
        asin((nozzle_diameter + 2*nozzle_wall_thickness)/sector_radius))
    print("iterating with angular offset " +
          str(track_offset) + " degrees")
    num_nozzles = int(sweep/track_offset)
    print("generating " + str(num_nozzles) + " on this track..")
    segment_nozzle_area = segment_nozzle_area + \
        num_nozzles*(pi*(nozzle_diameter/2)**2)
    # initial offset
    cur_offset = degrees(
        asin((nozzle_diameter/2 + nozzle_wall_thickness)/sector_radius))
    for _ in range(num_nozzles):
        cur_nozzle = rotate([0, 0, cur_offset])(
            translate([sector_radius, 0, 0])(nozzle))
        disk_partition = disk_partition + cur_nozzle
        cur_offset = cur_offset + track_offset

    return disk_partition, segment_nozzle_area


if __name__ == "__main__":
    config = toml.load("configuration.toml")
    bucket_emitter_array(**config)
