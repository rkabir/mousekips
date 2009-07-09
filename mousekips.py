import globalkeybinding
import gtk
import time
from Xlib.display import Display
from Xlib import X
import Xlib

class KeyPointer:
  def __init__(self):
    self.display = Display ()
    self.screen = self.display.screen ()
    self.root = self.screen.root
    self.keymap = gtk.gdk.keymap_get_default ()
    keyval = gtk.keysyms.Return
    self.finish_keycode = self.keymap.get_entries_for_keyval(keyval)[0][0]
  def launch_cb(self, keybinding):
    print 'Grabbing Keyboard Focus'
    self.root.grab_keyboard(True, X.GrabModeAsync, X.GrabModeAsync,
                                  X.CurrentTime)
    print 'Placing pointer'
    self.screen_handler()
    try:
      self.display.ungrab_keyboard(X.CurrentTime)
      self.display.flush()
      print 'Finished placing pointer'
    except:
      gtk.main_quit()

  def setup_movementkeys(self, mapping_dict):
    self.movement_dict = mapping_dict
    self.movement_keycodes = {}
    for key in mapping_dict:
      keyval = gtk.gdk.unicode_to_keyval(ord(key))
      keycode = self.keymap.get_entries_for_keyval(keyval)[0][0]
      self.movement_keycodes[keycode] = mapping_dict[key]

  def setup_keymapping(self, mapping_array):
    # Map the keys to an x,y pair of where the key falls on the keyboard
    self.keyboard_keyvals = {}
    self.keymapping_array = mapping_array
    self.max_height = len(mapping_array)
    self.max_width = max([ len(x) for x in mapping_array ])
    for y in xrange(len(mapping_array)):
      for x in xrange(len(mapping_array[y])):
        keyval = gtk.gdk.unicode_to_keyval(ord(mapping_array[y][x]))
        self.keyboard_keyvals[keyval] = (x, y)

  def keypress_cb(self, e):
    # Find the coordinates of the key pressed

    try:
      # Check if this is a keypress event (not a release or button, etc)
      if e.__class__ is not Xlib.protocol.event.KeyPress:
        return
      keycode = e.detail
      state = e.state

      w = self.screen.width_in_pixels
      h = self.screen.height_in_pixels
      # Find out if there are any modifiers being pressed
      # If ctrl + movement key is being pressed, move over by some amount
      if state & X.ControlMask and keycode in self.movement_keycodes:
        print "Control Hold Movement Keys"
        movement = self.movement_keycodes[keycode]
        # move the cursor a little
        # Not sure how to calculate the amount to move by?
        # Maybe take the smallest h_block, w_block we have and divide into thirds?
        h_block = float(h) / self.max_height / 3
        w_block = float(w) / self.max_width / 3

        cursor_position = self.root.query_pointer()
        x = cursor_position.root_x
        y = cursor_position.root_y
        to_x, to_y = x, y
        if movement == 'left':
          to_x = x - w_block
        if movement == 'down':
          to_y = y + h_block
        if movement == 'up':
          to_y = y - w_block
        if movement == 'right':
          to_x = x + w_block

      else:
        keyval_tuple = self.keymap.translate_keyboard_state(e.detail, e.state, e.type)
        keyval, group, level, modifiers = keyval_tuple
        x, y = self.keyboard_keyvals[keyval]
        h_block = float(h) / len(self.keymapping_array)
        w_block = float(w) / len(self.keymapping_array[y])
      # divide the width by the number of rows we have and multiply by x to
      # figure out where the cursor goes

        to_x = w_block * x + (w_block / 2)
        to_y = h_block * y + (h_block / 2)

      print to_x, to_y
      self.root.warp_pointer(to_x, to_y)
    except KeyError, v:
      pass
    return e.detail == self.finish_keycode

  def error(self):
    pass

  def screen_handler(self):
    self.root.change_attributes(event_mask = X.KeyPressMask)
    self.screen = self.display.screen()
    while True:
      print 'next event'
      event = self.root.display.next_event()
      try:
        if self.keypress_cb(event):
          break
      except Exception, e:
        print e
        break
    self.root.change_attributes(event_mask = X.NoEventMask)
    self.display.allow_events(X.AsyncKeyboard, X.CurrentTime)
    self.display.allow_events(X.AsyncPointer, X.CurrentTime)

keymapping = [ "1234567890",
               "!@#$%^&*()",
               "qwertyuiop",
               "QWERTYUIOP",
               "asdfghjkl;",
               "ASDFGHJKL:",
               "zxcvbnm,./",
               "ZXCVBNM<>?" ]
keymovements = { "h" : "left",
                 "j" : "down",
                 "k" : "up",
                 "l" : "right" }

kp = KeyPointer()
kp.setup_keymapping(keymapping)
kp.setup_movementkeys(keymovements)

gtk.gdk.threads_init ()
keybinding = globalkeybinding.GlobalKeyBinding ("/apps/mousepy", "launch")
keybinding.connect ('activate', kp.launch_cb)
keybinding.grab ()
keybinding.start ()

gtk.main ()
