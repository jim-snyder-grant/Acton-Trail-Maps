convert -size 600x220 xc:white -fill none  -font Arial\
      -draw 'fill white stroke black stroke-width 3 rectangle 2,2 598,218' \
         -draw 'font-size 45 stroke black fill black text 40,45  "Legend"' \
        \
         -draw 'font-size 35 stroke black fill black text 40,95  "Fishing Trail"' \
          -draw "stroke black fill none stroke-width 7 stroke-dasharray 10 10 path 'M 300,80 A 800,1000  0  0,0 490,80'" \
         \
         \
          -draw 'font-size 35 stroke black fill black text 40,145  "Meadow"' \
          -draw 'fill rgb(202,216,162) stroke black stroke-width 3 rectangle 300,115 340,145' \
          \
          -draw 'font-size 35 stroke black fill black text 40,195  "Parking"' \
          -draw 'fill rgb(234,238,221) stroke black stroke-width 3 rectangle 300,165 340,195' \
          -gravity northwest     local_parking.png  -compose Over -geometry x25+305+170    -composite \
         \
          legend.png

