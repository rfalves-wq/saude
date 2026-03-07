/* auto atualizar */
setInterval(function(){
location.reload();
},8000);


/* alerta sonoro */
document.addEventListener("DOMContentLoaded",function(){

let vermelho=document.querySelector(".alerta-vermelho");

if(vermelho){

setTimeout(function(){

let audio=new Audio("https://www.soundjay.com/buttons/sounds/beep-07.mp3");
audio.play().catch(()=>{});

},500);

}

});