from pdb import set_trace

class StructDict_base(object):
    def __init__(self):
        self.__dict__["__type_name__"] = self.__type_name__
        self.__dict__["__dict_db__"] = dict()
        self.__dict__["__field_names__"] = self.__field_names__
        self.__dict__["__initialized__"] = False
        if len(self.__field_names__):
            for field_name in self.__field_names__:
                self.__dict__["__dict_db__"][field_name] = None
        self.__dict__["__initialized__"] = True

    def __getattr__(self, key):
        try:
            return self.__dict_db__[key]
        except:
            set_trace()
            pass

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
    base_type = type(type_name, (StructDict_base,), {})
    base_type.__dict_db__   = dict()
    base_type.__type_name__ = type_name
    base_type.__field_names__ = field_names
    if len(field_names):
        for field_name in field_names:
            base_type.__dict__["__dict_db__"][field_name] = None
    return base_type
    


if __name__ == "__main__":
    from pdb import set_trace
    Struct_A_type = StructDict("Struct_A_t")
    Struct_A = Struct_A_type()
    Struct_A.a=  "Hello"
    Struct_A.b=  "Hello"
    
    Struct_B_type = StructDict("Struct_B_t", ["c", "d"])
    Struct_B = Struct_B_type()
    Struct_B.c=  "Hello1"
    Struct_B.d=  "Hello2"
    Struct_B.c=  "Hello3"

    print(Struct_A_type.__type_name__)
    print(Struct_B_type.__type_name__)
    print(Struct_A.__dict_db__)
    print(Struct_B.__dict_db__)
    set_trace()
    pass

