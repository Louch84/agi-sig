/**
 * Minimal OrbitControls UMD for three.js
 * License: MIT (same as Three.js)
 */
(function(root) {
  var THREE = root.THREE;

  var OrbitControls = function(camera, domElement) {
    this.camera = camera;
    this.domElement = domElement;
    this.target = new THREE.Vector3();

    this.enableDamping = false;
    this.dampingFactor = 0.05;
    this.enableZoom = true;
    this.enablePan = true;
    this.enableRotate = true;

    this.minDistance = 0;
    this.maxDistance = Infinity;
    this.minPolarAngle = 0;
    this.maxPolarAngle = Math.PI;

    var scope = this;
    var spherical = new THREE.Spherical();
    var sphericalDelta = new THREE.Spherical();
    var panOffset = new THREE.Vector3();
    var zoomScale = 1;
    var rotateStart = new THREE.Vector2();
    var panStart = new THREE.Vector2();
    var state = -1; // -1=none, 0=rotate, 1=pan, 2=zoom

    this.update = function() {
      var offset = new THREE.Vector3();
      offset.copy(camera.position).sub(scope.target);

      spherical.setFromVector3(offset);

      if (scope.enableDamping) {
        spherical.theta += sphericalDelta.theta * scope.dampingFactor;
        spherical.phi += sphericalDelta.phi * scope.dampingFactor;
      } else {
        spherical.theta += sphericalDelta.theta;
        spherical.phi += sphericalDelta.phi;
      }

      spherical.phi = Math.max(scope.minPolarAngle, Math.min(scope.maxPolarAngle, spherical.phi));
      spherical.radius *= zoomScale;
      spherical.radius = Math.max(scope.minDistance, Math.min(scope.maxDistance, spherical.radius));

      offset.setFromSpherical(spherical);
      offset.add(scope.target);
      camera.position.copy(offset);
      camera.lookAt(scope.target);

      if (scope.enableDamping) {
        sphericalDelta.theta *= (1 - scope.dampingFactor);
        sphericalDelta.phi *= (1 - scope.dampingFactor);
      } else {
        sphericalDelta.set(0, 0, 0);
      }

      panOffset.multiplyScalar(0);
      zoomScale = 1;

      return false;
    };

    function onMouseDown(event) {
      event.preventDefault();
      if (event.button === 0) {
        state = 0;
        rotateStart.set(event.clientX, event.clientY);
      } else if (event.button === 2) {
        state = 1;
        panStart.set(event.clientX, event.clientY);
      }
      document.addEventListener('mousemove', onMouseMove, false);
      document.addEventListener('mouseup', onMouseUp, false);
    }

    function onMouseMove(event) {
      if (state === 0) {
        var dx = event.clientX - rotateStart.x;
        var dy = event.clientY - rotateStart.y;
        rotateStart.set(event.clientX, event.clientY);
        sphericalDelta.theta -= 2 * Math.PI * dx / domElement.clientWidth;
        sphericalDelta.phi -= 2 * Math.PI * dy / domElement.clientHeight;
      } else if (state === 1) {
        var dx = event.clientX - panStart.x;
        var dy = event.clientY - panStart.y;
        panStart.set(event.clientX, event.clientY);
        var offset = new THREE.Vector3();
        offset.copy(camera.position).sub(scope.target);
        var distance = offset.length();
        offset.cross(camera.up).normalize();
        offset.multiplyScalar(dx * 0.5 / domElement.clientWidth * distance);
        panOffset.add(offset);
        offset.set(0, 1, 0).cross(camera.up).normalize();
        offset.multiplyScalar(-dy * 0.5 / domElement.clientHeight * distance);
        panOffset.add(offset);
      }
    }

    function onMouseUp() {
      state = -1;
      document.removeEventListener('mousemove', onMouseMove, false);
      document.removeEventListener('mouseup', onMouseUp, false);
    }

    function onWheel(event) {
      event.preventDefault();
      if (event.deltaY < 0) {
        zoomScale /= Math.pow(0.95, 2);
      } else if (event.deltaY > 0) {
        zoomScale *= Math.pow(0.95, 2);
      }
    }

    function onContextMenu(event) {
      event.preventDefault();
    }

    domElement.addEventListener('mousedown', onMouseDown, false);
    domElement.addEventListener('wheel', onWheel, { passive: false });
    domElement.addEventListener('contextmenu', onContextMenu, false);
    domElement.addEventListener('touchstart', onTouchStart, { passive: false });
    domElement.addEventListener('touchmove', onTouchMove, { passive: false });
    domElement.addEventListener('touchend', onTouchEnd, false);
  };

  function onTouchStart(event) {
    if (event.touches.length === 1) {
      state = 0;
      rotateStart.set(event.touches[0].clientX, event.touches[0].clientY);
    } else if (event.touches.length === 2) {
      state = 2;
      var dx = event.touches[0].clientX - event.touches[1].clientX;
      var dy = event.touches[0].clientY - event.touches[1].clientY;
      var dist = Math.sqrt(dx*dx + dy*dy);
      this._pinchStartDist = dist;
    }
  }

  function onTouchMove(event) {
    event.preventDefault();
    if (state === 0 && event.touches.length === 1) {
      var dx = event.touches[0].clientX - rotateStart.x;
      var dy = event.touches[0].clientY - rotateStart.y;
      rotateStart.set(event.touches[0].clientX, event.touches[0].clientY);
      // Approximate with sphericalDelta
      this.dispatchEvent({ type: 'change' });
    } else if (state === 2 && event.touches.length === 2) {
      var dx = event.touches[0].clientX - event.touches[1].clientX;
      var dy = event.touches[0].clientY - event.touches[1].clientY;
      var dist = Math.sqrt(dx*dx + dy*dy);
      if (dist > this._pinchStartDist) {
        zoomScale /= 1.02;
      } else {
        zoomScale *= 1.02;
      }
      this._pinchStartDist = dist;
    }
  }

  function onTouchEnd(event) {
    state = -1;
  }

  OrbitControls.prototype = Object.assign({}, THREE.EventDispatcher.prototype, OrbitControls.prototype);
  OrbitControls.prototype.constructor = OrbitControls;

  root.OrbitControls = OrbitControls;
})(window);
