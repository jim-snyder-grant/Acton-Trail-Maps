#!/bin/bash

# Build the declination
# Start with a transparent screen:
convert -size 160x400 xc:transparent -font Arial declination.png

# True north line:
convert declination.png -stroke black -draw "stroke-width 3 line 130,380 130,46" declination.png

# Label north line with star:
convert declination.png -stroke black -draw "polygon 130,1 134,8 140,8 135,13 136,19 130,16 124,19 125,13 120,8 126,8" declination.png


# Magnetic north arrow:
convert declination.png -stroke black -draw "stroke-width 3 line 130,380 54,90" declination.png
convert declination.png -stroke black -draw "stroke-width 3 line 54,90 54,125" declination.png
convert declination.png -stroke black -draw "stroke-width 3 line 54,90 56,123" declination.png
convert declination.png -stroke black -draw "stroke-width 3 line 54,90 58,121" declination.png
convert declination.png -stroke black -draw "stroke-width 3 line 54,90 60,119" declination.png

# Label magnetic arrow:
convert declination.png -stroke black -pointsize 18 -annotate 345x345+40+88 "MN" declination.png


# Dotted arc:
convert declination.png -stroke black -fill none -draw "stroke-width 2 stroke-dasharray 2 2 path 'M 54,90 A 150,150 0 0,1 130,80'" declination.png


# Date of declination:
convert declination.png -stroke black -draw 'font-size 20 text 108 398 "2016"' declination.png

# Label declination value:
convert declination.png -stroke black -draw "stroke-width 2 line 2,220 110,220" declination.png
convert declination.png -stroke black -draw 'font-size 24 text 24 216 "14.6°"' declination.png
convert declination.png -stroke black -draw 'font-size 20 text  0 239 "259 MILS"' declination.png




#         -draw 'font-size 35 stroke black fill black text 40,95  "Fishing Trail"' \
#          -draw "stroke black fill none stroke-width 7 stroke-dasharray 10 10 path 'M 300,80 A 800,1000  0  0,0 490,80'" \
#         \
#         \
#          -draw 'font-size 35 stroke black fill black text 40,145  "Meadow"' \
#          -draw 'fill rgb(202,216,162) stroke black stroke-width 3 rectangle 300,115 340,145' \
#          \
#          -draw 'font-size 35 stroke black fill black text 40,195  "Parking"' \
#          -draw 'fill rgb(234,238,221) stroke black stroke-width 3 rectangle 300,165 340,195' \
#          -gravity northwest     local_parking.png  -compose Over -geometry x25+305+170    -composite \
#         \
#          legend.png

