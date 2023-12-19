from maya import OpenMaya


def create_float_ptr():
    u_util = OpenMaya.MScriptUtil()
    u_util.createFromDouble(0.0)
    float_ptr = u_util.asFloatPtr()
    return float_ptr


def get_float_from_float_ptr(float_ptr):
    u_util = OpenMaya.MScriptUtil()
    float_val = u_util.getFloat(float_ptr)
    return float_val


def create_int_ptr():
    u_util = OpenMaya.MScriptUtil()
    int_ptr = u_util.asIntPtr()
    return int_ptr


def get_int_from_int_ptr(int_ptr):
    u_util = OpenMaya.MScriptUtil()
    float_val = u_util.getInt(int_ptr)
    return float_val

# ______________________________________________________________________________________________________________________
# pointer_utils.py
