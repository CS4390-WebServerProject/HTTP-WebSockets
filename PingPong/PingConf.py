#!/bin/python
try:
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser

class PingConf:

    def __init__(self, configPath):
        parser = ConfigParser()
        parser.read(configPath)
        self.config = {}

        # Read sections
        for section in parser.sections():
            sectionName = section
            # Create new section
            if parser.has_option(section, 'port'):
                port = parser.get(section, 'port')
                if port != '80':
                    sectionName += ':' + parser.get(section, 'port')

            self.config[sectionName] = {}

            # Populate with options
            options = parser.options(section)
            for option in options:
                self.config[sectionName][option] = parser.get(section, option)

    def hasHost(self, host):
        print(host)
        if host in self.config:
            return True
        return False

    def getConfig(self, host, option):
        if option in self.config[host]:
            return self.config[host][option]
        else:
            return None
