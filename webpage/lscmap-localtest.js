

function formatLngLat(x, dim) {
    var dirs = {
            lat: ['N', 'S'],
            lng: ['E', 'W']
        }[dim] || '',
        dir = dirs[x >= 0 ? 0 : 1],
        abs = Math.abs(x),
        whole = Math.floor(abs),
        fraction = abs - whole,
        fractionMinutes = fraction * 60,
        minutes = Math.floor(fractionMinutes),
        seconds = Math.floor((fractionMinutes - minutes) * 60);

    return whole + '°'+
        (minutes ? minutes + "'" : '') +
        (seconds ? seconds + '"' : '') + dir;
}


// 42.42917,-71.51583,42.55694,-71.35667]
var looseBounds = new mapboxgl.LngLatBounds([-71.8578, 42.3236], [-71.1436,42.6537])     
var closeBounds = new mapboxgl.LngLatBounds([-71.50583, 42.43861], [-71.38528,42.53583])    
    
var urlParams;
var currentState;
(window.onpopstate = function () {
    var match,
        pl     = /\+/g,  // Regex for replacing addition symbol with a space
        search = /([^&=]+)=?([^&]*)/g,
        decode = function (s) { return decodeURIComponent(s.replace(pl, " ")); },
        query  = window.location.search.substring(1);

    urlParams = {};
    currentState = window.history.state;
    while (match = search.exec(query))
       urlParams[decode(match[1])] = decode(match[2]);
})();

var startZoom = 12.1; // default zoom
var startCenter = new mapboxgl.LngLat(-71.4338,42.486);
    
mapboxgl.accessToken = 'pk.eyJ1Ijoiamltc2ciLCJhIjoiNDhhdHdCZyJ9.ZV92MDJEE14leO3JMm89Yw';
var map = new mapboxgl.Map({
    container: 'map', // container id
    style: 
    'mapbox://styles/mapbox/outdoors-v9',
    center: startCenter , // starting position
    maxBounds: looseBounds,
    zoom: 9.1 // starting zoom  
});
  

    
function updatePositionInfo(where)
{
    document.getElementById('position-info').innerHTML =              
        formatLngLat(where.lng, 'lng') +' ('+where.lng.toFixed(4)+')' + ' ' + formatLngLat(where.lat, 'lat') +' ('+where.lat.toFixed(4)+')';  
}

    
function updateURL()
{
    var center = map.getBounds().getCenter();
    var newURL = window.location.pathname + '?' +'zoom='+map.getZoom().toFixed(2)+'&lng=' + center.lng.toFixed(6) + '&lat=' + center.lat.toFixed(6);
    window.history.replaceState(currentState, "", newURL );
}
    
map.on('zoom', function (e) {
    updateURL();
});

map.on('mousemove', function (e) {
    updatePositionInfo(e.lngLat);
    updateURL();
});
// Add zoom and rotation controls to the map.
map.addControl(new mapboxgl.NavigationControl());
// Add geolocate control to the map.
map.addControl(new mapboxgl.GeolocateControl());
// disable map rotation using right click + drag
map.dragRotate.disable();
// disable map rotation using touch rotation gesture
map.touchZoomRotate.disableRotation();
// scale(s)
map.addControl(new mapboxgl.ScaleControl({unit: 'imperial'}));
map.addControl(new mapboxgl.ScaleControl({unit: 'metric'}));
    
map.on('load', function () {
    if (urlParams.zoom){
       startZoom = urlParams.zoom;
    }
    if (urlParams.lng && urlParams.lat){
        startCenter = new mapboxgl.LngLat(urlParams.lng, urlParams.lat);
    }
    map.addSource("yellow-trails", {
        "type": "geojson",
        "data": "./yellow.geojson",
    });
   
    map.addLayer({
        'id': 'yellow-highlight',
        'type': 'line',
        'source': "yellow-trails",
        'layout': {
                "visibility": "visible",
                "line-join": "bevel"
            },
            "paint": {
                "line-color": {
                    "base": 1,
                    "stops": [
                        [
                            11.8,
                            "hsl(0, 0%, 0%)"
                        ],
                        [
                            12.8,
                            "hsl(61, 85%, 50%)"
                        ]
                    ]
                },
                "line-width": {
                    "base": 1,
                    "stops": [
                        [
                            10,
                            0
                        ],
                        [
                            11.8,
                            1.5
                        ],
                        [
                            15,
                            8
                        ]
                    ]
                },
                "line-translate": [
                    0,
                    0
                ],
                "line-opacity": 0.9
            },
    });
     map.addLayer({
        'id': 'yellow-pattern',
        'type': 'line',
        'source': "yellow-trails",
        "layout": {
                "visibility": "visible"
            },
            "paint": {
                "line-width": 3,
                "line-dasharray": [
                    5,
                    2
                ],
                "line-opacity": {
                    "base": 1,
                    "stops": [
                        [
                            13.7,
                            0
                        ],
                        [
                            13.8,
                            0.8
                        ]
                    ]
                }
            }
    });
    map.easeTo({duration:3000, zoom:startZoom, center:startCenter});
    updatePositionInfo(startCenter);
    
});
