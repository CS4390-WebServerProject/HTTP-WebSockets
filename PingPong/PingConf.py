#!/bin/python

class PingConf:
    def __init__(self, configPath):
        self.conf = { 'gzip': 'off', 'caching': 'off' }

        lineCount = 1
        try:
            with open(configPath) as f:
                for line in f:
                    # Ignore comments
                    if line[0] != '#':
                        # Makes sure config lines end with semicolon
                        if line[len(line)-1] == ';':
                            line = line[:-1]
                            
                            # Make sure line is not empty
                            if line != '':
                                keyValue = line.split(' ')
                                # Get key and value
                                key = keyValue[0]
                                value = keyValue[1]

                                # Check to make sure it's a valid key
                                if self.defaults.has_key(key):
                                    # Check to make sure value is valid
                                    if value == 'off' or value == 'on':
                                        # Add to configuration
                                        self.conf[key] = value
                                    else:
                                        raise SyntaxError("Invalid value '{0}' on line {1} in {2}.".format(value, lineCount, configPath))
                                else:
                                    raise SyntaxError("Invalid key'{0}' on line {1} in {2}.".format(key, lineCount, configPath))
                            else:
                                raise SyntaxError("Empty line with semicolon at {1} in {2}.".format(lineCount, configPath))

                    # Increment line count
                    lineCount += 1
        except IOError:
            print("Config {0} does not exist.".format(configPath))
