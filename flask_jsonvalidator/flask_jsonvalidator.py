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

MSG = "msg"
ERR = "error"

class Validator(ABC):
    
    @abstractmethod
    def validate(self,data):
        pass
    
class IntValidator(Validator):
    """Validator for Integers"""
    
    def __init__(self, *args, **kwargs):
        self._args = args
        if not set(kwargs).issubset({"max", "min", "nullable", "err_msg"}):
            diff = {"max", "min"}.difference(kwargs)
            raise TypeError("Unknown keyword arguments %r" % list(diff))
        self.max = kwargs.get("max")
        self.min = kwargs.get("min")
        self.nullable  = kwargs.get("nullable", True)
        self.err_msg = kwargs.get("err_msg", None)
        
    def validate(self, value):
        if not value and self.nullable:
            return (True, None)

        if type(value) == int:
            satifies_max = self.max >= value if self.max else True
            satifies_min = self.min <= value if self.min else True

            if not satifies_max:
                return (satifies_max, { MSG : f"Value must be less than {self.max}" })

            if not satifies_min:
                return (satifies_min, { MSG : f"Value must be greater than {self.min}" })

            return (True, None)

        return (False, { MSG : f"Value must be an Integer and not null" })
    
    
class FloatValidator(Validator):
    """Validator for Floats"""
    
    def __init__(self, *args, **kwargs):
        self._args = args
        if not set(kwargs).issubset({"max", "min", "nullable", "err_msg"}):
            diff = {"max", "min"}.difference(kwargs)
            raise TypeError("Unknown keyword arguments %r" % list(diff))
        self.max = kwargs.get("max")
        self.min = kwargs.get("min")
        self.nullable  = kwargs.get("nullable", True)
        self.err_msg = kwargs.get("err_msg", None)
        
    def validate(self, value):
        if not value and self.nullable:
            return (True, None)

        if type(value) == float:
            satifies_max = self.max >= value if self.max else True
            satifies_min = self.min <= value if self.min else True

            if not satifies_max:
                return (satifies_max, { MSG : f"Value must be less than {self.max}" })

            if not satifies_min:
                return (satifies_min, { MSG : f"Value must be greater than {self.min}" })

            return (True, None)

        return (False, { MSG : f"Value must be an Float and not null" })
    
class StringValidator(Validator):
    """Validator for Strings"""
    
    def __init__(self, *args, **kwargs):
        self._args = args
        if not set(kwargs).issubset({"max", "min", "regex", "fullmatch", "nullable", "err_msg"}):
            diff = {"max", "min", "regex", "fullmatch", "nullable"}.difference(kwargs)
            raise TypeError("Unknown keyword arguments %r" % list(diff))
        self.max   = kwargs.get("max")
        self.min   = kwargs.get("min")
        self.regex = kwargs.get("regex")
        self.fullmatch = kwargs.get("fullmatch", True)
        self.nullable  = kwargs.get("nullable", True)
        self.err_msg = kwargs.get("err_msg", None)
        
    def validate(self, value):
        if not value and self.nullable:
            return (True, None)

        if type(value) == str and value:
            satifies_max = self.max >= len(value) if self.max else True
            satifies_min = self.min <= len(value) if self.min else True

            if not satifies_max:
                return (satifies_max, { MSG : f"Length of value must be less than {self.max}" })

            if not satifies_min:
                return (satifies_min, { MSG : f"Length of value must be greater than {self.min}" })

            if self.regex:
                if self.fullmatch:
                    satifies_regex = bool(re.compile(self.regex).fullmatch(value))
                else:
                    satifies_regex = bool(re.compile(self.regex).match(value))
                
                if not satifies_regex:
                    return (satifies_regex, { MSG : f"String must match {self.regex}" })

            return (True, None)

        return (False, { MSG : f"Value must be an String and not null" })
    
class BooleanValidator(Validator):
    """Validator for Booleans"""
    
    def __init__(self, *args, **kwargs):
        self._args = args
        if not set(kwargs).issubset({"nullable", "err_msg"}):
            diff = {"nullable"}.difference(kwargs)
            raise TypeError("Unknown keyword arguments %r" % list(diff))
        self.nullable  = kwargs.get("nullable", True)
        self.err_msg = kwargs.get("err_msg", None)
        
    def validate(self, value):
        if not value and self.nullable:
            return (True, None)

        if type(value) == bool:
            return (True, None)
        
        return (True, { MSG : "Value must be Boolean and not null" })
    
class ArrayValidator(Validator):
    """Validator for Arrays"""
    
    def __init__(self, *args, **kwargs):
        self._args = args
        if not set(kwargs).issubset({"nullable", "err_msg"}):
            diff = {"nullable"}.difference(kwargs)
            raise TypeError("Unknown keyword arguments %r" % list(diff))
        self.nullable  = kwargs.get("nullable", True)
        self.err_msg = kwargs.get("err_msg", None)
        
    def validate(self, value):
        if not value and self.nullable:
            return (True, None)

        if type(value) == list:
            return (True, None)
        
        return (False, { MSG : "Value must be an Array or a List" })
    
    
class ArrayOfValidator(Validator):
    """Validator for Arrays with specific values"""
    
    def __init__(self, validator, *args, **kwargs):
        self._args = args
        if not set(kwargs).issubset({"nullable", "err_msg"}):
            diff = {"nullable"}.difference(kwargs)
            raise TypeError("Unknown keyword arguments %r" % list(diff))
        self.nullable  = kwargs.get("nullable", True)
        self.of = validator
        self.err_msg = kwargs.get("err_msg", None)
        
    def validate(self, value):
        if not value and self.nullable:
            return (True, None)

        if type(value) == list:
            # TODO: Optimize item check
            for item in value:
                error, msg = self.of.validate(item)
                if not error:
                    return (False, { MSG : f"An error occured validating some values in the Array/List", "value(s) error" : msg })
            return (True, None)
        return (False, { MSG : "Value must be an Array or a List" })
    
class JSONValidator(Validator):
    """Validator for JSON data"""
    
    # Keys: Parameter name
    # Values: A Validator
    validators = dict()
    
    def check_parameters(self, parameters):
        if not set(self.validators).issubset(set(parameters)):
            return False
        return True
    
    def validate(self, json):
        out = {}
        has_error = False
        wanted_params = list(self.validators.keys())
        seen = []
        for k,v in json.items():
            validator = self.validators.get(k)
            if validator:
                seen.append(wanted_params.index(k))
                if isinstance(validator, Validator):
                    error, msg = validator.validate(v)
                    if not error:
                        out[k] = { ERR : msg, "value" : v, "err_msg" : validator.err_msg }
                        has_error = True

        if len(seen) < len(wanted_params):
            for i,k in enumerate(wanted_params):
                if i not in seen:
                    out[k] = { ERR : "Value is missing!", "value" : None }
                    has_error = True

        if has_error:
            return (False, out)

        return (True, None)
