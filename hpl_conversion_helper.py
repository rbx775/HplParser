import math

def __round_to_hpl_float(f):
    return round(f, 4)

def __round_tuple(t):
    return tuple(__round_to_hpl_float(x) for x in t)

def __swizzle(_t):
    return (_t[0],_t[2],_t[1])

def __swizzle_rot(_t):
    return (-_t[0],_t[2],_t[1])

def convert_to_hpl_vec3(vec3):
    vec3 = __round_tuple(vec3)
    return str(__swizzle(tuple(vec3))).translate(str.maketrans({'(': '', ')': '', ',': ''}))

def convert_to_hpl_rotation(vec3):
    vec3 = __round_tuple(vec3)
    return str(__swizzle_rot(tuple(vec3))).translate(str.maketrans({'(': '', ')': '', ',': ''}))

def convert_to_hpl_rotation_radians(vec3):
    vec3 = __round_tuple(vec3)
    #  Why?
    return str((vec3[0] * (math.pi / 180), vec3[2], vec3[1])).translate(str.maketrans({'(': '', ')': '', ',': ''}))

def convert_to_hpl_vec2(vec2):
    vec2 = __round_tuple(vec2)
    return str(tuple(vec2)).translate(str.maketrans({'(': '', ')': '', ',': ''}))

def convert_to_hpl_location(vec3):
    vec3 = __round_tuple(vec3)
    return (-vec3[0],vec3[1],vec3[2])

def convert_variable_to_hpl(var):
    if type(var) == list:
        return str(var[1])
    else:
        return str(var)