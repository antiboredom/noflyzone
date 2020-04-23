function getDistanceFromLatLonInKm(lat1, lon1, lat2, lon2) {
  var R = 6371; // Radius of the earth in km
  var dLat = deg2rad(lat2 - lat1); // deg2rad below
  var dLon = deg2rad(lon2 - lon1);
  var a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(deg2rad(lat1)) *
      Math.cos(deg2rad(lat2)) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);
  var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  var d = R * c; // Distance in km
  return d;
}

function deg2rad(deg) {
  return deg * (Math.PI / 180);
}

async function init() {
  let res = await fetch("parsed_results.json");
  let data = await res.json();

  const fromColors = ["rgba(250, 198, 14, 0.4)", "rgba(250, 198, 14, 0.4)"];
  const toColors = ["rgba(50, 167, 13, 0.8)", "rgba(210, 0, 30, 0.8)"];

  // const fromColors = ["rgba(0, 255, 255, 0.4)", "rgba(255, 255, 0, 0.4)"];
  // const toColors = ["rgba(46, 191, 44, 0.8)", "rgba(255, 0, 0, 0.8)"];

  // const fromColors = ["rgb(0, 255, 255)", "rgb(255, 255, 0)"];
  // const toColors = ["rgb(0, 255, 0)", "rgb(255, 0, 0)"];

  let arcs = [];

  Object.keys(data).forEach((country) => {
    const target = [data[country].lon, data[country].lat];

    for (let sourceName of data[country].good) {
      sourceName = sourceName.toUpperCase();
      if (data[sourceName]) {
        const source = [data[sourceName].lon, data[sourceName].lat];
        const a = source[0] - target[0];
        const b = source[1] - target[1];
        arcs.push({
          startLat: source[1],
          startLng: source[0],
          endLat: target[1],
          endLng: target[0],
          // arcAltitude: Math.random(),
          // arcAltitude: getDistanceFromLatLonInKm(source[1], source[0], target[1], target[0]) / 17000,
          color: [fromColors[0], toColors[0]],
        });
      }
    }

    for (let sourceName of data[country].bad) {
      sourceName = sourceName.toUpperCase();
      if (data[sourceName]) {
        const source = [data[sourceName].lon, data[sourceName].lat];
        const a = source[0] - target[0];
        const b = source[1] - target[1];
        arcs.push({
          startLat: source[1],
          startLng: source[0],
          endLat: target[1],
          endLng: target[0],
          // arcAltitude: Math.sqrt(a * a + b * b) / 300,
          // arcAltitude: getDistanceFromLatLonInKm(source[1], source[0], target[1], target[0]) / 17000,
          color: [fromColors[1], toColors[1]],
        });
      }
    }
  });

  const Globe = new ThreeGlobe()
    // .globeImageUrl("//unpkg.com/three-globe/example/img/earth-night.jpg")
    // .globeImageUrl("//unpkg.com/three-globe/example/img/earth-blue-marble.jpg")
    .globeImageUrl("bwmap1.png")
    // .globeImageUrl("bwmap2.png")
    // .globeImageUrl("shutterstock.webp")
    // .globeImageUrl("water_16k.png")
    .showAtmosphere(false)
    // .showGraticules(true)
    // .arcsData(arcsData)
    .arcsData(arcs)
    // .arcStroke(0.4)
    .arcStroke(0.5)
    // .arcAltitude("arcAltitude")
    .arcAltitudeAutoScale(0.45)
    .arcColor("color");

  // Setup renderer
  const renderer = new THREE.WebGLRenderer();
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setClearColor(0x1a1a1a, 1);
  document.getElementById("globeViz").appendChild(renderer.domElement);

  // Setup scene
  const scene = new THREE.Scene();
  scene.add(Globe);
  scene.add(new THREE.AmbientLight(0xbbbbbb));
  scene.add(new THREE.DirectionalLight(0xffffff, 0.6));

  // Setup camera
  const camera = new THREE.PerspectiveCamera();
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  camera.position.z = 230;

  // Add camera controls
  const tbControls = new TrackballControls(camera, renderer.domElement);
  tbControls.minDistance = 101;
  tbControls.rotateSpeed = 2;
  tbControls.zoomSpeed = 0.1;

  window.addEventListener("resize", () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });

  const play = document.getElementById("radio-button");
  const audio = document.getElementById("radio");
  const about = document.getElementById("about");
  const container = document.querySelector(".inner-container");

  play.addEventListener("click", () => {
    audio.play();
    // container.style.display = "none";
    // document.querySelector(".container").style.background =
    // "rgba(0, 0, 0, 0.5)";
    document.querySelector(".container").style.display = "none";
    about.style.display = "block";

    // document.querySelector("#video").src += "?autoplay=1";
    // play.style.display = "none";
  });

  about.addEventListener("click", () => {
    container.style.display = "flex";
    about.style.display = "none";
    document.querySelector(".container").style.display = "flex";
    // document.querySelector(".container").style.background =
    // "rgba(0, 0, 0, 0.9)";
    // play.style.display = "none";
  });

  function animate() {
    tbControls.update();
    renderer.render(scene, camera);
    requestAnimationFrame(animate);
    Globe.rotation.x += 0.0001;
    Globe.rotation.y += 0.0002;
  }

  animate();
}

init();
