convert -size 1060x70 xc:white  -font Nimbus-Sans-L-Bold\
      -draw 'fill white stroke black stroke-width 3 rectangle 10,40 986,70' \
      -draw 'fill black stroke black stroke-width 3 rectangle 10,40 132,70' \
      -draw 'fill black stroke black stroke-width 3 rectangle 254,40 376,70' \
      -draw 'fill black stroke black stroke-width 3 rectangle 498,40 986,70' \
      scale.png
convert scale.png  -gravity east -pointsize 28 -annotate +10+20 'Feet' scale.png
convert scale.png  -gravity center -pointsize 30 -annotate -520-15  '0' scale.png
convert scale.png  -gravity center -pointsize 30 -annotate -398-15  '125' scale.png
convert scale.png  -gravity center -pointsize 30 -annotate -276-15  '250' scale.png
convert scale.png  -gravity center -pointsize 30 -annotate -32-15  '500' scale.png
convert scale.png  -gravity center -pointsize 30 -annotate +456-15  '1000' scale.png

