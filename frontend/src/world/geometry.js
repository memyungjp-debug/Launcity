import * as THREE from 'three';
import {CITY_RADIUS,makeStreetNetwork} from './scenery';
export {makeScenery} from './scenery';
export const districtData=[
 {id:'meme',name:'MEME QUARTER',color:'#b6f36e',x:-38,z:-25,points:[[-75,-61],[-7,-61],[-7,-4],[-25,2],[-75,-4]]},
 {id:'defi',name:'DEFI HEIGHTS',color:'#f1bd6c',x:34,z:-28,points:[[3,-61],[70,-61],[82,-42],[77,-6],[3,-6]]},
 {id:'ai',name:'NEURAL DISTRICT',color:'#bca4f7',x:35,z:35,points:[[4,5],[76,5],[76,58],[57,69],[4,66]]},
 {id:'culture',name:'THE WATERFRONT',color:'#68d5df',x:-38,z:36,points:[[-76,6],[-23,9],[-7,5],[-7,66],[-61,66],[-76,45]]}
];
export const mat=(color,extra={})=>new THREE.MeshStandardMaterial({color,roughness:.75,metalness:.15,...extra});
export function box(parent,x,y,z,w,h,d,material){const m=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),material);m.position.set(x,y+h/2,z);parent.add(m);return m;}
export function line(parent,points,color,opacity=1){const g=new THREE.BufferGeometry().setFromPoints(points.map(p=>new THREE.Vector3(...p)));const l=new THREE.Line(g,new THREE.LineBasicMaterial({color,transparent:true,opacity}));parent.add(l);return l;}
export function floorShape(parent,points,color,opacity=1,y=.05){const s=new THREE.Shape();points.forEach(([x,z],i)=>i?s.lineTo(x,-z):s.moveTo(x,-z));s.closePath();const m=new THREE.Mesh(new THREE.ShapeGeometry(s),new THREE.MeshBasicMaterial({color,transparent:true,opacity,side:THREE.DoubleSide}));m.rotation.x=-Math.PI/2;m.position.y=y;parent.add(m);return m;}
function textPlane(parent,text,x,z,color,size=7,width=40){const c=document.createElement('canvas');c.width=1024;c.height=128;const ctx=c.getContext('2d');ctx.font='500 46px monospace';ctx.fillStyle=color;ctx.textAlign='center';ctx.fillText(text,512,82);const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;const p=new THREE.Mesh(new THREE.PlaneGeometry(width,size),new THREE.MeshBasicMaterial({map:t,transparent:true,opacity:.66,depthWrite:false}));p.rotation.x=-Math.PI/2;p.position.set(x,.12,z);parent.add(p);}
export function makeTerrain(scene){
 const ground=box(scene,0,-1,0,CITY_RADIUS*2+120,.7,CITY_RADIUS*2+120,mat('#15201b'));
 const territories=new THREE.Group();scene.add(territories);
 districtData.forEach(d=>{
  floorShape(territories,d.points,d.color,.044,.03);
  line(territories,[...d.points,d.points[0]].map(([x,z])=>[x,.09,z]),d.color,.45);
  textPlane(scene,d.name,d.x,d.z+(d.z<0?-27:27),d.color,4.2,36);
 });
 const asphalt=mat('#141c21');makeStreetNetwork(scene);
 const lane=mat('#50635e',{emissive:'#94bfad',emissiveIntensity:.25});
 box(scene,0,-.05,0,5,.07,320,asphalt);box(scene,0,-.05,0,320,.07,5,asphalt);
 [-2.1,2.1].forEach(x=>{box(scene,x,.005,0,.035,.03,320,lane);box(scene,0,.005,x,320,.03,.035,lane);});
 // The canal and its small bridges distinguish the waterfront from the inner city.
 box(scene,-86,-.08,20,9,.05,215,mat('#0a252b',{metalness:.9,roughness:.3}));
 [-91,-81].forEach(x=>box(scene,x,.06,20,.7,.35,215,mat('#20393c')));
 [-54,0,54].forEach(z=>box(scene,-86,.3,z,16,.5,4,mat('#364348')));
 const plaza=new THREE.Mesh(new THREE.CylinderGeometry(7.8,8,0.35,64),mat('#263432'));plaza.position.y=.2;scene.add(plaza);
 const ring=new THREE.Mesh(new THREE.TorusGeometry(6.6,.07,4,60),new THREE.MeshBasicMaterial({color:'#b6f36e'}));ring.rotation.x=Math.PI/2;ring.position.y=.4;scene.add(ring);
 const crystal=new THREE.Mesh(new THREE.OctahedronGeometry(2.1),mat('#c3f795',{emissive:'#8bd55d',emissiveIntensity:.8,metalness:.65}));crystal.position.y=5;scene.add(crystal);
 textPlane(scene,'GENESIS PLAZA',0,11,'#aabbb4',3,21);
 return {territories,crystal,ground};
}
function windowTexture(color){const c=document.createElement('canvas');c.width=64;c.height=128;const ctx=c.getContext('2d');ctx.fillStyle='#172a29';ctx.fillRect(0,0,64,128);ctx.fillStyle=color;for(let y=7;y<128;y+=13)for(let x=7;x<64;x+=13){ctx.globalAlpha=(x+y)%3===0?.35:.7;ctx.fillRect(x,y,5,6);}const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;t.wrapS=t.wrapT=THREE.RepeatWrapping;return t;}
export const tokenHeight=cap=>cap==null?4:Math.min(38,5+Math.log10(Math.max(cap,1000)/100000+1)*7.2);
export function makeTower(scene,token,index){
 const group=new THREE.Group();group.position.set(token.x,0,token.z);scene.add(group);
 const height=tokenHeight(token.market_cap),color=token.color || '#b6f36e',w=4.6+(index%3)*.65;
 const plot=new THREE.Mesh(new THREE.BoxGeometry(w+5,.18,w+5),mat(color,{transparent:true,opacity:.09}));group.add(plot);
 line(group,[[-w/2-2,.16,-w/2-2],[w/2+2,.16,-w/2-2],[w/2+2,.16,w/2+2],[-w/2-2,.16,w/2+2],[-w/2-2,.16,-w/2-2]],color,.6);
 const building=new THREE.Group();group.add(building);
 const texture=windowTexture(color);
 const facade=mat('#7d9384',{map:texture,emissive:color,emissiveMap:texture,emissiveIntensity:.42,metalness:.45,roughness:.5});
 const roofMat=mat(color,{emissive:color,emissiveIntensity:.1});
 const base=box(building,0,0,0,w*1.2,2.2,w*1.2,mat('#43554f'));
 const levels=index%3===0?3:2;
 let top=2.2;
 for(let j=0;j<levels;j++){
  const partHeight=(height-2.2)/levels,ww=w*(1-j*.18),dd=w*(1-j*.12);
  box(building,0,top,0,ww,partHeight,dd,facade);
  box(building,0,top+partHeight-.12,0,ww+.18,.2,dd+.18,roofMat);
  [-1,1].forEach(s=>box(building,s*ww/2,top,dd/2,.075,partHeight,.075,new THREE.MeshBasicMaterial({color,transparent:true,opacity:.7})));
  top+=partHeight;
 }
 if(index%2===0){box(building,0,height,0,.11,3.2,.11,roofMat);const light=new THREE.Mesh(new THREE.SphereGeometry(.2,8,6),new THREE.MeshBasicMaterial({color}));light.position.set(0,height+3.3,0);building.add(light);}
 box(building,.7,height,-.6,1.1,.65,1.2,mat('#425957'));
 group.traverse(obj=>{if(obj.isMesh)obj.userData.tokenId=token.id;});
 return {group,building,height,token,targetHeight:height};
}