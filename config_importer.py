from os.path import exists #don't know if this is strictly nessecary

def grab_config(configPath):    
    if exists(configPath):
        with open(configPath) as config:
            output = {}
            for line in config:
                templine = line.replace(" ", "").replace("	", "")
                commentStart = min_pref_positive(templine.find("#"), templine.find("//"))
                equalpos = templine.find("=")
                if equalpos+1: #if = found
                    key = templine[:equalpos]
                    value = cast(templine[equalpos+1:])
                    output[key] = value
            return output
    else:
        print("Could not find given file")
        return
    
def min_pref_positive(a,b):
    if (a>0 and b>0) or (a<0 and b<0):
        return min(a,b)
    if a>0:
        return a
    return b

def cast(val):
    tests = [int, float]
    for test in tests:
        try:
            return test(val)
        except:
            continue
    if val.upper() == "TRUE" or val.upper() == "T":
        return True
    if val.upper() == "FALSE" or val.upper() == "F":
        return False
    if val[-1] == "\n":
        return val[:-1]
    return val

