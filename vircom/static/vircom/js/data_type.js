var field;
var option=0;
function fields() {
    
    field++;
    var objTo = document.getElementById('fields')
    var divtest = document.createElement("div");
	divtest.setAttribute("class", "form-group removeclass"+field);
	//var rdiv = 'removeclass'+field;
    divtest.innerHTML = '<div class="row" style="width: 1000px"><div class="col-sm-3 nopadding"><div class="form-group"> <label for="InputName">Field Name</label> <input type="text" class="form-control" id="InputName" aria-describedby="fieldName" placeholder="Enter field name" name="name"> </div> </div> <div class="col-sm-3 nopadding"> <div class="form-group"><label for="FormControlType">Type</label><select class="form-control" id="FormControlSelectType" name="type"> <option>Text</option> <option>Long Text</option> <option>Integer</option> <option>Decimal Number</option> <option>Date</option> <option>Time</option> <option>Image</option> <option>Video</option> <option>Audio</option> <option>Location</option> </select></div> </div> <div class="col-sm-2 nopadding" style="margin-bottom: 0;"> <div class="form-group form-check-inline" style="margin-top: 30px;"> <input type="checkbox" class="form-check-input" id="checkbox'+ field +'" style="width: 20px; height: 20px;" name="enumerated" value="No" onclick="enumeration('+ field +');"> <label class="form-check-label" for="enumeratedCheck" style="font-weight: normal; margin-bottom: 0;">Enumerated</label> </div> </div> <div class="col-sm-3 nopadding"> <div class="input-group"> <div class="form-group"><label for="FormControlRequired">Required Field?</label><select class="form-control" id="FormControlSelectRequired" name="required"> <option>Yes</option> <option>No</option> </select> </div> <div class="input-group-btn" style="top: 13px;"><label for="FormControlRemoveField"> </label><button class="btn btn-danger" type="button" onclick="remove_fields('+ field +');"> <span class="glyphicon glyphicon-minus" aria-hidden="true"></span> </button></div> </div> </div> <div id="optionsField'+ field +'" class="optionsField'+ field +'" style="width: 1000px"> </div> </div>';
    
    objTo.appendChild(divtest)
}
   function remove_fields(field_id) {
	   $('.removeclass'+field_id).remove();
   }

function addOption(field_id){
    option++;
    var objTo = document.getElementById('optionsField'+field_id);
    var divtest = document.createElement("div");
    divtest.setAttribute("class", "form-group option"+option);
    divtest.innerHTML = '<div style="width: 250px; margin-left: 50px;"><div class="input-group"><div class="form-group"><input type="text" class="form-control" id="InputOption" aria-describedby="option" placeholder="Enter an option" name="option'+ field_id +'"></div><div class="input-group-btn"><label for="FormControlRemoveField"></label><button class="btn btn-danger" type="button" onclick="removeOption('+ option +');"><span class="glyphicon glyphicon-minus" aria-hidden="true"></span> </button></div></div></div>';
    objTo.appendChild(divtest)
}   

function removeOption(option_id) {
    $('.option'+option_id).remove();
}

function enumeration(field_id){
    var checkbox = document.getElementById("checkbox"+field_id);

    if (checkbox.checked == true){
        $('#checkbox'+field_id).val(field_id);
        option++;
        var objTo = document.getElementById('optionsField'+field_id);
        var divtest = document.createElement("div");
        divtest.setAttribute("class", "form-group option"+option);
        divtest.innerHTML = '<div style="width: 250px; margin-left: 50px;"><div class="input-group"><div class="form-group"><input type="text" class="form-control" id="InputOption" aria-describedby="option" placeholder="Enter an option" name="option'+ field_id +'"></div><div class="input-group-btn"><label for="FormControlRemoveField"></label><button class="btn btn-success" type="button" onclick="addOption('+ field_id +');"><span class="glyphicon glyphicon-plus" aria-hidden="true"></span> </button></div></div></div>';
        objTo.appendChild(divtest)
    }
    else{
        $('#checkbox'+field_id).val("No");
        $('.optionsField'+field_id).empty();
    }    
}



  