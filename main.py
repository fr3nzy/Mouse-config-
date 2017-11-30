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
		

		os.chdir(cwd[:-1])
		if os.path.isfile('.pointers'):
			print('overwriting..')
			os.system('rm -rf .pointers')
			os.system('touch .pointers')
		else:
			os.system('touch .pointers')
			
		# counters
		counter=0
		position=0
		ctr=0	
		for i in xinput_output:	
			if i in ']':
				x = len(xinput_output) - (counter)
				x = xinput_output[:-x]  # remove from end to after ']'
				if ctr >= 1:
					x = x[position:]
					x = x[7:]
				else:
					x = x[7:]
				variable = '{}'.format(x)
				
				with open('{}/.pointers'.format(cwd[:-1]), 'a') as f:
					f.write('{}\n'.format(variable))
				
				position = counter
				ctr+=1
			counter+=1
		
		with open('.pointers', 'r') as f:
			for line in f:
				if 'slave  pointer' in line:
					print(line)
					ctr=0
					for item in line:
						# find id
						if item in '=':
							if self.confirm_id(ctr, line):
								print('\tPointer id -- {}\n\n\n'.format(self.slave_id))
						ctr+=1
					
		#	if self.confirm_slave('s', counter, xinput_output):
		#			print('SUCCESS --------------------------------------  !!!!!')
				
        
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
		
		"""	
		pointers = []  # empty list 
		
		isSpace = 0  # counter for whitespace breaks
		ctr = 0 # counter for iter
		char_ctr = 0  # counter for number of chars in each string
		for i in pointers:
			print(i)
			for item in i:
				char_ctr += 1
				if ' ' in i:
					isSpace += 1
					if isSpace == 5:
						x = pointers[ctr]
						x = x[char_ctr:]
			ctr += 1
		print('x')
		print(x)
					
		print('This is: {}'.format(ctr))"""
		
	def confirm_id(self, index, cmd):
		self.slave_id = []
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
			
		
		
#	def confirm_slave(self, char, index, cmd):
#		# if char = 's' then trim all items before 's'. step by step character search for 'slave'
#		cmd = cmd[index:]
#		ctr_l=0
#		for i in cmd:
#			if (ctr_l==0) and (i in 'l'):
#				cmd = cmd[1:]
#				ctr_a=0
#				for x in cmd:
#					if (ctr_a==0) and (x in 'a'):
#						cmd = cmd[1:]
#						ctr_v=0
#						for y in cmd:
#							if (ctr_v==0) and (y in 'v'):
#								cmd = cmd[1:]
#								ctr_e=0
#								for z in cmd:
#									if (ctr_e==0) and (z in 'e'):
#										cmd = cmd[1:]
#										ctr_space=0
#										for a in cmd:
#											if (ctr_space==0) and (a in ' '):
#												cmd = cmd[1:]
#												ctr_p=0
#												for b in cmd:
#													if (ctr_p==0) and (b == ' '):
#														cmd = cmd[1:]
#														ctr_p1=0
#														for b in cmd:
#															if (ctr_p1==0) and (b == 'p'):
#																cmd = cmd[1:]
#																ctr_o=0
#																for c in cmd:
#																	if (ctr_o==0) and (c in 'o'):
#																		cmd = cmd[1:]
#																		ctr_i=0
#																		for d in cmd:
#																			if (ctr_i==0) and (d in 'i'):
#																				cmd = cmd[1:]
#																				ctr_n=0
#																				for e in cmd:
#																					if (ctr_n==0) and (e in 'n'):
#																						return True
#																					ctr_n+=1
#																			ctr_i+=1
#																	ctr_o+=1
#															ctr_p1+=1
#														ctr_p+=1
#											ctr_space+=1
#									ctr_e+=1
#							ctr_v+=1
#					ctr_a+=1
#			ctr_l+=1
			
				
										
				
			
        
        
window = mouse_config()
window.show_all()
window.connect("delete-event", Gtk.main_quit)
Gtk.main()
