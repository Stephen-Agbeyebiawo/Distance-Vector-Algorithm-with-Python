# Distance-Vector-Algorithm-with-Python
Code for DV routers
Algorithm includes split horizon to prevent route loops.
A timer to keep track of neighbors. Timer is reset whenever a route advert is received from a neighbor. When the timer expires, the neighborship relationship is broken. The router recalculates routes to remove dead route from the table.
