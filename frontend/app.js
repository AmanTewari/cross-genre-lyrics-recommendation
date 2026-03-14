document.addEventListener('DOMContentLoaded', function () {

var elems = document.querySelectorAll('.tabs');
M.Tabs.init(elems);

});


function recommendByTitle(){

let title = document.getElementById("songTitle").value.trim();

if(title === ""){

M.toast({html:"Please enter a song title"});
return;

}

let results = [

{title:"Shape of You",artist:"Ed Sheeran"},
{title:"Blinding Lights",artist:"The Weeknd"},
{title:"Levitating",artist:"Dua Lipa"},
{title:"Believer",artist:"Imagine Dragons"},
{title:"Stay",artist:"Justin Bieber"},
{title:"Perfect",artist:"Ed Sheeran"}

];

displayResults(results,"titleResults");

}


function recommendByLyrics(){

let lyrics = document.getElementById("lyricsInput").value.trim();

let wordCount = lyrics.split(/\s+/).length;

if(lyrics === ""){

M.toast({html:"Please paste lyrics"});
return;

}

if(wordCount < 20){

M.toast({html:"Please enter longer lyrics for analysis"});
return;

}

let results = [

{title:"Someone Like You",artist:"Adele"},
{title:"Fix You",artist:"Coldplay"},
{title:"Halo",artist:"Beyonce"},
{title:"Rolling in the Deep",artist:"Adele"},
{title:"Yellow",artist:"Coldplay"},
{title:"Let Her Go",artist:"Passenger"}

];

displayResults(results,"lyricsResults");

}


function displayResults(data,elementId){

let box = document.getElementById(elementId);

let html = "";

data.forEach(song=>{

html += `

<div class="songCard">

<div style="font-size:40px">🎵</div>

<div class="songTitle">${song.title}</div>

<div class="songArtist">${song.artist}</div>

</div>

`;

});

box.innerHTML = html;

}