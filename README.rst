The pants server
================

This is the meet server for the pants project.

::
    GET  /calls/{token}  →  Get the app
    POST /calls/{token}  →  Add an incoming call + simple push notif
    POST /calls/         →  Create the call link


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
