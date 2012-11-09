Robocom
================

Robocom is the central communication server for the projects.
It outputs things in the JSON format and receives things via
GET data.

Using it
--------

### Transmitting things to the server ###

The server uses simple GET data so transmitting things to it
can be done by simply adding things to the URL.

Example:

http://serverurl/receive?foo=bar

### Receiving things from the server ###

http://serverurl/ outputs anything that has been transmitted to the server
in JSON format.

Protocol
--------

I'll specify a protocol later
