# o365-dag

This is a simple flask server that once configured will pull o365 attribtes
from the REST interface, translate the corresponding response (XML/json) into
an EDL for consumption by a paloalto firewall or panorama. For further
information on EDLs, the following notes have been provided.

## Contents

`doc/` - documentation and notes around o365 and palo alto
`examples` - manufacturer supplied sample programs
`start.bat` - start the server on a windows host
`start.sh` - start the server on a linux/unix host
tenent-ip-edl.py - flask service router
o365ipAddr.py - python library representing o365 API


## References

 1. External Dynamic List - [doc](doc/paloaltonetworks-external-dynamic-list.md)
 2. Office 365 API - [doc](doc/office-365-api.md)

