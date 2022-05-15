import tkinter as tk
import tkinter.filedialog
from tkinter import ttk
import os
# import ffmpeg
from PIL import *
from time import time
import subprocess
import toml

# local imports
# from parser import parse
from draw_lid import draw_lid
# from draw_water_bracket import draw_water_bracket
import sys
sys.path.append('../')

# create a gui that can load in and edit all files in RepVap


'''parse the given toml file string and return a dictionary'''


def parse(toml_string):
    # toml_dict = toml.loads(toml_string)
    # open the toml file and read it as a string
    with open(toml_string, 'r') as toml_file:
        toml_string = toml_file.read()

    return toml_string


# TODO: rework this for windows. Re evaluate strategy for visualizing and iterating parameters.
class Interactive_RepVap(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("RepVap Interactive")
        self.geometry("800x600")

        # create a frame for the text box and scroll bar
        self.txt_frm = tk.Frame(self)
        self.txt_frm.pack(side="top", fill="both", expand=True)
        self.txt_frm.grid_rowconfigure(0, weight=1)
        self.txt_frm.grid_columnconfigure(0, weight=1)

        # create a text box widget
        self.txt = tk.Text(self.txt_frm, borderwidth=3, relief="sunken")
        self.txt.config(font=("consolas", 12), undo=True, wrap='word')
        self.txt.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

        # create a scroll bar for the text box
        self.scrollb = tk.Scrollbar(self.txt_frm, command=self.txt.yview)
        self.scrollb.grid(row=0, column=1, sticky='nsew')
        self.txt['yscrollcommand'] = self.scrollb.set

        # create a frame for the buttons
        self.btn_frm = tk.Frame(self)
        self.btn_frm.pack(side="top", fill="x", expand=False)
        self.btn_frm.grid_columnconfigure(0, weight=1)

        # create buttons
        self.load_btn = ttk.Button(
            self.btn_frm, text="Load RepVap File", command=self.load_file)
        self.load_btn.grid(row=0, column=0, sticky='ew')
        self.save_btn = ttk.Button(
            self.btn_frm, text="Save RepVap File", command=self.save_file)
        self.save_btn.grid(row=1, column=0, sticky='ew')
        self.quit_btn = ttk.Button(
            self.btn_frm, text="Quit", command=self.quit)
        self.quit_btn.grid(row=2, column=0, sticky='ew')

        # create a frame for the video
        self.video_frm = tk.Frame(self)
        self.video_frm.pack(side="top", fill="both", expand=True)
        self.video_frm.grid_rowconfigure(0, weight=1)
        self.video_frm.grid_columnconfigure(0, weight=1)

        # create a button to render and play the video
        self.render_btn = ttk.Button(
            self.video_frm, text="Render", command=self.render)
        self.render_btn.grid(row=0, column=0, sticky='ew')

        # display the text "Rendering.." when the Render button is pressed
        self.render_text = tk.StringVar()
        self.render_text.set("Ready to Render.")

        # create a label to display the text in the root window
        self.render_label = tk.Label(
            self.video_frm, textvariable=self.render_text)
        self.render_label.grid(row=1, column=0, sticky='ew')

        # either draw these on one canvas or create buttons
        # to select and close one at a time
        draw_lid()
        print("finished drawing lid")
        # print("drawing the water_bracket")
        # draw_water_bracket()

        # set the text box to be the size of the window
        self.txt.config(width=self.winfo_width(), height=self.winfo_height())

        # bind the <Return> key to run
        self.bind('<Return>', self.run)

        # bind the <Control-s> key to save
        self.bind('<Control-s>', self.save_file)

        # bind the <Control-o> key to load
        self.bind('<Control-o>', self.load_file)

        # bind the <Control-q> key to quit
        self.bind('<Control-q>', self.quit)

        # set the text to be empty
        self.txt.insert('1.0', "")
        self.txt.focus_set()

    def load_file(self, *args):
        # change file type on the next line to be toml
        ftypes = [('toml', '*.toml'), ('All files', '*')]
        dlg = tkinter.filedialog.Open(self, filetypes=ftypes)
        fl = dlg.show()
        if fl != '':
            # read in the file content and parse it then display it
            with open(fl, 'r') as f:
                self.txt.insert(1.0, f.read())
                self.txt.focus_set()
                content = parse(self.txt.get(1.0, tk.END))
                self.txt.delete(1.0, tk.END)
                self.txt.insert(1.0, content)

    # make the same changes made to load_file
    def save_file(self, *args):
        ftypes = [('toml', '*.toml'), ('All files', '*')]
        dlg = tkinter.filedialog.SaveAs(self, filetypes=ftypes)
        fl = dlg.show()
        if fl != '':
            with open(fl, 'w') as f:
                f.write(self.txt.get(1.0, tk.END))

    def render(self):
        '''
        renders the given file name with Openscad to
        a .stl and and updates the video widget to show a slideshow of the rendered files.
        '''
        # get all scad files in the directory above the module dir by os.walk then call openscad on them to render them
        scad_files = []
        for root, dirs, files in os.walk(os.path.join(os.path.dirname(__file__), "..")):
            for file in files:
                if file.endswith(".scad"):
                    scad_files.append(os.path.join(root, file))

        for target_file in scad_files:
            # while these are rendering, we'll need to update the user
            self.render_text.set("Rendering {}".format(target_file))
            # update the text box
            self.render_label.update()

            output_file = target_file.replace(".scad", ".stl")
            # call this in parallel
            subprocess.call(["openscad", "-o", output_file, target_file])
            # now call openscad for a png
            subprocess.call(
                ["openscad", "-o", output_file.replace(".stl", ".png"), target_file])

        # reset the Render text
        self.render_text.set("Ready to Render.")
        self.render_label.update()

        # create a list of the files to show in the slideshow using all files in the above directory recursively searching for .png files
        files = []
        target_file = "tmp.mp4"
        module_directory = os.path.dirname(os.path.realpath(__file__))
        # now remove the file name from the path
        module_directory = module_directory.replace(
            os.path.basename(module_directory), "")
        # now go up one directory
        module_directory = os.path.dirname(module_directory)
        # add the forward slash to the end of the path
        module_directory = module_directory + "/"
        print("got dir " + module_directory)

        # walk module directory create a list of all png files
        results = []
        for root, dirs, files in os.walk(module_directory):
            for file in files:
                if file.endswith(".png"):
                    print("got png" + file)
                    results.append(os.path.join(root, file))
        files = results

        # set the input file names
        ffmpeg.input(files)
        # set the output video file name
        ffmpeg.output(target_file + ".mp4")

        # set the output file format
        ffmpeg.set_format('mp4')

        # render the files
        ffmpeg.run()

        # update the video widget to show the slideshow
        self.video_frm.destroy()
        self.video_frm = tk.Frame(self)
        self.video_frm.pack(side="top", fill="both", expand=True)
        self.video_frm.grid_rowconfigure(0, weight=1)
        self.video_frm.grid_columnconfigure(0, weight=1)

        self.slideshow = tk.Label(self.video_frm)
        self.slideshow.grid(row=0, column=0, sticky="nsew")
        self.slideshow.pack(fill="both", expand=True)
        self.slideshow.config(borderwidth=3, relief="sunken")

        # create a slideshow of the files
        for i in range(len(files)):
            self.slideshow.image = Image.open(files[i])
            self.slideshow.config(
                image=self.slideshow.image, width=self.slideshow.image.width, height=self.slideshow.image.height)
            self.slideshow.image.close()
            self.slideshow.update()
            time.sleep(1)

    def run(self, *args):
        pass

    def quit(self, *args):
        self.destroy()
        self.quit()


# now let's run it
if __name__ == "__main__":
    app = Interactive_RepVap()
    app.mainloop()
