#!/usr/bin/env python

"""Rezyn is a static website generator in Python
"""

# default
import sys
import os
import re
import shutil
import math
import getopt
import subprocess
import random

# requirements
import datetime
import dateutil.parser
import lxml.html
import lxml.etree
import yaml
import markdown
import bbcode
import slimit
import pytz

# local copy
import minifycss

# library code
import nsdict
import solon

# Internal debugging / tracing
LOG = True
if LOG:
	import pdb
	import traceback
def log(*args, **kwargs):
	if LOG:
		for arg in args:
			sys.stderr.write(str(arg))
		sys.stderr.write("\n")

solon.LOG=True
#####################################################

def readfile(filename):
	with open(filename, "r") as f:
		return f.read()

def writefile(filename, contents):
	with open(filename, "w") as f:
		f.write(contents)

def parsedate(date_str):
	d = dateutil.parser.parse(date_str)
	return d.strftime('%Y/%m/%d %H:%M:%S')

def separateheader(text):
	# If there is a YAML header the protocol is to separate it from the main body
	# content using a single "---" line.
	spec = r'^---\s*\n(.*)^---\s*\n(.*)'
	# re needs to match newlines and be multi-line aware
	flags = re.DOTALL | re.M
	m = re.match(spec, text, flags)
	if not m:
		# no match, return the whole text as the body
		return "", text
	fileheader, filebody = m.groups()
	return fileheader, filebody

#####################################################

class Rezyn:

	def __init__(self, config):
		self.solon = solon.Solon(config)
		self.bbparser = bbcode.Parser()

	def parsebb(self, text):
		parser = bbcode.Parser()
		return parser.format(text)

	def parsemd(self, text):
		return markdown.markdown(text)

	def texttohtml(self, ext, text):
		# convert the body text into an html snippet, if it not an html file
		if ext == '.md':
			html = self.parsemd(text)
		elif ext == ".bb":
			html = self.parsebb(text)
		elif ext == ".html":
			html = text
		else:
			raise NoConversion("Do not know how to turn [%s] into HTML" % ext)
		return html

	def readfile(self, filename):
		"""Read content and metadata from file into a dictionary."""

		# Each file has a slug, which is pretty much its basename
		path, ext = os.path.splitext(filename)
		dirpath, base = os.path.split(path)
		slug = base
		content = nsdict.NSDict({
			'slug': slug,
		})

		# Read file content.
		filecontent = unicode(readfile(filename), encoding='utf-8')

		# split the yaml frontmatter and body text
		fileheader, filebody = separateheader(filecontent)
		fm = yaml.safe_load(fileheader)
		if fm is not None:
			# it is not an error if no yaml is present, the file simply has no metadata
			content.update(fm)

		# convert the body text into an html snippet, if it not an html file
		text = self.texttohtml(ext.lower(), filebody)

		# create an xml representation of the document
		# we have to add a root element, since the text may or may not have one
		root = lxml.html.fromstring("<div class='filecontent'>" + text + "</div>")

		# find all images, and prepare them for lightbox
		imgs = root.findall(".//img")
		if 'thumbnail' not in content and len(imgs) > 0:
			# if thumbnail was not set, and we have images, set it to the first image
			content['thumbnail'] = imgs[0].attrib["src"]

		# convert the html tree back to text
		text = lxml.html.tostring(root)
		content['content'] = text

		# convert the string date into a raw datetime we can work with
		if 'date' in content:
			datestr = content['date']
			content['date'] = dateutil.parser.parse(datestr)

		# escape any html entitied in the title here:
		#content['title'] = xml.sax.saxutils.escape(content['title'])

		return content

	def readcontent(self, contentpath):
		contentpath = os.path.join(self.solon.context.config.srcdir, contentpath)
		log("loading content from [%s]" % contentpath)
		# load everything in the path into env
		for dirName, subdirList, fileList in os.walk(contentpath):
			root = dirName[len(contentpath)+1:]
			for fileName in fileList:
				if fileName == ".DS_Store":
					continue
				fullpath = os.path.join(dirName, fileName)
				if 0:
					base, ext = os.path.split(fileName)
					var = os.path.join("content", root, base)
				else:
					var = os.path.join("content", root, fileName)
				log("adding content ", var)
				filecontent = self.readfile(fullpath)
				if self.solon.context['config/publish_all'] or "nopublish" not in filecontent:
					log("readcontent: adding content to [%s]" % var)
					self.solon.context[var] = filecontent

	def readtemplates(self, templatepath, depth = None):
		templatepath = os.path.join(self.solon.context.config.srcdir, templatepath)
		# load everything in the template folder
		for level, (dirName, subdirList, fileList) in enumerate(os.walk(templatepath)):
			root = dirName[len(templatepath)+1:]
			for fileName in fileList:
				fullpath = os.path.join(dirName, fileName)
				var = os.path.join("template", root, fileName)
				log("adding template ", var)
				self.solon.addtemplate(var, readfile(fullpath))
			if depth is not None and level == depth:
				break

	def generatecsskeyfiles(self, usedebugchecksum, sourcedir, targetdir):
		# grab the keys for each file in the static dir
		csskeys = {}
		for dirName, subdirList, fileList in os.walk(sourcedir):
			for fileName in fileList:
				base, ext = os.path.splitext(fileName)
				if ext.lower() == ".css":
					fullsourcepath = os.path.join(dirName, fileName)
					log("generatecsskeyfiles on [%s]" % fullsourcepath)
					# generate a unique key for the file
					if usedebugchecksum:
						# debug build: we want to generate a new key each build, so that the browser will be forced to reload these files
						key = hex(random.getrandbits(32))
					else:
						# deploy: we want the keys to remain stable between edits, so we use part of the commit hashes
						status = subprocess.check_output(["git", "status", "--short", fullsourcepath])
						if len(status) > 0:
							if status.startswith("??"):
								print "css file [%s] is not under git control" % fullsourcepath
							else:
								print "css file [%s] has local modifications" % fullsourcepath
							sys.exit(0)
						key = subprocess.check_output(["git", "log", "-n", "1", "--pretty=format:%H", "--", fullsourcepath])
						log("found key [%s]" % key)
						if len(key) == 0:
							print "css file [%s] has no git checksum" % fullsourcepath
							sys.exit(0)
						assert(len(key) == 40) # check that we actually have a commit hash TODO: this needs to be more thorough.
						key = key[:16]
					log("key is [%s]" % key)
					# add the key as csskeys.basename for each file, so that the page.html can find it.
					csskeys[base] = key
					# rename the target file
					subdirName = dirName[len(sourcedir) + 1:]
					fulltargetpath = os.path.join(targetdir, subdirName, fileName)
					renamepath = os.path.join(targetdir, subdirName, base + "-" + key + ext)
					log("renaming [%s] to [%s]" % (fulltargetpath, renamepath))
					shutil.move(fulltargetpath, renamepath)
		return csskeys

	def minifydir(self, path):

		for dirName, subdirList, fileList in os.walk(path):
			for fileName in fileList:
				if fileName == ".DS_Store":
					continue
				base, ext = os.path.splitext(fileName)
				filename = os.path.join(dirName, fileName)
				if ext.lower() == ".css":
					mincss = minifycss.minify(readfile(filename))
					writefile(filename, mincss)
				elif ext.lower() == ".js":
					minjs = slimit.minify(readfile(filename))
					writefile(filename, minjs)

	def setup(self):

		# set up timezone
		tz = pytz.timezone(self.solon.context['config/timezone'])
		self.solon.context['config/tz'] = tz
		self.solon.context['config/now'] = datetime.datetime.now(tz)
		self.solon.context['config/current_year'] = self.solon.context['config/now'].year

		targetdir = os.path.join(self.solon.context.config.tgtdir, self.solon.context.config.tgtsubdir)
		staticdir = os.path.join(self.solon.context.config.srcdir, self.solon.context.config.staticdir)
		log("setup sourcedir [%s] -> targetdir [%s]" % (staticdir, targetdir))

		# remove the target directory
		log("removing targetdir [%s]" % targetdir)
		try:
			#if os.path.exists(targetdir):
			#	
			shutil.rmtree(targetdir)
		except Exception as e:
			print "Exception:", e
			pass

		# copy everything from static to the target directory
		log("copy sourcedir [%s] to targetdir [%s]" % (staticdir, targetdir))
		shutil.copytree(staticdir, targetdir)
		if "config/minify" in self.solon.context and self.solon.context["config/minify"]:
			# web minify (css and js)
			log("minify web in targtdir [%s]" % targetdir)
			self.minifydir(targetdir)

		# rename css files with keys
		# TODO this needs to be an option, but the templates can hardcode access to 'csskeys' now so this needs thought.
		csskeys = self.generatecsskeyfiles(self.solon.context["config/debug"], staticdir, targetdir)
		# make the keys available to the template(s)
		self.solon.context['csskeys'] = csskeys

	def process(self):

		self.setup()

		#### Read in website content + templates

		self.readcontent(self.solon.context["config/contentdir"])
		self.readtemplates(self.solon.context["config/templatedir"])

		# post process the data

		posts = [self.solon.context['content/blog'][post] for post in self.solon.context['content/blog'].keys()]
		sortedposts = sorted(posts, key=lambda values: values['date'], reverse=True)
		self.solon.context['content/sortedposts'] = sortedposts

		# render the templates

		self.solon.rendertemplate("template/rss.tpl")
		self.solon.rendertemplate("template/site.tpl")
		self.solon.rendertemplate("template/sitemap.txt")
		self.solon.rendertemplate("template/robots.txt")

		for filename, content in self.solon.context.output.dict().iteritems():
			path = os.path.join(self.solon.context['config/tgtdir'], self.solon.context['config/tgtsubdir'], filename)
			log("writing [%s]..." % path)
			writefile(path, content)


class BaseException(Exception):
	def __init__(self, message):
		self.message = message

	def __str__(self):
		return self.message

class NoConversion(BaseException):
	def __init__(self, message):
		BaseException.__init__(self, message)


def usage(self, exitcode, program, message):
	print """\
Usage: %s [-d|--debug] [--config=<CONF>] [--targetdir=<DIR>] [--publish-all] [--help]
Where:
	--debug specifies the site should be built to debug
	--config=<CONFIG> specifies where to find the CONFIG file
	--targetdir=<DIR> specifies the output to go to the subdirectory DIR. This directory
		will be deleted & recreated during the running of the program!
		This defaults to "_http"
	--publish-all will publish all content, even if marked 'nopublish'
	--help prints this help and exits
""" % program
	sys.exit(exitcode)

def processargs(argv):

	filelist = []

	configname = 'config.yml'
	tgtdir = "_http"
	dbg_site_url = 'http://localhost:8000'
	tgtsubdir = None
	publish_all = False
	debug = False
	srcdir = None

	try:
		optlist, args = getopt.gnu_getopt(argv[1:], 's:dc:T:t:ph', ['sourcedir=', 'debug', 'config=', 'targetdir=', 'targetsubdir=', 'publish-all', 'help'])
	except getopt.GetoptError as err:
		usage(-2, argv[0], err)
	for opt, arg in optlist:
		if opt in ('-c', '--config'):
			configname = arg
		elif opt in ('-s', '--sourcedir'):
			srcdir = arg
		elif opt in ('-T', '--targetdir'):
			tgtdir = arg
		elif opt in ('-t', '--targetsubdir'):
			tgtsubdir = arg
		elif opt in ('-p', '--publish-all'):
			publish_all = True
		elif opt in ('-h', '--help'):
			usage(0, argv[0], '')
		elif opt in ('-d', '--debug'):
			debug = True
		else:
			usage(-1, argv[0], "unknown argument [%s]" % opt)
	if len(args) > 0:
		usage(-1, argv[0], "illegal arguments: %s" % (" ".join(args)))

	if srcdir is None:
		srcdir = os.path.split(configname)[0]

	config = nsdict.NSDict(yaml.safe_load(readfile(configname)))

	config['config'].update({
		'srcdir' 						: srcdir,
		'tgtdir' 						: tgtdir,
		'base_path'						: '',
		'publish_all'					: publish_all,
		'debug'							: debug,
	})

	if tgtsubdir:
		config['config/tgtsubdir'] = tgtsubdir

	if debug:
		config['config/site_url'] = dbg_site_url
	
	return config

if __name__=="__main__":
	import pdb
	import traceback
	try:
		config = processargs(sys.argv)

		rezyn = Rezyn(config)
		rezyn.process()
	except:
		traceback.print_exc()
		pdb.post_mortem()


