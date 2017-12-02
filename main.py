#!python3

# requirements - cron

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Gio

import subprocess
import os
import time


class mouse_config(Gtk.Window):
	def __init__(self):
        
		Gtk.Window.__init__(self, title="Mouse Config")
		self.set_position(Gtk.WindowPosition.CENTER)
		self.set_border_width(10)
		
		headerBar = Gtk.HeaderBar()
		headerBar.set_show_close_button(True)
		headerBar.props.title = 'Velocity'
		self.set_titlebar(headerBar)
		
		about_button = Gtk.Button()
		icon = Gio.ThemedIcon(name='help-about-symbolic')
		image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
		about_button.add(image)
		headerBar.pack_start(about_button)
        
		global mouseCombo
		mouseCombo = Gtk.ComboBoxText()
		mouseCombo.connect("changed", self.mouse_selected)
		mouseCombo.set_size_request(360, 30)
		
		accel_label = Gtk.Label()
		accel_label.set_markup("<b>Acceleration</b>")
		
		adjustment = Gtk.Adjustment(value=0,
        							lower=0,
        							upper=100,
        							step_increment=1,
        							page_increment=5,
        							page_size=0)
		self.accel_spin = Gtk.SpinButton()
		self.accel_spin.set_adjustment(adjustment)
		self.accel_value = self.accel_spin.get_value()
		self.accel_value = int(self.accel_value)
		self.accel_spin.connect("value-changed", self.accel_spin_changed)
		
		decel_label = Gtk.Label()
		decel_label.set_markup("<b>Deceleration</b>")
        
		adjustment = Gtk.Adjustment(value=0,
        							lower=0,
        							upper=100,
        							step_increment=1,
        							page_increment=5,
        							page_size=0)
		self.decel_spin = Gtk.SpinButton()
		self.decel_spin.set_adjustment(adjustment)
		self.decel_value = self.decel_spin.get_value()
		self.decel_spin.connect('value-changed', self.decel_spin_changed)
		
		self.startup_checkButton = Gtk.CheckButton(label="Run on Startup")
		self.startup_checkButton.connect('toggled', self.startup_check_changed)
		
		grid = Gtk.Grid()	
		
		listBox = Gtk.ListBox()
		empty_label = Gtk.Label('')
		
		row1 = Gtk.ListBoxRow()
		hbox1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=140)
		hbox1.pack_start(accel_label, True, True, 0)
		hbox1.pack_start(self.accel_spin, False, True, 0)
		row1.add(hbox1)
		listBox.add(row1)
		
		row2 = Gtk.ListBoxRow()
		hbox2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=140)
		hbox2.pack_start(decel_label, True, True, 0)
		hbox2.pack_start(self.decel_spin, False, True, 0)
		row2.add(hbox2)
		listBox.add(row2)	
		
		row3 = Gtk.ListBoxRow()
		hbox3 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
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
		self.home = os.environ["HOME"] + '/'
		print(self.home)
		os.chdir(self.home)
		if os.path.isdir(".mouse_config") == False:
			os.mkdir(".mouse_config")              
			os.chdir(".mouse_config")
		os.chdir(self.home+'.mouse_config')
		
		# create file '.pointers'
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
				
				with open('.pointers', 'a') as f:
					f.write('{}\n'.format(x))
				
				position = counter 
				ctr+=1
			counter+=1
		
		# search for pointer, trim whitespace and get id of device in 'line'
		self.p_names = []  # to hold pointer names
		self.p_ids = []  # to hold pointer ids
		self.name_id = {}  # dictionary to hold 'name':id
		ctr1=0
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
							# add name and id to dict 'self.name_id'
							self.name_id[self.p_names[ctr1]] = self.p_ids[ctr1]
							print(ctr1)
							print(self.name_id)
							ctr1+=1
						ctr+=1
						
		########################################################
		for device in self.p_names:
			mouseCombo.append_text(device)
		########################################################
				
        
	def mouse_selected(self, mouseCombo):
		# i really don't know why this is working
		self.chosen = mouseCombo.get_active_text()
		for k,v in self.name_id.items()	:
			if self.chosen == k:
					self.id = v
		list_prop = subprocess.run(['xinput', 'list-props', str(self.id)], stdout=subprocess.PIPE).stdout.decode('utf-8')

		with open('.list_props', 'w') as f:
			f.write(list_prop)
		
		# search for property id in .list_props which contains the output of 'xinput list-props device_id'
		ctr4=0
		with open('.list_props', 'r') as f:
			for line in f:
				if 'Accel Constant Deceleration' in line:
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
						ctr4+=1
			if (ctr4 == 0):
				time.sleep(0.5)
				dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
					Gtk.ButtonsType.OK, 'Deceleration mode not available!')
				dialog.format_secondary_text('Constant deceleration is not available for this device')
				dialog.run()
				dialog.destroy()
        
        
	def accel_spin_changed(self, accel_spin):
		self.accel_value = self.accel_spin.get_value()
		self.accel_value = int(self.accel_value)
		print(self.accel_value)
		os.system('xset m {}'.format(self.accel_value))
		
		
	def decel_spin_changed(self, decel_spin):
		self.decel_value = self.decel_spin.get_value()
		if mouseCombo.get_active_text():
			os.system('xinput set-prop {} {} {}'.format(self.id, self.prop_id, self.decel_value))
		else:
			dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
				Gtk.ButtonsType.OK, 'No device selected!')
			dialog.format_secondary_text('Select a device to change deceleration')
			dialog.run()
			dialog.destroy()
		
		
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
        
	def startup_check_changed(self, startup_checkButton):
		if	startup_checkButton.get_active() == True:
			with open('startup.sh', 'w') as f:
				f.write('xset m {}\n'.format(self.accel_value))
				f.write('xinput set-prop {} {} {}'.format(self.id, self.prop_id, self.decel_value))
			os.system('chmod +x startup.sh')
			os.system('#crontab -e && @reboot {}startup.sh'.format(self.home))
			print('yay')
		else:
			print('damn')
			os.system('rm startup.sh')
		
        
window = mouse_config()
window.show_all()
window.connect("delete-event", Gtk.main_quit)
Gtk.main()
