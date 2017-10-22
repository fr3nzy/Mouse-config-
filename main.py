#!/usr/bin/env python3
from gi.repository import Gtk, Gdk
import os, subprocess

class mouse_config(Gtk.Window):
    def __init__(self):
        
        Gtk.Window.__init__(self, title="Mouse Config")
        self.set_default_size(420, 200)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        fix = Gtk.Fixed()
        self.add(fix)
        
        global mouseCombo
        mouseCombo = Gtk.ComboBoxText()
        mouseCombo.connect("changed", self.mouse_selected)
        mouseCombo.set_size_request(120, 30)
        fix.put(mouseCombo, 5, 8)
        xinput_output = os.popen("xinput --list --short | awk -F\"\t\" '{$1}'").readlines()
        # TODO: extract name of mouse AND id from the output of above command
        
        for item in xinput_output:
            xinput_output_item = xinput_output[item]
            mouseCombo.append("item {}".format(item), xinput_output_item)
        
        
        accel_label = Gtk.Label()
        accel_label.set_markup("<b>Mouse Acceleration:</b>")
        fix.put(accel_label,10 ,45)
        
        adjustment = Gtk.Adjustment(value=0,
        																	lower=0,
        																	upper=25,
        																	step_increment=1,
        																	page_increment=5,
        																	page_size=0)
        self.accel_spin = Gtk.SpinButton()
        self.accel_spin.set_adjustment(adjustment)
        self.accel_spin.connect("value-changed", self.accel_spin_changed)
        fix.put(self.accel_spin, 130, 70)
        
        
        decel_label = Gtk.Label()
        decel_label.set_markup("<b>Mouse Deceleration:</b>")
        fix.put(decel_label, 10, 110)
        
        adjustment = Gtk.Adjustment(value=0,
        																	lower=-20,
        																	upper=25,
        																	step_increment=1,
        																	page_increment=5,
        																	page_size=0)
        self.decel_spin = Gtk.SpinButton()
        self.decel_spin.set_adjustment(adjustment)
        fix.put(self.decel_spin, 130, 135)
        
        self.startup_checkButton = Gtk.CheckButton(label="Run on Startup")
        self.startup_checkButton.set_active(True)
        if self.startup_checkButton.get_active():
            self.run_commands_on_startup()
        fix.put(self.startup_checkButton, 280, 180)
        
    def mouse_selected(self):
        self.mouse = mouseCombo.get_active_text()
        
    def run_commands_on_startup(self):
        home = os.environ["HOME"]
        os.chdir(home)
        if os.path.isdir(".mouse_config") == False:
        	os.mkdir(".mouse_config")
        os.chdir(".mouse_config")
        
	def accel_spin_changed(self):
		accel_value = self.accel_spin.get_value()
		subprocess.call("xset m {}".format(accel_value))
        
        
window = mouse_config()
window.show_all()
window.connect("delete-event", Gtk.main_quit)
Gtk.main()
