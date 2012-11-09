Robocom
========
Robocom is the central communication server for the projects.
It outputs things in the JSON format and receives things via
GET data.

Using it
--------
### Starting a new game ###
Starting a new game is done by sending a request to
http://serverurl/newgame
This will reset the database, effectively rendering a *tabula rasa*.

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
I'll specify a protocol as I create it
