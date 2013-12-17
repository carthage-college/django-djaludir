var MAX_CRITERIA = 5;
var criteria = 0;
var SELECT_VALUES = 'ids.firstname^First Name,ids.lastname^Last Name,alum.cl_yr^Class year,home_state^Home State,home_city^Home City,ids.id^ID Number,maiden.lastname^Maiden Name,activity^Activity/Sport,major1.txt^Primary Major,major2.txt^Secondary Major,job_title^Job Title';

function updateCriteria(){
    criteria = $('#formfieldset div.search').length;
    $('input[name="maxCriteria"]').val(criteria);
}

function createBlock(fieldName, searchTerm){
    if (fieldName === undefined || fieldName == null) fieldName = '';
    if (searchTerm === undefined || searchTerm == null) searchTerm = '';

    if(criteria < MAX_CRITERIA){
        var $divObj = $('<div>').addClass('form-row').addClass('search');
        $('<select>').attr('name','within' + criteria).appendTo($divObj);

        $('<span> contains </span>').appendTo($divObj);
        $('<input>').attr({'type':'text','name':'term' + criteria,'class':'medium'}).val(searchTerm).appendTo($divObj);

        if(criteria < MAX_CRITERIA - 1){
            $('<span>&nbsp;</span>').appendTo($divObj);
            $('<input>').attr({'type':'button','name':'add_search','class':'button'}).val('ADD').click(createBlock).appendTo($divObj);
        }

        $('#submitrow').before($divObj);
        clearSelect('select[name="within' + criteria + '"]');
        loadSelectKeyVal('select[name="within' + criteria + '"]', SELECT_VALUES, false);
        $('select[name="within' + criteria + '"]').val(fieldName);

        updateCriteria();

        if(criteria > 1){
            $('<input />').attr({'type':'button','class':'button','name':'delete','value':'DELETE'}).click(deleteBlock).appendTo($divObj);
        }
    }
}

function deleteBlock(){
    $(this).parent('.form-row').remove();
    var curRow = 1;
    $('#formfieldset div.search').each(function(){
        $(this).find('select[name^="within"]').attr('name','within' + curRow);
        $(this).find('input[name^="term"]').attr('name','term' + curRow);
        if($(this).find('input[name="add_search"]').length == 0){
            var $deleteObj = $(this).find('input[name="delete"]');
            $('<span>&nbsp;</span>').insertBefore($deleteObj);
            $('<input>').attr({'type':'button','name':'add_search','class':'button'}).val('ADD').click(createBlock).insertBefore($deleteObj);
        }
        curRow++;
    });
    updateCriteria();
}