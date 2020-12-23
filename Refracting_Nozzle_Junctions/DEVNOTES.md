# DESIGN

Treehouse Mode: integrate rafting into tree support structure, emphasize bridging. 

heirarchical parametric build: once one simpler object is defined in the parts list,
its parameters will be reused and built upon for more complex parts (modular iterative approach)

it is the research goal of this project in particular to implement object oriented design 
in parametric CAD software. The long term goal of this will be to implement primitives such
as snap-on components parametrically and arbitrarily into other designs to more easily create components
that can be connected without fasteners and scaled outside the print volume.
    - The ultimate goal of this would be a pull request to solidpython or a forked library with said
        primitive. pull request would require very simple and abstract implementation on par with hole()().

        This is an example of a permanent joint, a removable fastener is more complex but interesting for 
        modularly replacable/repairable parts:
        male, female = joint(size, offset)(first_object, second_object) 
            - where male and female are respective first and second objects with addded joints/cavities 
              and first/second objects are unioned for the joining surface solution given offset.
            - use union() and rectangular prism (offset sets dimensions) to implement offset. 
              fill the resultant manifold with joints/cavities then add back to first and second 
              object respectively. offset is Point tuple type where second coordinates are 
              rect prism lengths and first are center coordinate projecting from first into second.
            - exact fastener geometry is generative solving for max surface area given size,
              which is proportional to strength and plasticity. Size also dictates whether printing 
              is practical. Can also pass in a joint_geometry object which may be simpler to implement.
              size fills offset union manifold.
            - consider cones with 1 slit along axis of rotation as generic joint geometry to 
              maximize reverse force. Can have multiple cones in a sequence given depth 
              of manifold and size parameter.
            - size of None returns a maximized size given offset unioned manifold.

# DESIGN FLOW 

create junctions for t and cross connectors using functional paradigm 
(cross builds on t junction)

create nozzle using t/cross junction that adds a refracting cone as a
separate snap on component with a smaller nozzle size 
(~1.2-1.7mm empirically, 2mm is probably best).

create a number on the filename to indicate how many are required 
to match tube diameter cross section (this is a simple solution.)
