$(document).ready(function () {
    //@naresh action dynamic childs
    var next = 0;
    $("#add-more").click(function(e){
        e.preventDefault();
        var addto = "#field" + next;
        var addRemove = "#field" + (next);
        next = next + 1;
        var newIn = ' <div id="field'+ next +'" name="field'+ next +'"><div class="form-group"><label for="InputName">Field Name</label><input type="text" class="form-control" id="InputName" aria-describedby="fieldName" placeholder="Enter field name" name="name" required><div class="invalid-feedback">You should enter a field name.</div></div><div class="form-group"> <label for="FormControlType">Type</label><select class="form-control" id="FormControlSelectType" name="type"><option>Text</option><option>Number</option></select></div><div class="form-group"><label for="FormControlRequired">Required Field?</label><select class="form-control" id="FormControlSelectRequired" name="required"><option>Yes</option><option>No</option></select></div>';
        var newInput = $(newIn);
        var removeBtn = '<button id="remove' + (next - 1) + '" class="btn btn-danger remove-me" >Remove</button></div></div><div id="field">';
        var removeButton = $(removeBtn);
        $(addto).after(newInput);
        $(addRemove).after(removeButton);
        $("#field" + next).attr('data-source',$(addto).attr('data-source'));
        $("#count").val(next);  
        
            $('.remove-me').click(function(e){
                e.preventDefault();
                var fieldNum = this.id.charAt(this.id.length-1);
                var fieldID = "#field" + fieldNum;
                $(this).remove();
                $(fieldID).remove();
            });
    });

});