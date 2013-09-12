#!/bin/sh


DEBUG=0
if [ "$1" == "--debug" ]; then
    DEBUG=1
fi


SOURCE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DEST="$SOURCE/../diyrss/static"

compile_css() {
    lessc --yui-compress $SOURCE/main.less
}

compile_css > $DEST/css/main.css &

jobs
wait
sleep 1
