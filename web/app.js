// Leitor visual do mapa original. Não interpreta scripts Ruby nem simula missões.
const cv=document.querySelector('canvas'),ctx=cv.getContext('2d',{alpha:false}),T=32;
let filaImagem=Promise.resolve();
// Limita a abertura simultânea de arquivos, inclusive nos servidores locais.
const imagem=nome=>{if(!nome)return Promise.resolve(null);const p=filaImagem.then(async()=>{const im=new Image();im.src='assets/'+nome.split('/').map(encodeURIComponent).join('/');try{await im.decode();}catch(e){throw Error('Não foi possível abrir a imagem: '+nome,{cause:e});}return im;});filaImagem=p.catch(()=>{});return p;};
const padroes=await fetch('data/autotiles.json').then(r=>r.json());
let mapa,atlas,autos,personagens=new Map(),jogador={x:0,y:0,dir:2},passo=null,direcao=0,tempo=0,anterior=performance.now(),carregando=false;
// Figurino de Kanto do próprio Fire Ash para a prévia; o jogo completo deverá
// resolver o figurino a partir do estado da história, inclusive nas trocas.
const avatar=await imagem('Characters/trchar000_1.png');
const vetores={2:[0,1],4:[-1,0],6:[1,0],8:[0,-1]},bits={2:1,4:2,6:4,8:8};
function tile(x,y,z){return mapa.camadas[x+y*mapa.largura+z*mapa.largura*mapa.altura]??0;}
function permite(x,y,dir){
 if(x<0||y<0||x>=mapa.largura||y>=mapa.altura)return false;
 for(let z=2;z>=0;z--){const id=tile(x,y,z);if(!id)continue;const p=mapa.passagens[id]??15;if(p&bits[dir])return false;if((mapa.prioridades[id]??0)===0)return true;}
 return true;
}
function livre(x,y,dir){const v=vetores[dir];return permite(x,y,dir)&&permite(x+v[0],y+v[1],10-dir);}
async function carregar(id){
 carregando=true;document.getElementById('estado').hidden=false;
 try{
  mapa=await fetch('data/mapa-'+id+'.json').then(r=>{if(!r.ok)throw Error('Área indisponível');return r.json();});
  [atlas,autos]=await Promise.all([Promise.all(Object.entries(mapa.assets.tileset).map(async([id,nome])=>[Number(id),await imagem(nome)])).then(a=>new Map(a)),Promise.all(mapa.assets.autotiles.map(imagem))]);
  personagens.clear();await Promise.all(mapa.eventosVisuais.map(async e=>personagens.set(e.id,await imagem(e.grafico))));
  const inicio=id===33?[19,32]:id===5?[18,20]:[7,6];jogador={x:inicio[0],y:inicio[1],dir:2};passo=null;direcao=0;
  document.querySelector('select').value=String(id);document.getElementById('nome').textContent=mapa.nome.replace('\\PN', 'Ash');document.getElementById('estado').hidden=true;
 }catch(e){document.getElementById('estado').textContent=e.message;throw e;}finally{carregando=false;}
}
function desenharTile(id,x,y){
 if(id<48)return;
 if(id>=384){const k=id-384;ctx.drawImage(atlas.get(Math.floor(k/128)),k%8*T,Math.floor(k/8)%16*T,T,T,x,y,T,T);return;}
 const a=autos[Math.floor(id/48)-1];if(!a)return;
 const quadro=Math.floor(tempo*4)%Math.max(1,Math.floor(a.width/96));
 if(a.height===32){ctx.drawImage(a,Math.floor(tempo*4)%Math.max(1,a.width/32)*32,0,32,32,x,y,32,32);return;}
 const p=padroes[id%48];for(let i=0;i<4;i++){const k=p[i]-1;ctx.drawImage(a,quadro*96+k%6*16,Math.floor(k/6)*16,16,16,x+i%2*16,y+Math.floor(i/2)*16,16,16);}
}
function corpo(im,x,y,dir,quadro=0,opacidade=255){const w=im.width/4,h=im.height/4;ctx.globalAlpha=opacidade/255;ctx.drawImage(im,quadro%4*w,(dir/2-1)*h,w,h,x+16-w/2,y+32-h,w,h);ctx.globalAlpha=1;}
function quadro(agora){
 const dt=Math.min(.05,(agora-anterior)/1000);anterior=agora;tempo+=dt;
 const dpr=Math.min(2,devicePixelRatio||1),w=innerWidth,h=innerHeight;
 if(cv.width!==Math.round(w*dpr)||cv.height!==Math.round(h*dpr)){cv.width=Math.round(w*dpr);cv.height=Math.round(h*dpr);}
 ctx.setTransform(dpr,0,0,dpr,0,0);ctx.fillStyle='#14252d';ctx.fillRect(0,0,w,h);
 if(mapa&&!carregando){
  if(!passo&&direcao){jogador.dir=direcao;if(livre(jogador.x,jogador.y,direcao)){const v=vetores[direcao];passo={x:jogador.x,y:jogador.y,tx:jogador.x+v[0],ty:jogador.y+v[1],t:0};}}
  if(passo){passo.t=Math.min(1,passo.t+dt/.16);jogador.x=passo.x+(passo.tx-passo.x)*passo.t;jogador.y=passo.y+(passo.ty-passo.y)*passo.t;if(passo.t===1){jogador.x=passo.tx;jogador.y=passo.ty;passo=null;}}
  const zoom=2,larg=w/zoom,alt=h/zoom,cx=Math.max(larg/2,Math.min(mapa.largura*T-larg/2,jogador.x*T+16)),cy=Math.max(alt/2,Math.min(mapa.altura*T-alt/2,jogador.y*T+16));
  ctx.scale(zoom,zoom);ctx.translate(Math.round(larg/2-cx),Math.round(alt/2-cy));ctx.imageSmoothingEnabled=false;
  const itens=[],x0=Math.max(0,Math.floor((cx-larg/2)/T)-2),y0=Math.max(0,Math.floor((cy-alt/2)/T)-5),x1=Math.min(mapa.largura,Math.ceil((cx+larg/2)/T)+2),y1=Math.min(mapa.altura,Math.ceil((cy+alt/2)/T)+2);
  for(let y=y0;y<y1;y++)for(let x=x0;x<x1;x++)for(let z=0;z<3;z++){const id=tile(x,y,z),p=mapa.prioridades[id]??0;if(p)itens.push({y:(y+p)*T,z,desenhar:()=>desenharTile(id,x*T,y*T)});else desenharTile(id,x*T,y*T);}
  for(const e of mapa.eventosVisuais){const im=personagens.get(e.id);if(im)itens.push({y:(e.y+1)*T,z:1,desenhar:()=>corpo(im,e.x*T,e.y*T,e.direcao,e.quadro,e.opacidade)});}
  itens.push({y:(jogador.y+1)*T,z:1,desenhar:()=>corpo(avatar,jogador.x*T,jogador.y*T,jogador.dir,passo?Math.floor(tempo*8)%4:0)});
  itens.sort((a,b)=>a.y-b.y||a.z-b.z);for(const i of itens)i.desenhar();
 }
 requestAnimationFrame(quadro);
}
document.querySelector('select').onchange=e=>carregar(Number(e.target.value));
const teclas={ArrowDown:2,ArrowLeft:4,ArrowRight:6,ArrowUp:8,KeyS:2,KeyA:4,KeyD:6,KeyW:8};
addEventListener('keydown',e=>{if(teclas[e.code]){e.preventDefault();direcao=teclas[e.code];}});addEventListener('keyup',e=>{if(teclas[e.code]===direcao)direcao=0;});addEventListener('blur',()=>direcao=0);
for(const b of document.querySelectorAll('button[data-dir]')){b.onpointerdown=e=>{e.preventDefault();b.setPointerCapture(e.pointerId);direcao=Number(b.dataset.dir);};b.onpointerup=b.onpointercancel=()=>direcao=0;}
window.fireAshTeste={get mapa(){return mapa;},get jogador(){return jogador;},permite,carregar};
await carregar(33);requestAnimationFrame(quadro);
