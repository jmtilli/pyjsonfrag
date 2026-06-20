import pyjsonfrag

class Customer(object):
  def __init__(self, customerId = None, name = None, accountCount = None, totalBalance = None):
    if customerId is not None:
      self.customerId = int(customerId)
    else:
      self.customerId = None
    self.name = name
    if accountCount is not None:
      self.accountCount = int(accountCount)
    else:
      self.accountCount = None
    if totalBalance is not None:
      self.totalBalance = float(totalBalance)
    else:
      self.totalBalance = None
  def __repr__(self):
    return ("Customer(%d,%s,%d,%.2f)" % (self.customerId,self.name,self.accountCount,self.totalBalance))

context = []
cs = {}
c = None

def start_dict(stream, key):
  global c
  context.append(key)
  if context == [None, "customers", None]:
    c = Customer()
def start_array(stream, key):
  context.append(key)
def end_dict(stream, key):
  context.pop()
def end_array(stream, key):
  context.pop()
def handle_string(stream, key, val):
  if key == "name":
    c.name = val
def handle_number(stream, key, num, is_integer):
  if key == "id":
    cs[int(num)] = c
    c.customerId = int(num)
  elif key == "accountCount":
    c.accountCount = int(num)
  elif key == "totalBalance":
    c.totalBalance = num

handler = pyjsonfrag.JsonHandler(start_dict=start_dict, start_array=start_array, end_dict=end_dict, end_array=end_array, handle_string=handle_string, handle_number=handle_number)
stream = pyjsonfrag.JsonStream(handler)
with open("customers.json", "r") as f:
  while True:
    buf = f.read(4096)
    if buf == '':
      stream.feed(buf, 0, len(buf), True)
      break
    else:
      stream.feed(buf, 0, len(buf), False)
print(cs)
