from pdb import set_trace

class StructDict_base(object):
    def __init__(self, field_names=[]):
        if len(field_names):
            self.__dict__["__field_names__"] = field_names
        self.__dict__["__initialized__"] = False
        if len(field_names):
            self.__dict__["__dict_db__"] = dict()
            self.__dict__["__field_names__"] = field_names
            for field_name in field_names:
                self.__dict__["__dict_db__"][field_name] = None
        self.__dict__["__initialized__"] = True

    def __getattr__(self, key):
        return self.__dict_db__[key]

    def __setattr__(self, attr, value):
        if self.__initialized__:
            if len(self.__field_names__):
                if attr in self.__field_names__:
                    self.__dict_db__[attr] = value
                else:
                    set_trace()
                    pass
                    raise Exception("Attribute not among class initialization attributes")
            else:
                self.__dict_db__[attr] = value
        else:
            super(StructDict, self).__setattr__(attr, value)
 

def StructDict(type_name, field_names=list()):
    StructDict_base.__dict_db__   = dict()
    StructDict_base.__type_name__ = type_name
    StructDict_base.__field_names__ = field_names
    if len(field_names):
        for field_name in field_names:
            StructDict_base.__dict__["__dict_db__"][field_name] = None
    return StructDict_base
    


if __name__ == "__main__":
    from pdb import set_trace
    Struct_A_type = StructDict()
    Struct_A = Struct_A_type()
    Struct_A.a=  "Hello"
    Struct_A.b=  "Hello"
    
    Struct_B_type = StructDict(["c", "d"])
    Struct_B = Struct_B_type()
    Struct_B.c=  "Hello1"
    Struct_B.d=  "Hello2"
    Struct_B.c=  "Hello3"

    print(Struct_A.__dict_db__)
    print(Struct_B.__dict_db__)
    set_trace()
    pass

