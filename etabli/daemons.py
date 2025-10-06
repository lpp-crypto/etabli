#!/usr/bin/env python

from .utils import *
from .etabli import *


class PrepareDaemon:
    def __init__(self, config):
        self.config = config




    def __enter__(self):
        return self

    
    def __close__(self, exc_type, exc_value, traceback):
        

    


class WaybarDaemon:
    def __init__(self, config, output):
        self.config = config
        self.output = output


    def pango_formatted(self):
        return ""
    # !TODO! pango_formatted


    def __enter__(self):
        return self

    def __close__(self, exc_type, exc_value, traceback):
        pass
