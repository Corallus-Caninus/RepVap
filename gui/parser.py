
'''parse the given toml file string and return a dictionary'''
def parse(toml_string):
    #toml_dict = toml.loads(toml_string)
    #open the toml file and read it as a string
    with open(toml_string, 'r') as toml_file:
        toml_string = toml_file.read()

    return toml_string
