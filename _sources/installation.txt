Installation instructions
============================

To use this library you need a central data store that is accessible on all client machines. On our system
this is an nfs-mounted shared directory. This is where all of the data will be stored. The directory structure
is as described in :doc:`organization`.

To setup client machines, you need to:

* Install this library (in some standard Python-library way)

* Set the ``PADRE_ROOT`` environment variable to the data directory

 