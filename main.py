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
		self.set_border_width(5)
        
		global mouseCombo
		mouseCombo = Gtk.ComboBoxText()
		mouseCombo.connect("changed", self.mouse_selected)
		mouseCombo.set_size_request(360, 30)
		
		accel_label = Gtk.Label()
		accel_label.set_markup("<b>Mouse Acceleration:</b>")
		
		adjustment = Gtk.Adjustment(value=0,
        							lower=0,
        							upper=100,
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
        							upper=100,
        							step_increment=1,
        							page_increment=5,
        							page_size=0)
		self.decel_spin = Gtk.SpinButton()
		self.decel_spin.set_adjustment(adjustment)
		
		self.startup_checkButton = Gtk.CheckButton(label="Run on Startup")
		self.startup_checkButton.set_active(True)
		if self.startup_checkButton.get_active():
			self.run_commands_on_startup()
			
		
		grid = Gtk.Grid()	
		
		listBox = Gtk.ListBox()
		empty_label = Gtk.Label('')
		
		row1 = Gtk.ListBoxRow()
		hbox1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50) # TODO set spacing to dynamically change according to window size
		hbox1.pack_start(accel_label, True, True, 0)
		hbox1.pack_start(self.accel_spin, False, True, 0)
		row1.add(hbox1)
		listBox.add(row1)
		
		row2 = Gtk.ListBoxRow()
		hbox2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50) # TODO set spacing to dynamically change according to window size
		hbox2.pack_start(decel_label, True, True, 0)
		hbox2.pack_start(self.decel_spin, False, True, 0)
		row2.add(hbox2)
		listBox.add(row2)	
		
		row3 = Gtk.ListBoxRow()
		hbox3 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50) # TODO set spacing to dynamically change according to window size
		hbox3.pack_end(self.startup_checkButton, False, True, 0)
		row3.add(hbox3)
		listBox.add(row3)
		

		grid.add(mouseCombo)
		grid.attach(empty_label, 0, 2, 1, 1)
		grid.attach(listBox, 0, 4, 1, 2)
		self.add(grid)
	
		
		#####################################################################################################################
		#####################################################################################################################
		
		xinput_output = subprocess.run(['xinput','--list'], stdout=subprocess.PIPE).stdout.decode('utf-8')	
		cwd = subprocess.run(['pwd'], stdout=subprocess.PIPE).stdout.decode('utf-8')
		# TODO: change pwd to home directory 
		
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
		self.p_names = []  # to hold pointer names
		self.p_ids = []  # to hold pointer ids
		with open('.pointers', 'r') as f:
			for line in f:
				if 'slave  pointer' in line:
					ctr=0
					for item in line:  
						# find id

						if item in '=':  # '=' is followed by the id
							if self.confirm_id(ctr, line):
								print('\tPointer id -- {}\n\n\n'.format(self.p_ids))
							self.trim_whitespace(ctr, line)
						ctr+=1
						
		########################################################
		for device in self.p_names:
			mouseCombo.append_text(device)
		########################################################
				
        
	def mouse_selected(self, mouseCombo):
		list_prop = subprocess.run(['xinput', 'list-props', str(self.p_ids)], stdout=subprocess.PIPE).stdout.decode('utf-8')

		with open('.list_props', 'w') as f:
			f.write(list_prop)
		
		# search for property id in .list_props which contains the output of 'xinput list-props device_id'
		with open('.list_props', 'r') as f:
			for line in f:
				if 'Accel Constant Deceleration' in line:
					print('ay')
					ctr=0
					print(line)
					for i in line:
						if '(' in i:
							ctr1=0
							for a in line:
								if ctr1 == (ctr+1):
									if a.isdigit():
										self.property = int(a)
										ctr2=0
										for b in line:
											if ctr2 == (ctr+2):
												if b.isdigit():
													self.property = (self.property * 10) + int(b)
													ctr3=0
													for c in line:
														if ctr3 == (ctr+3):
															if c.isdigit():
																self.property = (self.property * 10) + int(c)
																self.prop_id = self.property
																print('Property id: {}'.format(self.prop_id))
														ctr3+=1
											ctr2+=1
								ctr1+=1
						ctr+=1
        

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
		self.p_names.append(self.p_name)
				  
				
	def confirm_id(self, index, cmd):
		self.cmd = cmd[index:]
		for a in self.cmd:
			if (a in '='):
				self.cmd = self.cmd[1:]
				for b in self.cmd:
					if b.isdigit():
						self.p_id = b
						self.p_id = int(self.p_id)
						self.cmd = self.cmd[1:]
						for c in self.cmd:
							if c.isdigit():
								self.p_id = (self.p_id * 10) + int(c)
								self.p_ids.append(self.p_id)
								return True
							else:
								self.p_ids.append(self.p_id)
								return True					
			else:
				self.cmd = self.cmd[1:]		
		
			
										
				
        
        
window = mouse_config()
window.show_all()
window.connect("delete-event", Gtk.main_quit)
Gtk.main()
