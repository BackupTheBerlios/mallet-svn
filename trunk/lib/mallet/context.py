# Copyright (C) 2004 Sridhar Ratna <sridhar@users.berlios.de>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software 
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

"""Context Data

Context object is shared between many modules and plugins. Context object 
help client to access the internals such as configuration, main window, etc..
"""

import os.path
import inspect
import syck, ydump


class Context:

    """Application context. Shared data repository
    This is a singleton class
    
    Configuration variables
    =======================
    >>> ctx['editor.font'] = 'Monospace'
    >>> size = int( ctx['editor.fontsize'] )
    """

    def __init__(self, app_settings_directory):
        self.app_settings_directory = app_settings_directory
        
        if not os.path.exists(app_settings_directory):
            os.makedirs(app_settings_directory)
        self.conf_file = conf_file = os.path.join(app_settings_directory, 
                                        'configuration')
        if not os.path.exists(conf_file):
            open(conf_file, 'w').close()
            
        self._config = AppConfig(open(conf_file).read())
        
    def _cleanup(self):
        """Called when application is supposed to exit"""
        # write conf file
        yaml = self._config.to_yaml()
        open(self.conf_file, 'w').write(yaml)
        
    def __getitem__(self, var_path):
        try:
            return self._config.get(var_path)
        except NoConfigVariable:
            return self._config.create(var_path)
            
    def __setitem__(self, var_path, value):
        try:
            self._config.set(var_path, value)
        except NoConfigVariable:
            self._config.create(var_path, value)
            
    # singleton trick
    #  see init_context()
    def __call__(self):
        return self
        
def init_context():
    app_settings_directory = os.path.expanduser('~/.config/mallet')
    # singleton trick
    global Context
    Context = Context(app_settings_directory)            


class NoConfigVariable(Exception):

    """No such configuration variable is found"""
    

class AppConfig:

    """Represent application preferences stored in a YAML file
    
    Access to nodes is through dot-seperated list. For example, to access
    a/b/c, use var_path='a.b.c'
    """
    
    def __init__(self, pref_string):
        self._data = syck.load(pref_string)
        
    def get(self, var_path):
        """Get value"""
        obj = self._data
        for var in var_path.split('.'):
            try:
                obj = obj[var]
            except ItemError:
                raise NoConfigVariable
        return obj
        
    def set(self, var_path, value):
        """Set value"""
        obj = self._data
        vars = var_path.split('.')
        for var in vars[:-1]:
            try:
                obj = obj[var]
            except ItemError:
                raise NoConfigVariable
        obj[vars[-1]] = value
        
    def create(self, var_path, default=''):
        """Create the variable with hierarchy
        
        Suppose, if var_path = 'a.b.c' and only 'a' exists, both 'b' and 'c'
        will be created in hierarchy
        
        Return new node's value
        """
        obj = self._data
        vars = var_path.split('.')
        for var in vars[:-1]:
            try:
                obj = obj[var]
            except ItemError:
                obj[var] = {}
                obj = obj[var]
                
        var = vars[-1]
        try:
            obj = obj[var]
        except ItemError:
            obj[var] = default
            obj = obj[var]
        return obj
        
    def to_yaml(self):
        """Return as yaml string"""
        return ydump.dump(self._data)
        
        
init_context()
