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

"""Utility functions, classes for GTK"""

import sys
import os.path
import inspect
import gtk
import pango

from mallet.context import ctx

class NotebookLabel(gtk.HBox):

    """Common notebook tab label widget with text and close button"""
    
    def __init__(self, text):
        gtk.HBox.__init__(self)
        self.close = gtk.Button()
        self.text = gtk.Label(text)
        close_img = gtk.Image()
        close_img.set_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
        self.close.add(close_img)
        self.close.set_relief(gtk.RELIEF_NONE)
        w,h = gtk.icon_size_lookup(gtk.ICON_SIZE_MENU)
        self.close.set_size_request(w,h)
        self.close.set_focus_on_click(False)
        
        self.pack_start(self.text)
        self.pack_start(self.close)
        self.show_all()
        
    def set_text(self, text):
        self.text.set_text(text)
        
    def get_text(self, text):
        self.text.get_text()
        
    def set_color(self, r=0,g=0,b=0):
        """Set the color of text label"""
        list = pango.AttrList()
        list.insert(pango.AttrForeground(r,g,b, end_index=-1))
        self.text.set_attributes(list)


class GtkExceptionReporter:

    """Handlers all exception globally and reports data in a dialog 
    providing options to debug, continue or stop the program
    """
    
    def __init__(self):
        sys.excepthook =self._exception_cb
    
    def _exception_cb(self, typ, value, tb):
        if hasattr(sys, 'ps1') or not sys.stderr.isatty():
            # we are in interactive mode or we don't have a tty-like
            # device, so we call the default hook
            sys.__excepthook__(type, value, tb)
        else:
            import traceback, pdb
            msg = gtk.MessageDialog(parent=ctx.main_window,
                                    flags=gtk.DIALOG_MODAL,
                                    type=gtk.MESSAGE_ERROR,
                                    message_format="Exception! Look at console for debugging.")
            msg.add_buttons(gtk.STOCK_OK, gtk.RESPONSE_OK)
            msg.run()
            msg.destroy()
            print color_bright_red
            traceback.print_exception(type, value, tb)
            print color_none
            print 
            # ...then start the debugger in post-mortem mode.
            print color_bright_blue
            pdb.pm()
            print color_none
            
            
_hook = GtkExceptionReporter()


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

    def open(self, parent=None):
        dlg = self.getOpenDlg(parent=parent)
        return self.getFilename(dlg, True)

    def save(self, parent=None):
        dlg = self.getSaveDlg(parent=parent)
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


# Xterm color codes:
colornames = ['none', 'black', 'red', 'green', 'brown', 'blue', 'magenta',
'cyan', 'light_gray', 'dark_gray', 'bright_red', 'bright_green', 'yellow',
'bright_blue', 'purple', 'bright_cyan', 'white']

color_none         = chr(27) + "[0m"
color_black        = chr(27) + "[30m"
color_red          = chr(27) + "[31m"
color_green        = chr(27) + "[32m"
color_brown        = chr(27) + "[33m"
color_blue         = chr(27) + "[34m"
color_magenta      = chr(27) + "[35m"
color_cyan         = chr(27) + "[36m"
color_light_gray   = chr(27) + "[37m"
color_dark_gray    = chr(27) + "[30;1m"
color_bright_red   = chr(27) + "[31;1m"
color_bright_green = chr(27) + "[32;1m"
color_yellow       = chr(27) + "[33;1m"
color_bright_blue  = chr(27) + "[34;1m"
color_purple       = chr(27) + "[35;1m"
color_bright_cyan  = chr(27) + "[36;1m"
color_white        = chr(27) + "[37;1m"

__all__ = ['FileDialog', 'ActionControllerMixin', 'NotebookLabel']
