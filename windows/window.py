#
# This file is part of Dragonfly.
# (c) Copyright 2007, 2008 by Christo Butcher
# Licensed under the LGPL.
#
#   Dragonfly is free software: you can redistribute it and/or modify it 
#   under the terms of the GNU Lesser General Public License as published 
#   by the Free Software Foundation, either version 3 of the License, or 
#   (at your option) any later version.
#
#   Dragonfly is distributed in the hope that it will be useful, but 
#   WITHOUT ANY WARRANTY; without even the implied warranty of 
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU 
#   Lesser General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public 
#   License along with Dragonfly.  If not, see 
#   <http://www.gnu.org/licenses/>.
#

"""
    This file implements a Window class as an interface to the Win32
    window control and placement.
"""


import win32gui
import dragonfly.windows.rectangle as rectangle_
import dragonfly.windows.monitor as monitor_


#===========================================================================

class Window(object):

    #-----------------------------------------------------------------------
    # Class attributes to retrieve existing Window objects.

    _windows_by_name = {}
    _windows_by_handle = {}

    #-----------------------------------------------------------------------
    # Class methods to create new Window objects.

    def get_foreground(cls):
        handle = win32gui.GetForegroundWindow()
        window = Window(handle=handle)
        return window
    get_foreground = classmethod(get_foreground)


    #=======================================================================
    # Methods for initialization and introspection.

    def __init__(self, handle=None):
        assert isinstance(handle, int)      # or handle == None
        self._handle = handle

    def __str__(self):
        return "%s(%d)" % (self.__class__.__name__, self._handle)

    #-----------------------------------------------------------------------
    # Methods that control attribute access.

    def _set_handle(self, handle):
        assert isinstance(handle, int)
        self._handle = handle
    handle = property(fget=lambda self: self._handle,
                      fset=_set_handle,
                      doc="Protected access to handle attribute.")

    #-----------------------------------------------------------------------
    # Direct access to various Win32 methods.

    def _win32gui_func(name):
        func = getattr(win32gui, name)
        return lambda self: func(self._handle)

    _get_rect           = _win32gui_func("GetWindowRect")
    _destroy            = _win32gui_func("DestroyWindow")
    _set_foreground     = _win32gui_func("SetForegroundWindow")
    _bring_to_top       = _win32gui_func("BringWindowToTop")
    _get_window_text    = _win32gui_func("GetWindowText")
    _get_class_name     = _win32gui_func("GetClassName")


    def _win32gui_test(name):
        test = getattr(win32gui, name)
        fget = lambda self: test(self._handle) and True or False
        return property(fget=fget,
                        doc="Shortcut to win32gui.%s() function." % name)

    is_valid        = _win32gui_test("IsWindow")
    is_enabled      = _win32gui_test("IsWindowEnabled")
    is_visible      = _win32gui_test("IsWindowVisible")
    is_minimized    = _win32gui_test("IsIconic")
#   is_maximized    = _win32gui_test("IsZoomed")

    #-----------------------------------------------------------------------
    # Methods related to window geometry.

    def get_position(self):
        l, t, r, b = self._get_rect()
        w = r - l; h = b - t
        print "dimensions", l, t, w, h
        return rectangle_.Rectangle(l, t, w, h)

    def set_position(self, rectangle):
        assert isinstance(rectangle, rectangle_.Rectangle)
        l, t, w, h = rectangle.ltwh
        print "dimensions", l, t, w, h
        win32gui.MoveWindow(self._handle, l, t, w, h, 1)

    def get_containing_monitor(self):
        center = self.get_position().center
        for monitor in monitor_.monitors:
            if monitor.rectangle.contains(center):
                return monitor
        # Fall through, return first monitor.
        return monitor_.monitors[0]

    def get_normalized_position(self):
        monitor = self.get_containing_monitor()
        rectangle = self.get_position()
        rectangle.renormalize(monitor.rectangle, rectangle_.unit)
        return rectangle

    def set_normalized_position(self, rectangle, monitor=None):
        if not monitor: monitor = self.get_containing_monitor()
        rectangle.renormalize(rectangle_.unit, monitor.rectangle)
        self.set_position(rectangle)
