convert -size 2550x3300 canvas:white temp.png
composite  \( NorthActonMapForGuidebook.png  -geometry "160%" \) -gravity south -geometry "+0+150"  temp.png temp.png
composite title_north_acton.png -gravity north -geometry +0+200   temp.png temp.png
convert temp.png -size 2550x3300 -units 'PixelsPerInch' -density 300 mNorthActon.pdf
rm temp.png

