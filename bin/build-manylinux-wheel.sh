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

cd /io || exit
mkdir -p wheelhouse || exit

for version in ${PYTHON_VERSIONS} ; do
    for variant in $(get-variants "${version}") ; do
        "/opt/python/cp${version}-cp${version}${variant}/bin/pip" --no-cache-dir wheel /io -w wheelhouse/
    done
done

for f in wheelhouse/*.whl ; do
    /usr/local/bin/auditwheel repair "${f}"
done
