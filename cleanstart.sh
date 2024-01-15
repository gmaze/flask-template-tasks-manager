#!/usr/bin/env bash

\rm apps/logs/*
\rm apps/db.sqlite3
\rm -r apps/static/results/*

export FLASK_APP=run.py
export DEBUG=1
flask run
