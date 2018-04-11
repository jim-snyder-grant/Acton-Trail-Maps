
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

var STARTZOOM = 12.1;
var newZoom = STARTZOOM; 
var STARTCENTER = new mapboxgl.LngLat(-71.4338,42.486);
var newCenter = STARTCENTER;
var ZOOMPADDING = 40;
var ZOOMTIME = 3300; // milliseconds
var FASTZOOMTIME = 1100; 

var whichLandInfo = null;
var landName = null;
    
mapboxgl.accessToken = 'pk.eyJ1Ijoiamltc2ciLCJhIjoiNDhhdHdCZyJ9.ZV92MDJEE14leO3JMm89Yw';
var map = new mapboxgl.Map({
    container: 'map', // container id
    style: 'mapbox://styles/jimsg/civ17sdex00l02io48dp99x1m', //stylesheet location
    center: STARTCENTER , // starting position
    maxBounds: looseBounds,
    attributionControl: true,
    zoom: 9.1 // starting zoom  
});

// put our ugly control in with the mapbox conttrols
var LowerRightControls = document.getElementsByClassName('mapboxgl-ctrl-bottom-right')[0];
// console.log(LowerRightControls);

LowerRightControls.insertBefore(document.getElementById('position-info'), LowerRightControls.firstChild);

$( document ).ready(function() {
    
    $("#dropdown-goto").load("dropdown.html", function(){});
    
    $('.dropdown-button').dropdown({
      inDuration: 300,
      outDuration: 225,
      constrainWidth: false,
      belowOrigin: true, // Displays dropdown below the button
      alignment: 'right' 
    });
      
   $("#dropdown-goto").on( "click", function( event ) {
        land = event.target.innerHTML;
        envelope = Envelopes[land].envelope;
    //    console.log(land, envelope);
        map.fitBounds(envelope,  {duration:ZOOMTIME, padding: {top: ZOOMPADDING, bottom:ZOOMPADDING, left: ZOOMPADDING, right: ZOOMPADDING}});
        whichLandInfo = Envelopes[land];
        landName = land;
    });
    $('#aerial-view').on('click', function(e) {
        var a = $(this).data('state');
        var b = $(this).prop('checked');
        if (a && b) {
            b = false;
            $(this).prop('checked', b);
        }
        $(this).data('state', b);
        map.setPaintProperty('mapbox-satellite', 'raster-opacity', b ? 0.82 : 0);
        map.setLayoutProperty('parking', 'visibility', b ? "none": "visible");
        map.setLayoutProperty('grass', 'visibility', b ? "none": "visible");
        
    })
    $('#bay-circuit-trail').on('click', function(e) {
        var a = $(this).data('state');
        var b = $(this).prop('checked');
        if (a && b) {
            b = false;
            $(this).prop('checked', b);
        }
        $(this).data('state', b); 
        map.setLayoutProperty('bct', 'visibility', b ? "visible": "none");

    })
     $( "#zoom-in" ).on( "click", function( event ) {
         event.preventDefault();
        map.zoomTo(map.getZoom()+1,  {duration:FASTZOOMTIME});
    });
     $( "#zoom-out" ).on( "click", function( event ) {
         event.preventDefault();
        map.zoomTo(map.getZoom()-1,  {duration:FASTZOOMTIME});
    });
});  

function updatePositionInfo(where)
{
    newPosition= 'lat ' + where.lat.toFixed(4)+'<br>lon ' + where.lng.toFixed(4);  
    document.getElementById('position-info').innerHTML =  newPosition;  
       
}
   
function updateURL()
{
    var center = map.getBounds().getCenter();
    var newURL = window.location.pathname + '?' +'zoom='+map.getZoom().toFixed(2)+'&lng=' + center.lng.toFixed(6) + '&lat=' + center.lat.toFixed(6);
    window.history.replaceState(currentState, "", newURL );
}

map.on('moveend', function() {
        var center = map.getCenter()
//        console.log("map centerlat/lng:")
//        console.log(center.lat)
//        console.log(center.lng)

    // find first conservation land where the envelope encompasses the map center
        // or see if we were sent here by a conservation land menu item
        
        if (!whichLandInfo)
        {
            for (var cl in Envelopes)
            {
//                console.log(cl)
//                console.log(Envelopes[cl].envelope[0][1]);
//                console.log(Envelopes[cl].envelope[1][1]);
//                console.log(Envelopes[cl].envelope[1][0]);
//                console.log(Envelopes[cl].envelope[0][0]);                
                if (    center.lat > Envelopes[cl].envelope[0][1] && 
                        center.lat < Envelopes[cl].envelope[1][1] && 
                        center.lng > Envelopes[cl].envelope[0][0] && 
                        center.lng < Envelopes[cl].envelope[1][0])
                {
                    whichLandInfo = Envelopes[cl]; 
                    landName = cl; 
                    break;     
                }
            }
        }
    
        if (whichLandInfo)
        {   
            $("#card-land-name").attr("href", whichLandInfo.url);
            $("#card-land-name").html(landName + '<i class="material-icons">info</i>' );
            
            $("#info-card").attr( "data-tooltip", "For more information about " + landName);
            $("#info-card").tooltip();
            
            $("#info-card").css("visibility", "visible");  
        }
        else {
            $("#info-card").css("visibility", "hidden");  
        }
        whichLandInfo = null;
        
});

map.on('zoomend', function (e) {
    updateURL();
});

map.on('mousemove', function (e) {
    updatePositionInfo(e.lngLat);
    updateURL();
});
// Add geolocate control to the map.
map.addControl(new mapboxgl.GeolocateControl({
    positionOptions: {enableHighAccuracy: true},
    fitBoundsOptions: {maxZoom: 16}, // Default 15
    trackUserLocation: true
}),'bottom-right');

// disable map rotation using right click + drag
map.dragRotate.disable();
// disable map rotation using touch rotation gesture
map.touchZoomRotate.disableRotation();
// scale(s)
map.addControl(new mapboxgl.ScaleControl({unit: 'imperial'}));
// map.addControl(new mapboxgl.ScaleControl({unit: 'metric'}));
    
map.on('load', function () {
    if (urlParams.goto){
        switch (urlParams.goto) {
        case 'town':
                newZoom = STARTZOOM;
                newCenter = STARTCENTER;
        break;
        }
    }
    if (urlParams.zoom){
       newZoom = urlParams.zoom;
    }
    if (urlParams.lng && urlParams.lat){
        newCenter = new mapboxgl.LngLat(urlParams.lng, urlParams.lat);
    }
    var b = $('#bay-circuit-trail').prop('checked');
    map.setLayoutProperty('bct', 'visibility', b ? "visible": "none");
    
    map.easeTo({duration:3000, zoom:newZoom, center:newCenter});
    updatePositionInfo(newCenter);
    
});
