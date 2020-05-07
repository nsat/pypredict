#!/bin/bash

PYTHON_VERSIONS=$@

if [[ -z "${PYTHON_VERSIONS}" ]] ; then
    echo "Usage: $(basename $0) <version>..." >&2
    echo "  A version is the two numbers in the major.minor python that you want to build" >&2
    echo "  Example: for python 2.7 and 3.8 both" >&2
    echo "" >&2
    echo "    $ $(basename $0) 27 38" >&2
    exit 1
fi

function get-variants() {
    local version="$1"

    if [[ "${version}" = '38' ]] ; then
        echo /
    elif [[ "${version}" = '27' ]] ; then
        echo m mu
    else
        echo m
    fi
}

cd /io

for version in ${PYTHON_VERSIONS} ; do
    for variant in $(get-variants "${version}") ; do
        /opt/python/cp${version}-cp${version}${variant}/bin/python setup.py bdist_wheel
    done
done

for f in dist/*.whl ; do
    /opt/python/cp37-cp37m/bin/auditwheel repair "${f}"
done
