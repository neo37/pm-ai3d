/* 3D-карта объектов ИПМ на MapLibre GL с облётом камеры (flyTo).
   Стиль: openfreemap/liberty (бесплатно, без токена, с 3D-зданиями). */
(function () {
  "use strict";

  var STYLE = "https://tiles.openfreemap.org/styles/liberty";
  var MOSCOW = [37.6173, 55.7558];

  function esc(s) {
    return (s || "").replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  function add3DBuildings(map) {
    try {
      var layers = map.getStyle().layers || [];
      var labelLayer = null;
      for (var i = 0; i < layers.length; i++) {
        if (layers[i].type === "symbol" && layers[i].layout && layers[i].layout["text-field"]) {
          labelLayer = layers[i].id;
          break;
        }
      }
      if (map.getLayer("astryx-3d-buildings")) return;
      map.addLayer(
        {
          id: "astryx-3d-buildings",
          source: "openmaptiles",
          "source-layer": "building",
          type: "fill-extrusion",
          minzoom: 13,
          paint: {
            "fill-extrusion-color": [
              "interpolate", ["linear"], ["get", "render_height"],
              0, "#d7dbe2", 60, "#c3c9d4", 160, "#aab2c0"
            ],
            "fill-extrusion-height": [
              "interpolate", ["linear"], ["zoom"],
              13, 0, 15.5, ["coalesce", ["get", "render_height"], 8]
            ],
            "fill-extrusion-base": ["coalesce", ["get", "render_min_height"], 0],
            "fill-extrusion-opacity": 0.85
          }
        },
        labelLayer
      );
    } catch (e) { /* style may lack the source; ignore */ }
  }

  function makeMarker(map, p, onClick) {
    var el = document.createElement("div");
    el.className = "mk";
    el.style.color = p.color || "#c8963e";
    var pulse = document.createElement("div");
    pulse.className = "mk-pulse";
    el.appendChild(pulse);
    var pin = document.createElement("div");
    pin.className = "mk-pin";
    pin.style.background = p.color || "#c8963e";
    el.appendChild(pin);
    el.title = p.title;

    var popupHtml =
      '<div class="pop">' +
      (p.image ? '<img src="' + esc(p.image) + '" alt="">' : "") +
      '<div class="pop-body">' +
      '<span class="pop-cat" style="color:' + esc(p.color) + '">' + esc(p.categoryLabel) + "</span>" +
      "<h4>" + esc(p.title) + "</h4>" +
      (p.address ? "<p>" + esc(p.address) + (p.approximate ? " · <i>≈</i>" : "") + "</p>" : "") +
      (p.url ? '<a href="' + esc(p.url) + '">Подробнее →</a>' : "") +
      "</div></div>";

    var popup = new maplibregl.Popup({ offset: 28, closeButton: false }).setHTML(popupHtml);
    var marker = new maplibregl.Marker({ element: el, anchor: "bottom" })
      .setLngLat([p.lng, p.lat])
      .setPopup(popup)
      .addTo(map);

    el.addEventListener("click", function () {
      if (onClick) onClick(p, marker);
    });
    return marker;
  }

  window.initAstryxMap = function (opts) {
    opts = opts || {};
    var container = opts.container;
    if (!container || typeof maplibregl === "undefined") return;

    var interactive = opts.interactive !== false;
    var autoTour = opts.autoTour !== false;

    var map = new maplibregl.Map({
      container: container,
      style: STYLE,
      center: opts.center || MOSCOW,
      zoom: opts.zoom || 10.4,
      pitch: 50,
      bearing: -14,
      interactive: interactive,
      attributionControl: true,
      cooperativeGestures: !!opts.cooperative
    });

    if (interactive) {
      map.addControl(new maplibregl.NavigationControl({ showCompass: true }), "bottom-right");
    }
    map.scrollZoom.disable && !interactive && map.scrollZoom.disable();

    var markers = [];
    var tour = { timer: null, idx: 0, playing: false };

    function stopTour() {
      tour.playing = false;
      if (tour.timer) { clearTimeout(tour.timer); tour.timer = null; }
      var b = document.getElementById(opts.playBtn);
      if (b) b.textContent = "Запустить облёт";
    }

    function flyToProject(p, i) {
      map.flyTo({
        center: [p.lng, p.lat],
        zoom: 15.2,
        pitch: 58,
        bearing: -20 + (i % 8) * 6,
        duration: 3200,
        essential: true
      });
    }

    function step(projects) {
      if (!tour.playing) return;
      var p = projects[tour.idx % projects.length];
      var mk = markers[tour.idx % projects.length];
      flyToProject(p, tour.idx);
      map.once("moveend", function () {
        if (!tour.playing) return;
        if (mk && mk.getPopup && !mk.getPopup().isOpen()) mk.togglePopup();
        tour.timer = setTimeout(function () {
          if (mk && mk.getPopup && mk.getPopup().isOpen()) mk.togglePopup();
          tour.idx++;
          step(projects);
        }, 2600);
      });
    }

    function playTour(projects) {
      if (!projects.length) return;
      tour.playing = true;
      var b = document.getElementById(opts.playBtn);
      if (b) b.textContent = "Остановить облёт";
      step(projects);
    }

    map.on("load", function () {
      add3DBuildings(map);
      var host = document.getElementById(container);
      if (host && host.classList.contains("hero-map")) host.classList.add("ready");
      var loader = document.getElementById(opts.loader);
      if (loader) loader.classList.add("hide");

      fetch("/api/projects.json")
        .then(function (r) { return r.json(); })
        .then(function (data) {
          var projects = (data.projects || []).filter(function (p) {
            return p.lat && p.lng;
          });
          if (!projects.length) return;

          var bounds = new maplibregl.LngLatBounds();
          projects.forEach(function (p, i) {
            markers.push(
              makeMarker(map, p, function (proj, mk) {
                stopTour();
                map.flyTo({ center: [proj.lng, proj.lat], zoom: 15.5, pitch: 58, duration: 1400 });
              })
            );
            bounds.extend([p.lng, p.lat]);
          });

          if (!opts.center) {
            map.fitBounds(bounds, { padding: opts.padding || 80, pitch: 50, bearing: -14, duration: 0, maxZoom: 12 });
          }

          // controls
          var playBtn = document.getElementById(opts.playBtn);
          if (playBtn) {
            playBtn.addEventListener("click", function () {
              if (tour.playing) stopTour();
              else playTour(projects);
            });
          }
          var resetBtn = document.getElementById(opts.resetBtn);
          if (resetBtn) {
            resetBtn.addEventListener("click", function () {
              stopTour();
              map.fitBounds(bounds, { padding: opts.padding || 80, pitch: 50, bearing: -14, duration: 1500, maxZoom: 12 });
            });
          }

          // any user drag stops the tour
          map.on("dragstart", stopTour);

          if (autoTour) {
            setTimeout(function () { playTour(projects); }, 500);
          }
        })
        .catch(function () {});
    });

    return map;
  };

  // Simple single-point map (contacts / project detail)
  window.initPointMap = function (container, lng, lat, label) {
    if (!container || typeof maplibregl === "undefined") return;
    var map = new maplibregl.Map({
      container: container,
      style: STYLE,
      center: [lng, lat],
      zoom: 15,
      pitch: 50,
      bearing: -14
    });
    map.addControl(new maplibregl.NavigationControl(), "top-right");
    map.on("load", function () {
      add3DBuildings(map);
      var el = document.createElement("div");
      el.className = "mk";
      var pin = document.createElement("div");
      pin.className = "mk-pin";
      pin.style.background = "#c8963e";
      el.appendChild(pin);
      var m = new maplibregl.Marker({ element: el, anchor: "bottom" }).setLngLat([lng, lat]);
      if (label) m.setPopup(new maplibregl.Popup({ offset: 28 }).setHTML("<div class='pop-body'><b>" + label + "</b></div>"));
      m.addTo(map);
    });
    return map;
  };
})();
