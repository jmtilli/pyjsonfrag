import pyjsonfrag

with open("customers.json", "r") as f:
  print(pyjsonfrag.jsonstream_tree_parse(f.read()))
