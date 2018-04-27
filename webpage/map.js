
var looseBounds = new mapboxgl.LngLatBounds([-71.8578, 42.3236], [-71.1436,42.6537]);   
var closeBounds = new mapboxgl.LngLatBounds([-71.50583, 42.43861], [-71.38528,42.53583]);
    
var urlParams;
var currentState;
(window.onpopstate = function () {
//    console.log("popstate begin")
    var match;
    var pl     = /\+/g;  // Regex for replacing addition symbol with a space
    var search = /([^&=]+)=?([^&]*)/g;
    var decode = function (s) { return decodeURIComponent(s.replace(pl, " ")); };
    var query  = window.location.search.substring(1);

    urlParams = {};
    currentState = window.history.state;
    while (match = search.exec(query))
       urlParams[decode(match[1])] = decode(match[2]);
//    console.log("popstate end: ")
//    console.log(urlParams);
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
    zoom: 9.1, // starting zoom  
    preserveDrawingBuffer: true
});

var hasMouse = null;

// finding out if there is mouse support
// https://stackoverflow.com/a/35133651
$(window).bind('mousemove.hasMouse',function(){
    $(window).unbind('.hasMouse');
    hasMouse=true;
}).bind('touchstart.hasMouse',function(){
    $(window).unbind('.hasMouse');
    hasMouse=false;
});

// put our ugly control in with the mapbox conttrols
var LowerRightControls = document.getElementsByClassName('mapboxgl-ctrl-bottom-right')[0];
// console.log(LowerRightControls);

LowerRightControls.insertBefore(document.getElementById('position-info'), LowerRightControls.firstChild);

function gotoLand(where)
{
   envelope = Envelopes[where].envelope;
    //    console.log(land, envelope);
    if (envelope)
    {
        $("#info-card").css("visibility", "hidden");
        map.fitBounds(envelope,  {duration:ZOOMTIME, padding: {top: ZOOMPADDING, bottom:ZOOMPADDING, left: ZOOMPADDING, right: ZOOMPADDING}});
        whichLandInfo = Envelopes[where];
        landName = where;
    }
}

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
        gotoLand(land);
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
     $( "#card-action" ).on( "click", function( event ) {
        window.location = whichLandInfo.url;
    });
     $( "#card-land-name" ).on( "click", function( event ) {
         window.location = whichLandInfo.url;
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

function updateInfobox()
{
    if (whichLandInfo && "None" != whichLandInfo.url)
    {   
        $("#card-land-name").html("&nbsp;" + landName + "&nbsp;");
        $("#info-card").css("visibility", "visible");  
    }
    else {
        $("#info-card").css("visibility", "hidden");  
    }
}

map.on('movestart', function() {
        whichLandInfo = null;
});


map.on('moveend', function() {
        var center = map.getCenter()

    // find first conservation land where the envelope encompasses the map center
        // or see if we were sent here by a conservation land menu item
        
        if (!whichLandInfo)
        {
            for (var cl in Envelopes)
            {           
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
        updateInfobox();        
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
    var b = $('#bay-circuit-trail').prop('checked');
    map.setLayoutProperty('bct', 'visibility', b ? "visible": "none");

    if (urlParams.goto){
        gotoLand(urlParams.goto);
    } 
    else
    {
        if (urlParams.zoom){
            newZoom = urlParams.zoom;
        }
        if (urlParams.lng && urlParams.lat){
            newCenter = new mapboxgl.LngLat(urlParams.lng, urlParams.lat);
        }
    
        map.easeTo({duration:3000, zoom:newZoom, center:newCenter});
        updatePositionInfo(newCenter);
    }
    if (!hasMouse)
    {
         $('.tooltipped').tooltip('remove');
    }
});
 map.on('click', function (e) {
        landName = null;
        whichLandInfo = null
        features = null;
//        console.log(e)
//        console.log(e.point)
    
        features = map.queryRenderedFeatures(
                e.point,
                { layers: ['bounds'] });    
        
        if (features && features[0])
        {
//            console.log(features)
            landName = features[0].properties.name;
        }
        if (landName)
        {
            whichLandInfo = Envelopes[landName]; 
        }
//        console.log("e, landName, whichLandInfo")
//        console.log(e)
//        console.log(landName)
//        console.log(whichLandInfo)
     

        updateInfobox();
    });
