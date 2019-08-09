import struct
from copy import copy

import uproot

class Util(object):

    def __init__(self):
        self._written = {}
        self.tobjstring_count = 0

    _format_cntvers = struct.Struct(">IH")

    def _putclass(self, cursor, obj, keycursor):
        start = cursor.index - keycursor.index
        buf = b""
        objct, clsname = obj
        if id(objct) in self._written and clsname in self._written:
            buf += cursor.put_fields(self._format_putobjany1, self._written[id(objct)] | uproot.const.kClassMask)
            return buf
        if clsname in self._written:
            buf += cursor.put_fields(self._format_putobjany1, self._written[clsname] | uproot.const.kClassMask)
        else:
            buf += cursor.put_fields(self._format_putobjany1, uproot.const.kNewClassTag)
            buf += cursor.put_cstring(clsname)
            self._written[clsname] = (start + uproot.const.kMapOffset) | uproot.const.kClassMask
            self._written[id(objct)] = start - 4 + uproot.const.kMapOffset
        if clsname == "THashList" or clsname == "TList":
            buf += self.parent_obj.put_tlist(cursor, objct)
        elif clsname == "TObjString":
            self.tobjstring_count += 1
            buf += self.parent_obj.put_tobjstring(cursor, objct, self.tobjstring_count)
        elif clsname == "TBranch":
            buf += objct.write(cursor)
        elif clsname == "TLeafI":
            buf += objct.put_tleafI(cursor)
        return buf

    _format_putobjany1 = struct.Struct(">I")
    def put_objany(self, cursor, obj, keycursor):
        copy_cursor = copy(cursor)
        cursor.skip(self._format_putobjany1.size)
        class_buf = b""
        objct, clsname = obj
        if id(objct) in self._written and clsname in self._written:
            class_buf = self._putclass(cursor, obj, keycursor)
            buff = b""
        if objct != [] and objct != None:
            class_buf = self._putclass(cursor, obj, keycursor)
            buff = copy_cursor.put_fields(self._format_putobjany1, len(class_buf) | uproot.const.kByteCountMask)
        else:
            buff = copy_cursor.put_fields(self._format_putobjany1, len(class_buf))
        buff += class_buf
        return buff

    def set_obj(self, parent_obj):
        self.parent_obj = parent_obj
