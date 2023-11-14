"""
DEF Parser
Author: Tri Minh Cao
Email: tricao@utdallas.edu
Date: August 2016
"""

from lef_def_parser.def_util import *
from lef_def_parser.util import *


class DefParser:
    """
    DefParser will parse a DEF file and store related information of the design.
    """

    def __init__(self, def_file):
        self.file_path = def_file
        # can make the stack to be an object if needed
        self.stack = []
        # store the statements info in a list
        self.sections = []
        self.property = None
        self.components = None
        self.pins = None
        self.nets = None
        self.tracks = []
        self.gcellgrids = []
        self.rows = []
        self.diearea = None
        self.version = None
        self.dividerchar = None
        self.busbitchars = None
        self.design_name = None
        self.units = None
        self.scale = None

    def parse(self):
        """
        Main method to parse the DEF file
        :return: void
        """
        print ("Start parsing DEF file...")
        # open the file and start reading
        f = open(self.file_path, "r+")
        # the program will run until the end of file f
        for line in f:
            # split the string by the plus '+' sign
            parts = split_plus(line)
            for each_part in parts:
                # split each sub-string by space
                info = split_space(each_part)
                if len(info) > 0:
                    #print info
                    if info[0] == "PINS":
                        new_pins = Pins(int(info[1]))
                        self.stack.append(new_pins)
                        # print (new_pins.type)
                    elif info[0] == "VERSION":
                        self.version = info[1]
                    elif info[0] == "DIVIDERCHAR":
                        self.dividerchar = info[1]
                    elif info[0] == "BUSBITCHARS":
                        self.busbitchars = info[1]
                    elif info[0] == "DESIGN" and len(info) <= 3:
                        # differentiate with the DESIGN statement inside
                        # PROPERTYDEFINITIONS section.
                        self.design_name = info[1]
                    elif info[0] == "UNITS":
                        self.units = info[2]
                        self.scale = info[3]
                    elif info[0] == "PROPERTYDEFINITIONS":
                        new_property = Property()
                        self.stack.append(new_property)
                    elif info[0] == "DIEAREA":
                        info_split = split_parentheses(info)
                        pt1 = (int(info_split[1][0]), int(info_split[1][1]))
                        pt2 = (int(info_split[2][0]), int(info_split[2][1]))
                        self.diearea = [pt1, pt2]
                    elif info[0] == "COMPONENTS":
                        new_comps = Components(int(info[1]))
                        self.stack.append(new_comps)
                    elif info[0] == "NETS":
                        new_nets = Nets(int(info[1]))
                        self.stack.append(new_nets)
                    elif info[0] == "TRACKS":
                        new_tracks = Tracks(info[1])
                        new_tracks.pos = int(info[2])
                        new_tracks.do = int(info[4])
                        new_tracks.step = int(info[6])
                        new_tracks.layer = info[8]
                        self.tracks.append(new_tracks)
                    elif info[0] == "GCELLGRID":
                        new_gcellgrid = GCellGrid(info[1])
                        new_gcellgrid.pos = int(info[2])
                        new_gcellgrid.do = int(info[4])
                        new_gcellgrid.step = int(info[6])
                        self.gcellgrids.append(new_gcellgrid)
                    elif info[0] == "ROW":
                        new_row = Row(info[1])
                        new_row.site = info[2]
                        new_row.pos = (int(info[3]), int(info[4]))
                        new_row.orient = info[5]
                        new_row.do = int(info[7])
                        new_row.by = int(info[9])
                        new_row.step = (int(info[11]), int(info[12]))
                        self.rows.append(new_row)
                    elif info[0] == "END":
                        if len(self.stack) > 0:
                            self.sections.append(self.stack.pop())
                        # print ("finish")
                    else:
                        if len(self.stack) > 0:
                            latest_obj = self.stack[-1]
                            latest_obj.parse_next(info)
        f.close()
        # put the elements in sections list into separate variables
        for sec in self.sections:
            if sec.type == "PROPERTY_DEF":
                self.property = sec
            elif sec.type == "COMPONENTS_DEF":
                self.components = sec
            elif sec.type == "PINS_DEF":
                self.pins = sec
            elif sec.type == "NETS_DEF":
                self.nets = sec
        print ("Parsing DEF file done.\n")

    
    def write_def(self, new_def, back_end=True, front_end=True):
        """
        Write a new def file based on the information in the DefParser object.
        Note: this method writes all information
        :param new_def: path of the new DEF file
        :param back_end: write BEOL information or not.
        :param front_end: write FEOL info or not.
        :return: void
        """
        f = open(new_def, mode="w+")
        print("Writing DEF file...")
        f.write(self.to_def_format())
        print("Writing done.")
        f.close()


