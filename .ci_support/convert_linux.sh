#!/bin/bash
sed -e '/\[win\]/d' -e '/\[macarm\]/d' -e '/\[macos\]/d' environment.yml  > tmp.yml
mv tmp.yml environment.yml
