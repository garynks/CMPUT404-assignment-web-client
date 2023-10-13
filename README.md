CMPUT404-assignment-web-client
==============================

CMPUT404-assignment-web-client

See requirements.org (plain-text) for a description of the project.

Make a simple web-client like curl or wget

## Docker Instructions
Run the following commands in the root
```bash
docker build -t web-client-tests .
docker run --name test -d -it  web-client-tests
docker exec -it test bash
```

In the docker container,
```bash
python3 freetests.py
```

Contributors / Licensing
========================

Generally everything is LICENSE'D under the Apache 2 license by Abram Hindle, 
https://github.com/tywtyw2002, and https://github.com/treedust

But the server.py example is derived from the python documentation
examples thus some of the code is Copyright © 2001-2013 Python
Software Foundation; All Rights Reserved under the PSF license (GPL
compatible) http://docs.python.org/2/library/socketserver.html

