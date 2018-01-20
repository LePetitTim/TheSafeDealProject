function display_form() 
{
	document.getElementById('id01').style.display='block'
	var modal = document.getElementById('id01');

	window.onclick = function(event) {
    	if (event.target == modal) {
        	modal.style.display = "none";
    	}
	}

}