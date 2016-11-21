convert -size 450x280 xc:white -fill none  -font Nimbus-Sans-L-Bold \
      -draw 'fill white stroke black stroke-width 3 rectangle 2,2 448,278' \
         -draw 'font-size 45 font Nimbus-Sans-L-Bold stroke black fill black text 40,50  "Legend"' \
        \
         -draw 'font-size 32 font Nimbus-Sans-L stroke black fill black text 40,95  "Fishing Trail"' \
          -draw "stroke black fill none stroke-width 7 stroke-dasharray 10 10 path 'M 300,80 A 700,900  0  0,0 410,80'" \
         \
         \
          -draw 'font-size 32 font Nimbus-Sans-L stroke black fill black text 40,145  "Meadow"' \
          -draw 'fill rgb(202,216,162) stroke black stroke-width 3 rectangle 300,115 340,145' \
          \
          -draw 'font-size 32 font Nimbus-Sans-L stroke black fill black text 40,195  "Parking"' \
          -draw 'fill rgb(234,238,221) stroke black stroke-width 3 rectangle 300,165 340,195' \
          -gravity northwest     local_parking.png  -compose Over -geometry x25+307+168    -composite \
          -draw 'font-size 28 font Nimbus-Sans-L stroke black fill black text 40,225  "Contour interval five meters"' \
         \
          legend.png

