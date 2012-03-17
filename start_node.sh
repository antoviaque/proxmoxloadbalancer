#!/bin/bash

twistd --pidfile=log/node$1.pid --logfile=log/node$1.log -noy node$1.tac
