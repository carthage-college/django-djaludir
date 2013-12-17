$(document).ready(function(){
    $('#advancedSettings').hide();
    $('#settingsLink').click(function(){ $('#advancedSettings, #generalSettings').toggle(); });
    $('input[name="relativeCount"]').val($('.relativeBlock').length);
    $('input[name="activityCount"]').val($('#activityList li').length);
    $('input[name="athleticCount"]').val($('#athleticList li').length);

    $('input[name="addRelative"]').click(function(){
        var addedRelatives = $('.relativeBlock').length + 1;
        $('<div />').addClass('form-row relativeBlock').append($('<label />').text('Relative:'))
            .append($('<input />').attr({'type':'text','name':'relativeFname' + addedRelatives,'size':'12'}))
            .append($('<input />').attr({'type':'text','name':'relativeLname' + addedRelatives,'size':'12'}))
            .append($('<select />').attr('name','relativeText' + addedRelatives))
        .insertBefore($(this));

        loadSelectKeyVal('select[name="relativeText' + addedRelatives + '"]', relationships);
        $('input[name="relativeCount"]').val(addedRelatives);
    });

    $('input[name="addActivity"]').click(function(){
        var addedActivities = $('#activityList li').length + 1;
        $('<li />')
            .html($('<input />').attr({'type':'text','name':'activity' + addedActivities,'size':'25'}))
            .insertAfter($('#activityList li:last'));
        $('input[name="activityCount"]').val(addedActivities);
    });

    $('input[name="addTeam"]').click(function(){
        var addedTeams = $('#athleticList li').length + 1;
        $('<li>')
            .html($('<input />').attr({'type':'text','name':'athletic' + addedTeams,'size':'25'}))
            .insertAfter($('#athleticList li:last'));
        $('input[name="athleticCount"]').val(addedTeams);
    });

    $('a.privacyToggle').each(function(){
        var cbName = $(this).parent().find('input.privacyToggle').attr('name');
        $(this).click({chkBoxName: cbName}, togglePrivacy);
        setPrivacy(cbName.replace(/privacy/i,''), false);
    });

    $('input[name="privacy"]').click(function(){
        switch($(this).val()){
            case '0':
                setPrivacy('Personal,Family,Academics,Professional,Address', true);
                break;
            case '1':
                setPrivacy('Family,Academics,Professional,Address', true);
                setPrivacy('Personal', false);
                break;
            case '2':
                setPrivacy('Family,Professional,Address', true);
                setPrivacy('Personal,Academics', false);
                break;
            case '3':
                setPrivacy('Personal,Family,Academics,Professional,Address', false);
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
    $chkBox = $('input[name="' + chkBoxName + '"]');
    $linkObj = $chkBox.parent().find('a.privacyToggle');
    var isPublic = $chkBox.is(':checked');
    $linkObj.text('Information is: ' + (isPublic ? 'Private' : 'Public'));
    $chkBox.prop('checked', !isPublic);
    $('input[name="privacy"][value="4"]').prop('checked', true);
}

function setPrivacy(chkBoxName, isPrivate){
    $.each(chkBoxName.split(','), function(index, value){
        $chkBox = $('input[name="privacy' + value + '"]');
        $chkBox.parent().find('a.privacyToggle').text('Information is: ' + (isPrivate ? 'Private' : 'Public'));
        $chkBox.prop('checked', !isPrivate);
    });
}