window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};

// script used in availble dates form
  var dates = []; 
  document.getElementById("add").onclick = function(e){
  e.preventDefault();
  dates.push(document.getElementById("availble").value)
 	const p = document.createElement('p'); 
 	p.innerHTML = document.getElementById("availble").value 
  document.getElementById("availble_form").appendChild(p)
  document.getElementById("dates_form").value = dates
}