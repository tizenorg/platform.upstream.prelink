#!/bin/bash
CC="${CC:-gcc} ${LINKOPTS} -Wl,--copy-dt-needed-entries" ; echo "CC=$CC"
CCLINK="${CCLINK:-${CC} -Wl,--dynamic-linker=`echo ./ld*.so.*[0-9]`} -Wl,--copy-dt-needed-entries"
CXX="${CXX:-g++} ${LINKOPTS} -Wl,--copy-dt-needed-entries" ; echo "CXX=$CXX"
CXXLINK="${CXXLINK:-${CXX} -Wl,--dynamic-linker=`echo ./ld*.so.*[0-9]`} -Wl,--copy-dt-needed-entries"
PRELINK=${PRELINK:-../src/prelink -c ./prelink.conf -C ./prelink.cache --ld-library-path=. --dynamic-linker=`echo ./ld*.so.*[0-9]`}
srcdir=${srcdir:-`dirname $0`}
savelibs() {
  for i in $LIBS $BINS; do cp -p $i $i.orig; done
}
comparelibs() {
  for i in $LIBS $BINS; do
    cp -p $i $i.new
    echo $PRELINK -u $i.new
    $PRELINK -u $i.new || exit
    cmp -s $i.orig $i.new || exit
    rm -f $i.new
    echo $PRELINK -y $i \> $i.new
    $PRELINK -y $i > $i.new || exit
    cmp -s $i.orig $i.new || exit
    rm -f $i.new
  done
}
