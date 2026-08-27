#!/usr/bin/env python3
import pyjsonfrag 
import getopt
import sys

def usage():
  print("Usage: py_json_pp.js [-t] [-T] [-n] [-C [-C]] [-c count]", file=sys.stderr)
  sys.exit(1)

commentargcnt = 0
input_trailing_comma = False
use_tabs_for_indentation = False
nopretty = False
indentation_level = -1
try:
  opts, args = getopt.getopt(sys.argv[1:], "tTnCc:")
except getopt.GetoptError:
  usage()
for o,a in opts:
  if o == "-C":
    commentargcnt+=1
  elif o == "-T":
    input_trailing_comma = True
  elif o == "-t":
    use_tabs_for_indentation = True
  elif o == "-n":
    nopretty = True
  elif o == "-c":
    try:
      indentation_level = int(a)
      if indentation_level < 0:
        usage()
    except:
      usage()
  else:
    assert False

output_comments = (commentargcnt >= 2)
input_comments = (commentargcnt >= 1)
if indentation_level < 0:
  indentation_level = (use_tabs_for_indentation and 1 or 4)
if nopretty:
  indentation_level = None

class MySink(pyjsonfrag.JsonSink):
  def __init__(self):
    super().__init__(use_tabs_for_indentation, indentation_level)
  def sink_data(self, dat):
    sys.stdout.write(dat)
sink = MySink()

class MyHandler(pyjsonfrag.JsonHandler):
  def start_dict(self, key):
    if key is not None:
      sink.put_start_dict(key)
    else:
      sink.add_start_dict()
  def start_array(self, key):
    if key is not None:
      sink.put_start_array(key)
    else:
      sink.add_start_array()
  def end_dict(self, key):
    sink.end_dict()
  def end_array(self, key):
    sink.end_array()
  def handle_string(self, key, val):
    if key is not None:
      sink.put_string(key, val)
    else:
      sink.add_string(val)
  def handle_number(self, key, val, is_int):
    if key is not None:
      if is_int:
        sink.put_number(key, val)
      else:
        sink.put_flop(key, val)
    else:
      if is_int:
        sink.add_number(val)
      else:
        sink.add_flop(val)
  def handle_null(self, key):
    if key is not None:
      sink.put_null(key)
    else:
      sink.add_null()
  def handle_boolean(self, key, val):
    if key is not None:
      sink.put_boolean(key, val)
    else:
      sink.add_boolean(val)
  def handle_comment(self, comma_seen, comment, is_multiline):
    if output_comments:
      sink.comment(comma_seen, comment, is_multiline)
handler = MyHandler()
stream = pyjsonfrag.JsonStream(handler)

if input_comments:
  stream.allow_comments()
if input_trailing_comma:
  stream.allow_trailing_comma()

while True:
  buf = sys.stdin.read(4096)
  if len(buf) < 4096:
    stream.feed(buf, 0, len(buf), True)
    break
  else:
    stream.feed(buf, 0, len(buf), False)
sys.stdout.write('\n')
