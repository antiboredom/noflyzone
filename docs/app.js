//https://deck.gl/#/documentation/deckgl-api-reference/layers/arc-layer?section=installation
//
const tt = document.getElementById("tooltip");
const debug = false;

let dgl;

async function init() {
  function rotateCamera(timestamp) {
    const bearing = (timestamp / 900) % 360;

    let zoom = 1 + timestamp / 20000;
    if (zoom > zoomTarget) zoom = zoomTarget;

    let pitch = timestamp / 600;
    if (pitch > pitchTarget) pitch = pitchTarget;

    const lon = 0;
    const lat = 0;

    // const lon = Math.sin(timestamp / 10000) * 10;
    // const lat = Math.cos(timestamp / 10000) * 10;

    // console.log(zoom, pitch);
    // const zoom = Math.abs(Math.sin(timestamp / 10000)) * 1 + 1;
    // const pitch = Math.abs(Math.sin(timestamp / 10000)) * 60;

    deckgl.setProps({
      viewState: {
        longitude: lon,
        latitude: lat,
        bearing: bearing,
        zoom: zoom,
        pitch: pitch,
      },
    });

    requestAnimationFrame(rotateCamera);
  }

  const pitchTarget = 60;
  const zoomTarget = 2;

  let res = await fetch("parsed_results.json");
  let data = await res.json();

  const fromColors = [
    [0, 255, 255, 80],
    [255, 255, 0, 80],
  ];

  const toColors = [
    [0, 255, 0, 200],
    [255, 0, 0, 200],
  ];

  const deckgl = new deck.DeckGL({
    mapboxApiAccessToken:
      "pk.eyJ1Ijoic3BsYXZpZ25lIiwiYSI6ImNrOTRxOGl3dzAxb3czZnE5c3B6ZmFtdWMifQ.sSnfEHis7T6DsuBlKDATfw",
    // mapStyle: "mapbox://styles/splavigne/ck94w3u371mgg1iqmo2ccfigs",
    mapStyle: "mapbox://styles/splavigne/ck94yb3hd2plm1io3k0noxct0",
    initialViewState: {
      longitude: 0,
      latitude: 0,
      zoom: 1,
      maxZoom: 15,
      pitch: 0,
      bearing: 0,
    },
    controller: true,
    layers: [],
  });

  dgl = deckgl;

  let arcs = [];

  Object.keys(data).forEach((country) => {
    const target = [data[country].lon, data[country].lat];

    for (let sourceName of data[country].good) {
      sourceName = sourceName.toUpperCase();
      if (data[sourceName]) {
        const source = [data[sourceName].lon, data[sourceName].lat];
        arcs.push({
          source: source,
          target: target,
          type: 0,
          fromName: sourceName,
          toName: country,
        });
      }
    }

    for (let sourceName of data[country].bad) {
      sourceName = sourceName.toUpperCase();
      if (data[sourceName]) {
        const source = [data[sourceName].lon, data[sourceName].lat];
        arcs.push({
          source: source,
          target: target,
          type: 1,
          fromName: sourceName,
          toName: country,
        });
      }
    }
  });

  const arcLayer = new deck.ArcLayer({
    id: "arc",
    data: arcs,
    pickable: true,
    getSourcePosition: (d) => d.source,
    getTargetPosition: (d) => d.target,
    getSourceColor: (d) => fromColors[d.type],
    getTargetColor: (d) => toColors[d.type],
    getWidth: 5,
    getHeight: 0.5,
    getTilt: () => Math.random() * 40 - 20,
    onHover: ({ object, x, y }) => {
      if (!debug) return;

      if (object) {
        const tooltip = `${object.fromName} to ${object.toName} ${object.target}, ${object.source}`;
        tt.innerHTML = tooltip;
        tt.style.display = "block";
        tt.style.left = x + "px";
        tt.style.top = y + "px";
      }
    },
  });

  deckgl.setProps({
    layers: [arcLayer],
  });

  const play = document.getElementById("radio-button");
  const audio = document.getElementById("radio");

  play.addEventListener("click", () => {
    audio.play();
    play.style.display = "none";
  });

  rotateCamera(0);
}

init();
