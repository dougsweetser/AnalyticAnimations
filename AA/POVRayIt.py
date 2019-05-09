#!/usr/bin/env python
# coding: utf-8

# # Animating Stuff using POVRay

# POVRay makes beautiful ray tracings that look 3D. It does not look like the project is under active development, bummer! A few classes are used to make gif animations.

# In[4]:


import pdb
import re
import unittest
import collections as co
import pandas as pd

from bunch import Bunch
from copy import deepcopy
from glob import glob
from pathlib import Path

# Tools for manipulating quaternions.
from Q8 import Q8, Q8States;
from FrameIt import FrameIt;


# Class DrawIt
# * space_bins, an array of xyz arrays, may be blank string if empty
# * base - default: greens_w_sky.pov
# * delta - default: sphere.pov
# * pov_dict OBJECT, NUMBERS, TEXTURE, SCALE, ROTATE, TRANSLATE,
# * index xyz, txy, tx, ty, tz - default: xyz
# * dirs_dict - default: ../masters, ../pings, ../povs, ../gifs
# * n - frame integer to start with, default: 1000
# 
# functions:
# - read_base
# - read_delta
# - substitute
# - write_pov
# - draw pov
# - add_index
# - **run**, cycles through space_bin

# In[5]:


class DrawIt(object):
    """Given a dictionary of frames with xyz positions, draws frame_N."""
    
    def __init__(self, space_bins, base="green_w_sky.pov", delta="small_sphere.pov",
                 pov_dict=None, key="xyz.2.png", povray_options="-GA +H400 +W400", 
                 dirs_dict=None, output_name='', cleanup=True, n=1000):
        
        self.opt = Bunch()
        self.opt.space_bins = space_bins
        self.opt.base = base
        self.opt.delta = delta
        self.opt.pov_dict = pov_dict
        self.opt.key = key
        self.opt.povray_options = povray_options
        self.opt.dirs_dict = dirs_dict
        self.opt.output_name = output_name
        self.opt.cleanup = True
        self.opt.n = n
        
        if dirs_dict is None:
            # Directories orgainized by extensions, know here as the "key".
            self.opt.dirs = Bunch()
            self.opt.dirs.gif = "pov_files/gifs"
            self.opt.dirs.key = "pov_files/keys"
            self.opt.dirs.master = "pov_files/masters"
            self.opt.dirs.pov = "pov_files/povs"
            self.opt.dirs.png = "pov_files/pngs"
            
        if output_name == '':
            self.opt.output_name = "out.{b}.{d}".format(b=base, d=delta).replace(r'.pov', '')

    def file_to_array(self, dir_name, file_name):
        """Read a file, return an array."""
    
        with open("{dn}/{fn}".format(dn=dir_name, fn=file_name), "r") as fn:
            lines = fn.readlines()
    
        return lines
    
    def array_to_file(self, dir_name, file_name, *lines):
        """Write array to a file. Note: lines can be a list."""
    
        file_name = "{dn}/{fn}".format(dn=dir_name, fn=file_name)
     
        with open(file_name, "w") as fn:
        
            for line in lines:
                for stuff in line:
                    fn.writelines(stuff)
                    
    def array_subs(self, lines, sub_dict):
        """Looks to make all substitutions provided in sub_dict."""
    
        new_lines = []
    
        for line in lines:
        
            for key, value in sub_dict.items():
            
                rewrite = re.sub(key, r'{}'.format(value), line)
                line = rewrite
        
            new_lines.append(rewrite)
        
        return new_lines

    def povray_it(self, input_path, output_path):
        """Given a numbered .pov file,, runs povray on it to create a png file."""
        
        get_ipython().system(' exec 2> /dev/null; povray {self.opt.povray_options} {input_path} +O{output_path}')
        
        return _exit_code
        
    def label_it(self, input_path, label_png_path=''):
        """Adds a label to a png IF a label_png_path is supplied."""
        
        get_ipython().system(' convert {input_path} \\( {label_png_path} -resize 50% \\) -gravity southeast -composite {input_path}')
        
        return _exit_code
    
    def draw_space_bins(self):
        """Draw all the xyz bins using the other functions in a loop."""
        
        base_lines = self.file_to_array(self.opt.dirs.master, self.opt.base)
        delta_lines = self.file_to_array(self.opt.dirs.master, self.opt.delta)
        
        for n, space_bin in self.opt.space_bins.items():
            
            lines = deepcopy(base_lines)
            
            if not isinstance(space_bin, str):
                
                for space in space_bin:
                
                    delta_line = deepcopy(delta_lines)
                    
                    X, Y, Z = space
                    XYZ_dict = {'X':str(X)[:5], 'Y':str(Y)[:5], 'Z':str(Z)[:5]}
                    delta_sub = self.array_subs(delta_line, XYZ_dict)
                    
                    lines.append(delta_sub)
            
            bin_name = "{on}.{n}".format(on=self.opt.output_name,
                                         n=n + self.opt.n)
            print("bin_name: ", bin_name)
            pov_name, png_name = bin_name + ".pov", bin_name + ".png"
            pov_path = "{dn}/{pn}".format(dn=self.opt.dirs.pov, pn=pov_name)
            png_path = "{dn}/{pn}".format(dn=self.opt.dirs.png, pn=png_name)
            
            self.array_to_file(self.opt.dirs.pov, pov_name, lines)
            self.povray_it(pov_path, png_path)
            self.label_it(png_path, "{dn}/{k}".format(dn=self.opt.dirs.key, k=self.opt.key))
                          
        output_pngs = "{dn}/{on}*.png".format(dn=self.opt.dirs.png, on=self.opt.output_name)
        output_gif = "{dn}/{on}.gif".format(dn=self.opt.dirs.gif, on=self.opt.output_name)
        get_ipython().system(' convert {output_pngs} {output_gif}')
                          
        print("created gif: ", output_gif)
        return _exit_code
    
    def cleanup(self):
        """Remove output_name.nnnn.pov and output_name.nnnn.png files."""
        
        pov_paths = "{dn}/{pn}.*.pov".format(dn=self.opt.dirs.pov, pn=self.opt.output_name)
        png_paths = "{dn}/{pn}.*.png".format(dn=self.opt.dirs.png, pn=self.opt.output_name)
        
        p_paths = glob(pov_paths) + glob(png_paths)
        for p_path in p_paths:
            Path(p_path).unlink()


# In[10]:


class TestDrawIt(unittest.TestCase):
    
    q1234 = Q8([1, -.9, -.8, .4])
    dv = Q8([.1, .02, .03, .04])
    q_list = []

    for q in q1234.ops(dv, op="add", dim=40):
        q_list.append(q)

    q_linear_states = Q8States(q_list)
    
    frame_me = FrameIt(q_linear_states, frames=10)
    frame_me_space = frame_me.run()
    draw_me = DrawIt(frame_me_space)
    
    def test_1000_opt(self):
        self.assertTrue(len(self.draw_me.opt.space_bins) > 3)
        self.assertTrue(self.draw_me.opt.base == 'green_w_sky.pov')
        self.assertTrue(self.draw_me.opt.delta == 'small_sphere.pov')
        self.assertTrue(self.draw_me.opt.dirs.pov == 'pov_files/povs')
        self.assertTrue(self.draw_me.opt.key == 'xyz.2.png')
        self.assertTrue(self.draw_me.opt.output_name == 'out.green_w_sky.small_sphere')
        self.assertTrue(self.draw_me.opt.n == 1000)
        
    def test_1010_file_to_array(self):
        
        lines = self.draw_me.file_to_array(self.draw_me.opt.dirs.master, self.draw_me.opt.base)
        self.assertTrue(len(lines) > 10)
        
    def test_1020_array_to_file(self):
        lines = self.draw_me.file_to_array(self.draw_me.opt.dirs.master, self.draw_me.opt.base)
        self.draw_me.array_to_file(self.draw_me.opt.dirs.master, "dummy.bear", lines)
        file_path = Path("{}/{}".format(self.draw_me.opt.dirs.master, "dummy.bear"))
        self.assertTrue(file_path.is_file())
        
    def test_1030_array_subs(self):
        lines = self.draw_me.file_to_array(self.draw_me.opt.dirs.master, "small_sphere.pov")
        XYZ = {'X': 0.1, 'Y': 0.2, 'Z': 0.3}
        new_lines = self.draw_me.array_subs(lines, XYZ)
        print(new_lines)
        self.assertTrue(new_lines[0] == 'sphere{ <0.1,0.2,0.3>,0.1 \n')
        
    def test_1040_povray_it(self):
        exit_code = self.draw_me.povray_it('pov_files/masters/green_w_sky.pov', 'pov_files/pngs/dummy.1000.png')
        self.assertFalse(exit_code)
    
    def test_1050_label_it(self):
        exit_code = self.draw_me.label_it('pov_files/pngs/dummy.1000.png', 'pov_files/keys/xyz.2.png')
        self.assertFalse(exit_code)
    
    def test_1060_draw_space_bins(self):
        exit_code = self.draw_me.draw_space_bins()
        self.assertFalse(exit_code)
    
    def test_1070_cleanup(self):
        self.assertTrue(Path("pov_files/pngs/out.green_w_sky.small_sphere.1000.png").is_file())
        self.draw_me.cleanup()
        self.assertFalse(Path("pove_files/pngs/out.green_w_sky.small_sphere.1000.png").is_file())
    
    def test_9999_cleanUp(self):
        file_path = Path("{}/{}".format(self.draw_me.opt.dirs.master, "dummy.bear"))
        file_path.unlink()
    
suite = unittest.TestLoader().loadTestsFromModule(TestDrawIt())
unittest.TextTestRunner().run(suite);


# ! rm ../.ipynb_checkpoints/pov_generator-checkpoint.ipynb 
# ![](../gifs/out.green_w_sky.small_sphere.gif)

# In[ ]:




