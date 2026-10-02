import * as THREE from 'three';
import {mergeGeometries} from 'three/examples/jsm/utils/BufferGeometryUtils.js';

// Batch static streets/trees by shared material without changing the city's geometry.
// Keep interactive towers, moving objects, transparent territory layers and instances separate.
export const batchScenery=(scene,excluded)=>{
 scene.updateMatrixWorld(true);
 const batches=new Map();
 scene.traverse(object=>{
  if(!object.isMesh||object.isInstancedMesh||excluded.has(object)||Array.isArray(object.material)||object.material.transparent)return;
  const key=object.material.uuid;
  if(!batches.has(key))batches.set(key,[]);
  batches.get(key).push(object);
 });
 batches.forEach(objects=>{
  if(objects.length<2)return;
  const geometries=objects.map(object=>object.geometry.clone().applyMatrix4(object.matrixWorld));
  const geometry=mergeGeometries(geometries,false);
  geometries.forEach(item=>item.dispose());
  if(!geometry)return;
  const merged=new THREE.Mesh(geometry,objects[0].material);
  merged.name='batched-city-scenery';
  scene.add(merged);
  objects.forEach(object=>{object.removeFromParent();object.geometry.dispose();});
 });
};