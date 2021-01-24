import re
from abc import ABC, abstractmethod

# TODO: __repr__

__all__ = [
    "IntValidator",
    "FloatValidator",
    "StringValidator",
    "BooleanValidator",
    "ArrayValidator",
    "ArrayOfValidator",
    "JSONValidator"
]

class Validator(ABC):
    
    @abstractmethod
    def validate(self,data):
        pass
    
class IntValidator(Validator):
    """Validator for Integers"""
    
    def __init__(self, *args, **kwargs):
        self._args = args
        if not set(kwargs).issubset({"max", "min", "nullable"}):
            diff = {"max", "min"}.difference(kwargs)
            raise TypeError("Unknown keyword arguments %r" % list(diff))
        self.max = kwargs.get("max")
        self.min = kwargs.get("min")
        self.nullable  = kwargs.get("nullable", True)
        
    def validate(self, value):
        if not value and self.nullable:
            return True
        if type(value) == int:
            satifies_max = self.max >= value if self.max else True
            satifies_min = self.min <= value if self.min else True
            return satifies_max and satifies_min
        
        return False
    
class FloatValidator(Validator):
    """Validator for Floats"""
    
    def __init__(self, *args, **kwargs):
        self._args = args
        if not set(kwargs).issubset({"max", "min", "nullable"}):
            diff = {"max", "min"}.difference(kwargs)
            raise TypeError("Unknown keyword arguments %r" % list(diff))
        self.max = kwargs.get("max")
        self.min = kwargs.get("min")
        self.nullable  = kwargs.get("nullable", True)
        
    def validate(self, value):
        if not value and self.nullable:
            return True
        if type(value) == float:
            satifies_max = self.max >= value if self.max else True
            satifies_min = self.min <= value if self.min else True
            return satifies_max and satifies_min
        return False
    
    
class StringValidator(Validator):
    """Validator for Strings"""
    
    def __init__(self, *args, **kwargs):
        self._args = args
        if not set(kwargs).issubset({"max", "min", "regex", "fullmatch", "nullable"}):
            diff = {"max", "min", "regex", "fullmatch", "nullable"}.difference(kwargs)
            raise TypeError("Unknown keyword arguments %r" % list(diff))
        self.max   = kwargs.get("max")
        self.min   = kwargs.get("min")
        self.regex = kwargs.get("regex")
        self.fullmatch = kwargs.get("fullmatch", True)
        self.nullable  = kwargs.get("nullable", True)
        
    def validate(self, value):
        if not value and self.nullable:
            return True
        if type(value) == str:
            satifies_max = self.max >= len(value) if self.max else True
            satifies_min = self.min <= len(value) if self.min else True
            current_saticfactory = satifies_max and satifies_min
            
            if self.regex:
                if self.fullmatch:
                    satifies_regex = bool(re.compile(self.regex).fullmatch(value))
                else:
                    satifies_regex = bool(re.compile(self.regex).match(value))
                current_saticfactory = current_saticfactory and current_saticfactory
            return current_saticfactory
        return False
    
class BooleanValidator(Validator):
    """Validator for Booleans"""
    
    def __init__(self, *args, **kwargs):
        self._args = args
        if not set(kwargs).issubset({"nullable"}):
            diff = {"nullable"}.difference(kwargs)
            raise TypeError("Unknown keyword arguments %r" % list(diff))
        self.nullable  = kwargs.get("nullable", True)
        
    def validate(self, value):
        if not value and self.nullable:
            return True
        if type(value) == bool:
            return True
        
        return False
    
class ArrayValidator(Validator):
    """Validator for Arrays"""
    
    def __init__(self, *args, **kwargs):
        self._args = args
        if not set(kwargs).issubset({"nullable"}):
            diff = {"nullable"}.difference(kwargs)
            raise TypeError("Unknown keyword arguments %r" % list(diff))
        self.nullable  = kwargs.get("nullable", True)
        
    def validate(self, value):
        if not value and self.nullable:
            return True
        if type(value) == list:
            return True
        
        return False
    
    
class ArrayOfValidator(Validator):
    """Validator for Arrays with specific values"""
    
    def __init__(self, validator, *args, **kwargs):
        self._args = args
        if not set(kwargs).issubset({"nullable"}):
            diff = {"nullable"}.difference(kwargs)
            raise TypeError("Unknown keyword arguments %r" % list(diff))
        self.nullable  = kwargs.get("nullable", True)
        self.of = validator
        
    def validate(self, value):
        if not value and self.nullable:
            return True
        if type(value) == list:
            # TODO: Optimize item check
            for item in value:
                if not self.of.validate(item):
                    return False
        
        return True
    
class JSONValidator(Validator):
    """Validator for JSON data"""
    
    # Keys: Parameter name
    # Values: A Validator
    validators = dict()
    
    def check_parameters(self, parameters, json_parameters):
        if not set(json_parameters).issubset(set(parameters)):
            return False
        return True
    
    def validate(self, json):
        for k,v in json.items():
            validator = self.validators.get(k)
            if validator:
                if isinstance(validator, Validator):
                    if not validator.validate(v):
                        return False
                
        return True
