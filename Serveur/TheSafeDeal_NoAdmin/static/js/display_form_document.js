function display_form(file_key) 
{
	document.getElementById(file_key).style.display='block'
	var modal = document.getElementById(file_key);

	window.onclick = function(event) {
    	if (event.target == modal) {
        	modal.style.display = "none";
    	}
	}
}