# PyJsonFrag: a powerful combined tree-based and event-based parser for JSON

Typically, JSON is parsed by a tree-based parser unlike XML that can be parsed by a tree-based parser or an event-based parser. Event-based parsers are fast and have a low memory footprint, but a drawback is that it is cumbersome to write the required event handlers. Tree-based parsers make the code easier to write, to understand and to maintain but have a large memory footprint as a drawback. Sometimes, JSON is used for huge files such as database dumps that would be preferably parsed by event-based parsing, or so it would appear at a glance, because a tree-based parser cannot hold the whole parse tree in memory at the same time, if the file is huge.

## How to install: PyJsonFrag at PyPI

PyJsonFrag is available at [PyPI](https://pypi.org/project/pyjsonfrag/).

How to install:
```
python3 -m pip install pyjsonfrag
```

## Example application: customers in a major bank

Let us consider an example application: a listing of a customers in a major bank that has 30 million customers. The test file is in the following format:

```
{
  "customers": [
    {
      "id": 1,
      "name": "Clark Henson",
      "accountCount": 1,
      "totalBalance": 5085.96
    },
    {
      "id": 2,
      "name": "Elnora Ericson",
      "accountCount": 3,
      "totalBalance": 3910.11
    },
    ...
  ]
}
```

The example format requires about 100 bytes per customer plus customer name length. If we assume an average customer name is 15 characters long, the required storage is about 115 bytes per customer. For 30 million customers, this is 3.5 gigabytes. In the example, the file is read to the following structure:

```
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
```

## Python jsonstream API

For XML, there is Simple API for XML (SAX). However, for JSON the usual parse
methods read the whole data into memory at once, not supporting event-driven
parsing. Thus, we provide Python jsonstream API to provide the possibility
for event-driven parsing. It is faster and less memory-hungry than the "read
all at once" parsing methods, but it is cumbersome.

A jsonstream-based parser is implemented here:

```
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

handler = pyjsonfrag.JsonHandler(start_dict=start_dict, start_array=start_array, end_dict=end_dict,
            end_array=end_array, handle_string=handle_string, handle_number=handle_number)
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
```

It can be seen that the parser is quite cumbersome and the code to construct a customer is scattered to two different places. Yet it is fast and has a low memory footprint.

## Parser with the new library

What if we could combine the benefits of the jsonstream-based approach with the benefits of the "read whole parse tree into memory" based approach? A parse tree fragment for a single customer dictionary is small enough to be kept in memory. This is what the new library is about. Here is the code to parse the customer file with the new library:

```
# FIXME
```

Note how the code is significantly more simple than for the event-based approach. Performance is close to the event-based approach, and memory consumption is essentially the same as for the event-based approach.

Of course, the new library supports getting the whole parse tree in memory:

```
import pyjsonfrag

with open("customers.json", "r") as f:
  print(pyjsonfrag.jsonstream_tree_parse(f.read()))
```

## License

All of the material related to PyJsonFrag is licensed under the following MIT
license:

Copyright (C) 2026 Juha-Matti Tilli

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
