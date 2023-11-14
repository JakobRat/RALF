"""
Data Structures for LEF Parser
Author: Tri Minh Cao
Email: tricao@utdallas.edu
Date: August 2016
"""
from util import *

class Statement:
    """
    General class for all types of Statements in the LEF file
    """

    def __init__(self):
        pass

    def parse_next(self, data):
        """
        Method to add information from a statement from LEF file to the
        Statement object.
        :param data: a list of strings that contains pieces of information
        :return: 1 if parsing is done, -1 if error, otherwise, return the
        object that will be parsed next.
        """
        # the program assumes the syntax of LEF file is correct
        if data[0] == "MACRO":
            name = data[1]
            new_state = Macro(name)
            return new_state
        elif data[0] == "LAYER" and len(data) == 2: # does not have ;
            name = data[1]
            new_state = Layer(name)
            return new_state
        elif data[0] == "VIA":
            name = data[1]
            new_state = Via(name)
            return new_state
        elif data[0] == "END":
            return 1
        return 0

    def __str__(self):
        """
        turn a statement object into string
        :return: string representation of Statement objects
        """
        s = ""
        s += self.type + " " + self.name
        return s


class Macro(Statement):
    """
    Macro class represents a MACRO (cell) in the LEF file.
    """

    def __init__(self, name):
        # initiate the Statement superclass
        Statement.__init__(self)
        self.type = 'MACRO'
        self.name = name
        # other info is stored in this dictionary
        self.info = {}
        # pin dictionary
        self.pin_dict = {}

    def __str__(self):
        """
        turn a statement object into string
        :return: string representation of Statement objects
        """
        s = ""
        s += self.type + " " + self.name + "\n"
        for key in self.info:
            if key == "PIN":
                s += "    " + key + ":\n"
                for pin in self.info[key]:
                    s += "    " + str(pin) + "\n"
            else:
                s += "    " + key + ": " + str(self.info[key]) + "\n"
        return s

    def parse_next(self, data):
        """
        Method to add information from a statement from LEF file to a Macro
        object.
        :param data: a list of strings that contains pieces of information
        :return: 0 if in progress, 1 if parsing is done, -1 if error,
        otherwise, return the object that will be parsed next.
        """
        if data[0] == "CLASS":
            self.info["CLASS"] = data[1]
        elif data[0] == "ORIGIN":
            x_cor = float(data[1])
            y_cor = float(data[2])
            self.info["ORIGIN"] = (x_cor, y_cor)
        elif data[0] == "FOREIGN":
            self.info["FOREIGN"] = data[1:]
        elif data[0] == "SIZE":
            width = float(data[1])
            height = float(data[3])
            self.info["SIZE"] = (width, height)
        elif data[0] == "SYMMETRY":
            self.info["SYMMETRY"] = data[1:]
        elif data[0] == "SITE":
            self.info["SITE"] = data[1]
        elif data[0] == "PIN":
            new_pin = Pin(data[1])
            self.pin_dict[data[1]] = new_pin
            if "PIN" in self.info:
                self.info["PIN"].append(new_pin)
            else:
                self.info["PIN"] = [new_pin]
            return new_pin
        elif data[0] == "OBS":
            new_obs = Obs()
            self.info["OBS"] = new_obs
            return new_obs
        elif data[0] == "END":
            if data[1] == self.name:
                return 1
            else:
                return -1
        return 0

    def get_pin(self, pin_name):
        return self.pin_dict[pin_name]


class Pin(Statement):
    """
    Class Pin represents a PIN statement in the LEF file.
    """

    def __init__(self, name):
        Statement.__init__(self)
        self.type = "PIN"
        self.name = name
        self.info = {}

    def __str__(self):
        s = ""
        for layer in self.info["PORT"].info["LAYER"]:
            s += layer.type + " " + layer.name + "\n"
        return s

    def parse_next(self, data):
        if data[0] == "DIRECTION":
            self.info["DIRECTION"] = data[1]
        elif data[0] == "USE":
            self.info["USE"] = data[1]
        elif data[0] == "PORT":
            new_port = Port()
            self.info["PORT"] = new_port
            return new_port
        elif data[0] == "SHAPE":
            self.info["SHAPE"] = data[1]
        elif data[0] == "END":
            if data[1] == self.name:
                return 1
            else:
                return -1
        # return 0 when we parse a undefined statement
        return 0

    def is_lower_metal(self, split_layer):
        return self.info["PORT"].is_lower_metal(split_layer)

    def get_top_metal(self):
        return self.info["PORT"].get_top_metal()


class Port(Statement):
    """
    Class Port represents an PORT statement in the LEF file.
    """

    # Note: PORT statement does not have name
    def __init__(self):
        Statement.__init__(self)
        self.type = "PORT"
        self.name = ""
        self.info = {}

    def parse_next(self, data):
        if data[0] == "END":
            return 1
        elif data[0] == "LAYER":
            name = data[1]
            new_layerdef = LayerDef(data[1])
            if "LAYER" in self.info:
                self.info["LAYER"].append(new_layerdef)
            else:
                self.info["LAYER"] = [new_layerdef]
        elif data[0] == "RECT":
            # error if the self.info["LAYER"] does not exist
            self.info["LAYER"][-1].add_rect(data)
        elif data[0] == "POLYGON":
            self.info["LAYER"][-1].add_polygon(data)
        return 0

    def is_lower_metal(self, split_layer):
        lower = True
        for layer in self.info["LAYER"]:
            if compare_metal(layer.name, split_layer) >= 0:
                lower = False
                break
        return lower

    def get_top_metal(self):
        highest = "poly"
        for layer in self.info["LAYER"]:
            if compare_metal(layer.name, highest) > 0:
                highest = layer.name
        return highest




class Obs(Statement):
    """
    Class Obs represents an OBS statement in the LEF file.
    """

    # Note: OBS statement does not have name
    def __init__(self):
        Statement.__init__(self)
        self.type = "OBS"
        self.name = ""
        self.info = {}

    def __str__(self):
        s = ""
        for layer in self.info["LAYER"]:
            s += layer.type + " " + layer.name + "\n"
        return s

    def parse_next(self, data):
        if data[0] == "END":
            return 1
        elif data[0] == "LAYER":
            name = data[1]
            new_layerdef = LayerDef(data[1])
            if "LAYER" in self.info:
                self.info["LAYER"].append(new_layerdef)
            else:
                self.info["LAYER"] = [new_layerdef]
        elif data[0] == "RECT":
            # error if the self.info["LAYER"] does not exist
            self.info["LAYER"][-1].add_rect(data) # [-1] means the latest layer
        elif data[0] == "POLYGON":
            self.info["LAYER"][-1].add_polygon(data)
        return 0


class LayerDef:
    """
    Class LayerDef represents the Layer definition inside a PORT or OBS
    statement.
    """

    # NOTE: LayerDef has no END statement
    # I think I still need a LayerDef class, but it will not be a subclass of
    #  Statement. It will be a normal object that stores information.
    def __init__(self, name):
        self.type = "LayerDef"
        self.name = name
        self.shapes = []

    def add_rect(self, data):
        x0 = float(data[1])
        y0 = float(data[2])
        x1 = float(data[3])
        y1 = float(data[4])
        points = [(x0, y0), (x1, y1)]
        rect = Rect(points)
        self.shapes.append(rect)

    def add_polygon(self, data):
        points = []
        # add each pair of (x, y) points to a list
        for idx in range(1, len(data) - 2, 2):
            x_cor = float(data[idx])
            y_cor = float(data[idx+1])
            points.append([x_cor, y_cor])
        polygon = Polygon(points)
        self.shapes.append(polygon)


class Rect:
    """
    Class Rect represents a Rect definition in a LayerDef
    """

    # Question: Do I really need a Rect class?
    def __init__(self, points):
        self.type = "RECT"
        self.points = points


class Polygon:
    """
    Class Polygon represents a Polygon definition in a LayerDef
    """
    def __init__(self, points):
        self.type = "POLYGON"
        self.points = points


class Layer(Statement):
    """
    Layer class represents a LAYER section in LEF file.
    """
    def __init__(self, name):
        # initiate the Statement superclass
        Statement.__init__(self)
        self.type = "LAYER"
        self.name = name
        self.layer_type = None
        self.spacing_table = None
        self.spacing = None
        self.width = None
        self.pitch = None
        self.direction = None
        self.offset = None
        self.resistance = None
        self.thickness = None
        self.height = None
        self.capacitance = None
        self.edge_cap = None
        self.property = None

    def parse_next(self, data):
        """
        Method to add information from a statement from LEF file to a Layer
        object.
        :param data: a list of strings that contains pieces of information
        :return: 0 if in progress, 1 if parsing is done, -1 if error,
        otherwise, return the object that will be parsed next.
        """
        if data[0] == "TYPE":
            self.layer_type = data[1]
        elif data[0] == "SPACINGTABLE":
            pass
        elif data[0] == "SPACING":
            self.spacing = float(data[1])
        elif data[0] == "WIDTH":
            self.width = float(data[1])
        elif data[0] == "PITCH":
            self.pitch = float(data[1])
        elif data[0] == "DIRECTION":
            self.direction = data[1]
        elif data[0] == "OFFSET":
            self.offset = (float(data[1]), float(data[2]))
        elif data[0] == "RESISTANCE":
            if self.layer_type == "ROUTING":
                self.resistance = (data[1], float(data[2]))
            elif self.layer_type == "CUT":
                self.resistance = float(data[1])
        elif data[0] == "THICKNESS":
            self.thickness = float(data[1])
        elif data[0] == "HEIGHT":
            self.height = float(data[1])
        elif data[0] == "CAPACITANCE":
            self.capacitance = (data[1], float(data[2]))
        elif data[0] == "EDGECAPACITANCE":
            self.edge_cap = float(data[1])
        elif data[0] == "PROPERTY":
            self.property = (data[1], float(data[2]))
        elif data[0] == "END":
            if data[1] == self.name:
                return 1
            else:
                return -1
        return 0

class Via(Statement):
    """
    Via class represents a VIA section in LEF file.
    """
    def __init__(self, name):
        # initiate the Statement superclass
        Statement.__init__(self)
        self.type = "VIA"
        self.name = name
        self.layers = []

    def parse_next(self, data):
        if data[0] == "END":
            return 1
        elif data[0] == "LAYER":
            name = data[1]
            new_layerdef = LayerDef(data[1])
            self.layers.append(new_layerdef)
        elif data[0] == "RECT":
            self.layers[-1].add_rect(data) # [-1] means the latest layer
        elif data[0] == "POLYGON":
            self.layers.add_polygon(data)
        return 0

