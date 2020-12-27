# a GUI that processes photogrammetry of a user supplied
# image to increase precision and reduce measurement labor
import tkinter as tk
import PIL
import numpy as n


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widget()

    def create_widget(self):
        # TODO: just use pack this time it's much simpler and resize scales
        self.arg = tk.StringVar() 
        self.args = []

        self.item = tk.Entry(self, textvariable = self.arg)
        self.item.pack(side="left")

        self.test_button = tk.Button(self, text='debug', command= self.debug_print)
        self.test_button.pack(side="right")

        self.exit_button = tk.Button(
            self, text="EXIT", fg="green", command=self.master.destroy)
        self.exit_button.pack(side="bottom")
    
    def debug_print(self):
        print("{}".format(self.arg.get()))
        self.args.append(self.arg.get())
        print("{}".format(self.args))

root = tk.Tk()
app = Application(master=root)
app.master.title("Water Block Mount Generator")
app.mainloop()


# TODO: need parallax photogrammetry to get depth since VRMs are definitely not coplanar to screws etc.

# request user dimensions of water cooling block (x,y,z)
# this is the only information needed to form a basis for the measurements

# instruct the user to place the water cooling block where they would like it mounted
# take user panoramic nadir video (everyone with an iphone knows how this works)

# request the user clicks twice (for average) each corner of the block, each nozzle and the center

# sorbel filter the image

# compare the surface of the water cooling block found by the bounds of the sorbel edges
# (The sides not including the nozzle, 1/2 the block as a right triangle) to the user found corners,
# if within tolerance proceed, else recommend to flour or dust the object to prevent reflections and restart

# localize all pixels in image solution (calculate mm/pixel)

# have the user click on all screw pixels, entering screw params each time.
# (retain value in window so they can click each screw type in sequence)

# have the user click on all VRM/VRAM etc. corners, bounding a surface (no param entry)

# generate configuration for water_bracket and call.
