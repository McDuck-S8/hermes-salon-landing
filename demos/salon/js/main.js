document.addEventListener("DOMContentLoaded",()=>{
const t=document.querySelector(".nav-toggle"),n=document.querySelector(".nav");
t&&n&&t.addEventListener("click",()=>n.classList.toggle("active"));
document.querySelectorAll('a[href^="#"]').forEach(a=>{a.addEventListener("click",e=>{e.preventDefault();const t=document.querySelector(a.getAttribute("href"));t&&t.scrollIntoView({behavior:"smooth"})})});
const h=document.querySelector(".header");window.addEventListener("scroll",()=>{h.classList.toggle("scrolled",window.scrollY>50)})
});