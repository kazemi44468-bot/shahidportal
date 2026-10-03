const MONTHS=["فروردین","اردیبهشت","خرداد","تیر","مرداد","شهریور","مهر","آبان","آذر","دی","بهمن","اسفند"];
const WEEK=["شنبه","یکشنبه","دوشنبه","سه‌شنبه","چهارشنبه","پنجشنبه","جمعه"];
const events=[
 {date:"۱۳۵۹/۰۶/۳۱",type:"واقعه",title:"آغاز جنگ تحمیلی",desc:"آغاز جنگ ایران و عراق و شروع دوره‌ای مهم در تاریخ دفاع مقدس.",tags:"جنگ دفاع مقدس عراق ایران"},
 {date:"۱۳۶۰/۰۳/۳۱",type:"شهادت",title:"شهادت دکتر مصطفی چمران",desc:"شهادت مصطفی چمران در دهلاویه.",tags:"مصطفی چمران دهلاویه شهید"},
 {date:"۱۳۶۱/۰۳/۰۳",type:"عملیات",title:"آزادسازی خرمشهر",desc:"پایان عملیات بیت‌المقدس و آزادسازی خرمشهر.",tags:"بیت المقدس خرمشهر عملیات"},
 {date:"۱۳۶۴/۱۱/۲۰",type:"عملیات",title:"آغاز عملیات والفجر ۸",desc:"آغاز عملیات والفجر ۸ در منطقه فاو.",tags:"والفجر ۸ فاو عملیات"},
 {date:"۱۳۶۵/۱۰/۱۹",type:"عملیات",title:"آغاز عملیات کربلای ۵",desc:"آغاز عملیات کربلای ۵ در منطقه شلمچه.",tags:"کربلای ۵ شلمچه عملیات"}
];
const $=id=>document.getElementById(id);
const fa=n=>String(n).replace(/\d/g,x=>"۰۱۲۳۴۵۶۷۸۹"[x]);
const en=n=>String(n).replace(/[۰-۹]/g,x=>"۰۱۲۳۴۵۶۷۸۹".indexOf(x));
const key=(y,m,d)=>y+"/"+String(m).padStart(2,"0")+"/"+String(d).padStart(2,"0");
const partFormatter=new Intl.DateTimeFormat("en-US-u-ca-persian",{timeZone:"Asia/Tehran",year:"numeric",month:"numeric",day:"numeric"});
const cache=new Map();
let todayJ=null,state={y:1405,m:7,d:1};

function parts(date){const p={};partFormatter.formatToParts(date).forEach(x=>{if(x.type==="year"||x.type==="month"||x.type==="day")p[x.type]=Number(x.value)});return p}
function currentJ(){const p=parts(new Date());return {y:p.year,m:p.month,d:p.day}}
function gregForJ(y,m,d){
 const ck=y+"-"+m+"-1";
 if(!cache.has(ck)){
  const approx=Date.UTC(y+621,2,20,12),found=null;
  let f=null;
  for(let i=-380;i<=380;i++){const g=new Date(approx+i*86400000),p=parts(g);if(p.year===y&&p.month===m&&p.day===1){f=g;break}}
  if(!f)throw new Error("Jalali date not found");
  cache.set(ck,f)
 }
 return new Date(cache.get(ck).getTime()+(d-1)*86400000)
}
function daysInMonth(y,m){const a=gregForJ(y,m,1),b=m===12?gregForJ(y+1,1,1):gregForJ(y,m+1,1);return Math.round((b-a)/86400000)}
function weekIndex(g){return (g.getUTCDay()+1)%7}
function eventDate(e){const a=e.date.split("/").map(Number);return key(a[0],a[1],a[2])}
function eventsFor(y,m,d){const k=key(y,m,d);return events.filter(e=>eventDate(e)===k)}
function displayDate(y,m,d){return fa(d)+" "+MONTHS[m-1]+" "+fa(y)}
function selectDate(y,m,d,redraw=true){if(y<1300)return;state={y:y,m:m,d:d};if(redraw)draw()}
function draw(){$("mt").textContent=MONTHS[state.m-1]+" "+fa(state.y);drawMonth();drawWeek();drawYear();renderToday()}
function drawMonth(){
 let html=WEEK.map(x=>'<div class="wd">'+x+"</div>").join("");
 const first=gregForJ(state.y,state.m,1),off=weekIndex(first),len=daysInMonth(state.y,state.m);
 for(let i=0;i<off;i++)html+='<div class="blank"></div>';
 for(let d=1;d<=len;d++){
  const es=eventsFor(state.y,state.m,d),sel=d===state.d;
  html+='<button class="day '+(sel?"sel":"")+'" data-day="'+d+'" aria-label="'+displayDate(state.y,state.m,d)+'"><em>'+fa(d)+"</em>"+(es.length?'<div class="dots">'+es.slice(0,3).map(e=>'<i title="'+e.title+'"></i>').join("")+"</div><small>"+fa(es.length)+" رویداد</small>":"")+"</button>"
 }
 $("grid").innerHTML=html;
 document.querySelectorAll("#grid .day").forEach(b=>b.onclick=()=>selectDate(state.y,state.m,Number(b.dataset.day)));
 renderDayDetails("dayDetails",state.y,state.m,state.d)
}
function drawWeek(){
 const selected=gregForJ(state.y,state.m,state.d),start=new Date(selected.getTime()-weekIndex(selected)*86400000);
 let html="";
 for(let i=0;i<7;i++){
  const g=new Date(start.getTime()+i*86400000),p=parts(g),es=eventsFor(p.year,p.month,p.day);
  html+='<button class="weekDay '+(p.year===state.y&&p.month===state.m&&p.day===state.d?"sel":"")+'" data-y="'+p.year+'" data-m="'+p.month+'" data-d="'+p.day+'"><b>'+WEEK[i]+"</b><strong>"+fa(p.day)+"</strong><span>"+MONTHS[p.month-1]+"</span>"+(es.length?'<em>'+fa(es.length)+" رویداد</em>":"")+"</button>"
 }
 $("weekGrid").innerHTML=html;
 document.querySelectorAll("#weekGrid .weekDay").forEach(b=>b.onclick=()=>selectDate(Number(b.dataset.y),Number(b.dataset.m),Number(b.dataset.d)));
 renderDayDetails("weekDetails",state.y,state.m,state.d)
}
function drawYear(){
 let html="";
 for(let m=1;m<=12;m++){
  const len=daysInMonth(state.y,m),first=gregForJ(state.y,m,1),off=weekIndex(first);
  let mini="";
  for(let i=0;i<off;i++)mini+='<span class="empty"></span>';
  for(let d=1;d<=len;d++){const es=eventsFor(state.y,m,d);mini+='<button class="'+(es.length?"has":"")+(m===state.m&&d===state.d?" sel":"")+'" data-m="'+m+'" data-d="'+d+'" title="'+(es.length?es.map(e=>e.title).join("،"):"")+'">'+fa(d)+"</button>"}
  html+='<article class="mc '+(m===state.m?"active":"")+'"><button class="mcTitle" data-month="'+m+'"><b>'+MONTHS[m-1]+'</b><span>'+fa(len)+" روز</span></button><div class="mini">"+mini+"</div></article>"
 }
 $("yearView").innerHTML=html;
 document.querySelectorAll(".mcTitle").forEach(b=>b.onclick=()=>{state.m=Number(b.dataset.month);state.d=Math.min(state.d,daysInMonth(state.y,state.m));setView("month");draw()});
 document.querySelectorAll(".mini button").forEach(b=>b.onclick=()=>{state.m=Number(b.dataset.m);state.d=Number(b.dataset.d);setView("month");draw()})
}
function renderDayDetails(id,y,m,d){
 const box=$(id),es=eventsFor(y,m,d);
 box.innerHTML='<div class="detailHead"><div><span>تاریخ انتخاب‌شده</span><strong>'+displayDate(y,m,d)+'</strong></div><span class="countBadge">'+fa(es.length)+" رویداد</span></div>"+(es.length?'<div class="detailList">'+es.map(eventCard).join("")+'</div>':'<div class="emptyState">برای این روز هنوز رویدادی در داده‌های تقویم ثبت نشده است.</div>')
}
function eventCard(e){return '<article class="detailEvent"><span class="eventType">'+e.type+"</span><strong>"+e.title+"</strong><p>"+e.desc+"</p><small>"+e.tags+"</small></article>"}
function renderToday(){
 todayJ=todayJ||currentJ();
 $("todayDate").textContent=displayDate(todayJ.y,todayJ.m,todayJ.d);
 const es=eventsFor(todayJ.y,todayJ.m,todayJ.d);
 $("todaySummary").textContent=es.length?fa(es.length)+" رویداد مرتبط با امروز ثبت شده است.":"برای امروز هنوز رویداد ثبت‌شده‌ای در داده‌های محلی تقویم وجود ندارد.";
 $("todayEvents").innerHTML=es.length?es.slice(0,4).map(eventCard).join(""):'<article class="emptyEvent"><strong>رویدادی برای امروز ثبت نشده است</strong><small>با تکمیل بانک رویدادها، اطلاعات این بخش به‌صورت خودکار نمایش داده می‌شود.</small></article>'
}
function moveMonth(delta){let m=state.m+delta,y=state.y;if(m<1){m=12;y--}else if(m>12){m=1;y++}if(y<1300)return;state.y=y;state.m=m;state.d=Math.min(state.d,daysInMonth(y,m));draw()}
function goToday(){state={y:todayJ.y,m:todayJ.m,d:todayJ.d};draw()}
function setView(v){document.querySelectorAll(".tabs button").forEach(b=>b.classList.toggle("on",b.dataset.v===v));$("monthView").hidden=v!=="month";$("weekView").hidden=v!=="week";$("yearView").hidden=v!=="year"}
function search(){
 const q=en($("q").value.trim()).toLowerCase(),kind=$("kind").value;
 if(!q&&!kind){$("resultsBox").hidden=true;return}
 const dateMatch=q.match(/^(\d{4})[\/\-.](\d{1,2})[\/\-.](\d{1,2})$/);
 if(dateMatch){const y=Number(dateMatch[1]),m=Number(dateMatch[2]),d=Number(dateMatch[3]);if(y>=1300&&m>=1&&m<=12&&d>=1&&d<=daysInMonth(y,m)){state={y:y,m:m,d:d};setView("month");draw()}}
 const list=events.filter(e=>{const text=[e.title,e.desc,e.tags,e.type,e.date].join(" ").toLowerCase();return (!q||text.includes(q))&&(!kind||e.type===kind)});
 $("resultsBox").hidden=false;$("resultsCount").textContent=fa(list.length)+" نتیجه";
 $("searchResults").innerHTML=list.length?list.map((e,i)=>'<button class="resultItem" data-i="'+i+'"><span>'+e.type+'</span><div><strong>'+e.title+'</strong><small>'+e.date+" · "+e.desc+"</small></div></button>").join(""):'<div class="emptyState">نتیجه‌ای برای جست‌وجوی شما پیدا نشد.</div>';
 document.querySelectorAll(".resultItem").forEach((b,i)=>b.onclick=()=>{const e=list[i],a=e.date.split("/").map(Number);state={y:a[0],m:a[1],d:a[2]};setView("month");draw();$("calendar").scrollIntoView({behavior:"smooth",block:"start"})})
}
function clearSearch(){$("q").value="";$("kind").value="";$("resultsBox").hidden=true}
function init(){
 todayJ=currentJ();state={y:todayJ.y,m:todayJ.m,d:todayJ.d};
 $("prev").onclick=()=>moveMonth(-1);$("next").onclick=()=>moveMonth(1);$("goToday").onclick=goToday;
 $("searchBtn").onclick=search;$("clearSearch").onclick=clearSearch;$("q").addEventListener("keydown",e=>{if(e.key==="Enter")search()});
 document.querySelectorAll(".tabs button").forEach(b=>b.onclick=()=>{setView(b.dataset.v);draw()});
 $("hamb").onclick=()=>document.querySelector(".nav").classList.toggle("mobileOpen");
 draw()
}
init();