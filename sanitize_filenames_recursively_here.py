# Blacklisted symbols that will be replaced in filenames.
blacklist = ["\\", "/", ":", "*", "?", "\"", "<", ">", "|", "\0"]
	
# Reserved words on Windows (and other exceptions).
reserved = [
	"CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4", "COM5",
	"COM6", "COM7", "COM8", "COM9", "LPT1", "LPT2", "LPT3", "LPT4", "LPT5",
	"LPT6", "LPT7", "LPT8", "LPT9", "Thumbs.db:encryptable", 
]

"""
Return a fairly safe version of the filename.
We don't limit ourselves to ascii, because we want to keep municipality
names, etc, but we do want to get rid of anything potentially harmful,
and make sure we do not exceed Windows filename length limits.
Hence a less safe blacklist, rather than a whitelist.
"""


# Below is the section of code taken and re-used with original licence from:
# https://pypi.org/project/sanitize-filename/ by Leo Wallentin | J++ Stockholm


#==============================================================================
#MIT License

#Copyright (c) 2020 J++ Stockholm

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.
#==============================================================================
"""A permissive filename sanitizer."""
import unicodedata
import re

# A list to fill up with exceptions for manual treatment.
exceptions = []

def sanitize(filename, root):
	if filename in reserved:
		exceptions.append(os.path.join(root, filename))
	else:
		filename = "".join(c for c in filename if c not in blacklist)
		# Remove all charcters below code point 32
		filename = "".join(c for c in filename if 31 < ord(c))
		filename = unicodedata.normalize("NFKD", filename)
		filename = filename.rstrip(". ")  # Windows does not allow these at end
		filename = filename.strip()
		if all([x == "." for x in filename]):
			filename = "__" + filename
		if len(filename) == 0:
			filename = "__"
		if len(filename) > 255:
			parts = re.split(r"/|\\", filename)[-1].split(".")
			if len(parts) > 1:
				ext = "." + parts.pop()
				filename = filename[:-len(ext)]
			else:
				ext = ""
			if filename == "":
				filename = "__"
			if len(ext) > 254:
				ext = ext[254:]
			maxl = 255 - len(ext)
			filename = filename[:maxl]
			filename = filename + ext
			# Re-check last character (if there was no extension)
			filename = filename.rstrip(". ")
			if len(filename) == 0:
				filename = "__"
	return filename
	

def test_invalid_chars():
	"""Make sure invalid characters are removed in filenames."""
	root = "/abc/efg"
	assert(sanitize("A/B/C",root) == "ABC")
	assert(sanitize("A*C.d",root) == "AC.d")


def test_invalid_suffix():
	"""Dots are not allowed at the end."""
	root = "/abc/efg"
	assert(sanitize("def.",root) == "def")
	assert(sanitize("def.ghi",root) == "def.ghi")
	assert(sanitize("X" * 1000 + ".",root).endswith("X"))


def test_long_names():
	"""Make sure long names are truncated."""
	root = "/abc/efg"
	assert(len(sanitize("X" * 300, root)) == 255)
	assert(len(sanitize(".".join(["X" * 100, "X" * 100, "X" * 100]),root)) == 255)
	assert(len(sanitize(".".join(["X" * 300, "X" * 300, "X" * 300]),root)) == 255)
	assert(len(sanitize("." * 300 + ".txt", root)) == 255)


def test_unicode_normalization():
	"""Names should be NFKD normalized."""
	root = "/abc/efg"
	assert(sanitize("ў", root) == chr(1091)+chr(774))


def test_extensions():
	"""Filename extensions should be preserved when possible."""
	really_long_name = "X" * 1000 + ".pdf"
	root = "/abc/efg"
	assert(sanitize(really_long_name, root).endswith(".pdf"))
	assert(sanitize("X" * 1000, root).endswith("X"))
	assert(sanitize("X" * 100 + "." + "X" * 100 + ".pdf", root).endswith(".pdf"))
	assert(sanitize("X" * 100 + "." + "X" * 400, root).endswith("X"))
	assert(sanitize("X" * 100 + "." + "X" * 400 + ".pdf", root).endswith(".pdf"))
	
# ==============================================================================
# End of the borrowed section of code.







import os

# https://stackoverflow.com/questions/287871/how-to-print-colored-text-to-the-terminal 
class col: 
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKCYAN = '\033[96m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	RED = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

# Perform tests from code above, in any case changes were made to it.
test_extensions()
test_invalid_chars()
test_invalid_suffix()
test_long_names()
test_unicode_normalization()

def c_prompt(prompt): 
	try: inp = input(prompt+" : ").rstrip()
	except KeyboardInterrupt: inp = ''
	return inp 

def cl(): os.system('cls' if os.name == 'nt' else 'clear')

def divider(): 
	d_line = '─' * 80
	print(d_line)

def get_exceptions():
	divider()
	print(col.WARNING, "Filenames were not changed due to being exceptions (see reserved list).", col.ENDC)
	divider()
	for filename in exceptions:
		print(col.WARNING, filename, col.ENDC)
	print()
	
def sanitize_recursively():
	print()
	for root, subdirs, files in os.walk("."):
		for entry in files:
			sanitized = sanitize(entry, root)
			if entry != sanitized:
				print(root)
				print("inp:", col.RED, entry, col.ENDC)
				print("out:", col.OKGREEN, sanitized, col.ENDC)
				print()
				src = os.path.join(root, entry)
				dst = os.path.join(root, sanitized)
				# https://stackoverflow.com/questions/44506197/how-to-handle-oserror-errno-36-file-name-too-long
				try:
					os.rename(src, dst)
				except OSError as exc:
					if exc.errno == 36:
						print(col.RED, "ERROR: Filename is too long, edit it manually (I don't know how to handle it).", col.ENDC)
						print(col.RED, "File name was not changed", col.ENDC)
					else:
						raise  # re-raise previously caught exception
	get_exceptions()

				
				
def sanitize_recursively_cold():
	print()
	for root, subdirs, files in os.walk("."):
		for entry in files:
			sanitized = sanitize(entry, root)
			if entry != sanitized:
				print(root)
				print("inp (COLD RUN):", col.RED, entry, col.ENDC)
				print("out (COLD RUN):", col.OKGREEN, sanitized, col.ENDC)
				print()
	get_exceptions()
		
if __name__ == "__main__":
	cl()
	abs_path = os.path.abspath(".")
	print(col.RED, "Perform filename sanitization recursively in this location:", col.ENDC)
	print(abs_path)
	print(col.OKGREEN, "Y - yes, N - no, C - cold run (no file change, only print output)", col.ENDC)
	msg = col.RED + "(Y | N | C)" + col.ENDC
	inp = c_prompt(msg)
	if (inp == "Y") or (inp == "y"):
		sanitize_recursively()
	elif (inp == "C") or (inp == "c"):
		sanitize_recursively_cold()
