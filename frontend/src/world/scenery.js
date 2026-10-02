import * as THREE from 'three';

export const CITY_RADIUS=720;
const STREET=18;
const colors=['#56645f','#485c5a','#60706a','#465552','#67756b','#52615d'];
const material=(color,extra={})=>new THREE.MeshStandardMaterial({color,roughness:.82,metalness:.12,...extra});

function windowTexture(){
 const canvas=document.createElement('canvas');canvas.width=64;canvas.height=128;
 const ctx=canvas.getContext('2d');ctx.fillStyle='#b2bdb7';ctx.fillRect(0,0,64,128);
 for(let row=0;row<12;row++)for(let column=0;column<6;column++){
  ctx.fillStyle=(row*7+column*11)%5===0?'#d5dfba':'#536862';
  ctx.fillRect(5+column*10,5+row*10,3,4);
 }
 const texture=new THREE.CanvasTexture(canvas);texture.colorSpace=THREE.SRGBColorSpace;
 texture.magFilter=THREE.LinearFilter;texture.minFilter=THREE.LinearMipmapLinearFilter;
 return texture;
}

function instances(scene,name,entries,mat){
 const mesh=new THREE.InstancedMesh(new THREE.BoxGeometry(1,1,1),mat,entries.length);
 mesh.name=name;const dummy=new THREE.Object3D();
 entries.forEach((p,index)=>{
  dummy.position.set(p.x,p.y+p.h/2,p.z);dummy.scale.set(p.w,p.h,p.d);dummy.updateMatrix();
  mesh.setMatrixAt(index,dummy.matrix);if(p.color)mesh.setColorAt(index,new THREE.Color(p.color));
 });
 mesh.computeBoundingSphere();scene.add(mesh);return mesh;
}

// Dense neutral city fabric, never token entities: no IDs, labels, market values or click targets.
export function makeScenery(scene,tokens){
 const bodies=[],roofs=[],podiums=[],details=[];
 let seed=72;const random=()=>{seed=(seed*16807)%2147483647;return(seed-1)/2147483646;};
 for(let bx=-CITY_RADIUS;bx<CITY_RADIUS;bx+=STREET)for(let bz=-CITY_RADIUS;bz<CITY_RADIUS;bz+=STREET){
  const inner=Math.abs(bx)<180&&Math.abs(bz)<180;
  const lots=inner?[[4.8,4.8],[13.2,4.8],[4.8,13.2],[13.2,13.2]]:[[9,9]];
  for(const [dx,dz] of lots){
   const x=bx+dx,z=bz+dz,w=inner?6.25+random()*.65:12.5+random(),d=inner?6.25+random()*.65:12.5+random();
   // Maintain walkable token plots, the central plaza and the existing canal.
   if(Math.hypot(x,z)<11+Math.max(w,d)/2)continue;
   if(x+w/2>-91.5&&x-w/2<-80.5&&z+d/2>-88&&z-d/2<129)continue;
   const nearest=tokens.reduce((min,t)=>Math.min(min,Math.hypot(t.x-x,t.z-z)),Infinity);
   if(nearest<8+Math.max(w,d)/2)continue;
   let h=inner?4+random()*8:5+random()*10;
   if(nearest<24)h=Math.min(h,3.6+random()*1.8);
   const color=colors[Math.floor(random()*colors.length)],setback=random()>.6;
   podiums.push({x,z,y:0,w:w+.3,d:d+.3,h:.25,color:'#3a4942'});
   bodies.push({x,z,y:.25,w,d,h:h*.72,color});
   bodies.push({x:x+(setback?.28:0),z,y:.25+h*.72,w:w*(setback?.76:.96),d:d*(setback?.85:.96),h:h*.28,color});
   roofs.push({x:x+(setback?.28:0),z,y:h+.25,w:w*(setback?.8:1),d:d*(setback?.89:1),h:.18,color});
   if(random()>.35)details.push({x:x+w*.12,z:z-d*.14,y:h+.45,w:w*.23,d:d*.26,h:.45+random()*.55,color:'#61746c'});
  }
 }
 instances(scene,'city-building-podiums',podiums,material('#ffffff'));
 instances(scene,'city-building-facades',bodies,material('#ffffff',{map:windowTexture()}));
 instances(scene,'city-building-rooftops',roofs,material('#a8b5a4'));
 instances(scene,'city-rooftop-details',details,material('#d0d8ce'));
 return {buildingCount:podiums.length};
}

export function makeStreetNetwork(scene){
 const roads=[],markings=[],curbs=[];
 for(let road=-CITY_RADIUS;road<=CITY_RADIUS;road+=STREET){
  roads.push({x:road,z:0,y:-.1,w:3.1,h:.1,d:CITY_RADIUS*2});
  roads.push({x:0,z:road,y:-.1,w:CITY_RADIUS*2,h:.1,d:3.1});
  for(const offset of [-1.65,1.65]){
   curbs.push({x:road+offset,z:0,y:0,w:.16,h:.12,d:CITY_RADIUS*2});
   curbs.push({x:0,z:road+offset,y:0,w:CITY_RADIUS*2,h:.12,d:.16});
  }
  if(Math.abs(road)<=180)for(let dash=-180;dash<=180;dash+=6){
   if(Math.abs(dash%18)<2)continue;
   markings.push({x:road,z:dash,y:.01,w:.07,h:.015,d:1.4});
   markings.push({x:dash,z:road,y:.01,w:1.4,h:.015,d:.07});
  }
 }
 instances(scene,'city-streets',roads,material('#18231f'));
 instances(scene,'city-sidewalks',curbs,material('#46554b'));
 instances(scene,'city-road-markings',markings,material('#768875'));
}