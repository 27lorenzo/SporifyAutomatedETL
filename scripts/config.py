import configparser
import os
import sys

class config(object):
    def __init__ (self):
        root_dir = os.path.dirname(os.path.abspath(__file__))

        self.config_hidden = configparser.ConfigParser()
        self.config_hidden.sections()
        self.config_hidden.read(os.path.join(root_dir, 'config_hidden.ini'))

    def readh(self, section, field):
        if field:
            return self.config_hidden[section].get(field)

    def read(self, section, field):
        if field:
            return self.config[section].get(field)

    def get_weight_severity(self, find):
        r = self.read('Severity Weight', find)
        if r:
            return r
        else:
            return 1 # default value
