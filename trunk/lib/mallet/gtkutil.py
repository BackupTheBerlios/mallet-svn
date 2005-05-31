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

"""Utility functions, classes for GTK"""

import os.path
import inspect
import gtk


class ActionControllerMixin:

    """Automatically connect callbacks to UIAction
    
    During __init__, call the single method `connectActionCallbacks` passing
    the ActionGroup which contains the Actions. All callback methods in the
    class will be automatically connected to the appropriate Action
    """

    def connectActionCallbacks(self, action_group):
        """Connect cb_<action_name> methods to the corresponding Actions"""
        # generate Action names list from callback methods
        methods = [x[0] for x in inspect.getmembers(self) \
                   if inspect.ismethod(x[1])]
        startWith = 'on_'
        actions_list = [x[len(startWith):] for x in methods \
                        if x.startswith(startWith)]

        # Connect the callback for each action
        for action_name in actions_list:
            action = action_group.get_action(action_name)
            callback = getattr(self, '%s%s' % (startWith, action_name))
            # The "activate" signal is emitted when Action is 'performed'.
            action.connect("activate", callback)


class FileDialog:

    """Abstracts common file dialog operations"""

    # Last accessed file or directory
    last_accessed = None

    def open(self):
        dlg = self.getOpenDlg()
        return self.getFilename(dlg, True)

    def save(self):
        dlg = self.getSaveDlg()
        return self.getFilename(dlg, False, True)

    # Advanced methods

    def getSaveDlg(self, title="Save as", parent=None):
        """Return Save File dialog"""
        return gtk.FileChooserDialog(title, parent,
                              action=gtk.FILE_CHOOSER_ACTION_SAVE,
                              buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK))

    def getOpenDlg(self, title="Open file", parent=None):
        """Return Open File dialog"""
        return gtk.FileChooserDialog(title, parent,
                              action=gtk.FILE_CHOOSER_ACTION_OPEN,
                              buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))

    def getFilename(self, dlg, forceValidFile=False, mustNotExist=False):
        """Return filename as selected by the user from dialog `dlg`

        if `forceValidFile` then the selected file must exists,
        else if `mustNotExist`, the selectef file should not exists
        """
        if FileDialog.last_accessed:
            dlg.set_current_folder(FileDialog.last_accessed)
        dlg.set_default_response(gtk.RESPONSE_OK)
        filename = None
        while 1:
            response = dlg.run()
            if response == gtk.RESPONSE_OK:
                filename = dlg.get_filename()
            else:
                dlg.destroy()
                return None
            if not forceValidFile:
                if mustNotExist:
                    if filename and os.path.exists(filename):
                        # warn user about existing file
                        msg = gtk.MessageDialog(parent=dlg,
                                          flags=gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT,
                                          type=gtk.MESSAGE_ERROR,
                                          buttons=gtk.BUTTONS_OK,
                                          message_format="File already exists. It cannot be overwritten")
                        msg.run()
                        msg.destroy()
                        continue
                dlg.destroy()
                break
            if filename and os.path.exists(filename):
                dlg.destroy()
                break
        
        if filename:
            FileDialog.last_accessed = filename
        return filename
