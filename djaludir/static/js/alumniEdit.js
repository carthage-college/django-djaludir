var LEVEL_0_HIDE = 'Personal,Family,Academics,Professional,Address',
    LEVEL_1_HIDE = 'Family,Academics,Professional,Address',
    LEVEL_1_SHOW = 'Personal',
    LEVEL_2_HIDE = 'Family,Professional,Address',
    LEVEL_2_SHOW = 'Personal,Academics',
    LEVEL_3_SHOW = 'Personal,Family,Academics,Professional,Address';

$(document).ready(function(){
    //Set the current counters for relatives, activities, and athletics
    $('input[name="relativeCount"]').val($('.relativeBlock').length);
    $('input[name="activityCount"]').val($('#activityList li').length);
    $('input[name="athleticCount"]').val($('#athleticList li').length);

    //Attach functionality to "Add Relative" button
    $('input[name="addRelative"]').click(function(){

        //Increment relative counter
        var addedRelatives = $('.relativeBlock').length + 1;

        //Create HTML for relative form
        $('<fieldset />').append($('<ol />').addClass('relativeBlock')
            .append($('<li>').addClass('ctrlHolder')
                .append($('<h3 />').append($('<label />').text('Relative First Name')))
                .append($('<input />').attr({'type':'text','name':'relativeFname' + addedRelatives}))
            )
            .append($('<li>').addClass('ctrlHolder')
                .append($('<h3 />').append($('<label />').text('Relative Last Name')))
                .append($('<input />').attr({'type':'text','name':'relativeLname' + addedRelatives}))
            )
            .append($('<li>').addClass('ctrlHolder')
                .append($('<h3 />').append($('<label />').text('Relationship')))
                .append($('<select />').attr({'type':'text','name':'relativeText' + addedRelatives}))
            )
        ).insertBefore($(this));

        //Populate select box with family relationships
        loadSelectKeyVal('select[name="relativeText' + addedRelatives + '"]', relationships);

        //Update hidden relative count field
        $('input[name="relativeCount"]').val(addedRelatives);
    });

    //Attach functionality to "Add Activity" button
    $('input[name="addActivity"]').click(function(){

        //Increment activity counter
        var addedActivities = $('#activityList li').length + 1;

        //Create HTML for activity form
        $('<li />')
            .html($('<input />').attr({'type':'text','name':'activity' + addedActivities,'placeholder':'Activity Name'}))
            .insertAfter($('#activityList li:last'));

        //Update hidden activity count field
        $('input[name="activityCount"]').val(addedActivities);
    });

    //Attach functionality to "Add Athletic Team" button
    $('input[name="addTeam"]').click(function(){

        //Increment athletic counter
        var addedTeams = $('#athleticList li').length + 1;

        //Create HTML for athletic form
        $('<li>')
            .html($('<input />').attr({'type':'text','name':'athletic' + addedTeams,'placeholder':'Athletic Team'}))
            .insertAfter($('#athleticList li:last'));

        //Update hidden athletic count field
        $('input[name="athleticCount"]').val(addedTeams);
    });

    //Attach functionality to each Privacy link (currently in the heading of each fieldset)
    $('a.privacyToggle').each(function(){
        //Get the name of the checkbox
        var cbName = $(this).parent().find('input.privacyToggle').attr('name');

        //Attach togglePrivacy() to the click event of the checkbox
        $(this).click({chkBoxName: cbName}, togglePrivacy);

        //Initialize privacy setting
        setPrivacy(cbName.replace(/privacy/i,''), false);
    });

    //Attach functionality to privacy radio buttons
    $('input[name="privacy"]').click(function(){
        switch($(this).val()){
            case '0':
                setPrivacy(LEVEL_0_HIDE, true);
                break;
            case '1':
                setPrivacy(LEVEL_1_HIDE, true);
                setPrivacy(LEVEL_1_SHOW, false);
                break;
            case '2':
                setPrivacy(LEVEL_2_HIDE, true);
                setPrivacy(LEVEL_2_SHOW, false);
                break;
            case '3':
                setPrivacy(LEVEL_3_SHOW, false);
                break;
            case '4':
                break;
        }
    });
});

function togglePrivacy(chkBoxName){
    if(typeof chkBoxName != 'string'){
        chkBoxName = chkBoxName.data.chkBoxName;
    }
    setPrivacy(chkBoxName.replace(/privacy/i,''), $chkBox.is(':checked'));

    //When someone clicks a link, reset the privacy radio button to the "Custom" setting
    $('input[name="privacy"][value="4"]').prop('checked', true);
}

/********************************************************
 * chkBoxName (string) - a single checkbox name or comma-delimited list of checkbox names
 * isPrivate (boolean) - dictates the new privacy setting
*********************************************************/
function setPrivacy(chkBoxName, isPrivate){
    //Loop through each checkbox name in the chkBoxName variable
    $.each(chkBoxName.split(','), function(index, value){
        $chkBox = $('input[name="privacy' + value + '"]');
        $chkBox.parent().find('a.privacyToggle').text('Information is: ' + (isPrivate ? 'Private' : 'Visible to Alumni'));
        $chkBox.prop('checked', !isPrivate);
    });
}

/********************************************************
 * Based on the privacy fields specifed during page load,
 * select the appropriate radio button setting
********************************************************/
function initPrivacy(privateFields){
    //Let "Custom" be the default setting
    var index = '4';
    /*
     * Remove the trailing comma, split the string into an array, sort the elements
     * alphabetically, and rejoin the elements as a single string
    */
    privateFields = privateFields.replace(/^(.*),$/i,'$1').split(',').sort().join(',');
    switch(privateFields){
        case LEVEL_0_HIDE.split(',').sort().join(','):
            index = '0';
            break;
        case LEVEL_1_HIDE.split(',').sort().join(','):
            index = '1';
            break;
        case LEVEL_2_HIDE.split(',').sort().join(','):
            index = '2';
            break;
        case '':
            index = '3';
            break;
    }
    $('input[name="privacy"][value="' + index + '"]').click();
}
