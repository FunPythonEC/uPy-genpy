from . import md5

"""
Message class copied from:
https://github.com/ros/genpy
"""


class Message(object):

    __slots__ = ["_connection_header"]

    def __init__(self, *args, **kwds):

        if args and kwds:
            raise TypeError(
                "Message constructor may only use args OR keywords, not both"
            )
        if args:
            if len(args) != len(self.__slots__):
                raise TypeError(
                    "Invalid number of arguments, args should be %s"
                    % str(self.__slots__)
                    + " args are"
                    + str(args)
                )
            for i, k in enumerate(self.__slots__):
                setattr(self, k, args[i])
        else:
            # validate kwds
            for k, v in kwds.items():
                if k not in self.__slots__:
                    raise AttributeError(
                        "%s is not an attribute of %s" % (k, self.__class__.__name__)
                    )

            for k in self.__slots__:
                if k in kwds:
                    setattr(self, k, kwds[k])
                else:
                    setattr(self, k, None)


"""
Since a Python file with the message class is nedeed
this class is responsible about writing that file
"""


class MessageGenerator(object):
    def __init__(self, addr):

        self.addr = addr

    # method to create message
    def create_message(self):

        # struct primitive data types and default types
        def_types = {
            "bool": "<B",
            "byte": "<b",
            "char": "<B",
            "float32": "<f",
            "float64": "<d",
            "int8": "<b",
            "int16": "<h",
            "int32": "<i",
            "int64": "<q",
            "string": "<I%ss",
            "uint8": "<B",
            "uint16": "<H",
            "uint32": "<I",
            "uint64": "<Q",
        }

        # getting script name and dir
        script_addr = self.addr.split("/")[0]
        script_name = self.addr.split("/")[1].split(".")[0]

        # manage init file
        initpy = open("{}/__init__.py".format(script_addr), "a")
        initpy.write("from ._{} import {}\n".format(script_name, script_name))
        initpy.close()

        # script created
        script = open("{}/_{}.py".format(script_addr, script_name), "w")
        # import input
        script.write("import ustruct as struct\nfrom ugenpy.message import Message\n")

        # file with types and varibles is opened
        f = open(self.addr, "r")
        md5string = ""
        msgfile = f.read()
        f.close()
        data = msgfile.split("\n")
        data = [i for i in data if (i.isspace() == False and len(i) != 0)]
        md5string = data[0]

        # md5 is calculated
        for i in range(1, len(data)):
            md5string += "\n{}".format(data[i])

        md5hash = md5.digest(md5string)
        classdef = """class {}(Message):
            _md5sum = "{}"
            _type = "{}"
            _has_header = False
            _full_text = '''{}'''\n""".format(
            script_name, md5hash, "{}/{}".format(script_addr, script_name), md5string
        )

        # first part is written
        script.write(classdef)

        # slots part
        slots = "['{}'".format(data[0].split(" ")[1])
        for i in range(1, len(data)):
            slots += ",'{}'".format(data[i].split(" ")[1])
        slots += "]"

        # slots type part
        slots_type = "['{}'".format(data[0].split(" ")[0])
        for i in range(1, len(data)):
            slots_type += ",'{}'".format(data[i].split(" ")[0])
        slots_type += "]"

        # slots types and args to define self attributes
        initdef = """
            __slots__ = {}
            _slots_types = {}        
            
            def __init__(self, *args, **kwds):
            
                if args or kwds:
                    super({}, self).__init__(*args, **kwds)\n""".format(
            slots, slots_type, script_name
        )
        script.write(initdef)

        # asigning self attributes
        for i in range(0, len(data)):
            temp = [data[i].split(" ")[0], data[i].split(" ")[1]]
            if "bool" in temp[0]:
                val = "False"
            elif "string" in temp[0]:
                val = "''"
            elif "float" in temp[0]:
                val = "0."
            else:
                val = "0"
            script.write(
                """
                    if self.{} is None:
                        self.{} = {}""".format(
                    temp[0], temp[0], val
                )
            )

        script.write(
            """
            
            def _get_types(self):
                return self._slot_types
            
            def serialize(self, buff):
                try:"""
        )
        # serialization part
        for i in range(0, len(data)):
            temp = data[i].split(" ")[1]
            print(
                "data type processed: "
                + data[i].split(" ")[0]
                + " to be "
                + def_types.get(data[i].split(" ")[0])
            )
            if "string" in data[i].split(" ")[0]:
                script.write(
                    """
                    buff.write(struct.pack('<I%ss'%len(self.{}),len(self.{}),self.{}))""".format(
                        temp, temp, temp
                    )
                )

            else:
                script.write(
                    """
                    buff.write(struct.pack('{}',self.{}))""".format(
                        def_types.get(data[i].split(" ")[0]), data[i].split(" ")[1]
                    )
                )

        script.write(
            """
                except Exception as e:
                    print(e)
            
            def deserialize(self, str):
                try:
                    end = 0"""
        )

        for i in range(0, len(data)):
            temp = data[i].split(" ")[1]
            temppack = data[i].split(" ")[0]

            if "string" in temppack:
                script.write(
                    """
                    start = end
                    end += 4
                    (length,) = struct.unpack('<I', str[start:end])
                    start = end
                    end += length
                    self.{} = str[start:end].decode('utf-8')""".format(
                        temp
                    )
                )

            elif ("bool" or "byte" or "char" or "8") in temppack:
                script.write(
                    """
                    start = end
                    end += 1
                    (self.{},) = struct.unpack('{}', str[start:end])""".format(
                        temp, def_types.get(temppack)
                    )
                )

            elif "16" in temppack:
                script.write(
                    """
                    start = end
                    end += 2
                    (self.{},) = struct.unpack('{}', str[start:end])""".format(
                        temp, def_types.get(temppack)
                    )
                )

            elif "32" in temppack:
                script.write(
                    """
                    start = end
                    end += 4
                    (self.{},) = struct.unpack('{}', str[start:end])""".format(
                        temp, def_types.get(temppack)
                    )
                )

            elif "64" in temppack:
                script.write(
                    """
                    start = end
                    end += 8
                    (self.{},) = struct.unpack('{}', str[start:end])""".format(
                        temp, def_types.get(temppack)
                    )
                )

        script.write(
            """
                    return self
                except Exception as e:
                    print(e)"""
        )

        script.close()
