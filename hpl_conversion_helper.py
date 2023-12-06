def __swizzle(_t):
    return (_t[0],_t[2],_t[1])

def convert_to_hpl_vec3(vec3):
    return str(__swizzle(tuple(vec3))).translate(str.maketrans({'(': '', ')': '', ',': ''}))

def convert_to_hpl_vec2(vec2):
    return str(tuple(vec2)).translate(str.maketrans({'(': '', ')': '', ',': ''}))

def convert_to_hpl_location(vec3):
    return (-vec3[0],vec3[1],vec3[2])