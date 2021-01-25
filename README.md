# SimpleNoC

> DISCLAIMER: This is just a small personal project, with many limitations and shortcomings.

This codebase is used to simulate the behavior of a simple Network On Chip. Networks On Chip, often call NoC, are used to build scalable interconnects between several processing elements in hardware designs.

An example of how to use the library is provided in [the test file](test/test_mesh_2x2.py).

The library is packaged with the [setup.py](setup.py) file. It has no external dependancies but requires a modern python interpreter (python 3.6+).

The tests are written for pytest and wrapped in tox. They assume that python 3.9 is installed (that is the case on my machine) but that can be changed in the [tox.ini](tox.ini) file.

This project was inspired by the online lectures from [Prof. Dr. Ben H. Juurlink](https://www.youtube.com/channel/UCPSsA8oxlSBjidJsSPdpjsQ/videos) from the AES department of the _Technische Universitat Berlin_. The videos are available on his YouTube channel for free. In particular, the videos [4.3.2 Scalable Cache Coherence](https://www.youtube.com/watch?v=VlU41fxzbrU&list=PLeWkeA7esB-OgNoVkE2lW2cVBxpDbu92h&index=9) and [4.3.2 Full Directory Protocol](https://www.youtube.com/watch?v=rTnp1PdTE4k&list=PLeWkeA7esB-OgNoVkE2lW2cVBxpDbu92h&index=10) are particularly relevant to our implementation.

Our implementation follows the Full Directory MSI based cache coherence protocol. We tried to be faithful to what would be feasible in a hardware implementation, although some shortcuts were taken. Ideas were also recycled from other fields, for instance the _embedded_ field in our protocol is inspired by internet cookies and is used to create some state in a mostly stateless protocol.

Field | Value
--- | ---
:pencil: Contributors | roadelou
:email: Contacts | 
:date: Creation Date | 2021-01-16
:bulb: Language | Markdown Document

### EOF
