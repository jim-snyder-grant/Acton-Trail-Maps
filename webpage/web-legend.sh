convert -size 1000x200 xc:white -fill none  -font Nimbus-Sans-L \
        -draw 'fill green rectangle 450,18 480,30' \
        -draw 'font-size 15 font Nimbus-Sans-L stroke black fill black text 500,30  "Acton Conservation Land"' \
        \
        -draw 'fill rgb(0,200,100) rectangle 450,48 480,60' \
        -draw 'font-size 15 font Nimbus-Sans-L stroke black fill black text 500,60  "Acton Town Land"' \
        \
        -draw "stroke yellow fill none stroke-width 6                      path 'M 230,25 A 700,900  0  0,0 280,25'" \
        -draw "stroke black fill none stroke-width 3 stroke-dasharray 12 6 path 'M 230,25 A 700,900  0  0,0 280,25'" \
        -draw 'font-size 15 font Nimbus-Sans-L stroke black fill black text 300,30  "Main Trail"' \
        \
        -draw "stroke blue   fill none stroke-width 6                      path 'M 230,55 A 700,900  0  0,0 280,55'" \
        -draw "stroke black  fill none stroke-width 3 stroke-dasharray 8 8 path 'M 230,55 A 700,900  0  0,0 280,55'" \
        -draw 'font-size 15 font Nimbus-Sans-L stroke black fill black text 300,60  "Secondary Trail"' \
        \
        -draw "stroke red    fill none stroke-width 6                      path 'M 230,85 A 700,900  0  0,0 280,85'" \
        -draw "stroke black  fill none stroke-width 3 stroke-dasharray 5 5 path 'M 230,85 A 700,900  0  0,0 280,85'" \
        -draw 'font-size 15 font Nimbus-Sans-L stroke black fill black text 300,90 "Access Trail"' \
        \
        -draw "stroke black  fill none stroke-width 3 stroke-dasharray 4 4 path 'M 230,115 A 700,900  0  0,0 280,115'" \
        -draw 'font-size 15 font Nimbus-Sans-L stroke black fill black text 300,120  "Unblazed Trail"' \
        \
        -draw 'font-size 15 font Nimbus-Sans-L stroke black fill black text 150,30  "Parking"' \
        -draw 'fill rgb(234,238,221) stroke black stroke-width 1 rectangle 100,17 130,33' \
        -gravity northwest     local_parking.png  -compose Over -geometry x14+105+19    -composite \
        \
        web-legend.png

