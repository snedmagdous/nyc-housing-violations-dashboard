/**
 * TypeScript declarations for leaflet.heat
 *
 * Extends the Leaflet types to include the heatLayer method
 */

import * as L from 'leaflet';

declare module 'leaflet' {
  interface HeatLayerOptions {
    minOpacity?: number;
    maxZoom?: number;
    max?: number;
    radius?: number;
    blur?: number;
    gradient?: { [key: number]: string };
  }

  function heatLayer(
    latlngs: Array<[number, number] | [number, number, number]>,
    options?: HeatLayerOptions
  ): L.Layer;

  namespace heatLayer {
    function addLatLng(latlng: [number, number] | [number, number, number]): L.Layer;
    function setLatLngs(latlngs: Array<[number, number] | [number, number, number]>): L.Layer;
    function setOptions(options: HeatLayerOptions): L.Layer;
    function redraw(): L.Layer;
  }
}
