#!/usr/env /bin/sh

LAYOUT_STRING="[\!@#\$%^&*(),\
                1234567890,\
                QWERTYUIOP,\
                qwertyuiop,\
                ASDFGHJKL:,\
                asdfghjkl;,\
                ZXCVBNM<>?,\
                zxcvbnm\,./]"
LAUNCH_STRING="<Control><Shift>a"
gconftool -s --type string "/apps/mousekips/launch" "$LAUNCH_STRING"
gconftool -s --type list --list-type string /apps/mousekips/layout "$LAYOUT_STRING"

