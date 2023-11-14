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

import abc

class Rule(metaclass = abc.ABCMeta):
    """Class to represent a rule.
    """
    @abc.abstractmethod
    def __init__(self, *, name : str) -> None:
        self._name = name
        

    def __repr__(self) -> str:
        cname = self.__class__.__name__
        return f"{cname}(name={self._name})"
    
    def __eq__(self, __value: object) -> bool:
        """Rules are equal if they have the same name.

        Args:
            __value (object): Object to be compared.

        Returns:
            bool: True if object is a rule, and have the same name.
        """
        return (isinstance(__value, Rule)) and (self._name == __value._name)
    
    def __hash__(self) -> int:
        return hash(self._name)
    
    @property
    def name(self) -> str:
        """Get the name of the rule.

        Returns:
            str: Name of the rule.
        """
        return self._name