# NOTE: consider 2d projections for printing a cut stencil guide
#       https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/3D_to_2D_Projection

# TODO: set geometry segments in header of render file instead of in geometry for production or in inheritance tree

# TODO: consider a snap hinge that pokes through inlet and outlet to hang from
#       bottom of lid with two small holes instead of large gash.

# TODO: refactor so some features can be an inheritance expansion library for solidpython such as Fastener which I will be using alot. import here so updates from other projects get propagated to this project

from math import *
import os
from solid2 import *
import toml
epsilon = 0.0001


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

#TODO: should have inhereted object here so the state is shared with the child 
#      class instead of being the primary member. all builders are fundamental objects (no children dependencies)
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
    add male fasteners to one side of the SprayRig and female fasteners to the other
    '''
    def add_fasteners(self):
        #TODO: need to rework this. cant add last segment get rid of this feature altogether in favor of tubing interconnect.
        #TODO: some of these operations are redundant and can be reduced
        #create a fastener at final_radius - wall_thickness
        far_fastener = fastener()\
                        .hght(2*self.wall_thickness)\
                        .wdth(self.wall_thickness/2)\
                        .lngth(self.wall_thickness/2)\
                        .hinge_hght(self.wall_thickness/2)\
                        .hinge_wdth(self.wall_thickness/2)\
                        .build()\
                        .rotate(180)\
                        .rotate([0,-90, 0])\
                        .forward(self.radius_major)\
                        .rotate([0, 0, self.angle-90])\
                        .up(1.5*self.height)
        near_fastener = fastener()\
                        .hght(2*self.wall_thickness)\
                        .wdth(self.wall_thickness/2)\
                        .lngth(self.wall_thickness/2)\
                        .hinge_hght(self.wall_thickness/2)\
                        .hinge_wdth(self.wall_thickness/2)\
                        .build()\
                        .rotate(180)\
                        .rotate([0, -90, 0])\
                        .forward(self.radius_minor+self.wall_thickness/2)\
                        .rotate([0, 0, self.angle-90])\
                        .up(1.5*self.height)
        bottom_near_fastener = fastener()\
                        .hght(2*self.wall_thickness)\
                        .wdth(self.wall_thickness/2)\
                        .lngth(self.wall_thickness/2)\
                        .hinge_hght(self.wall_thickness/2)\
                        .hinge_wdth(self.wall_thickness/2)\
                        .build()\
                        .rotate(180)\
                        .rotate([180, 90, 0])\
                        .forward(self.radius_minor)\
                        .rotate([0, 0, self.angle-90])\
                        .up(0.5*self.height)
        bottom_far_fastener = fastener()\
                        .hght(2*self.wall_thickness)\
                        .wdth(self.wall_thickness/2)\
                        .lngth(self.wall_thickness/2)\
                        .hinge_hght(self.wall_thickness/2)\
                        .hinge_wdth(self.wall_thickness/2)\
                        .build()\
                        .rotate(180)\
                        .rotate([180, 90, 0])\
                        .forward(self.radius_major-self.wall_thickness/2)\
                        .rotate([0, 0, self.angle-90])\
                        .up(0.5*self.height)

        #TODO: these should be part of fastener encapsulation
        #same as above but a little extra to allow for flexing in the fit cavity
        #we use fractions so the flexing scales with the majority/all materials
        #(all SCAD should scale as much as possible and with as few parameters 
        #as possible)
        #TODO: now repeat the above rotations for negations
        far_fastener_neg = fastener()\
                        .hght(2*self.wall_thickness)\
                        .wdth(self.wall_thickness/2)\
                        .lngth(self.wall_thickness)\
                        .hinge_hght(self.wall_thickness)\
                        .hinge_wdth(self.wall_thickness)\
                        .build()\
                        .rotate(180)\
                        .rotate([0,-90, 0])\
                        .forward(self.radius_major)\
                        .rotate([0, 0, self.angle-90])\
                        .up(1.5*self.height)#TODO: this should be based on lngth
        near_fastener_neg = fastener()\
                        .hght(2*self.wall_thickness)\
                        .wdth(self.wall_thickness/2)\
                        .lngth(self.wall_thickness)\
                        .hinge_hght(self.wall_thickness)\
                        .hinge_wdth(self.wall_thickness)\
                        .build()\
                        .rotate(180)\
                        .rotate([0, -90, 0])\
                        .forward(self.radius_minor+self.wall_thickness/2)\
                        .rotate([0, 0, self.angle-90])\
                        .up(1.5*self.height)
        bottom_near_fastener_neg = fastener()\
                        .hght(2*self.wall_thickness)\
                        .wdth(self.wall_thickness/2)\
                        .lngth(self.wall_thickness)\
                        .hinge_hght(self.wall_thickness)\
                        .hinge_wdth(self.wall_thickness)\
                        .build()\
                        .rotate(180)\
                        .rotate([180, 90, 0])\
                        .forward(self.radius_minor)\
                        .rotate([0, 0, self.angle-90])\
                        .up(0.5*self.height)
        bottom_far_fastener_neg = fastener()\
                        .hght(2*self.wall_thickness)\
                        .wdth(self.wall_thickness/2)\
                        .lngth(self.wall_thickness)\
                        .hinge_hght(self.wall_thickness)\
                        .hinge_wdth(self.wall_thickness)\
                        .build()\
                        .rotate(180)\
                        .rotate([180, 90, 0])\
                        .forward(self.radius_major-self.wall_thickness/2)\
                        .rotate([0, 0, self.angle-90])\
                        .up(0.5*self.height)

        #now add negative fasteners by rotating self.object 360-self.angle 
        #degrees and subtracting from itself
        self.object += far_fastener
        self.object += near_fastener
        self.object += bottom_near_fastener
        self.object += bottom_far_fastener
        #use neg objects instead
        self.object -= far_fastener_neg.rotate(-self.angle)
        self.object -= near_fastener_neg.rotate(-self.angle)
        self.object -= bottom_near_fastener_neg.rotate(-self.angle)
        self.object -= bottom_far_fastener_neg.rotate(-self.angle)

        return self
    '''
    adds a tube interconnect and rotate subtracts just like fasteners so
    each section can be plumbed together. conditionally cofigured with a
    calling method.
    '''
    def __add_interconnect(self):
        mean = (self.radius_major + self.radius_minor)/2
        interconnect = cylinder(r=self.tube_diameter/2, h=self.wall_thickness+self.tube_diameter/2, center=True, _fn=100)
        interconnect_neg = cylinder(r=self.tube_diameter/2-self.inlet_thickness, h=2*self.wall_thickness+self.tube_diameter/2, center=True, _fn=100)

        pagoda_nozzle = cylinder(d1=self.tube_diameter+self.inlet_thickness, \
                                    d2=self.tube_diameter-self.inlet_thickness, \
                                    h=self.tube_diameter, _fn=500, center=True)
        #pagoda_nozzle_neg = cylinder(d1=self.tube_diameter, \
        #                            d2=self.tube_diameter, \
        #                            h=self.tube_diameter, _fn=500, center=True)
        pagoda_nozzle_neg = cylinder(r=self.tube_diameter/2-self.inlet_thickness, \
                                     h=self.tube_diameter, _fn=500, center=True)

        pagoda_nozzle -= pagoda_nozzle_neg
        pagoda_nozzle = pagoda_nozzle\
                                .up(self.tube_diameter/2 + self.tube_diameter/4 + self.wall_thickness/2)
        #add pagoda to top of interconnect
        interconnect = interconnect + pagoda_nozzle


        #rotate it to where the fastener is
        interconnect = interconnect.translate([mean, 0, 0])
        interconnect_neg = interconnect_neg.translate([mean, 0, 0])
        #also move atop the nozzle_array
        interconnect = interconnect.up(self.height/2)
        interconnect_neg = interconnect_neg.up(self.height/2)
        #center the interconnect atop the xy plane
        interconnect = interconnect.up(self.height+self.tube_diameter/8)
        #move atop the xy plane
        #calculate the angle between the start and end of the array's reservoir
        #TODO: may need to move this based on tube_diameter inwards so tubing bends easier
        arc_angle = -sin((self.tube_diameter+2*self.wall_thickness)/(2*mean))*180/pi
        #arc_angle = sin(self.tube_diameter/(2*mean))*180/pi
        #swap mean
        #interconnect = interconnect.rotate([90,0,self.angle])
        interconnect = interconnect.rotate([0,0,self.angle])
        #NOTE: look here for bugs concerning tube clogs, this should be correct 
        #      but may have a rotational error
        interconnect_neg = interconnect_neg.rotate([0,0,self.angle])

        interconnect = interconnect.rotate(arc_angle)
        interconnect_neg = interconnect_neg.rotate(arc_angle)

        interconnect_neg = interconnect_neg.up(self.height+self.tube_diameter/8)

        #TODO: make hasattr functional and elegant
        if not hasattr(self,"is_endcap") or not self.is_endcap:
            print("adding interconnect")
            self.object += interconnect
            self.object -= interconnect_neg
        if not hasattr(self,"is_inlet") or not self.is_inlet:
            #chain this since this is a interconnecting segment
            print("adding inlet")
            self.object += interconnect.rotate(-self.angle-2*arc_angle)
            self.object -= interconnect_neg.rotate(-self.angle-2*arc_angle)

        return self
    '''
    accessor method for statefully configured interconnect method
    '''
    def middle(self):
        self.is_endcap = False
        self.is_inlet = False
        self.__add_interconnect()
        return self

    #NOTE: can always pass tubing through an inlet if we want to rush test SprayRig 
    #TODO: @DEPRECATED
    '''
    Add an endcap that allows passthrough of the tubing via a cylinder
    with pagoda nozzles (cones that increase the cylinder diameter to
    seal the tubing) on top and bottom. Also doesnt add interconnect
    '''
    def inlet(self):
        #just call middle()
        return self.middle()
#        mean = (self.radius_major + self.radius_minor)/2
#        #create the cylinder
#        #endcap = cylinder(d=self.tube_diameter+self.inlet_thickness,\
#        #                  h=self.height+self.wall_thickness,\
#        #                  _fn=500, center=True)
#        #endcap_neg = cylinder(d=self.tube_diameter, \
#                #                    h=self.height+self.wall_thickness,\
#                #                    _fn=500, center=True)
#        endcap = cylinder(r=self.tube_diameter/2,\
#                            h=self.height+self.tube_diameter/2,\
#                            _fn=500, center=True)
#        endcap_neg = cylinder(r=self.tube_diameter/2,\
#                            h=self.height+self.wall_thickness,\
#                            _fn=500, center=True)
#        endcap -= endcap_neg
#
#        #TODO: this pagoda doesnt taste like snozberries.
#        #add the pagoda fasteners
#        pagoda_nozzle = cylinder(d1=self.tube_diameter+self.inlet_thickness, \
#                                    d2=self.tube_diameter-self.inlet_thickness, \
#                                    h=self.tube_diameter, _fn=500, center=True)
#        #pagoda_nozzle_neg = cylinder(d1=self.tube_diameter, \
#        pagoda_nozzle_neg = cylinder(r=self.tube_diameter/2-self.inlet_thickness, \
#                                    h=self.tube_diameter, _fn=500, center=True)
#        pagoda_nozzle -= pagoda_nozzle_neg
#        pagoda_nozzle = pagoda_nozzle\
#                .up(self.tube_diameter/2 + self.tube_diameter/4 + self.wall_thickness/2)
#                                #.up(self.wall_thickness + self.height/2)
#        endcap += pagoda_nozzle
#        endcap = endcap.up(self.height/2 + self.tube_diameter/8)
#
#        #NOTE: 2*wall_thickness may be incorrect but passes my tests, 
#        #      look here for render errors on inlet
#        arc_angle = sin((self.tube_diameter+self.inlet_thickness+2*self.wall_thickness)/(2*mean))*180/pi
#        #move into position on self.object
#        #NOTE: up by 1.5*wall_thickness doesnt make sense to me but passes test, 
#        #      look here for endcap related errors
#        endcap = endcap\
#                    .forward(mean)\
#                    .rotate([0, 0, arc_angle-90])\
#                    .up(self.height/2)
#                    #.up(self.height+1.5*self.wall_thickness)
#        endcap_neg = endcap_neg\
#                    .forward(mean)\
#                    .rotate([0, 0, arc_angle-90])\
#                    .up(self.height/2)
#                    #.up(self.height+1.5*self.wall_thickness)
#        self.object += endcap
#        self.object -= endcap_neg
#
#        #add the male only interconnect
#        self.is_inlet = True
#        self.__add_interconnect()
#
#        return self
    '''
    same as inlet but doesnt have outlet and the tube goes
    all the way through.
    '''
    def endcap(self):
        #TODO: extend the middle inside segment
        mean = (self.radius_major + self.radius_minor)/2
        #create the cylinder
        #endcap = cylinder(d=self.tube_diameter+self.wall_thickness,\
        #                  h=self.height+self.wall_thickness,\
        #                  _fn=500, center=True)
        #endcap_neg = cylinder(d=self.tube_diameter, \
        #                    h=self.height+self.wall_thickness,\
        #                    _fn=500, center=True)
        #TODO: ensure nozzles dont hole this and there arent leaks
        endcap = cylinder(d=self.tube_diameter,\
                          h=self.height+self.wall_thickness+self.tube_diameter,\
                          _fn=500, center=True)
        #TODO: subtract after adding nozzles
        endcap_neg = cylinder(r=self.tube_diameter/2 - self.inlet_thickness, \
                            h=self.height+self.wall_thickness+self.tube_diameter,\
                            _fn=500, center=True)
        endcap -= endcap_neg

        #add the pagoda fasteners
        #TODO: ensure inlet_thickness is sufficient, if this leaks alot of 
        #      pressure will be lost and wont be detected by the user.
        pagoda_nozzle = cylinder(d1=self.tube_diameter+self.inlet_thickness, \
                                    d2=self.tube_diameter, \
                                    h=self.tube_diameter, _fn=500, center=True)
        pagoda_nozzle_neg = cylinder(r=self.tube_diameter/2-self.inlet_thickness, \
                                    h=self.tube_diameter, _fn=500, center=True)
        #pagoda_nozzle_neg = cylinder(d1=self.tube_diameter, \
        #                            d2=self.tube_diameter, \
        #                            h=self.tube_diameter, _fn=500, center=True)
        pagoda_nozzle -= pagoda_nozzle_neg

        pagoda_nozzle = pagoda_nozzle\
                                .up(self.wall_thickness + self.height/2 + self.tube_diameter/2)
        endcap += pagoda_nozzle

        #now create another pagoda nozzle for the bottom
        pagoda_nozzle = pagoda_nozzle\
                                .rotate([180,0,0])
        endcap += pagoda_nozzle

        #NOTE: 2*wall_thickness may be incorrect but passes my tests, 
        #      look here for render errors on inlet
        arc_angle = sin((self.tube_diameter+self.inlet_thickness+2*self.wall_thickness)/(2*mean))*180/pi
        #move into position on self.object
        #NOTE: up by 1.5*wall_thickness doesnt make sense to me but passes test, 
        #      look here for endcap related errors
        endcap = endcap\
                    .forward(mean)\
                    .rotate(self.angle/2-90)\
                    .up(self.height)
        endcap_neg = endcap_neg\
                    .forward(mean)\
                    .rotate(self.angle/2-90)\
                    .up(self.height)
        self.object += endcap
        self.object -= endcap_neg

        #add the female only interconnect
        self.is_endcap = True
        #TODO: interconnect is subtracting the endcap
        self.__add_interconnect()

        return self


    def build(self):
        return self.object

# TODO: rename nozzle_wall_thickness to a more intuitive spacing name
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
    assert (
        initial_radius < final_radius
    ), "ERROR: invalid nozzle and tube diameter, did you enter the radius measurements backwards?"
    assert (
        nozzle_diameter < tube_diameter
    ), "ERROR: nozzles must be smaller than the tubing!"

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

    #TODO: builder object should be inherited for building state then 
    #      returning a seperate constructed class that builds the object.
    #TODO: builder object should hide much more of the configuration. too many methods all at once
    #TODO: was additive in shell_angle and:
    #.ang(shell_angle)\
    #.second_ang(angle)\
    #TODO: TEST
    #Spray_Rig = SprayRig()\
    #                    .rad_maj(final_radius)\
    #                    .rad_min(initial_radius)\
    #                    .ang(angle)\
    #                    .hght(rig_depth+2*wall_thickness)\
    #                    .second_rad_maj(final_radius-wall_thickness)\
    #                    .second_rad_min(initial_radius+wall_thickness)\
    #                    .second_ang(shell_angle)\
    #                    .second_hght(rig_depth)\
    #                    .nozzle_rad(nozzle_diameter/2)\
    #                    .nozzle_hght(wall_thickness)\
    #                    .nozzle_wall_thick(nozzle_wall_thickness)\
    #                    .wall_thick(wall_thickness)\
    #                    .lid_thick(lid_thickness)\
    #                    .lid_len(lid_length)\
    #                    .tube_diam(tube_diameter)\
    #                    .inlet_thick(inlet_thickness)\
    #                    .center(True)\
    #                    .circle_arc_shell()\
    #                    .nozzle_array()\
    #                    .add_lip()\
    #                    .middle()\
    #                    .build()
    #                    #.endcap()\
    #                    #.inlet()\
    #                    #TODO: consolidate endcap and inlet nozzle parameterization
    #                    #.add_fasteners()\
    #                    #.middle()\
    #                    #TODO: nozzle_array shouldnt have to go first, also is not rendering correctly

    #                    #TODO: nozzle_array takes a long time to process, only run in production render this has been tested

    #                    #.circle_arc_segment()\
    #                    #.middle()\
    #                    #.inlet()\
    ##TODO: rotate into position
    #Spray_Rig = Spray_Rig.rotate([90,0,0])
    ##print("rendering.. " + str(index))
    #filename = "x" + str(num_segments) + "_" + "Spray_Rig_Segments" #+ str(index + 1)
    #scad_render_to_file(Spray_Rig, filename + ".scad")
    #os.system("openscad -o " + filename + ".stl " + filename + ".scad &")

    #TODO: inlet is just middle
    for enum in ["middle",  "endcap"]:
        #Configure
        Spray_Rig = SprayRig()\
                            .rad_maj(final_radius)\
                            .rad_min(initial_radius)\
                            .ang(angle)\
                            .hght(rig_depth+2*wall_thickness)\
                            .second_rad_maj(final_radius-wall_thickness)\
                            .second_rad_min(initial_radius+wall_thickness)\
                            .second_ang(shell_angle)\
                            .second_hght(rig_depth)\
                            .nozzle_rad(nozzle_diameter/2)\
                            .nozzle_hght(wall_thickness)\
                            .nozzle_wall_thick(nozzle_wall_thickness)\
                            .wall_thick(wall_thickness)\
                            .lid_thick(lid_thickness)\
                            .lid_len(lid_length)\
                            .tube_diam(tube_diameter)\
                            .inlet_thick(inlet_thickness)\
                            .center(True)\
                            .circle_arc_shell()\
                            .nozzle_array()\
                            .add_lip()
        #Specify
        cur = getattr(Spray_Rig, enum)()
        Spray_Rig = cur.build()
        Spray_Rig = Spray_Rig.rotate([90,0,0])
        #Render
        filename = None
        if enum == "middle":
            filename = "x" + str(num_segments-1) + "_" + "Spray_Rig_Segments" + "_" + enum
        else:
            filename = "Spray_Rig_Segment" + "_" + enum

        #filename = "x" + str(num_segments) + "_" + "Spray_Rig_Segments" + "_" + enum
        scad_render_to_file(Spray_Rig, filename + ".scad")
        os.system("openscad -o " + filename + ".stl " + filename + ".scad &")

if __name__ == "__main__":
    config = toml.load("configuration.toml")
    spray_rig(**config)
