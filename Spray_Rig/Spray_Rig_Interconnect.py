



from math import *
import os
from solid2 import *
import toml
epsilon = 0.0001

# Define slot types for clarity
SLOT_TYPE_NONE = 0
SLOT_TYPE_MALE = 1
SLOT_TYPE_FEMALE = 2

'''
a fastener and helper methods
'''
class BuildFastener():
    #defaults
    def __init__(self, angle=-45):
        self.angle = angle
    def hght(self, height):
        self.height = height
        return self
    def wdth(self, width):
        self.width = width
        return self
    def lngth(self, length):
        self.length = length
        return self
    def angle(self, angle):
        self.angle = angle
        return self
    def hinge_hght(self, hinge_height):
        self.hinge_height = hinge_height
        return self
    def hinge_wdth(self, hinge_width):
        self.hinge_width = hinge_width
        return self
    #TODO: OpenSCADObject inheritance has additional variable length params: research
class fastener(BuildFastener):
    def __init__(self):
        super().__init__()
        #init each super
        #TODO: make self.object inherited 
        self.object = None
    def build(self):
        #TODO: need a prism object, include the library here and 
        #      start extracting encapsulations
        base = cube([self.length, self.width, self.height])
        hinge = cube([self.hinge_width, self.hinge_width, self.hinge_height])
        hinge = hinge.rotate([0, self.angle, 0])
        #remove the top half
        hinge -= cube([self.hinge_width, self.hinge_width, self.hinge_height/2])
        #TODO: this is the hypotenuse of the square
        hinge = hinge.translate([self.hinge_width/2+self.length/2, 0, self.height-1.5*self.hinge_height])
        self.object = base + hinge
        return self.object

'''
a class that creates various partitions of circles extruded to 3D. Pizza slices that are integrated along the z axis.
'''
class BuildCirclePartitions():
    def __init__(self):
        self.radius_major = 0
        self.radius_minor = 0
        self.angle = 0
        self.height = 0
        self.Center = False
    def rad_maj(self, rad_maj):
        self.radius_major = rad_maj
        return self
    def rad_min(self, rad_min):
        self.radius_minor = rad_min
        return self
    def ang(self, angle):
        self.angle = angle
        return self
    def hght(self, height):
        self.height = height
        return self
    #TODO: this isnt as elegant but its functional
    def second_rad_maj(self, rad_maj):
        self.second_radius_major = rad_maj
        return self
    def second_rad_min(self, rad_min):
        self.second_radius_minor = rad_min
        return self
    def second_ang(self, angle):
        self.second_angle = angle
        return self
    def second_hght(self, second_height):
        self.second_height = second_height
        return self
    def center(self, Center):
        self.Center = Center
        return self
class CirclePartitions(BuildCirclePartitions):
    def __init__(self):
        super().__init__()
        #what type of circle partition has been built
        self.object = None
    #~EVALUATORS~
    #TODO: is_second is_bullshit
    #..for CirclePartitions lazy state builder
    '''
    creates a segment/partition of a circle
    '''
    def circle_segment(self, is_second=False):
        #create a rectangle of height height and width radius_major
        #TODO: this is a bad solution
        if is_second:
            rectangle = square([self.second_radius_major, self.second_height])
            circle_segment = rotate_extrude(angle=self.second_angle, _fn=500)(rectangle)
        else:
            rectangle = square([self.radius_major, self.height])
            circle_segment = rotate_extrude(angle=self.angle, _fn=500)(rectangle)
        #sweep the rectangle with rotation extrude
        self.object = circle_segment
        #TODO: this should be self but needs to be reworked in calling methods (circle_arc_segment)
        return self.object
    '''
    creates a circular arc which is a segment of a disk
    '''
    def circle_arc_segment(self, is_second=False):
        #create a circle segment
        #create a circle segment with minor radius
        #TODO: this is a bad solution
        if is_second:
            circle_segment = self.circle_segment(is_second=True)
            inner_rectangle = square([self.second_radius_minor, self.second_height])
            inner_circle = rotate_extrude(angle=2*self.second_angle, _fn=500)(inner_rectangle)
            circle_arc_segment = circle_segment - inner_circle

        else:
            circle_segment = self.circle_segment()
            inner_rectangle = square([self.radius_minor, self.height])
            #NOTE: 2* here to account for openscads marginal errors
            inner_circle = rotate_extrude(angle=2*self.angle, _fn=500)(inner_rectangle)
            circle_arc_segment = circle_segment - inner_circle
        #create a circle arc segment
        if self.Center and is_second:
            circle_arc_segment = circle_arc_segment.up(self.second_height/2)
            #TODO: this is regardless of if Center
            circle_arc_segment = circle_arc_segment\
                                .up(2*self.wall_thickness)\
                                .rotate((self.angle-self.second_angle)/2)
        elif self.Center == True:
            circle_arc_segment = circle_arc_segment.up(self.height/2)

        self.object = circle_arc_segment
        #move the circle arc segment to the origin
        return self
    '''
    creates a shell within a circle_arc_segment
    '''
    #TODO: just pass is_second here it shouldnt be a member of arc class
    def circle_arc_shell(self):
        #TODO: also specify angles
        #create a circle arc segment
        circle_arc_segment = self.circle_arc_segment().object
        #create second circle arc segment
        second_circle_arc_segment = self.circle_arc_segment(is_second=True).object
        #create a shell
        circle_arc_shell = circle_arc_segment - second_circle_arc_segment
        self.object = circle_arc_shell
        return self

'''
builds a SprayRig by sequentially transforming a CirclePartition object via methods.
'''
class BuildSprayRig():
    def nozzle_rad(self, nozzle_radius):
        self.nozzle_radius = nozzle_radius
        return self
    def nozzle_hght(self, nozzle_height):
        self.nozzle_height = nozzle_height
        return self
    def nozzle_wall_thick(self, nozzle_wall_thickness):
        self.nozzle_wall_thickness = nozzle_wall_thickness
        return self
    def wall_thick(self, wall_thickness):
        self.wall_thickness = wall_thickness
        return self
    def lid_thick(self, lid_thickness):
        self.lid_thickness = lid_thickness
        return self
    def tube_diam(self, tube_diameter):
        self.tube_diameter = tube_diameter
        return self
    def inlet_thick(self, inlet_thickness):
        self.inlet_thickness = inlet_thickness
        return self
    def lid_len(self, lid_length):
        self.lid_length = lid_length
        return self
class SprayRig(BuildSprayRig, CirclePartitions):
    def __init__(self):
        super().__init__()
    #TODO: extrude 2D for performance instead of iterating rotationally transformed matrix of cylinders
    def nozzle_array(self):
        #self.object = super().circle_arc_segment().object
        #now also remove cylinders from the bottom of the circle arc segment
        #create a cylinder
        print("~GENERATING NOZZLE ARRAY~")
        #TODO: all self mutations should be in stateful builder otherwise 
        #      state is scattered
        nozzle_spacing = 2*self.nozzle_radius + self.nozzle_wall_thickness

        nozzle = cylinder(r=self.nozzle_radius, \
                          h=self.nozzle_height, _fn=10, center=True)\
                     .up(self.nozzle_height/2+self.height/2)
        #generate the nozzle angles
        #move the cylinder to the origin
        #create a row of nozzles 
        #TODO: TEST: was:
        #total_track = floor((self.radius_major-self.radius_minor)/nozzle_spacing)
        total_track = floor((self.radius_major-self.radius_minor)/nozzle_spacing)
        #TODO: test that we dont intersect with the lip
        #TODO: make conditional builds functional and elegant
        if self.lid_length is not None and self.lid_thickness is not None:
            #TODO: 3*self.lid_thickness and move thickness in.
            total_track = floor((self.radius_major-self.radius_minor-2*self.lid_thickness)/nozzle_spacing)

        print("num tracks: ", total_track)
        #NOTE: first iteration is skipped 
        track = self.radius_minor + self.wall_thickness#TODO: TEST: was: 2*nozzle_spacing
        num_nozzles = 0
        #i=3
        #TODO: TEST also this seems to be a hack and is expected to not sweep parameters
        #calculate how many tracks will intersect with the inner_lip which is a distance of 2*self.lid_thickness
        i=0
        #i = ceil(self.lid_thickness/nozzle_spacing)
        #TODO: remove first radius iteration and first angle iteration
        while i < total_track:
            print("i: ", i)
            print("track: ", track)
            cur_nozzle = nozzle.forward(track)
            #TODO: algebraic reduction
            track_circumference = 2*pi*track*(self.angle/360)
            nozzle_spacing_circumference = track_circumference/2*nozzle_spacing
            angle_iter = nozzle_spacing_circumference/track
            #TODO: TEST this line was init 0
            cur_angle = 2*angle_iter
            print("angle_iter: ", angle_iter)
            #NOTE: we skip the first angle iter and the last for a 
            #      psuedo wall_thickness and correct later
            #cur_angle += angle_iter
            while cur_angle < self.angle-angle_iter:
                #tap a nozzle into the circle arc segment
                self.object = self.object - cur_nozzle.rotate([0, 0, 270 + cur_angle])
                cur_angle += angle_iter
                num_nozzles += 1
            i +=1
            track += nozzle_spacing

        print("num_nozzles: ", num_nozzles)

        #move the circle arc segment to the origin
        return self
    '''
    add a lip to the SprayRig object to
    attach it to the reservoir container.
    '''
    def add_lip(self):
        #the lip is rig_depth to ensure larger rigs have more support to the 
        #container to support the added fluid and structural weight

        #create the outer lip 
        #create a rectangle of height rig_depth and width wall_thickness, 
        #adding to the outer circumference of the array to make everything square.
        outer_height = self.lid_length
        outer_lip = square([self.lid_thickness, outer_height], center=True)\
        #move up by rig_depth
        #outer_lip = outer_lip.up(self.height)
        #move to final_radius
        outer_lip_2d = outer_lip.right(self.radius_major+1.5*self.lid_thickness)
        #rotate extrude the final radius
        outer_lip = rotate_extrude(angle=self.angle, _fn=500)(outer_lip_2d)

        #create the inner lip
        #inner_lip = square([self.lid_thickness, self.lid_length+self.height], center=True)\
        #move to final_radius - lid_thickness
        #inner_lip = inner_lip.right(self.radius_major-2*self.lid_thickness)
        inner_lip = outer_lip_2d.left(2*self.lid_thickness)
        #rotate extrude the final radius
        inner_lip = rotate_extrude(angle=self.angle, _fn=500)(inner_lip)
        #now create a swept rectangle to fill the space above the lips
        cover = square([3*self.lid_thickness,self.height], center=True)
        cover = cover.right(self.radius_major+self.lid_thickness/2)
        cover = rotate_extrude(angle=self.angle, _fn=500)(cover)
        cover = cover.up(outer_height/2+self.height/2)

        lip = outer_lip + inner_lip + cover
        lip = lip.down(outer_height/2-self.height/2)
        #lip = lip.down(self.lid_length/2-self.wall_thickness)
        #TODO: account for this in the model so the lip depth is accurate, 
        #      right now this effectively subtracts the depth
        #lip = lip.up(self.lid_length/2)
        self.object += lip
        #create a rectangle of height rig_depth and width wall_thickness 
        return self
    '''
    Helper to create the male (tongue) slot features.
    '''
    def _create_male_slot_features(self, mid_radial_pos, slot_thickness, slot_depth, single_slot_height, slot_vertical_spacing, height):
        tongue_base = cube([slot_depth, slot_thickness, single_slot_height], center=True)

        # Top tongue
        tongue_male_top = tongue_base.translate([mid_radial_pos, -slot_thickness/2, 0])
        tongue_male_top = tongue_male_top.up(height - slot_vertical_spacing - single_slot_height/2)

        # Bottom tongue
        tongue_male_bottom = tongue_base.translate([mid_radial_pos, -slot_thickness/2, 0])
        tongue_male_bottom = tongue_male_bottom.up(slot_vertical_spacing + single_slot_height/2)
        return tongue_male_top + tongue_male_bottom

    '''
    Helper to create the female (groove) slot features (negative space).
    '''
    def _create_female_slot_features(self, mid_radial_pos, slot_thickness, slot_depth, single_slot_height, slot_vertical_spacing, height, tolerance):
        groove_base = cube([slot_depth + tolerance, slot_thickness + tolerance, single_slot_height + tolerance], center=True)

        # Top groove
        groove_female_top = groove_base.translate([mid_radial_pos, (slot_thickness + tolerance)/2, 0])
        groove_female_top = groove_female_top.up(height - slot_vertical_spacing - (single_slot_height + tolerance)/2)

        # Bottom groove
        groove_female_bottom = groove_base.translate([mid_radial_pos, (slot_thickness + tolerance)/2, 0])
        groove_female_bottom = groove_female_bottom.up(slot_vertical_spacing + (single_slot_height + tolerance)/2)
        return groove_female_top + groove_female_bottom

    '''
    Adds male (tongue) and/or female (groove) slot connections to the radial faces
    of the segment, allowing multiple segments to interlock.
    left_slot_type: SLOT_TYPE_NONE, SLOT_TYPE_MALE, or SLOT_TYPE_FEMALE for the side at angle 0.
    right_slot_type: SLOT_TYPE_NONE, SLOT_TYPE_MALE, or SLOT_TYPE_FEMALE for the side at self.angle.
    '''
    def add_slot_connections(self, left_slot_type, right_slot_type):
        # Dimensions for the slot feature
        slot_thickness = self.wall_thickness / 2
        slot_depth = self.wall_thickness
        single_slot_height = self.height / 4
        slot_vertical_spacing = self.height / 4

        # Tolerance for the female part to ensure a snug fit
        tolerance = epsilon * 2

        # Calculate the radial position for the slot (mid-point of the segment's radial extent)
        mid_radial_pos = (self.radius_major + self.radius_minor) / 2

        # Create the base male and female features
        male_features = self._create_male_slot_features(mid_radial_pos, slot_thickness, slot_depth, single_slot_height, slot_vertical_spacing, self.height)
        female_features = self._create_female_slot_features(mid_radial_pos, slot_thickness, slot_depth, single_slot_height, slot_vertical_spacing, self.height, tolerance)

        # Apply features to the left side (angle 0)
        if left_slot_type == SLOT_TYPE_MALE:
            self.object += male_features
        elif left_slot_type == SLOT_TYPE_FEMALE:
            self.object -= female_features

        # Apply features to the right side (angle self.angle)
        if right_slot_type == SLOT_TYPE_MALE:
            self.object += male_features.rotate([0, 0, self.angle])
        elif right_slot_type == SLOT_TYPE_FEMALE:
            self.object -= female_features.rotate([0, 0, self.angle])

        return self

    # The inlet method is removed as it is replaced by the new slotting mechanism.
    # def inlet(self):
    #     pass

    def build(self):
        return self.object

def spray_rig(
    initial_radius,
    final_radius,
    nozzle_diameter,
    nozzle_wall_thickness,
    lid_thickness,
    lid_length,
    tube_diameter,
    inlet_thickness,
    wall_thickness,
    rig_depth,
    max_segment_size,
    epsilon,
):
    """
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
        array_spacing:
            the spacing between nozzle array rings for mechanical stability.
    """
    #TODO: rewrite the above param descriptions
    # Nonesense assertions:
    assert initial_radius < final_radius, \
        "ERROR: invalid nozzle and tube diameter, did you enter the radius measurements backwards?"
    assert nozzle_diameter < tube_diameter, \
        "ERROR: nozzles must be smaller than the tubing!"

    #Calculate the size of each segment's arclength and number of segments
    final_circumference = 2 * pi * final_radius
    num_segments = final_circumference / max_segment_size
    remainder = num_segments % 1
    print("num_segments: ", num_segments)
    print("max_segment_size: ", max_segment_size)
    print("remainder: ", remainder)
    #find all divisors that result in an integer for final_circumference
    divisors = []
    for i in range(1, floor(final_circumference)):
        divisors.append(final_circumference / i)
    print("divisors: ", divisors)
    #remave any divisors greater than the max_segment_size
    divisors = [x for x in divisors if x < max_segment_size]
    #find the closest divisor to max_segment_size
    closest_divisor = min(divisors, key=lambda x: abs(x - max_segment_size))
    print("closest_divisor: ", closest_divisor)

    num_segments = final_circumference / closest_divisor
    max_segment_size = closest_divisor
    #find the angle for the arc length given the now calculated max_segment_size
    angle = degrees(max_segment_size/final_radius)
    #the angle for the arc that has wall_thickness added to it for the rig
    #NOTE: this isnt perfect but neither is anything truly beautiful
    #TODO: ensure this shouldnt be subtractive (is initial and subtracted from final)
    #TODO: swap shell and angle positioning and make subtractive, this doesnt fit a circle due to wall_thickness*2*num_segments overlap
    #shell_angle=degrees((max_segment_size+2*wall_thickness)/final_radius)
    shell_angle=degrees((max_segment_size-2*wall_thickness)/final_radius)

    print("final_circumference: ", final_circumference)
    print("final_max_segment_size: ", max_segment_size)
    print("final_num_segments: ", num_segments)


    # Helper function to configure a base SprayRig segment
    def _configure_base_spray_rig(initial_radius, final_radius, angle, rig_depth, wall_thickness, shell_angle, nozzle_diameter, nozzle_wall_thickness, lid_thickness, lid_length, tube_diameter, inlet_thickness):
        return SprayRig() \
        .rad_maj(final_radius) \
        .rad_min(initial_radius) \
        .ang(angle) \
        .hght(rig_depth + 2 * wall_thickness) \
        .second_rad_maj(final_radius - wall_thickness) \
        .second_rad_min(initial_radius + wall_thickness) \
        .second_ang(shell_angle) \
        .second_hght(rig_depth) \
        .nozzle_rad(nozzle_diameter / 2) \
        .nozzle_hght(wall_thickness) \ # nozzle_height is typically wall_thickness
        .nozzle_rad(nozzle_diameter / 2) \
        .nozzle_hght(wall_thickness) \ # nozzle_height is typically wall_thickness
        .nozzle_wall_thick(nozzle_wall_thickness) \
        .wall_thick(wall_thickness) \
        .lid_thick(lid_thickness) \
        .lid_len(lid_length) \
        .tube_diam(tube_diameter) \
        .inlet_thick(inlet_thickness) \
        .center(True) \
        .circle_arc_shell() \
        .nozzle_array() \
        .add_lip()

    # Generate Middle Segment
    middle_segment_rig = _configure_base_spray_rig(initial_radius, final_radius, angle, rig_depth, wall_thickness, shell_angle, nozzle_diameter, nozzle_wall_thickness, lid_thickness, lid_length, tube_diameter, inlet_thickness)
    middle_segment_rig.add_slot_connections(SLOT_TYPE_MALE, SLOT_TYPE_FEMALE) # Middle segment: male on one side, female on other

    middle_segment_object = middle_segment_rig.build()
    middle_segment_object = middle_segment_object.rotate([90, 0, 0])
    scad_render_to_file(middle_segment_object, "Spray_Rig_Segment_Middle_Slotted.scad")
    os.system("openscad -o Spray_Rig_Segment_Middle_Slotted.stl Spray_Rig_Segment_Middle_Slotted.scad &")

    # Generate Endcap Segment
    endcap_segment_rig = _configure_base_spray_rig(initial_radius, final_radius, angle, rig_depth, wall_thickness, shell_angle, nozzle_diameter, nozzle_wall_thickness, lid_thickness, lid_length, tube_diameter, inlet_thickness)
    endcap_segment_rig.add_slot_connections(SLOT_TYPE_MALE, SLOT_TYPE_NONE) # Endcap segment: male on one side, no slot on other

    endcap_segment_object = endcap_segment_rig.build()
    endcap_segment_object = endcap_segment_object.rotate([90, 0, 0])
    scad_render_to_file(endcap_segment_object, "Spray_Rig_Segment_Endcap_Slotted.scad")
    os.system("openscad -o Spray_Rig_Segment_Endcap_Slotted.stl Spray_Rig_Segment_Endcap_Slotted.scad &")

if __name__ == "__main__":
    config = toml.load("configuration.toml")
    spray_rig(**config)
