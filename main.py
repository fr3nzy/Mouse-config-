#!python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

import subprocess
import os


class mouse_config(Gtk.Window):
	def __init__(self):
        
		Gtk.Window.__init__(self, title="Mouse Config")
		self.set_position(Gtk.WindowPosition.CENTER)
		self.set_default_size(420, 200)

        
		global mouseCombo
		mouseCombo = Gtk.ComboBoxText()
		mouseCombo.connect("changed", self.mouse_selected)
		mouseCombo.set_size_request(120, 30)
		
		
		accel_label = Gtk.Label()
		accel_label.set_markup("<b>Mouse Acceleration:</b>")
		
		adjustment = Gtk.Adjustment(value=0,
        							lower=0,
        							upper=25,
        							step_increment=1,
        							page_increment=5,
        							page_size=0)
		self.accel_spin = Gtk.SpinButton()
		self.accel_spin.set_adjustment(adjustment)
		self.accel_spin.connect("value-changed", self.accel_spin_changed)
		
		decel_label = Gtk.Label()
		decel_label.set_markup("<b>Mouse Deceleration:</b>")
        
		adjustment = Gtk.Adjustment(value=0,
        							lower=-20,
        							upper=25,
        							step_increment=1,
        							page_increment=5,
        							page_size=0)
		self.decel_spin = Gtk.SpinButton()
		self.decel_spin.set_adjustment(adjustment)
		
		self.startup_checkButton = Gtk.CheckButton(label="Run on Startup")
		self.startup_checkButton.set_active(True)
		if self.startup_checkButton.get_active():
			self.run_commands_on_startup()
	
		fix = Gtk.Fixed()	
		fix.put(mouseCombo, 5, 8)
		fix.put(accel_label,10 ,45)
		fix.put(self.accel_spin, 130, 70)
		fix.put(decel_label, 10, 110)
		fix.put(self.decel_spin, 130, 135)
		fix.put(self.startup_checkButton, 280, 180)
		self.add(fix)
		
		#####################################################################################################################
		#####################################################################################################################
		
		xinput_output = subprocess.run(['xinput','--list'], stdout=subprocess.PIPE).stdout.decode('utf-8')	
		cwd = subprocess.run(['pwd'], stdout=subprocess.PIPE).stdout.decode('utf-8')
		
		# create file '.pointers'
		os.chdir(cwd[:-1])
		if os.path.isfile('.pointers'):
			print('overwriting..')
			os.system('rm -rf .pointers')
			os.system('touch .pointers')
		else:
			os.system('touch .pointers')
			
		# counters
		counter=0
		position=0	# changes after first loop to counter - 
					# for each successful 'if' clause position is value of all characters to remove 
					# from start of variable 'x'		
		ctr=0	
		for i in xinput_output:	
			if i in ']':  # ']' is close to end of line
				x = len(xinput_output) - (counter)
				x = xinput_output[:-x]  # remove from end to after ']'  
				x = x[position:]  # slice first item in string
				x = x[7:]  # removes '⎜   ↳' from the start
				
				with open('{}/.pointers'.format(cwd[:-1]), 'a') as f:
					f.write('{}\n'.format(x))
				
				position = counter 
				ctr+=1
			counter+=1
		
		# search for pointer, trim whitespace and get id of device in 'line'
		with open('.pointers', 'r') as f:
			for line in f:
				if 'slave  pointer' in line:
					print(line)
					ctr=0
					for item in line:  
						# find id
						if item in '=':  # '=' is followed by the id
							if self.confirm_id(ctr, line):
								print('\tPointer id -- {}\n\n\n'.format(self.slave_id))
							self.trim_whitespace(ctr, line)
							print(self.p_name)
						ctr+=1
				
        
	def mouse_selected(self):
		self.mouse = mouseCombo.get_active_text()
        
	def run_commands_on_startup(self):
		home = os.environ["HOME"]
		os.chdir(home)
		if os.path.isdir(".mouse_config") == False:
			os.mkdir(".mouse_config")              
			os.chdir(".mouse_config")
        
	def accel_spin_changed(self, accel_spin):
		accel_value = self.accel_spin.get_value()
		acccel_value = str(accel_value)
		accel_value = int(accel_value)
		print(accel_value)
		os.system("xset m {}".format(accel_value))
		
	def trim_whitespace(self, index, cmd):
		to_trim = cmd[index:] 
		len_trim = len(to_trim)
		len_trim = len_trim + 2 # remove 'id'
		
		self.p_name = cmd[:-len_trim]
		
		# remove whitespace at end of len_trim
		# discard whitespace between words so whitespace must be more than 1 item
		ctr=0
		ctr1=0
		for i in self.p_name:
			if ' ' in i:
				for a in self.p_name:
					# if iter in first loop is one less than current iter 
					if ctr == (ctr1-1):  	
						# if second item is also whitespace
						if ' ' in a:
							# trim self.p_name of all items after first iter
							x = len(self.p_name) - ctr
							self.p_name = self.p_name[:-x]
					ctr1+=1 
			ctr+=1
				
		
		
	def confirm_id(self, index, cmd):
		self.slave_id = []  # pointer id
		self.cmd = cmd[index:]
		for a in self.cmd:
			if (a in '='):
				self.cmd = self.cmd[1:]
				for b in self.cmd:
					if (b.isdigit()):
						self.slave_id.append(b)
						self.cmd = self.cmd[1:]
						for c in self.cmd:
							if (c.isdigit()):
								self.slave_id.append(c)
								return True
							else:
								return True					
			else:
				self.cmd = self.cmd[1:]				
										
				
        
        
window = mouse_config()
window.show_all()
window.connect("delete-event", Gtk.main_quit)
Gtk.main()
