#!/usr/bin/python3

# NAME
#   Lauras Simple Template Enginge - LSTE
#
# SYNOPSIS
#   ./lste.py [--watch] [--path] [--destination]
#
# DESCRIPTION
#   This script generates a website to ./dist out of the given template
#   parts, the assets and the content itself
#
# EXAMPLE:
#   ./lste.py --path ./website-src --destination ./website
#
# OPTIONS
#   -p|--path         Sets the base directory for the website. If not setted
#                     LSTE uses the current active directory
#   -d|--destination  Sets the directory where the website is rendered to
#   -w|--watch        Automatically generates the website to ./dist
#                     if a file in /src, /assets or /parts changed
#
# LEGAL NOTE
#   Written and maintained by Laura Herzog (laura-herzog@outlook.com)
#   Permission to copy and modify is granted under the GPL license
#   Project Information: https://github.com/lauraherzog/lste/

import os, time, shutil, getopt, sys, configparser

class LSTE:
	base_path = os.getcwd()
	src_path = os.getcwd() + "/src"
	parts_path = os.getcwd() + "/parts"
	assets_path = os.getcwd() + "/assets"
	dist_path = os.getcwd() + "/dist"
	config_file = ""
	file_stack = {}
 
	def __init__(self):
		opts, args = getopt.getopt(sys.argv[1:], "hwp:d:", ["watch", "path", "destination"])
		run_watcher = False
		for operator, argument in opts:
			if operator in ("-w", "--watch"):
				run_watcher = True
			elif operator in ("-p", "--path"):
       
				# make path absolute
				if os.path.isabs(argument) == False:
					argument = os.path.abspath(argument)
     
				if os.path.isdir(argument):
					self.base_path = argument
					self.src_path = self.base_path + "/src"
					self.parts_path = self.base_path + "/parts"
					self.assets_path = self.base_path + "/assets"
					self.dist_path = self.base_path + "/dist"
				else:
					assert False, "directory does not exist"
			elif operator in ("-d", "--destination"):
				# make path absolute
				if os.path.isabs(argument) == False:
					argument = os.path.abspath(argument)
					self.dist_path = argument
			else:
				assert False, "unhandled option"

		# check for the lste configuration file
		if not os.path.isfile(self.base_path + '/lste.conf'):
			print("Error: lste.conf not found")
			exit()
		self.config_file = self.base_path + '/lste.conf'

		if run_watcher:
			self.setup_filestack(self)
			self.run_file_watcher(self)
		else:
			self.render_site(self)

	@staticmethod
	def render_site(self):

		# empty dist folder
		if os.path.isdir(self.dist_path):
			shutil.rmtree(self.dist_path)
		os.makedirs(self.dist_path)

		# copy assets folder
		shutil.copytree(self.assets_path, self.dist_path + '/assets')

		# load template files
		files = os.listdir(self.src_path)
		for file in files:
			print(f'Rendering template for: {file}')
			filename = self.src_path + '/' + file
			html = self.load_template_file(self, filename)
			html = self.load_custom_functions(self, html)
			html = html.lstrip()

			with open(f'{self.dist_path}/{file}',"w") as handle:
				handle.write(html)

		print(f'Finished rendering website')

	@staticmethod
	def load_template_file(self, filepath):
		with open(filepath) as handle:
			content = handle.read()
		html = self.load_template_parts(self, content)
		return html

	@staticmethod
	def load_template_parts(self, content):
		html = content
		for line in content.splitlines():
			# load the template part
			line = line.lstrip()
			if "<!-- [part: " in line:
				template_part = line.replace("<!-- [part: ", "")
				template_part = template_part.replace("] -->", "")
				template_part_filename = template_part
				template_part = self.parts_path + "/" + template_part + ".html"
				part_content = self.load_template_file(self, template_part)
				html = html.replace(f'<!-- [part: {template_part_filename}] -->', part_content)
		return html

	@staticmethod
	def load_custom_functions(self, content):
		html = content

		# Load Meta Data
		for line in content.splitlines():

			# active menu entry
			line = line.lstrip()
			if "<!-- [active-menu-entry: " in line:
				active_menu_entry = line.replace("<!-- [active-menu-entry: ", "")
				active_menu_entry = active_menu_entry.replace("] -->", "")
				active_menu_entry = active_menu_entry
				if active_menu_entry == "none":
					continue
				else:
					html = html.replace(f'<!-- [active-menu-entry: {active_menu_entry}] -->', '')
					html = html.replace(f'<li id="{active_menu_entry}">', f'<li class="active" id="{active_menu_entry}">')

			# title
			if "<!-- [title: " in line:
				title = line.replace("<!-- [title: ", "")
				title = title.replace("] -->", "")
				html = html.replace(f'<!-- [title: {title}] -->', '')
				html = html.replace(f'<!-- [func: title] -->', title)

			# keywords
			if "<!-- [meta-keywords: " in line:
				keywords = line.replace("<!-- [meta-keywords: ", "")
				keywords = keywords.replace("] -->", "")
				html = html.replace(f'<!-- [meta-keywords: {keywords}] -->', '')
				html = html.replace(f'<!-- [func: meta-keywords] -->', keywords)

			# description
			if "<!-- [meta-description: " in line:
				description = line.replace("<!-- [meta-description: ", "")
				description = description.replace("] -->", "")
				html = html.replace(f'<!-- [meta-description: {description}] -->', '')
				html = html.replace(f'<!-- [func: meta-description] -->', description)

		# timestamp
		timestamp = int(time.time())
		html = html.replace('<!-- [func: timestamp] -->', str(timestamp))
  
		# replace template variables if template did not set them
		config = configparser.ConfigParser()
		config.read(self.base_path + '/lste.conf')

		# replace config variables
		html = html.replace(f'<!-- [func: title] -->', config['lste']['title'])
		html = html.replace(f'<!-- [func: meta-keywords] -->', config['lste']['meta-keywords'])
		html = html.replace(f'<!-- [func: meta-description] -->', config['lste']['meta-description'])

		return html

	@staticmethod
	def setup_filestack(self):
		parts_files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(self.parts_path) for f in filenames]
		src_files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(self.src_path) for f in filenames]
		assets_files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(self.assets_path) for f in filenames]

		for part_file in parts_files:
			mtime = os.path.getmtime(part_file)
			self.file_stack[part_file] = mtime

		for src_file in src_files:
			mtime = os.path.getmtime(src_file)
			self.file_stack[src_file] = mtime

		for asset_file in assets_files:
			mtime = os.path.getmtime(asset_file)
			self.file_stack[asset_file] = mtime
   
		mtime = os.path.getmtime(self.config_file)
		self.file_stack[self.config_file] = mtime

	@staticmethod
	def run_file_watcher(self):
		print('Watching folders ./src, ./assets and ./parts for changes ...')

		while(True):
			change_found = False

			parts_files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(self.parts_path) for f in filenames]
			for part_file in parts_files:
				mtime = os.path.getmtime(part_file)
				if part_file not in self.file_stack or self.file_stack[part_file] != mtime:
					change_found = True

			src_files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(self.src_path) for f in filenames]
			for src_file in src_files:
				mtime = os.path.getmtime(src_file)
				if src_file not in self.file_stack or self.file_stack[src_file] != mtime:
					change_found = True
	
			assets_files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(self.assets_path) for f in filenames]
			for asset_file in assets_files:
				mtime = os.path.getmtime(asset_file)
				if asset_file not in self.file_stack or self.file_stack[asset_file] != mtime:
					change_found = True

			mtime = os.path.getmtime(self.config_file)
			if self.config_file not in self.file_stack or self.file_stack[self.config_file] != mtime:
				change_found = True

			if change_found:
				print('Change detected')
				self.render_site(self)
				self.setup_filestack(self)
				change_found = False
		
			time.sleep(500/1000)

if __name__ == "__main__":
	lste = LSTE()
