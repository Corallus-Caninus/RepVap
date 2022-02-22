# RepVap
A *majority* 3D printed evaporative cooler.

![alt text](https://dsm01pap006files.storage.live.com/y4mNqyVxHRCuLsbiG1snyHo6H32Yvp5lyeKOjdw8UTLaagMpep6PgvXyYDyVAsrQCaJMA1IWQW5bd5kfneQCrvnepA0ccWRS8XPv6znJRpFzMxWQkzo6voC1-LIzgdc1ezgkpW2hetO1HngxRHAqVOZKXqjaKllZkwiy8OCucqbqAo6xq_7sJmrXo9qRAKZSoqp?width=4160&height=3120&cropmode=none)
A RepVap made with a 5 Gallon bucket cooling a B550M plus motherboard chipset and ryzen 3600 clocked at 4650MHz all cores as a daily workstation.

This project is currently under active development. I have a working RepVap but you may need assistance.
Email me at ward.joshua92@yahoo.com.

requires OpenSCAD and python3 as well as solidpython.
essentially on ubuntu:


apt install openscad

apt install python3

pip install solidpython



Each folder contains a configuration file and a python file. Set the values in the configuration.toml then 
run the python program to generate your STls. A guide on building a RepVap out of a 5 gallon bucket is 
under development.

Suggested Slicing:

It is recommended to print with adaptive layering with tree supports only touching the bed to allow for precision on the print where needed.
These models were sliced in Cura.

# INLET FLANGE
Print standing up so the grooves are printed along the z axis.

# NOZZLE ARRAY
Print with adaptive layering and a low layer height. Reduce the layer width slightly (ex: 0.35mm on 0.4mm diameter nozzle)
nozzles should be touching the bed, this makes the pagoda cones a little difficult (adaptive layering helps) but yields better nozzles.

# WATER BRACKET
Print with the screw mounts touching the bed. Ensure good overlap with infill so the screw mounts dont seperate when threaded through.


RepVap is a high flow water chiller for cheap aluminum cooling blocks. Its intended use is for 
CPUs and the design is made to be very affordable (~$100 for all the bells and whistles).

RepVap is designed with SolidPython an OpenSCAD wrapper. All designs are parametric such that any container 
could be used (A gable fan on a large trash bin is not out of the question). All variations of the design can be changed in the respective configuration files for different 
motherboards or applications.

Bill of Materials: 
      https://docs.google.com/spreadsheets/d/1tjXMvY8Ov9ljX92phIoySIcV0aM8psuqZ-wuVCSjxi4/edit?usp=sharing
      
My initial prototype:
      https://docs.google.com/spreadsheets/d/1ESvuHrNF-DnBGYz-8B5h_lNTvHFGtqw5J4fCP3uyhEo/edit?usp=sharing

I also recommend the following Youtube videos:

      desertsun02's videos on DIY evaporative cooling.

      Major Hardware's video on 3d printed evaporative coolers and PC water cooling loops.

NOTE: RepVap cannot print itself. the name is simply an omage to the amazing RepRap project and the culture of 
      innovation therein.
