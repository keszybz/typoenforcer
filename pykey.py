#!/usr/bin/python
# -*- coding:utf-8; -*-

# Trimmed down version of pykey, extended to pick target window first.
#
# pykey -- a Python version of crikey,
# http://shallowsky.com/software/crikey
# Simulate keypresses under X11.
#
# This software is copyright 2008 by Akkana Peck,
# and copyright 2010 by Zbigniew Jędrzejewski-Szmek.
# Please share and re-use this under the terms of the GPLv2
# or, at your option, any later GPL version.

import sys, time
import re
import subprocess
import Xlib.display
import Xlib.X
import Xlib.XK
import Xlib.protocol.event

display = Xlib.display.Display()

def get_window_id():
    xwininfo = subprocess.Popen(['xwininfo'],
                                stdout=subprocess.PIPE, stderr=sys.stderr)
    output, errors = xwininfo.communicate()
    match = re.search(r'Window id: (0x[0-9a-f]+)', output)
    if match is None:
        raise ValueError('cannot find window id in xwininfo output')
    windowid = int(match.group(1), 16)
    return windowid

def get_window(windowid=None):
    #window = display.get_input_focus()._data["focus"];
    if windowid is None:
        windowid = get_window_id()
    window = display.create_resource_object('window', windowid)
    return window

special_X_keysyms = {
    ' ' : "space",
    '\t' : "Tab",
    '\n' : "Return",  # for some reason this needs to be cr, not lf
    '\r' : "Return",
    '\e' : "Escape",
    '!' : "exclam",
    '#' : "numbersign",
    '%' : "percent",
    '$' : "dollar",
    '&' : "ampersand",
    '"' : "quotedbl",
    '\'' : "apostrophe",
    '(' : "parenleft",
    ')' : "parenright",
    '*' : "asterisk",
    '=' : "equal",
    '+' : "plus",
    ',' : "comma",
    '-' : "minus",
    '.' : "period",
    '/' : "slash",
    ':' : "colon",
    ';' : "semicolon",
    '<' : "less",
    '>' : "greater",
    '?' : "question",
    '@' : "at",
    '[' : "bracketleft",
    ']' : "bracketright",
    '\\' : "backslash",
    '^' : "asciicircum",
    '_' : "underscore",
    '`' : "grave",
    '{' : "braceleft",
    '|' : "bar",
    '}' : "braceright",
    '~' : "asciitilde"
    }

def get_keysym(ch):
    keysym = Xlib.XK.string_to_keysym(ch)
    if keysym == 0 :
        # Unfortunately, although this works to get the correct keysym
        # i.e. keysym for '#' is returned as "numbersign"
        # the subsequent display.keysym_to_keycode("numbersign") is 0.
        if ch in special_X_keysyms:
            special = special_X_keysyms[ch]
            keysym = Xlib.XK.string_to_keysym(special)
    return keysym

def is_shifted(ch):
    if ch.isupper():
        return True
    if ch in '~!@#$%^&*()_+{}|:\"<>?':
        return True
    return False

def char_to_keycode(ch):
    keysym = get_keysym(ch)
    keycode = display.keysym_to_keycode(keysym)
    if keycode == 0 :
        print "Sorry, can't map", ch

    if (is_shifted(ch)) :
        shift_mask = Xlib.X.ShiftMask
    else :
        shift_mask = 0

    return keycode, shift_mask

def send_string(window, str):
    for ch in str :
        keycode, shift_mask = char_to_keycode(ch)
        if keycode == 0:
            keycode, shift_mask = char_to_keycode('_')

        print 'sending [{0!r}] keycode={1} with shift_mask={2}'.format(
            ch, keycode, shift_mask)
        for eventtype in (Xlib.protocol.event.KeyPress,
                          Xlib.protocol.event.KeyRelease):
            event = eventtype(root=display.screen().root,
                              window=window,
                              same_screen=0,
                              child=Xlib.X.NONE,
                              root_x=0, root_y=0,
                              event_x=0, event_y=0,
                              state=shift_mask,
                              detail=keycode,
                              time=int(time.time()))
            window.send_event(event, propagate=True)

if __name__ == '__main__':
    for arg in sys.argv[1:]:
        window = get_window()
        time.sleep(3)
        send_string(window, arg)
        display.sync()
