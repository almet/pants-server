The pants server
================

This is the meet server for the pants project.

::

    # A "*" means this URI requires authentication.

    * POST /call-url/      →  Create the call url a callee can click on.
      GET  /calls/{token}  →  Get the app (that's the url in question, which
                              displays an app)
      POST /calls/{token}  →  Add an incoming call (does a simple push notif
                              and gets room tokens)
    * GET  /calls/         →  List incoming calls for the authenticated user.


How to install?
---------------

::

    git clone https://github.com/ametaireau/pants-server.git
    cd pants-server && make install

How to run it?
--------------

::

    make runserver

How to run the tests?
---------------------

::

    make tests
