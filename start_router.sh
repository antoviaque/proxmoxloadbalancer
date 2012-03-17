#!/bin/bash

twistd --pidfile=log/router.pid --logfile=log/router.log -noy router.tac
