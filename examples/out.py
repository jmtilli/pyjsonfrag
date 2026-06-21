import pyjsonfrag
import sys

class MySink(pyjsonfrag.JsonSink):
  def __init__(self, tabs, indentamount):
    super().__init__(tabs, indentamount)
  def sink_data(self, dat):
    sys.stdout.write(dat)

s = MySink(False, 4)
s.add_start_dict()
s.put_start_dict("bar")
s.end_dict()
s.put_start_array("foo")
s.add_boolean(False)
s.comment(True, "foo")
s.add_boolean(True)
s.add_string("bar")
s.add_null()
s.add_number(123)
s.add_number_ex(123)
s.comment(True, "bar", True)
s.add_flop(123)
s.add_flop_ex(123)
s.add_start_array()
s.end_array()
s.comment(True, "quux\nbarf\n")
s.add_start_dict()
s.end_dict()
s.end_array()
s.put_number("a", 123)
s.put_number_ex("b", 123)
s.put_flop("c", 123)
s.put_flop_ex("d", 123)
s.put_boolean("e", False)
s.put_boolean("f", True)
s.put_null("g")
s.put_string("h", "quux")
s.end_dict()
sys.stdout.write("\n")

