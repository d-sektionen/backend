#!/bin/bash

cd /srv/api/website
kill `cat run.1.pid`
kill `cat run.2.pid`
