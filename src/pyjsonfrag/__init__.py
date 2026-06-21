import io
import json
import math

JSONSTREAM_MODE_KEYSTRING = 1
JSONSTREAM_MODE_KEYSTRING_ESCAPE = 2
JSONSTREAM_MODE_KEYSTRING_UESCAPE = 3
JSONSTREAM_MODE_STRING = 4
JSONSTREAM_MODE_STRING_ESCAPE = 5
JSONSTREAM_MODE_STRING_UESCAPE = 6
JSONSTREAM_MODE_TRUE = 7
JSONSTREAM_MODE_FALSE = 8
JSONSTREAM_MODE_NULL = 9
JSONSTREAM_MODE_FIRSTKEY = 10
JSONSTREAM_MODE_KEY = 11
JSONSTREAM_MODE_FIRSTVAL = 12
JSONSTREAM_MODE_VAL = 13
JSONSTREAM_MODE_COLON = 14
JSONSTREAM_MODE_COMMA = 15
JSONSTREAM_MODE_NUMBER = 16
JSONSTREAM_MODE_ENDWS = 17

def is_valid_json(s, allow_comments=False, allow_trailing_comma=False):
  handler = JsonHandler()
  stream = JsonStream(handler)
  if allow_comments:
    stream.allow_comments()
  if allow_trailing_comma:
    stream.allow_trailing_comma()
  try:
    stream.feed(s, 0, len(s), True)
    return True
  except:
    return False

def is_valid_json_errloc(s, allow_comments=False, allow_trailing_comma=False):
  handler = JsonHandler()
  stream = JsonStream(handler)
  if allow_comments:
    stream.allow_comments()
  if allow_trailing_comma:
    stream.allow_trailing_comma()
  try:
    stream.feed(s, 0, len(s), True)
    return {"valid": True}
  except:
    res = {"valid": False}
    if hasattr(stream, "errloc"):
      lines = s[:stream.errloc].split("\n")
      res["errloc"] = stream.errloc
      res["errline"] = len(lines)-1
      res["errcol"] = len(lines[-1])
    return res

def pretty_print(s,
                 indentation_level=4, use_tabs_for_indentation=False,
                 allow_comments=False, output_comments=False,
                 allow_trailing_comma=False):
  tojoin = []
  class MyJsonSink(JsonSink):
    def __init__(self):
      super().__init__(use_tabs_for_indentation, indentation_level)
    def sink_data(self, dat):
      tojoin.append(dat)
  sink = MyJsonSink()
  class MyJsonHandler(JsonHandler):
    def handle_comment(self, comma_seen, val, is_multiline):
      if output_comments:
        sink.comment(comma_seen, val, is_multiline)
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
    def handle_number(self, key, num, is_integer):
      if key is not None:
        if is_integer:
          sink.put_number(key, num)
        else:
          sink.put_flop(key, num)
      else:
        if is_integer:
          sink.add_number(num)
        else:
          sink.add_flop(num)
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
    def handle_string(self, key, val):
      if key is not None:
        sink.put_string(key, val)
      else:
        sink.add_string(val)
  handler = MyJsonHandler()
  stream = JsonStream(handler)
  stream.feed(s, 0, len(s), True)
  return ''.join(tojoin)

class JsonSink(object):
  def sink_data(self, dat):
    assert False # this method must be implemented
  def __init__(self, tabs, indentamount):
    if tabs:
      self.commanlindentchars = ",\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t"
    else:
      self.commanlindentchars = ",\n                                                                      "
    self.indentamount = indentamount
    self.curindentlevel = 0
    self.first = True
    self.veryfirst = True
    self.commentcomma = False
    self.commentnewline = False
  def internal_indent(self, comma):
    if self.indentamount is not None:
      toindent = self.curindentlevel * self.indentamount
    else:
      toindent = 0
    first = True
    indentchars = self.commanlindentchars
    off = 2
    do_extracomma = False
    if not comma:
      indentchars = indentchars[1:]
      off -= 1
    if self.commentcomma:
      comma = False
      self.commentcomma = False
    if self.indentamount is None:
      if comma:
        self.sink_data(",")
        return
      return
    if not self.commentnewline:
      if toindent == 0:
        if comma:
          self.sink_data(",\n")
          return
        self.sink_data("\n")
        return
    if self.commentnewline and not comma:
      first = False
    elif self.commentnewline and comma:
      first = False
      do_extracomma = True
    self.commentnewline = False
    while toindent > 0:
      thisround = toindent
      if thisround > len(indentchars)-2:
        thisround = len(indentchars)-2
      if first:
        sub = indentchars[0:(thisround+off)]
      else:
        sub = indentchars[off:(thisround+off)]
      self.sink_data(sub)
      toindent -= thisround
      first = False
    if do_extracomma:
      self.sink_data(", ")
  def internal_put_string(self, val):
    self.sink_data(json.dumps(str(val)))
  def internal_put_number(self, val):
    if type(val) == int:
      self.sink_data(str(val))
    else:
      fl = float(val)
      if not math.isfinite(fl):
        raise Exception("number not finite")
      self.sink_data(str(fl))
  def internal_put_number_ex(self, val):
    if type(val) == int:
      self.sink_data(str(val))
    else:
      fl = float(val)
      if not math.isfinite(fl):
        self.sink_data("null")
      else:
        self.sink_data(str(fl))
  def internal_put_flop(self, val):
    fl = float(val)
    if not math.isfinite(fl):
      raise Exception("number not finite")
    self.sink_data(str(fl))
  def internal_put_flop_ex(self, val):
    fl = float(val)
    if not math.isfinite(fl):
      self.sink_data("null")
    else:
      self.sink_data(str(fl))
  def put_start_dict(self, key):
    if self.veryfirst:
      raise Exception("logic error")
    self.internal_indent(not self.first)
    self.internal_put_string(key)
    self.first = True
    self.curindentlevel += 1
    if self.indentamount is None:
      self.sink_data(":{")
    else:
      self.sink_data(": {")
  def put_start_array(self, key):
    if self.veryfirst:
      raise Exception("logic error")
    self.internal_indent(not self.first)
    self.internal_put_string(key)
    self.first = True
    self.curindentlevel += 1
    if self.indentamount is None:
      self.sink_data(":[")
    else:
      self.sink_data(": [")
  def add_start_dict(self):
    if not self.veryfirst:
      self.internal_indent(not self.first)
    self.veryfirst = False
    self.first = True
    self.curindentlevel += 1
    self.sink_data("{")
  def add_start_array(self):
    if not self.veryfirst:
      self.internal_indent(not self.first)
    self.veryfirst = False
    self.first = True
    self.curindentlevel += 1
    self.sink_data("[")
  def end_dict(self):
    if self.curindentlevel == 0:
      raise Exception("logic error")
    self.curindentlevel -= 1
    if not self.first:
      self.internal_indent(False)
    self.first = False
    self.sink_data("}")
  def end_array(self):
    if self.curindentlevel == 0:
      raise Exception("logic error")
    self.curindentlevel -= 1
    if not self.first:
      self.internal_indent(False)
    self.first = False
    self.sink_data("]")
  def put_string(self, key, val):
    if self.veryfirst:
      raise Exception("logic error")
    self.internal_indent(not self.first)
    self.internal_put_string(key)
    if self.indentamount is None:
      self.sink_data(":")
    else:
      self.sink_data(": ")
    self.first = False
    self.internal_put_string(val)
  def add_string(self, val):
    if not self.veryfirst:
      self.internal_indent(not self.first)
    self.veryfirst = False
    self.internal_put_string(val)
    self.first = False
  def put_boolean(self, key, val):
    if self.veryfirst:
      raise Exception("logic error")
    self.internal_indent(not self.first)
    self.internal_put_string(key)
    if val:
      if self.indentamount is None:
        self.sink_data(":true")
      else:
        self.sink_data(": true")
    else:
      if self.indentamount is None:
        self.sink_data(":false")
      else:
        self.sink_data(": false")
    self.first = False
  def add_boolean(self, val):
    if not self.veryfirst:
      self.internal_indent(not self.first)
    self.veryfirst = False
    if val:
      self.sink_data("true")
    else:
      self.sink_data("false")
    self.first = False
  def put_null(self, key):
    if self.veryfirst:
      raise Exception("logic error")
    self.internal_indent(not self.first)
    self.internal_put_string(key)
    if self.indentamount is None:
      self.sink_data(":null")
    else:
      self.sink_data(": null")
    self.first = False
  def add_null(self):
    if not self.veryfirst:
      self.internal_indent(not self.first)
    self.veryfirst = False
    self.sink_data("null")
    self.first = False
  def comment(self, comma_seen, val, force_multiline=False):
    if "\r" in val or "\n" in val:
      force_multiline = True
    if force_multiline:
      if comma_seen:
        self.sink_data(", /*")
        self.commentcomma = True
        self.first = True
      else:
        self.sink_data(" /*")
      self.sink_data(val)
      self.sink_data("*/\n")
      self.commentnewline = True
      return
    if comma_seen:
      self.sink_data(", //")
      self.commentcomma = True
      self.first = True
    else:
      self.sink_data(" //")
    self.sink_data(val)
    self.sink_data("\n")
    self.commentnewline = True
  def put_number(self, key, val):
    if self.veryfirst:
      raise Exception("logic error")
    self.internal_indent(not self.first)
    self.internal_put_string(key)
    if self.indentamount is None:
      self.sink_data(":")
    else:
      self.sink_data(": ")
    self.first = False
    self.internal_put_number(val)
  def put_number_ex(self, key, val): # convert NaN/Inf to null
    if self.veryfirst:
      raise Exception("logic error")
    self.internal_indent(not self.first)
    self.internal_put_string(key)
    if self.indentamount is None:
      self.sink_data(":")
    else:
      self.sink_data(": ")
    self.first = False
    self.internal_put_number_ex(val)
  def put_flop(self, key, val):
    if self.veryfirst:
      raise Exception("logic error")
    self.internal_indent(not self.first)
    self.internal_put_string(key)
    if self.indentamount is None:
      self.sink_data(":")
    else:
      self.sink_data(": ")
    self.first = False
    self.internal_put_flop(val)
  def put_flop_ex(self, key, val): # convert NaN/Inf to null
    if self.veryfirst:
      raise Exception("logic error")
    self.internal_indent(not self.first)
    self.internal_put_string(key)
    if self.indentamount is None:
      self.sink_data(":")
    else:
      self.sink_data(": ")
    self.first = False
    self.internal_put_flop_ex(val)
  def add_number(self, val):
    if not self.veryfirst:
      self.internal_indent(not self.first)
    self.veryfirst = False
    self.internal_put_number(val)
    self.first = False
  def add_number_ex(self, val): # convert NaN/Inf to null
    if not self.veryfirst:
      self.internal_indent(not self.first)
    self.veryfirst = False
    self.internal_put_number_ex(val)
    self.first = False
  def add_flop(self, val):
    if not self.veryfirst:
      self.internal_indent(not self.first)
    self.veryfirst = False
    self.internal_put_flop(val)
    self.first = False
  def add_flop_ex(self, val): # convert NaN/Inf to null
    if not self.veryfirst:
      self.internal_indent(not self.first)
    self.veryfirst = False
    self.internal_put_flop_ex(val)
    self.first = False

class JsonHandler(object):
  def handle_comment(self, comma_seen, val, is_multiline):
    pass
  def start_dict(self, key):
    pass
  def start_array(self, key):
    pass
  def end_dict(self, key):
    pass
  def end_array(self, key):
    pass
  def handle_number(self, key, num, is_integer):
    pass
  def handle_string(self, key, val):
    pass
  def handle_boolean(self, key, val):
    pass
  def handle_null(self, key):
    pass

class FragmentHandler(JsonHandler):
  def __init__(self):
    self.stack = []
    self.fragstack = []
    self.collect = False
    self.val = None
  def path_is(self, path):
    return self.stack == path
  def start_frag_collection(self):
    self.collect = True
  def handle_frag_comment(self, comma_seen, val, is_multiline):
    pass
  def handle_comment(self, comma_seen, val, is_multiline):
    self.handle_frag_comment(comma_seen, val, is_multiline)
  def start_frag_dict(self, key):
    pass
  def start_dict(self, key):
    self.stack.append(key)
    if not self.collect:
      self.start_frag_dict(key)
    if self.collect:
      obj = {}
      if self.fragstack:
        if key is not None:
          self.fragstack[-1][key] = obj
        else:
          self.fragstack[-1].append(obj)
      self.fragstack.append(obj)
  def start_frag_array(self, key):
    pass
  def start_array(self, key):
    self.stack.append(key)
    if not self.collect:
      self.start_frag_array(key)
    if self.collect:
      obj = []
      if self.fragstack:
        if key is not None:
          self.fragstack[-1][key] = obj
        else:
          self.fragstack[-1].append(obj)
      self.fragstack.append(obj)
  def end_frag_dict(self, key, val):
    pass
  def end_dict(self, key):
    val = None
    if self.fragstack:
      val1 = self.fragstack.pop()
      if not self.fragstack:
        val = val1
        self.collect = False
    if not self.collect:
      self.end_frag_dict(key, val)
    self.stack.pop()
  def end_frag_array(self, key, val):
    pass
  def end_array(self, key):
    val = None
    if self.fragstack:
      val1 = self.fragstack.pop()
      if not self.fragstack:
        val = val1
        self.collect = False
    if not self.collect:
      self.end_frag_array(key, val)
    self.stack.pop()
  def handle_frag_number(self, key, num, is_integer):
    pass
  def handle_frag_string(self, key, val):
    pass
  def handle_frag_boolean(self, key, val):
    pass
  def handle_frag_null(self, key):
    pass
  def handle_number(self, key, num, is_integer):
    if is_integer:
      num = int(num)
    if self.collect and self.fragstack:
      if key is not None:
        self.fragstack[-1][key] = num
      else:
        self.fragstack[-1].append(num)
    if self.collect:
      return
    self.handle_frag_number(key, num, is_integer)
  def handle_string(self, key, val):
    if self.collect and self.fragstack:
      if key is not None:
        self.fragstack[-1][key] = val
      else:
        self.fragstack[-1].append(val)
    if self.collect:
      return
    self.handle_frag_string(key, val)
  def handle_boolean(self, key, val):
    if self.collect and self.fragstack:
      if key is not None:
        self.fragstack[-1][key] = val
      else:
        self.fragstack[-1].append(val)
    if self.collect:
      return
    self.handle_frag_boolean(key, val)
  def handle_null(self, key):
    val = None
    if self.collect and self.fragstack:
      if key is not None:
        self.fragstack[-1][key] = val
      else:
        self.fragstack[-1].append(val)
    if self.collect:
      return
    self.handle_frag_null(key)

class JsonStream(object):
  def __init__(self, handler):
    self.mode = JSONSTREAM_MODE_VAL
    self.sz = 0
    self.uescape = io.StringIO()
    self.c_comment_seen = False
    self.c_comment_seen_star = False
    self.cpp_comment_seen = False
    self.comment_seen_preliminary = False
    self.comments = False
    self.trailing_commas = False
    self.keypresent = False
    self.key = io.StringIO()
    self.keystack = []
    self.val = io.StringIO()
    self.handler = handler
    self.is_integer = False
    self.comma_seen = False
  def allow_comments(self):
    self.comments = True
  def allow_trailing_comma(self):
    self.trailing_commas = True
  def get_keystack(self): # for internal use only
    if (self.keystack[-1] == None):
      self.keypresent = False
      self.keystack.pop()
      return
    self.keypresent = True
    self.key = self.keystack[-1]
    self.keystack.pop()
  def put_keystack_1(self): # for internal use only
    if not self.keypresent:
      self.keystack.append(None)
      self.keypresent = False
      return
    self.keystack.append(self.key)
  def put_keystack_2(self): # for internal use only
    self.keypresent = False
  def get_key(self): # for internal use only
    if not self.keypresent:
      return None
    return self.key.getvalue()
  def strip_comment(self, buf, start, i, sz, eof): # for internal use only
    i+=1
    self.mode = JSONSTREAM_MODE_ENDWS
    while i < sz:
      if self.comments and (not self.comment_seen_preliminary) and (not self.cpp_comment_seen) and (not self.c_comment_seen) and buf[start+i] == '/':
        self.comment_seen_preliminary = True
        self.val = io.StringIO()
        i+=1
        continue
      if self.comment_seen_preliminary:
        if buf[start+i] == '*':
          self.comment_seen_preliminary = False
          self.c_comment_seen = True
          self.c_comment_seen_star = False
          self.val = io.StringIO()
          i+=1
          continue
        if buf[start+i] != '/':
          self.errloc = i
          raise Exception("illegal comment")
        self.comment_seen_preliminary = False
        self.cpp_comment_seen = True
        self.val = io.StringIO()
        i+=1
        continue
      if self.c_comment_seen:
        if buf[start+i] == '*':
          self.c_comment_seen_star = True
        elif self.c_comment_seen_star and buf[start+i] == '/':
          self.c_comment_seen = False
          self.c_comment_seen_star = False
          if self.handler.handle_comment:
            self.handler.handle_comment(self.comma_seen, self.val.getvalue(), True)
        else:
          if self.c_comment_seen_star:
            self.val.write('*')
          self.c_comment_seen_star = False
          self.val.write(buf[start+i])
        i+=1
        continue
      if self.cpp_comment_seen:
        if buf[start+i] == '\n':
          self.cpp_comment_seen = False
          if self.handler.handle_comment:
            self.handler.handle_comment(self.comma_seen, self.val.getvalue(), False)
        else:
          self.val.write(buf[start+i])
        i+=1
        continue
      if buf[start+i] == ' ' or buf[start+i] == '\n' or buf[start+i] == '\r' or buf[start+i] == '\t':
        i+=1
        continue
      self.errloc = i
      raise Exception("Overflow")
    if eof and (self.c_comment_seen or self.comment_seen_preliminary):
      self.errloc = i
      raise Exception("Unterminated beginning of comment")
  def feed(self, buf, start, sz, eof):
    if sz < 0 or start+sz > len(buf):
      raise Exception("out of bounds")
    if self.mode == JSONSTREAM_MODE_ENDWS:
      self.strip_comment(buf, start, -1, sz, eof)
      if eof:
        return 0
      return -1
    i = 0
    while i < sz:
      if self.mode == JSONSTREAM_MODE_ENDWS:
        i -= 1
        self.strip_comment(buf, start, i, sz, eof)
        if eof:
          return 0
        return -1
      if self.mode == JSONSTREAM_MODE_KEYSTRING:
        if buf[start+i] == '\\':
          self.mode = JSONSTREAM_MODE_KEYSTRING_ESCAPE
        elif buf[start+i] == '"':
          self.keypresent = True
          self.mode = JSONSTREAM_MODE_COLON
        else:
          self.key.write(buf[start+i])
        i += 1
        continue
      elif self.mode == JSONSTREAM_MODE_STRING:
        if buf[start+i] == '\\':
          self.mode = JSONSTREAM_MODE_STRING_ESCAPE
        elif buf[start+i] == '"':
          self.mode = JSONSTREAM_MODE_COMMA
          if not self.handler.handle_string:
            if len(self.keystack) == 0:
              self.strip_comment(buf, start, i, sz, eof)
              if eof:
                return 0
              return -1
            i += 1
            continue
          self.handler.handle_string(self.get_key(), self.val.getvalue())
          if len(self.keystack) == 0:
            self.strip_comment(buf, start, i, sz, eof)
            if eof:
              return 0
            return -1
        else:
          self.val.write(buf[start+i])
        i += 1
        continue
      elif self.mode == JSONSTREAM_MODE_KEYSTRING_ESCAPE:
        if buf[start+i] == 'b':
          self.key.write('\b')
        elif buf[start+i] == 'f':
          self.key.write('\f')
        elif buf[start+i] == 'r':
          self.key.write('\r')
        elif buf[start+i] == 'n':
          self.key.write('\n')
        elif buf[start+i] == 't':
          self.key.write('\t')
        elif buf[start+i] == 'u':
          self.mode = JSONSTREAM_MODE_KEYSTRING_UESCAPE
          self.uescape = io.StringIO()
        else:
          self.errloc = i
          raise Exception("Illegal sequence")
        i += 1
        continue
      elif self.mode == JSONSTREAM_MODE_STRING_ESCAPE:
        if buf[start+i] == 'b':
          self.val.write('\b')
        elif buf[start+i] == 'f':
          self.val.write('\f')
        elif buf[start+i] == 'r':
          self.val.write('\r')
        elif buf[start+i] == 'n':
          self.val.write('\n')
        elif buf[start+i] == 't':
          self.val.write('\t')
        elif buf[start+i] == 'u':
          self.mode = JSONSTREAM_MODE_STRING_UESCAPE
          self.uescape = io.StringIO()
        else:
          self.errloc = i
          raise Exception("Illegal sequence")
        i += 1
        continue
      elif self.mode == JSONSTREAM_MODE_STRING_UESCAPE and len(self.uescape.getvalue()) < 4:
        if (buf[start+i] >= '0' and buf[start+i] <= '9') or (buf[start+i] >= 'A' and buf[start+i] <= 'F') or (buf[start+i] >= 'a' and buf[start+i] <= 'f'):
          self.uescape.write(buf[start+i])
          if len(self.uescape.getvalue()) == 4:
            self.val.write(chr(int(self.uescape.getvalue(),16)))
            self.mode = JSONSTREAM_MODE_STRING
          i += 1
          continue
        raise Exception("Illegal unicode escape")
      elif self.mode == JSONSTREAM_MODE_KEYSTRING_UESCAPE and len(self.uescape.getvalue()) < 4:
        if (buf[start+i] >= '0' and buf[start+i] <= '9') or (buf[start+i] >= 'A' and buf[start+i] <= 'F') or (buf[start+i] >= 'a' and buf[start+i] <= 'f'):
          self.uescape.write(buf[start+i])
          if len(self.uescape.getvalue()) == 4:
            self.key.write(chr(int(self.uescape.getvalue(),16)))
            self.mode = JSONSTREAM_MODE_KEYSTRING
          i += 1
          continue
        raise Exception("Illegal unicode escape")
      if self.comments and (not self.comment_seen_preliminary) and (not self.cpp_comment_seen) and (not self.c_comment_seen) and buf[start+i] == '/' and (self.mode == JSONSTREAM_MODE_COLON or self.mode == JSONSTREAM_MODE_COMMA or self.mode == JSONSTREAM_MODE_FIRSTKEY or self.mode == JSONSTREAM_MODE_FIRSTVAL or self.mode == JSONSTREAM_MODE_KEY or self.mode == JSONSTREAM_MODE_VAL):
        self.comment_seen_preliminary = True
        self.val = io.StringIO()
        i += 1
        continue
      if self.comment_seen_preliminary:
        if buf[start+i] == '*':
          self.comment_seen_preliminary = False
          self.c_comment_seen = True
          self.c_comment_seen_star = False
          self.val = io.StringIO()
          i += 1
          continue
        if buf[start+i] != '/':
          self.errloc = i
          raise Exception("illegal comment")
        self.comment_seen_preliminary = False
        self.cpp_comment_seen = True
        self.val = io.StringIO()
        i += 1
        continue
      if self.c_comment_seen:
        if buf[start+i] == '*':
          self.c_comment_seen_star = True
        elif self.c_comment_seen_star and buf[start+i] == '/':
          self.c_comment_seen = False
          self.c_comment_seen_star = False
          if self.handler.handle_comment:
            self.handler.handle_comment(self.comma_seen, self.val.getvalue(), True)
        else:
          if self.c_comment_seen_star:
            self.val.write('*')
          self.c_comment_seen_star = False
          self.val.write(buf[start+i])
        i += 1
        continue
      if self.cpp_comment_seen:
        if buf[start+i] == '\n':
          self.cpp_comment_seen = False
          if self.handler.handle_comment:
            self.handler.handle_comment(self.comma_seen, self.val.getvalue(), False)
        else:
          self.val.write(buf[start+i])
        i += 1
        continue
      if (buf[start+i] == ' ' or buf[start+i] == '\n' or buf[start+i] == '\r' or buf[start+i] == '\t') and (self.mode == JSONSTREAM_MODE_COLON or self.mode == JSONSTREAM_MODE_COMMA or self.mode == JSONSTREAM_MODE_FIRSTKEY or self.mode == JSONSTREAM_MODE_FIRSTVAL or self.mode == JSONSTREAM_MODE_KEY or self.mode == JSONSTREAM_MODE_VAL):
        i += 1
        continue
      if self.mode == JSONSTREAM_MODE_COLON:
        if buf[start+i] != ':':
          self.errloc = i
          raise Exception("invalid JSON")
        self.mode = JSONSTREAM_MODE_VAL
        i += 1
        continue
      if self.mode == JSONSTREAM_MODE_COMMA:
        if buf[start+i] == ',':
          self.comma_seen = True
          if self.keypresent:
            self.mode = JSONSTREAM_MODE_KEY
            self.keypresent = False
          else:
            self.mode = JSONSTREAM_MODE_VAL
          i += 1
          continue
      self.comma_seen = False
      if (self.mode == JSONSTREAM_MODE_COMMA or self.mode == JSONSTREAM_MODE_FIRSTKEY or (self.trailing_commas and self.mode == JSONSTREAM_MODE_KEY)) and buf[start+i] == '}':
        if self.mode == JSONSTREAM_MODE_COMMA:
          if not self.keypresent:
            self.errloc = i
            raise Exception("invalid JSON")
          # could be array or dict
        self.mode = JSONSTREAM_MODE_COMMA
        self.get_keystack()
        if not self.handler.end_dict:
          if len(self.keystack) == 0:
            self.strip_comment(buf, start, i, sz, eof)
            if eof:
              return 0
            return -1
          i += 1
          continue
        self.handler.end_dict(self.get_key())
        if len(self.keystack) == 0:
          self.strip_comment(buf, start, i, sz, eof)
          if eof:
            return 0
          return -1
        i += 1
        continue
      if (self.mode == JSONSTREAM_MODE_COMMA or self.mode == JSONSTREAM_MODE_FIRSTVAL or (self.trailing_commas and self.mode == JSONSTREAM_MODE_VAL)) and buf[start+i] == ']':
        if self.mode == JSONSTREAM_MODE_COMMA or self.mode == JSONSTREAM_MODE_VAL:
          if self.keypresent or len(self.keystack) == 0:
            self.errloc = i
            raise Exception("invalid JSON")
          # could be array or dict
        self.mode = JSONSTREAM_MODE_COMMA
        self.get_keystack()
        if not self.handler.end_array:
          if len(self.keystack) == 0:
            self.strip_comment(buf, start, i, sz, eof)
            if eof:
              return 0
            return -1
          i += 1
          continue
        self.handler.end_array(self.get_key())
        if len(self.keystack) == 0:
          self.strip_comment(buf, start, i, sz, eof)
          if eof:
            return 0
          return -1
        i += 1
        continue
      if (self.mode == JSONSTREAM_MODE_FIRSTVAL or self.mode == JSONSTREAM_MODE_VAL) and buf[start+i] == '{':
        self.put_keystack_1()
        self.mode = JSONSTREAM_MODE_FIRSTKEY
        if not self.handler.start_dict:
          self.put_keystack_2()
          i += 1
          continue
        self.handler.start_dict(self.get_key())
        self.put_keystack_2()
        i += 1
        continue
      if (self.mode == JSONSTREAM_MODE_FIRSTVAL or self.mode == JSONSTREAM_MODE_VAL) and buf[start+i] == '[':
        self.put_keystack_1()
        self.mode = JSONSTREAM_MODE_FIRSTVAL
        if not self.handler.start_array:
          self.put_keystack_2()
          i += 1
          continue
        self.handler.start_array(self.get_key())
        self.put_keystack_2()
        i += 1
        continue
      if self.mode == JSONSTREAM_MODE_TRUE:
        if buf[start+i] != "true"[self.sz]:
          self.errloc = i
          raise Exception("invalid JSON")
        self.sz += 1
        if self.sz < 4:
          i += 1
          continue
        self.mode = JSONSTREAM_MODE_COMMA
        if not self.handler.handle_boolean:
          if len(self.keystack) == 0:
            self.strip_comment(buf, start, i, sz, eof)
            if eof:
              return 0
            return -1
          i += 1
          continue
        self.handler.handle_boolean(self.get_key(), True)
        if len(self.keystack) == 0:
          self.strip_comment(buf, start, i, sz, eof)
          if eof:
            return 0
          return -1
        i += 1
        continue
      if self.mode == JSONSTREAM_MODE_FALSE:
        if buf[start+i] != "false"[self.sz]:
          self.errloc = i
          raise Exception("invalid JSON")
        self.sz += 1
        if self.sz < 5:
          i += 1
          continue
        self.mode = JSONSTREAM_MODE_COMMA
        if not self.handler.handle_boolean:
          if len(self.keystack) == 0:
            self.strip_comment(buf, start, i, sz, eof)
            if eof:
              return 0
            return -1
          i += 1
          continue
        self.handler.handle_boolean(self.get_key(), False)
        if len(self.keystack) == 0:
          self.strip_comment(buf, start, i, sz, eof)
          if eof:
            return 0
          return -1
        i += 1
        continue
      if self.mode == JSONSTREAM_MODE_NULL:
        if buf[start+i] != "null"[self.sz]:
          self.errloc = i
          raise Exception("invalid JSON")
        self.sz += 1
        if self.sz < 4:
          i += 1
          continue
        self.mode = JSONSTREAM_MODE_COMMA
        if not self.handler.handle_null:
          if len(self.keystack) == 0:
            self.strip_comment(buf, start, i, sz, eof)
            if eof:
              return 0
            return -1
          i += 1
          continue
        self.handler.handle_null(self.get_key())
        if len(self.keystack) == 0:
          self.strip_comment(buf, start, i, sz, eof)
          if eof:
            return 0
          return -1
        i += 1
        continue
      if (self.mode == JSONSTREAM_MODE_VAL or self.mode == JSONSTREAM_MODE_FIRSTVAL) and buf[start+i] == 'n':
        self.mode = JSONSTREAM_MODE_NULL
        self.sz = 1
        i += 1
        continue
      if (self.mode == JSONSTREAM_MODE_VAL or self.mode == JSONSTREAM_MODE_FIRSTVAL) and buf[start+i] == 'f':
        self.mode = JSONSTREAM_MODE_FALSE
        self.sz = 1
        i += 1
        continue
      if (self.mode == JSONSTREAM_MODE_VAL or self.mode == JSONSTREAM_MODE_FIRSTVAL) and buf[start+i] == 't':
        self.mode = JSONSTREAM_MODE_TRUE
        self.sz = 1
        i += 1
        continue
      if (self.mode == JSONSTREAM_MODE_KEY or self.mode == JSONSTREAM_MODE_FIRSTKEY) and buf[start+i] == '"':
        self.mode = JSONSTREAM_MODE_KEYSTRING
        self.key = io.StringIO()
        i += 1
        continue
      if (self.mode == JSONSTREAM_MODE_VAL or self.mode == JSONSTREAM_MODE_FIRSTVAL) and buf[start+i] == '"':
        self.mode = JSONSTREAM_MODE_STRING
        self.val = io.StringIO()
        i += 1
        continue
      if (self.mode == JSONSTREAM_MODE_VAL or self.mode == JSONSTREAM_MODE_FIRSTVAL) and (buf[start+i] == '-' or (buf[start+i] >= '0' and buf[start+i] <= '9')):
        self.mode = JSONSTREAM_MODE_NUMBER
        self.is_integer = True
        self.val = io.StringIO()
      if self.mode == JSONSTREAM_MODE_NUMBER:
        if self.val.getvalue() == "" and buf[start+i] == '-':
          self.val.write(buf[start+i])
          i += 1
          continue
        if (self.val.getvalue() == "" or self.val.getvalue() == "-") and buf[start+i] >= '0' and buf[start+i] <= '9':
          self.val.write(buf[start+i])
          i += 1
          continue
        if (self.val.getvalue() != "0" and self.val.getvalue() != "-0") and buf[start+i] >= '0' and buf[start+i] <= '9':
          self.val.write(buf[start+i])
          i += 1
          continue
        if buf[start+i] == '.' and ("." not in self.val.getvalue()) and ("E" not in self.val.getvalue()) and ("e" not in self.val.getvalue()):
          self.is_integer = False
          self.val.write(buf[start+i])
          i += 1
          continue
        if (buf[start+i] == 'E' or buf[start+i] == 'e') and ("E" not in self.val.getvalue()) and ("e" not in self.val.getvalue()):
          self.is_integer = False
          self.val.write(buf[start+i])
          i += 1
          continue
        if (buf[start+i] == '-' or buf[start+i] == '+') and len(self.val.getvalue()) and (self.val.getvalue()[-1] == 'E' or self.val.getvalue()[-1] == 'e'):
          self.val.write(buf[start+i])
          i += 1
          continue
        if self.is_integer:
          numval = int(self.val.getvalue())
        else:
          numval = float(self.val.getvalue())
        self.mode = JSONSTREAM_MODE_COMMA
        if not self.handler.handle_number:
          if len(self.keystack) == 0:
            self.strip_comment(buf, start, i-1, sz, eof)
            if eof:
              return 0
            return -1
          continue # without i += 1 on purpose
        self.handler.handle_number(self.get_key(), numval, self.is_integer)
        if len(self.keystack) == 0:
          self.strip_comment(buf, start, i-1, sz, eof)
          if eof:
            return 0
          return -1
        continue # without i += 1 on purpose
      self.errloc = i
      raise Exception("invalid JSON")
    if self.mode == JSONSTREAM_MODE_NUMBER and eof:
      self.mode = JSONSTREAM_MODE_COMMA
      if not self.handler.handle_number:
        if len(self.keystack) == 0:
          return 0
        self.errloc = i
        raise Exception("invalid JSON")
      if self.is_integer:
        numval = int(self.val.getvalue())
      else:
        numval = float(self.val.getvalue())
      self.handler.handle_number(self.get_key(), numval, self.is_integer)
      if len(self.keystack) == 0:
        return 0
      self.errloc = i
      raise Exception("invalid JSON")
    if eof and (self.c_comment_seen or self.comment_seen_preliminary):
      self.errloc = i
      raise Exception("Unterminated beginning of comment")
    if len(self.keystack) == 0 and eof and self.mode == JSONSTREAM_MODE_ENDWS:
      return 0
    if eof:
      self.errloc = i
      raise Exception("invalid JSON, parsing not finished at end")
    return -1

def jsonstream_tree_parse(buf, allow_comments=False, allow_trailing_comma=False):
  class ElementContainer(object):
    def __init__(self):
      self.has_element = False
      self.element = None
  c = ElementContainer()
  stack = []
  class MyHandler(JsonHandler):
    def start_dict(self, key):
      obj = {}
      if not c.has_element:
        c.has_element = True
        c.element = obj
        stack.append(obj)
        return
      if key is not None:
        stack[-1][key] = obj
      else:
        stack[-1].append(obj)
      stack.append(obj)
    def start_array(self, key):
      obj = []
      if not c.has_element:
        c.has_element = True
        c.element = obj
        stack.append(obj)
        return
      if key is not None:
        stack[-1][key] = obj
      else:
        stack[-1].append(obj)
      stack.append(obj)
    def end_dict(self, key):
      stack.pop()
    def end_array(self, key):
      stack.pop()
    def handle_number(self, key, num, is_integer):
      if is_integer:
        num = int(num)
      if not c.has_element:
        c.has_element = True
        c.element = num
        return
      if key is not None:
        stack[-1][key] = num
      else:
        stack[-1].append(num)
      if not c.has_element:
        c.has_element = True
        c.element = num
    def handle_string(self, key, val):
      if not c.has_element:
        c.has_element = True
        c.element = val
        return
      if key is not None:
        stack[-1][key] = val
      else:
        stack[-1].append(val)
      if not c.has_element:
        c.has_element = True
        c.element = val
    def handle_boolean(self, key, val):
      if not c.has_element:
        c.has_element = True
        c.element = val
        return
      if key is not None:
        stack[-1][key] = val
      else:
        stack[-1].append(val)
    def handle_null(self, key):
      val = None
      if not c.has_element:
        c.has_element = True
        c.element = val
        return
      if key is not None:
        stack[-1][key] = val
      else:
        stack[-1].append(val)
  handler = MyHandler()
  stream = JsonStream(handler)
  if allow_comments:
    stream.allow_comments()
  if allow_trailing_comma:
    stream.allow_trailing_comma()
  stream.feed(buf, 0, len(buf), True)
  if not c.has_element:
    raise Exception("invalid JSON")
  return c.element

if __name__ == '__main__':
  handler = JsonHandler()
  buf = "//foo\n /* fof */ { //bar\n  \"foo\\u03a9\": [1 //baz\n, /*2,*/ 3 //quux\n], \"bar\": 4.0, \"baz\": {}, \"barf\": []   , \"quux\": [true, false, null,],  } // endcomment"
  stream = JsonStream(handler)
  stream.allow_comments()
  stream.allow_trailing_comma()
  print(stream.feed(buf, 0, len(buf), True))
  print(jsonstream_tree_parse(buf, True, True))
