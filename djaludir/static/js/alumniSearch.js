var MAX_CRITERIA = 5;
var criteria = 0;
var SELECT_VALUES = [
    'ids.firstname^First Name',
    'ids.lastname^Last Name',
    'alum.cl_yr^Class year',
    'ids.city^Home City',
    'ids.st^Home State',
    'ids.id^ID Number',
    'maiden.lastname^Maiden Name',
    'activity^Activity/Sport',
    'major1.txt^Primary Major',
    'major2.txt^Secondary Major',
    'job_title^Job Title',
].join(',');

$(document).ready(function(){
    // Initialize tablesorter plugin, disabling sort functionality
    // for "display" and "send message"
    $('#searchResults').tablesorter({
        headers: {
            3: { sorter:false },
            4: { sorter:false }
        }
    });

    // Before submitting the form, make sure that at least
    // one search field has data in it.
    // QUESTION: Should there be a minimum character limit (2-3 characters),
    // perhaps even as an aggregated calculation?
    $('form[name="searchForm"]').submit(function(){
        var hasData = false, errMsg = '';
        // Loop through the value of each row's search term
        $('#formfieldset div.search .looper').each(function(){
            // If the term is not an empty string
            if($(this).val().replace(/\s+/g,'') != ''){
                // hasData only needs to be true once for the form
                // to pass the hasData condition
                hasData = true;

                // Get the number of the current row
                index = $(this).attr('name').replace(/term/,'');

                // Access the value of the corresponding select box
                selectVal = $('select[name="within' + index + '"]').val();

                // If the user is searching either the Student ID
                // or the Class Year...
                // This is important because the logic in the search SQL
                // is different when dealing with numbers instead of strings
                if(selectVal == 'ids.id' || selectVal == 'alum.cl_yr'){

                    // Remove any whitespace in the search term
                    $(this).val($(this).val().replace(/\s+/g,''));

                    // If the term is not a number, generate an error message
                    if($(this).val().match(/^\d+$/) == null){
                        errMsg += $('select[name="within' + index + '"] option:selected').text() + ' must be a number\n';
                    }
                }
            }
        });
        // If no information was entered into any row's search term
        if(!hasData){
            alert('You must enter at least one search criteria.');
        }
        // If an error condition was met and a message was generated
        else if(errMsg.length > 0){
            alert(errMsg);
        }
        return hasData && errMsg.length == 0;
    })

    // Update the search criteria counter
    updateCriteria();

});

// Update the counter representing the number of rows of search criteria
function updateCriteria(){
    criteria = $('#formfieldset div.search').length;
    $('input[name="maxCriteria"]').val(criteria);
}

function buildStateField(name, value){
    selectField = '<select name="' + name + '" class="small looper">';
    for (var i = 0; i < STATES.length; i++) {
      if (value == STATES[i].abbreviation) {
        selected = ' selected'
      }else{
        selected = ''
      }
      option = '<option value="' + STATES[i].abbreviation + '"' + selected + '>';
      option += STATES[i].name + '</option>';
      selectField += option;
    }
    selectField += '</select>';
    return selectField
}

function createBlock(fieldName, searchTerm){
    // Default values for arguments
    if (fieldName === undefined || fieldName == null) fieldName = '';
    if (searchTerm === undefined || searchTerm == null) searchTerm = '';

    // Only create a new row if the total number of rows is less than
    // the number specified by MAX_CRITERIA
    if(criteria < MAX_CRITERIA){
        // Create row containing search fields
        var $divObj = $('<div>').addClass('form-row search');
        $('<select>').attr('name','within' + criteria).appendTo($divObj);

        $('<span> contains </span>').appendTo($divObj);

        // Create the "term" input box and, if a searchTerm argument
        // was specified, set the value of the box appropriately
        if (fieldName == 'ids.st') {
            field = buildStateField('term' + criteria, searchTerm);
            $divObj.append(field);
            //$("").val(searchTerm);
        } else {
            $('<input>').attr({'type':'text','name':'term' + criteria,'class':'medium looper'}).val(searchTerm).appendTo($divObj);
        }
        // If this is any row besides the last one,
        // append an "Add" button to the row
        if(criteria < MAX_CRITERIA - 1){
            $('<span>&nbsp;</span>').appendTo($divObj);
            $('<input>').attr({'type':'button','name':'add_search','class':'button'}).val('ADD').click(createBlock).appendTo($divObj);
        }

        // Insert the row into the search form
        $('#submitrow').before($divObj);

        // Initialize select box with approved search fields
        clearSelect('select[name="within' + criteria + '"]');
        loadSelectKeyVal('select[name="within' + criteria + '"]', SELECT_VALUES, false);

        // If the function was called with arguments specified,
        // set the appropriate value
        $('select[name="within' + criteria + '"]').val(fieldName);

        // Update the search criteria counter
        updateCriteria();

        // For any row other than the very first one,
        // append a "Delete" button to the
        if(criteria > 1){
            $('<input>').attr({'type':'button','class':'button','name':'delete','value':'DELETE'}).click(deleteBlock).appendTo($divObj);
        }
    }
}

// Delete the selected row and resequence the remaining rows
function deleteBlock(){
    // Delete the search condition row
    $(this).parent('.form-row').remove();

    // Initialize current row counter to "1"
    var curRow = 1;

    // After the chosen row is deleted, resequence fields
    $('#formfieldset div.search').each(function(){
        // Rename form fields to keep the sequencing correct
        $(this).find('select[name^="within"]').attr('name','within' + curRow);
        $(this).find('input[name^="term"]').attr('name','term' + curRow);

        // If the current row does not have the "Add" button
        // (because it was the last row), insert a new "Add" button
        if($(this).find('input[name="add_search"]').length == 0){
            // Identify the "Delete" button
            var $deleteObj = $(this).find('input[name="delete"]');

            // Insert an "Add" button and a spacer before the "Delete" button
            $('<span>&nbsp;</span>').insertBefore($deleteObj);
            $('<input>').attr({'type':'button','name':'add_search','class':'button'}).val('ADD').click(createBlock).insertBefore($deleteObj);
        }
        curRow++;
    });

    // Update the search criteria counter
    updateCriteria();
}


var STATES = [
    {
        "name": "Alabama",
        "abbreviation": "AL"
    },
    {
        "name": "Alaska",
        "abbreviation": "AK"
    },
    {
        "name": "American Samoa",
        "abbreviation": "AS"
    },
    {
        "name": "Arizona",
        "abbreviation": "AZ"
    },
    {
        "name": "Arkansas",
        "abbreviation": "AR"
    },
    {
        "name": "California",
        "abbreviation": "CA"
    },
    {
        "name": "Colorado",
        "abbreviation": "CO"
    },
    {
        "name": "Connecticut",
        "abbreviation": "CT"
    },
    {
        "name": "Delaware",
        "abbreviation": "DE"
    },
    {
        "name": "District Of Columbia",
        "abbreviation": "DC"
    },
    {
        "name": "Federated States Of Micronesia",
        "abbreviation": "FM"
    },
    {
        "name": "Florida",
        "abbreviation": "FL"
    },
    {
        "name": "Georgia",
        "abbreviation": "GA"
    },
    {
        "name": "Guam",
        "abbreviation": "GU"
    },
    {
        "name": "Hawaii",
        "abbreviation": "HI"
    },
    {
        "name": "Idaho",
        "abbreviation": "ID"
    },
    {
        "name": "Illinois",
        "abbreviation": "IL"
    },
    {
        "name": "Indiana",
        "abbreviation": "IN"
    },
    {
        "name": "Iowa",
        "abbreviation": "IA"
    },
    {
        "name": "Kansas",
        "abbreviation": "KS"
    },
    {
        "name": "Kentucky",
        "abbreviation": "KY"
    },
    {
        "name": "Louisiana",
        "abbreviation": "LA"
    },
    {
        "name": "Maine",
        "abbreviation": "ME"
    },
    {
        "name": "Marshall Islands",
        "abbreviation": "MH"
    },
    {
        "name": "Maryland",
        "abbreviation": "MD"
    },
    {
        "name": "Massachusetts",
        "abbreviation": "MA"
    },
    {
        "name": "Michigan",
        "abbreviation": "MI"
    },
    {
        "name": "Minnesota",
        "abbreviation": "MN"
    },
    {
        "name": "Mississippi",
        "abbreviation": "MS"
    },
    {
        "name": "Missouri",
        "abbreviation": "MO"
    },
    {
        "name": "Montana",
        "abbreviation": "MT"
    },
    {
        "name": "Nebraska",
        "abbreviation": "NE"
    },
    {
        "name": "Nevada",
        "abbreviation": "NV"
    },
    {
        "name": "New Hampshire",
        "abbreviation": "NH"
    },
    {
        "name": "New Jersey",
        "abbreviation": "NJ"
    },
    {
        "name": "New Mexico",
        "abbreviation": "NM"
    },
    {
        "name": "New York",
        "abbreviation": "NY"
    },
    {
        "name": "North Carolina",
        "abbreviation": "NC"
    },
    {
        "name": "North Dakota",
        "abbreviation": "ND"
    },
    {
        "name": "Northern Mariana Islands",
        "abbreviation": "MP"
    },
    {
        "name": "Ohio",
        "abbreviation": "OH"
    },
    {
        "name": "Oklahoma",
        "abbreviation": "OK"
    },
    {
        "name": "Oregon",
        "abbreviation": "OR"
    },
    {
        "name": "Palau",
        "abbreviation": "PW"
    },
    {
        "name": "Pennsylvania",
        "abbreviation": "PA"
    },
    {
        "name": "Puerto Rico",
        "abbreviation": "PR"
    },
    {
        "name": "Rhode Island",
        "abbreviation": "RI"
    },
    {
        "name": "South Carolina",
        "abbreviation": "SC"
    },
    {
        "name": "South Dakota",
        "abbreviation": "SD"
    },
    {
        "name": "Tennessee",
        "abbreviation": "TN"
    },
    {
        "name": "Texas",
        "abbreviation": "TX"
    },
    {
        "name": "Utah",
        "abbreviation": "UT"
    },
    {
        "name": "Vermont",
        "abbreviation": "VT"
    },
    {
        "name": "Virgin Islands",
        "abbreviation": "VI"
    },
    {
        "name": "Virginia",
        "abbreviation": "VA"
    },
    {
        "name": "Washington",
        "abbreviation": "WA"
    },
    {
        "name": "West Virginia",
        "abbreviation": "WV"
    },
    {
        "name": "Wisconsin",
        "abbreviation": "WI"
    },
    {
        "name": "Wyoming",
        "abbreviation": "WY"
    }
]
