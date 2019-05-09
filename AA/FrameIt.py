#!/usr/bin/env python
# coding: utf-8

# # FrameIt: Bin by the time value of a quaternion all positions in space

# What is the right relationship for time to space?
# 
# Time is orthagonal to space. This means two opposite things. First, they are profoundly different. Therefore the way you keep track of them must be unambiguously different. Second, they have an intimate relationship, both need each other.
# 
# Let's say one has a pile of quaternions that all have values that range from -1 to 1. How can this be graphed? It cannot be done in 3D space since a quaternion has 4 degrees of freedom. It can be done as a 3D animation. 
# 
# If one bin's the pile of quaternions by time, then each bin would represent the spatial information for that particular time window. The FrameIt class will take a quaternion series (many quaternions) and return a dictionary of frames. This satisfies the above guide about being orthogonal: a frame is not a location in space, but only a frame+spatial info can make a part of an animation.

# In[1]:


import math
import collections as co
import numpy as np
import sympy as sp
import pandas as pd

import unittest
from bunch import Bunch

# Tools for manipulating quaternions.
from Q8 import Q8, Q8States;


# Needed things:
# 
# 1. Start time int
# 2. End Time int
# 3. N frames
# 4. M Q8States
# 

# To do:
# Print out tx, ty, dz values.

# In[2]:


class FrameIt(object):
    """Given a Q8States, bins on time and write the values to a Dictionary."""
    
    def __init__(self, states, start=0, end=0, frames=100, quiet=False):
        
        self.opt = Bunch()
        self.opt.states = states
        self.opt.start = 0
        self.opt.end = 0
        self.opt.frames = frames
        self.opt.quiet = quiet
        
        # 2x the size but makes plots tx, ty, tz possible.
        self.txyz = states.txyz()
        if (start == 0) and (end == 0):
            self.opt.start = min(states.t())
            self.opt.end = max(states.t())
        
        self.events = Bunch()
        self.intervals = Bunch()
        
    def split_events(self, states=None, quiet=False):
        """Splits events into time and space arrays. Returns a pandas DataFrame"""
            
        if states is None:
            states = self.opt.states
            
        states_t = states.t()
        states_xyz = states.xyz()
            
        df_paired = pd.DataFrame([states_t, states_xyz], dtype="float", index=["t", "xyz"])
        df_txyz = df_paired.T
        
        if not (quiet or self.opt.quiet):
            print("t/xyz:\n", df_txyz)
 
        return df_txyz
            
    def __get_time_frames(self):
        """A linear space for time frames, can be based on values passes or when instance created."""
        
        t_frames = np.linspace(self.opt.start, self.opt.end, self.opt.frames)
        
        # Get all the intervals, needed to know which ones are empty, if any.
        df_t_frames = pd.DataFrame(t_frames)
        df_t_frames_cut = pd.cut(df_t_frames[0], t_frames, include_lowest=True)
        df_t_frames_cut_array = df_t_frames_cut.tolist()
        df_t_frames_cut_array.pop(0)
        
        for df_t_frame in df_t_frames_cut_array:
            self.intervals[df_t_frame] = ''
        
        return t_frames
    
    def bin_events_by_time(self, df_txyz, quiet=False):
        """Given a DataFrame with time and xyz, returns the DataFrame with a t_frame variable set."""            
        
        t_frames = self.__get_time_frames()
        
        df_txyz['t_frames'] = pd.cut(df_txyz.iloc[:, 0], t_frames, include_lowest=True)
        
        if not (quiet or self.opt.quiet):
            print("t/xyz bins:\n", df_txyz)
               
        return df_txyz
            
    def space_bins(self, df_txyz, quiet=False):
        """Create a dictionary with locations all the locations in space, with blanks as needed."""
 
        space = co.OrderedDict()
        
        counts = Bunch()
        counts.without_events = 0
        counts.with_events = 0
        counts.max_events = 0
        
        for i, interval in enumerate(self.intervals):
             
            if interval in df_txyz['t_frames'].values:
            
                events = df_txyz[df_txyz['t_frames'] == interval].iloc[:, 1].values
                space[i] = events
                counts.with_events += 1
                
                if len(events) > counts.max_events:
                    counts.max_events = len(events)
                    
            else:
                space[i] = ''
                counts.without_events += 1

        if not quiet or self.opt.quiet:
            
            for k, v in space.items():
            
                print("space_bins: {}/{}".format(k, v))
        
        print("frames without events: {}".format(counts.without_events))
        print("frames with events: {}".format(counts.with_events))
        print("Max events in one frame: {}".format(counts.max_events))
        
        return space
    
    def run(self):
        """Call functions to return dictionary of frames with locations in space."""
        
        df_txyz = self.split_events()
        self.bin_events_by_time(df_txyz)
        return self.space_bins(df_txyz)
        


# In[3]:


class TestFrameIt(unittest.TestCase):
    
    q1 = Q8([1, 1, 3, 4])
    q2 = Q8([2, 2, -3, -4])
    q3 = Q8([3, 3, 3, 4])
    q4 = Q8([4, 4, 3, 2])
    tri_state = Q8States([q1, q2, q3])
    five_state = Q8States([q1, q2, q3, q4, q3.conj()])
    
    def test_1000_opt(self):
        FIt = FrameIt(self.tri_state)
        self.assertTrue(FIt.opt.start == 1)
        self.assertTrue(FIt.opt.end == 3)
        self.assertTrue(FIt.opt.frames == 100)

    def test_1100_split_events(self):
        fi = FrameIt(self.tri_state)
        df = fi.split_events()
        self.assertTrue(df.iloc[0, 0] == 1.0)
        self.assertTrue(df.iloc[1, 0] == 2.0)
        self.assertTrue(df.iloc[2, 0] == 3.0)
        
    def test_1200_bin_events_by_time(self):    
        fi = FrameIt(self.tri_state, frames=3)
        df_split = fi.split_events(quiet=True)
        df_bin = fi.bin_events_by_time(df_split)
        self.assertTrue(df_bin.shape == (3, 3))
        self.assertTrue(df_bin[['t_frames']].iloc[2,0] == pd.Interval(2.0, 3.0, closed='right'))
     
    def test_1300_space_bins(self):
        fi = FrameIt(self.five_state, frames=10)
        df_split = fi.split_events(quiet=True)
        df_bin = fi.bin_events_by_time(df_split, quiet=True)
        df_space_bins = fi.space_bins(df_bin)
        self.assertTrue(len(df_space_bins[5]) == 2)
        
suite = unittest.TestLoader().loadTestsFromModule(TestFrameIt())
unittest.TextTestRunner().run(suite);


# In[4]:


get_ipython().system('jupyter nbconvert --to python FrameIt.ipynb')


# In[ ]:




