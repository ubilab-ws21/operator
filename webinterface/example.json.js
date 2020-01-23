let json = `{
 "nodes": [{
   "data": {
    "id": "a",
    "name": "A",
    "parent": "b"
   }
  },
  {
   "data": {
    "id": "b",
    "name": "B"
   }
  },
  {
   "data": {
    "id": "c",
    "name": "C",
    "parent": "b"
   }
  }, {
   "data": {
    "id": "d",
    "name": "D"
   }
  },
  {
   "data": {
    "id": "e",
    "name": "E"
   }
  },
  {
   "data": {
    "id": "f",
    "name": "F",
    "parent": "e"
   }
  }
 ],
 "edges": [{
   "data": {
    "id": "ad",
    "source": "a",
    "target": "d"
   }
  },
  {
   "data": {
    "id": "eb",
    "source": "e",
    "target": "b"
   }
  }
 ]
}`;