# ========================================================================
#
# SPDX-FileCopyrightText: 2023 Jakob Ratschenberger
# Johannes Kepler University, Institute for Integrated Circuits
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# SPDX-License-Identifier: Apache-2.0
# ========================================================================

from __future__ import annotations
import warnings

class Netlist:
    """
        Class to store parts of a raw ngspice netlist.
        The following parts are stored:
            - raw netlist
            - subcircuits (netlists and names)
            - top netlist
            - parameters of the top netlist
            - title
            
    """
    def __init__(self, raw_netlist : list[str]):
        self._raw_netlist = raw_netlist

        #setup a dict to store the netlists of sub-circuits
        self._subnetlists : dict[str, list[str]]
        self._subnetlists = {}
        
        #setup a list to store the top-level netlist
        self._net : list[str]
        self._net = []

        self._title : str
        self._title = None

        #setup a dict, to store circuit parameters
        self._params : dict[str, str]
        self._params = {}

        #build the netlist
        self._build_Net()
    
    
    def _build_Net(self):
        """
        Build the net from the raw netlist
        
        Returns
        -------
        None.

        """
        #get the netlists of sub-circuits
        self._subnetlists = self._get_subnets(self._raw_netlist)
        
        #get the netlist of the top-circuit
        self._get_top_net()
    
    def get_net(self) -> list[str]:
        """Get the preprocessed netlist.

        Returns:
            list[str]: List of the netlist statements.
        """
        return self._net
    
    def get_title(self) -> str:
        """Get the circuits title.

        Returns:
            str: Circuits title.
        """
        return self._title
    
    def get_params(self) -> dict[str, str]:
        """Get the parameters of the netlist.

        Returns:
            dict[str, str]: key: Parameter name, value: Value of the parameter, as str
        """
        return self._params
    
    def get_subnets(self) -> dict[str, list[str]]:
        """Get all sub-netlists of the netlist.

        Returns:
            dict[str, list[str]]: key: Name of the sub-circuit value: Sub-circuit netlist
        """
        return self._subnetlists
        
    def _get_top_net(self):
        """
            Sets the top netlist in self._net.
        
        Raises
        ------
            ValueError if netlist contains unsupported line. 
            

        Returns
        -------
        None.

        """
       
        in_subckt = False
        #iterate over the raw netlist
        for line in self._raw_netlist:
            
            #skip sub-circuits
            if line.startswith(".subckt"):
                in_subckt = True
                continue
            
            if line.startswith(".ends"):
                in_subckt = False
                continue
            
            #if not in a sub-circuit
            if not in_subckt:
                #check if the line is a command
                if line.startswith("."):
                    #if the command is a parameter statement -> add the parameter to the parameters dict
                    if line.startswith(".param"):
                        splitted = line.split()
                        self._append_params(splitted[1:])
                        continue

                    #if the command is a title statement -> set the title
                    elif line.startswith(".title"):
                        self._title = line[len(".title")+1:]
                        continue

                    #if the command is the end command -> done
                    elif line == ".end":
                        break

                    #if the command is a global statement -> raise a warning
                    elif line.upper().startswith(".GLOBAL"):
                        warnings.warn(f"Suppressing line: {line}! .GLOBAL statements aren't supported!") 
                        break
                    else:
                        raise  ValueError(f"Statement: {line} not supported!")
                else:
                    self._net.append(line)
        
            
    def _get_subnets(self, net : list[str]) -> dict[str, list[str]]:
        """Get the sub-circuit netlists.

        Args:
            net (list[str]): Top-level netlist.

        Returns:
            dict[str, list[str]]: key: Name of the sub-circuit. value: Netlist of the sub-circuit.
        """
        sub_net_dict = {}
        sub_nets = []
        
        #iterate over the lines of the netlist
        #and store the names of the sub-circuits
        for l in net:
            if l.startswith(".subckt"):
                sub_net_dict[l.split()[1]] = None
        
        #get the sub-circuit netlists
        for sub_circ_name in list(sub_net_dict.keys()):
            sub_net = self._get_subcir_net(sub_circ_name, net)
            sub_nets.append(sub_net)
        
        #set the sub-circuit netlists in the dict.
        for (i, n)  in zip(list(sub_net_dict.keys()), sub_nets):
            sub_net_dict[i] = n
                
        return sub_net_dict
        
    def _get_subcir_net(self, identn : str, netlist : list[str]) -> list[str]:
        """Get the netlist of the sub-circuit <identn>.

        Args:
            identn (str): Name of the sub-circuit.
            netlist (list[str]): Top-level netlist.

        Raises:
            ValueError: If the sub-circuit can't be found in the netlist.

        Returns:
            list[str]: Netlist of the sub-circuit.
        """
        subcirc = []
        in_subcirc = False
        found = False
        #iterate over the lines of the netlist
        for l in netlist:
            #find the sub-circuit
            splitted = l.split()
            if splitted[0] == ".subckt" and splitted[1] == identn:
                in_subcirc = True
                found = True
                subcirc.append(l)
                continue
            if l.startswith(".ends") and in_subcirc:
                in_subcirc = False
                subcirc.append(l)
                break
            if in_subcirc:
                subcirc.append(l)

        if found:
            return subcirc
        else:
            raise ValueError
            
    def _append_params(self, params : list[str]):
        """Append the parameters given in params, to the parameters dict.

        Args:
            params (list[str]): List of circuit parameters
        """
        #iterate over the parameters
        for p in params:
            #find the '='
            indx = p.find("=")

            #if a '=' were found
            if indx>=0:
                #get the name of the parameter
                ident = p[:indx]
                #get the value of the parameter
                expr = p[indx+1:]
                #save the parameter
                self._params[ident] = expr
        
class SubNetlist(Netlist):
    def __init__(self, raw_netlist) -> None:
        """
        Class to store the netlist of a subcircuit.

        Parameters
        ----------
        raw_netlist : list (str)
            Raw netlist of the subcircuit starting with 
            .subckt and ending with .ends

        Returns
        -------
        None
            DESCRIPTION.

        """
        super().__init__(raw_netlist)
        first_line = self._raw_netlist[0]
        last_line = self._raw_netlist[-1]
        
        self._ports = first_line.split()[2:]
        self._title = first_line.split()[1]
        self._raw_netlist[0] = f".title {self._title}"
        self._raw_netlist[-1] = ".end"
        self._get_top_net()
        self._raw_netlist[0] = first_line
        self._raw_netlist[-1] = last_line
        
    def get_nodes(self):
        """

        Returns
        -------
        list (str)
            Nodes of the subcircuit.

        """
        return self._ports
        