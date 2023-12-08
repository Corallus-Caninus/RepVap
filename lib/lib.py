import os
import subprocess
from solid import *
# contains library methods that may be refactored to the SolidPython library
def render_object(render_object, filename, path):
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
    # if on linux
    if os.name == 'posix':
        os.system("openscad -o " +
                filename + ".stl " + filename + ".scad")
    # if on windows
    if os.name == 'nt':
        # TODO: this doesnt work for some reason but did before
        print("openscad -o " + filename + ".stl " + filename + ".scad")
        command = '''powershell & 'C:\Program Files\OpenSCAD\openscad.exe' -o '''+filename+".stl "+filename+".scad"
        subprocess.call(command, shell=True)
        # fix the above command
        print("OpenSCAD has finished rendering the solution.")

