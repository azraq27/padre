Installation instructions
============================

User installation
-------------------

If your library is already setup and you just need to attach your client machine, you just need 3 things:

:data store:
	Likely this is a network drive that needs to be mounted on
	some system directory (e.g., /mnt/server_name or /Network/server_name)
:padre library:
	 This is just a standard Python library, hosted on PyPi and GitHub. You
	 can install the latest version with "pip install git+https://github.com/azraq27/padre"
	 or the latest release with "pip install padre"
:PADRE_ROOT:
	In whatever shell you are using you need to set the environment variable "PADRE_ROOT" to
	the directory where the data store is. For example, in bash you might put "export PADRE_ROOT
	/mnt/server/padre" in .bashrc
	
System installation
----------------------

