//
// map.js
//

const maps = document.querySelectorAll('[data-map]');

maps.forEach((el) => {
  const zoom = parseInt(el.getAttribute('data-zoom'));
  const markers = JSON.parse(el.getAttribute('data-markers'));

  const center = {
    lat: markers[0].position[0],
    lng: markers[0].position[1],
  };

  // Init map
  const map = new google.maps.Map(el, {
    center: center,
    zoom: zoom,
    disableDefaultUI: true,
  });

  // Get bounds
  const bounds = new google.maps.LatLngBounds();

  // Create markers
  markers.forEach(function (item, i) {
    const position = {
      lat: item.position[0],
      lng: item.position[1],
    };

    const infowindow = new google.maps.InfoWindow({
      content: item.info,
    });

    const marker = new google.maps.Marker({
      position: position,
      map: map,
    });

    marker.addListener('click', function () {
      infowindow.open(map, marker);
    });

    // Extend bounds
    bounds.extend(position);
  });

  // Fit markers into bounds
  if (!zoom) {
    map.fitBounds(bounds);
  }
});
