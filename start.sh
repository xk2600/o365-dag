#!/bin/sh
SRCROOT=`dirname $0` ; SRCROOT=`realpath $SRCROOT`
CALLERPATH=`pwd`
VENVROOT=$SRCROOT/venv
printf "SRCROOT: %s\nCALLERPATH: %s\nVENVROOT: %s" "$SRCROOT" "$CALLERPATH" "$VENVROOT"
for BIN in python3 pip3 flask; do
   which $BIN || { 
     echo "'$BIN' is not be executable in the current environment. please install '$BIN' or validate path."
   }
done
if [ ! -d "$VENVROOT" ] ; then
  # create virtual environment
  python3 -m venv $VENVROOT
  # activate virtual environment
  . $VENVROOT/bin/activate
  # install packages in freeze
  pip install flask requests-cache
fi


# disabled until validated
echo flask run --host=0.0.0.0

