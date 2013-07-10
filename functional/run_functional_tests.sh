#!/bin/bash
echo $WORKSPACE
[[ ! -z $WORKSPACE ]] || export WORKSPACE=$(pwd)
nosetests -q test_general_flow.py:adapter_tests --with-xunit --xunit-file=$WORKSPACE/functional.xml