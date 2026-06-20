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
  def __repr__(s):
    return ("Customer(%d,%s,%d,%.2f)" % (s.customerId,s.name,s.accountCount,s.totalBalance))

cs = {}

class MyHandler(pyjsonfrag.FragmentHandler):
  def start_frag_dict(self, key):
    if self.path_is([None, "customers", None]):
      self.start_frag_collection()
  def end_frag_dict(self, key, val):
    if self.path_is([None, "customers", None]):
      c = Customer(customerId=val["id"], name=val["name"],
                   accountCount=val["accountCount"], totalBalance=val["totalBalance"])
      cs[c.customerId] = c

handler = MyHandler()
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
