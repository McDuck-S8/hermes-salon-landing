import{a4 as v,a7 as M,aG as j,g as q,s as H,a as Y,b as Z,q as J,p as K,_ as u,l as _,c as Q,D as X,H as ee,N as te,e as ae,y as ne,E as re}from"./mermaid.core-owQLcZlc.js";import{p as ie}from"./chunk-4BX2VUAB-CtB6IS6S.js";import{p as se}from"./treemap-KMMF4GRG-AHi7G9rQ.js";import{d as L}from"./arc-CQEvJj0t.js";import{o as oe}from"./ordinal-BAJfh0Ze.js";import"./mermaid-VLURNSYL-BCsSiObj.js";import"./_baseUniq-BrOxIbAm.js";import"./_basePickBy-BYaD2163.js";import"./clone-D602xINV.js";import"./init-CB8r1oEK.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof globalThis<"u"?globalThis:typeof self<"u"?self:{};e.SENTRY_RELEASE={id:"b5bbbe1aff65d1bc6263114033a92e0f9fa61a35"}}catch{}})();try{(function(){var e=typeof window<"u"?window:typeof global<"u"?global:typeof globalThis<"u"?globalThis:typeof self<"u"?self:{},a=new e.Error().stack;a&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[a]="5d020009-8a37-4a16-a0bc-524cf1e19d5e",e._sentryDebugIdIdentifier="sentry-dbid-5d020009-8a37-4a16-a0bc-524cf1e19d5e")})()}catch{}function le(e,a){return a<e?-1:a>e?1:a>=e?0:NaN}function ce(e){return e}function de(){var e=ce,a=le,g=null,w=v(0),s=v(M),l=v(0);function o(t){var r,c=(t=j(t)).length,p,S,m=0,d=new Array(c),i=new Array(c),y=+w.apply(this,arguments),b=Math.min(M,Math.max(-M,s.apply(this,arguments)-y)),h,A=Math.min(Math.abs(b)/c,l.apply(this,arguments)),T=A*(b<0?-1:1),f;for(r=0;r<c;++r)(f=i[d[r]=r]=+e(t[r],r,t))>0&&(m+=f);for(a!=null?d.sort(function(x,D){return a(i[x],i[D])}):g!=null&&d.sort(function(x,D){return g(t[x],t[D])}),r=0,S=m?(b-c*T)/m:0;r<c;++r,y=h)p=d[r],f=i[p],h=y+(f>0?f*S:0)+T,i[p]={data:t[p],index:r,value:f,startAngle:y,endAngle:h,padAngle:A};return i}return o.value=function(t){return arguments.length?(e=typeof t=="function"?t:v(+t),o):e},o.sortValues=function(t){return arguments.length?(a=t,g=null,o):a},o.sort=function(t){return arguments.length?(g=t,a=null,o):g},o.startAngle=function(t){return arguments.length?(w=typeof t=="function"?t:v(+t),o):w},o.endAngle=function(t){return arguments.length?(s=typeof t=="function"?t:v(+t),o):s},o.padAngle=function(t){return arguments.length?(l=typeof t=="function"?t:v(+t),o):l},o}var ue=re.pie,N={sections:new Map,showData:!1},C=N.sections,z=N.showData,pe=structuredClone(ue),fe=u(()=>structuredClone(pe),"getConfig"),ge=u(()=>{C=new Map,z=N.showData,ne()},"clear"),he=u(({label:e,value:a})=>{if(a<0)throw new Error(`"${e}" has invalid value: ${a}. Negative values are not allowed in pie charts. All slice values must be >= 0.`);C.has(e)||(C.set(e,a),_.debug(`added new section: ${e}, with value: ${a}`))},"addSection"),me=u(()=>C,"getSections"),ye=u(e=>{z=e},"setShowData"),ve=u(()=>z,"getShowData"),O={getConfig:fe,clear:ge,setDiagramTitle:K,getDiagramTitle:J,setAccTitle:Z,getAccTitle:Y,setAccDescription:H,getAccDescription:q,addSection:he,getSections:me,setShowData:ye,getShowData:ve},we=u((e,a)=>{ie(e,a),a.setShowData(e.showData),e.sections.map(a.addSection)},"populateDb"),Se={parse:u(async e=>{const a=await se("pie",e);_.debug(a),we(a,O)},"parse")},be=u(e=>`
  .pieCircle{
    stroke: ${e.pieStrokeColor};
    stroke-width : ${e.pieStrokeWidth};
    opacity : ${e.pieOpacity};
  }
  .pieOuterCircle{
    stroke: ${e.pieOuterStrokeColor};
    stroke-width: ${e.pieOuterStrokeWidth};
    fill: none;
  }
  .pieTitleText {
    text-anchor: middle;
    font-size: ${e.pieTitleTextSize};
    fill: ${e.pieTitleTextColor};
    font-family: ${e.fontFamily};
  }
  .slice {
    font-family: ${e.fontFamily};
    fill: ${e.pieSectionTextColor};
    font-size:${e.pieSectionTextSize};
    // fill: white;
  }
  .legend text {
    fill: ${e.pieLegendTextColor};
    font-family: ${e.fontFamily};
    font-size: ${e.pieLegendTextSize};
  }
`,"getStyles"),xe=be,De=u(e=>{const a=[...e.values()].reduce((s,l)=>s+l,0),g=[...e.entries()].map(([s,l])=>({label:s,value:l})).filter(s=>s.value/a*100>=1).sort((s,l)=>l.value-s.value);return de().value(s=>s.value)(g)},"createPieArcs"),Ae=u((e,a,g,w)=>{_.debug(`rendering pie chart
`+e);const s=w.db,l=Q(),o=X(s.getConfig(),l.pie),t=40,r=18,c=4,p=450,S=p,m=ee(a),d=m.append("g");d.attr("transform","translate("+S/2+","+p/2+")");const{themeVariables:i}=l;let[y]=te(i.pieOuterStrokeWidth);y??=2;const b=o.textPosition,h=Math.min(S,p)/2-t,A=L().innerRadius(0).outerRadius(h),T=L().innerRadius(h*b).outerRadius(h*b);d.append("circle").attr("cx",0).attr("cy",0).attr("r",h+y/2).attr("class","pieOuterCircle");const f=s.getSections(),x=De(f),D=[i.pie1,i.pie2,i.pie3,i.pie4,i.pie5,i.pie6,i.pie7,i.pie8,i.pie9,i.pie10,i.pie11,i.pie12];let $=0;f.forEach(n=>{$+=n});const F=x.filter(n=>(n.data.value/$*100).toFixed(0)!=="0"),E=oe(D);d.selectAll("mySlices").data(F).enter().append("path").attr("d",A).attr("fill",n=>E(n.data.label)).attr("class","pieCircle"),d.selectAll("mySlices").data(F).enter().append("text").text(n=>(n.data.value/$*100).toFixed(0)+"%").attr("transform",n=>"translate("+T.centroid(n)+")").style("text-anchor","middle").attr("class","slice"),d.append("text").text(s.getDiagramTitle()).attr("x",0).attr("y",-400/2).attr("class","pieTitleText");const G=[...f.entries()].map(([n,I])=>({label:n,value:I})),k=d.selectAll(".legend").data(G).enter().append("g").attr("class","legend").attr("transform",(n,I)=>{const W=r+c,B=W*G.length/2,V=12*r,U=I*W-B;return"translate("+V+","+U+")"});k.append("rect").attr("width",r).attr("height",r).style("fill",n=>E(n.label)).style("stroke",n=>E(n.label)),k.append("text").attr("x",r+c).attr("y",r-c).text(n=>s.getShowData()?`${n.label} [${n.value}]`:n.label);const P=Math.max(...k.selectAll("text").nodes().map(n=>n?.getBoundingClientRect().width??0)),R=S+t+r+c+P;m.attr("viewBox",`0 0 ${R} ${p}`),ae(m,p,R,o.useMaxWidth)},"draw"),Te={draw:Ae},Ge={parser:Se,db:O,renderer:Te,styles:xe};export{Ge as diagram};
