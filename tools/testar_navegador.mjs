import{launch,open,sleep,until}from'../../pokemon-2d/tools/teste-3d/chrome.mjs';
import{mkdirSync,writeFileSync}from'node:fs';
import assert from'node:assert/strict';
mkdirSync('docs/shots',{recursive:true});
const b=await launch(),resultados=[];
try{
 const P=await open(b,'about:blank','fireash',{rede:true});
 await P.raw('Page.enable');await P.raw('Page.bringToFront');
 await P.raw('Emulation.setDeviceMetricsOverride',{width:844,height:390,deviceScaleFactor:2,mobile:true});
 await P.raw('Emulation.setTouchEmulationEnabled',{enabled:true,maxTouchPoints:5});
 await P.raw('Page.navigate',{url:'http://127.0.0.1:8710/'});
 assert(await until(()=>P.ev('!!window.fireAshTeste?.mapa&&document.getElementById("estado").hidden'),20000));
 for(const id of[33,5,3]){
  await P.ev(`fireAshTeste.carregar(${id})`);await sleep(150);
  const foto=await P.raw('Page.captureScreenshot',{format:'png',clip:{x:0,y:0,width:844,height:390,scale:.5}});
  writeFileSync(`docs/shots/mapa-${id}.png`,Buffer.from(foto.result.data,'base64'));
  const inicio=await P.ev(`(()=>{const t=fireAshTeste,p=t.jogador,vs={2:[0,1],4:[-1,0],6:[1,0],8:[0,-1]},dir=Object.keys(vs).map(Number).find(d=>t.permite(p.x,p.y,d)&&t.permite(p.x+vs[d][0],p.y+vs[d][1],10-d));return{x:p.x,y:p.y,dir,mapa:t.mapa.id};})()`);
  assert(inicio.dir,'Sem saída no ponto de teste');
  const ponto=await P.ev(`(()=>{const r=document.querySelector('button[data-dir="${inicio.dir}"]').getBoundingClientRect();return{x:r.x+r.width/2,y:r.y+r.height/2};})()`);
  await P.raw('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[ponto]});await sleep(260);
  await P.raw('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});await sleep(250);
  const fim=await P.ev('({...fireAshTeste.jogador})');
  assert(Math.hypot(fim.x-inicio.x,fim.y-inicio.y)>0,'Toque não moveu o personagem');
  assert(Number.isInteger(fim.x)&&Number.isInteger(fim.y),'Não terminou o passo');
  resultados.push({id,inicio,fim});
 }
 assert(!P.logs.length,P.logs.join('\n'));
 writeFileSync('docs/navegador.json',JSON.stringify({viewport:[844,390],dpr:2,resultados,erros:P.logs,combateIntegrado:false},null,2));
 console.log('Três áreas originais, movimento por toque e capturas em 844x390 OK.');
}finally{b.kill();}
