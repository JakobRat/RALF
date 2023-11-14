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