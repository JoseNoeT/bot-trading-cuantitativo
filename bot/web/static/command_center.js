"use strict";
const symbols=["WLDUSDT","BTCUSDT","ETHUSDT"];
const fmt=(v,d=2)=>Number.isFinite(Number(v))?Number(v).toLocaleString("es-CL",{maximumFractionDigits:d}):"—";
const fields=Object.fromEntries(symbols.map(s=>[s,document.querySelector('[data-symbol="'+s+'"]')]));
function write(s,k,value){fields[s].querySelector('[data-field="'+k+'"]').textContent=String(value);}
function selectView(id){document.querySelectorAll(".view").forEach(v=>v.classList.toggle("active",v.id===id));document.querySelectorAll(".nav").forEach(n=>n.classList.toggle("active",n.dataset.tab===id));}
document.querySelectorAll(".nav").forEach(b=>b.addEventListener("click",()=>selectView(b.dataset.tab)));
async function asset(symbol){
 write(symbol,"status","Consultando");
 try{
  const response=await fetch("/intelligence/"+symbol,{cache:"no-store"});
  const data=await response.json();
  if(!response.ok)throw Error(String(data.detail||"HTTP "+response.status));
  write(symbol,"status",data.status==="SETUP_DETECTED"?"Pre-señal":"En espera");
  write(symbol,"price",fmt(data.last_close,6)+" USDT");
  write(symbol,"source","Cierre 1m · "+new Date(data.last_close_time*1000).toLocaleTimeString("es-CL"));
  write(symbol,"trend",data.trend);write(symbol,"rsi",fmt(data.rsi14));
  write(symbol,"ema",fmt(data.ema20,5)+" / "+fmt(data.ema50,5));
  write(symbol,"atr",fmt(data.atr14,6));
  write(symbol,"reason",(data.reason||[]).join("; ")+" · NO OPERAR: riesgo sin verificar.");
 }catch(err){
  write(symbol,"status","Sin datos");write(symbol,"price","—");
  write(symbol,"source","Sin datos verificados");
  for(const k of ["trend","rsi","ema","atr"])write(symbol,k,"—");
  write(symbol,"reason",String(err.message||err)+" · NO OPERAR.");
 }
}
async function contextWld(){
 const node=document.getElementById("frames"),message=document.getElementById("context");
 try{
  const response=await fetch("/intelligence/WLDUSDT/multi",{cache:"no-store"});
  const data=await response.json();
  if(!response.ok)throw Error(String(data.detail||"HTTP "+response.status));
  node.replaceChildren();
  for(const tf of ["1d","4h","1h","15m"]){
   const x=data.timeframes[tf],card=document.createElement("div");card.className="frame";
   const label=document.createElement("small");label.textContent=tf.toUpperCase();
   const trend=document.createElement("strong");trend.className=x.trend==="alcista"?"up":x.trend==="bajista"?"down":"neutral";trend.textContent=x.trend;
   const price=document.createElement("small");price.textContent=fmt(x.close,6)+" USDT";
   const rsi=document.createElement("small");rsi.textContent="RSI "+fmt(x.rsi14);
   card.append(label,trend,price,rsi);node.append(card);
  }
  message.textContent=data.context+": "+data.explanation+" · NO OPERAR.";
 }catch(err){node.textContent="Contexto no disponible.";message.textContent=String(err.message||err)+" · NO OPERAR.";}
}
async function radarWld(){
 const node=document.getElementById("radar");
 try{
  const r=await fetch("/radar/WLDUSDT",{cache:"no-store"}),data=await r.json();
  if(!r.ok)throw Error(String(data.detail||"HTTP "+r.status));
  node.replaceChildren();
  const level=document.createElement("strong");level.className=data.level==="high"?"down":"neutral";level.textContent="Actividad observada: "+String(data.level).toUpperCase();
  const ratio=document.createElement("p");ratio.textContent="Volumen relativo 1m: "+(data.volume_relative==null?"Sin base":fmt(data.volume_relative,2)+"×");
  const flags=document.createElement("p");const keys=Object.entries(data.flags).filter(x=>x[1]).map(x=>x[0]);flags.textContent=keys.length?"Patrones: "+keys.join(", "):"Sin anomalías de vela destacables";
  const warning=document.createElement("p");warning.className="hint";warning.textContent="Ballena confirmada: NO. "+data.limitations;
  node.append(level,ratio,flags,warning);
 }catch(err){node.textContent="Radar sin datos verificados: "+String(err.message||err);}
}
function refreshAll(){symbols.forEach(asset);contextWld();radarWld();}
document.getElementById("refresh").addEventListener("click",refreshAll);refreshAll();setInterval(refreshAll,60000);
fetch("/source").then(r=>r.json()).then(data=>{document.getElementById("source").textContent="Fuente: "+String(data.data_source).toUpperCase();}).catch(()=>{document.getElementById("source").textContent="Fuente no verificada";});
const feed=document.getElementById("feed");let count=0;
const socket=new WebSocket((location.protocol==="https:"?"wss://":"ws://")+location.host+"/ws/signals");
socket.addEventListener("open",()=>{document.getElementById("socket").textContent="WebSocket conectado";});
socket.addEventListener("close",()=>{document.getElementById("socket").textContent="WebSocket desconectado";});
socket.addEventListener("message",ev=>{
 try{
  const v=JSON.parse(ev.data);
  if(!symbols.includes(v.symbol)||!Number.isFinite(Number(v.price))||Number(v.price)<=0)return;
  if(feed.querySelector(".empty"))feed.replaceChildren();
  const row=document.createElement("div");row.className="trade";
  for(const txt of [v.symbol,fmt(v.price,6)+" USDT",fmt(v.volume,8)+" unidades",new Date(Number(v.ts)*1000).toLocaleTimeString("es-CL")]){
    const span=document.createElement("span");span.textContent=txt;row.append(span);
  }
  feed.prepend(row);while(feed.children.length>30)feed.lastChild.remove();
  count++;document.getElementById("live-count").textContent=count+" eventos";
 }catch(e){console.warn("Evento inválido",e);}
});
setInterval(()=>{if(socket.readyState===WebSocket.OPEN)socket.send("ping");},20000);
