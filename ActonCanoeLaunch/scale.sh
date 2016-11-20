convert -size 1100x120 xc:white  -font Nimbus-Sans-L-Bold\
      -draw 'fill white stroke black stroke-width 3 rectangle 10,40 986,120' \
      -draw 'fill black stroke black stroke-width 3 rectangle 10,40 132,120' \
      -draw 'fill black stroke black stroke-width 3 rectangle 254,40 376,120' \
      -draw 'fill black stroke black stroke-width 3 rectangle 498,40 986,120' \
      scale.png
convert scale.png  -gravity west -pointsize 45 -annotate +990+20 'Feet' scale.png
convert scale.png  -gravity center -pointsize 34 -annotate -540-40  '0' scale.png
convert scale.png  -gravity center -pointsize 34 -annotate -418-40  '125' scale.png
convert scale.png  -gravity center -pointsize 34 -annotate -296-40  '250' scale.png
convert scale.png  -gravity center -pointsize 34 -annotate -51-40  '500' scale.png
convert scale.png  -gravity center -pointsize 34 -annotate +436-40  '1000' scale.png

