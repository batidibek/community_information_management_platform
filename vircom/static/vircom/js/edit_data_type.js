var field;
function fields() {
    
    field++;
    var objTo = document.getElementById('fields')
    var divtest = document.createElement("div");
	divtest.setAttribute("class", "form-group removeclass"+field);
	var rdiv = 'removeclass'+field;
    divtest.innerHTML = '<div class="row" style="width: 1000px"><div class="col-sm-3 nopadding"><div class="form-group"><label for="InputName">Field Name</label><input type="text" class="form-control" id="InputName" aria-describedby="fieldName"placeholder="Enter field name" name="name"></div></div><div class="col-sm-3 nopadding"><div class="form-group"><label for="FormControlType">Type</label><select class="form-control" id="FormControlSelectType" name="type"><option>Text</option><option>Long Text</option><option>Integer</option><option>Decimal Number</option></select></div></div><div class="col-sm-3 nopadding"><div class="input-group"><div class="form-group"><label for="FormControlRequired">Required Field?</label><select class="form-control" id="FormControlSelectRequired" name="required"><option>Yes</option><option>No</option></select></div><div class="input-group-btn" style="top: 13px;"><label for="FormControlRemoveField"> </label><button class="btn btn-danger" type="button" onclick="remove_fields('+ field +');"> <span class="glyphicon glyphicon-minus" aria-hidden="true"></span> </button></div></div></div></div>';
    
    objTo.appendChild(divtest)
}
   function remove_fields(rid) {
       field--;
	   $('.removeclass'+rid).remove();
   }


  