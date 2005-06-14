# Copyright (C) 2005 Sridhar Ratna <sridhar@users.berlios.de>
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


class ctx:

    """Application context. Shared data repository
    
    Note: This class object will be replaced with the instance object
          after instantiation (see `init_context` function).
          It is enough to do 'from context import ctx' to get the context
          instance.
          
    Configuration variables
    =======================
    >>> from context import ctx
    >>> ctx['editor.font'] = 'Monospace'
    >>> size = int( ctx['editor.fontsize'] )
    """
    
    main_window = property(fget=lambda self: self._get_mw())

    def __init__(self, app_settings_directory, get_main_window_func):
        self.app_settings_directory = app_settings_directory
        self._get_mw = get_main_window_func
        
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

        
def init_context(get_main_window_func):
    app_settings_directory = os.path.expanduser('~/.config/mallet')
    # singleton trick
    global ctx
    ctx = ctx(app_settings_directory, get_main_window_func)


class NoConfigVariable(Exception):

    """No such configuration variable is found"""
    

class AppConfig:

    """Represent application preferences stored in a YAML file
    
    Access to nodes is through dot-seperated list. For example, to access
    a/b/c, use var_path='a.b.c'
    """
    
    def __init__(self, pref_string):
        # Load default values first
        from mallet.config import data_dir
        default_pref = open(os.path.join(data_dir, 'default.yaml')).read()
        default_data = syck.load(default_pref)
        # Load from user preferences
        self._data = syck.load(pref_string)
        if self._data is None:
            self._data = {}
        self._data.update(default_data)
        
    def get(self, var_path):
        """Get value"""
        obj = self._data
        for var in var_path.split('.'):
            try:
                if type(obj) is not dict: raise KeyError
                obj = obj[var]
            except KeyError:
                raise NoConfigVariable
        return obj
        
    def set(self, var_path, value):
        """Set value"""
        obj = self._data
        vars = var_path.split('.')
        for var in vars[:-1]:
            try:
                if type(obj) is not dict: raise KeyError
                obj = obj[var]
            except KeyError:
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
                if type(obj) is not dict: raise KeyError
                obj = obj[var]
            except KeyError:
                obj[var] = {}
                obj = obj[var]
                
        var = vars[-1]
        try:
            if '__getitem__' not in dir(obj): raise KeyError
            obj = obj[var]
        except KeyError:
            obj[var] = default
            obj = obj[var]
        return obj
        
    def to_yaml(self):
        """Return as yaml string"""
        return ydump.dump(self._data)
