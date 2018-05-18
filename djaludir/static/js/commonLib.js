/*
**    A collection of common utilities employing jQuery to simplify basic repetitious tasks
**    I've done my best to provide comments where appropriate.
**
**    One of the recurring standards (and I use that term very loosely) is the first argument being passed in is
**    the jQuery selector. What I mean by this is a string representation of how you would access an element (or
**    elements) using jQuery. For example, if you have an element <select name="specificName"> on your page, you
**    would pass the function "select[name='specificName']".
**
**    IMPORTANT!!
**    I have spent some time testing these functions but it has not been exhaustive by any stretch of the imagination
**    so be alert for any unexpected behaviors. If a function is included in this library it means I have not seen any
**    problems with it and have used it without issue but your usage may differ from mine and I may not have tested
**    your case.
*/

/*
**    Description:    Populate select box with options generated from a delimited string
**    Arguments:        strObjSel (string) - jQuery selector string identifying the <select> object to be manipulated
**                    strOpts (string) - delimited list of values to be used in populating <option> collection
**                    createDefaultVal (boolean) [optional] - true by default, should an empty default value be created within the <select>
**                    delimChar (string) [optional] - a comma by default, the character used to split the strOpts string
*/
function loadSelect(strObjSel, strOpts, createDefaultVal, delimChar){
    if(delimChar === undefined || delimChar == null) { delimChar = ','; }
    if(createDefaultVal === undefined || createDefaultVal == null || createDefaultVal){ $(strObjSel).append($('<option />')); }

    $.each(strOpts.split(delimChar), function(index, value){
        $(strObjSel).append($('<option />').attr({'value':value}).text(value));
    });
}

/*
**    Description:    Populate select box with <option> generated from a delimited string containing text and values
**    Arguments:        strObjSel (string) - jQuery selector string identifying the <select> object to be manipulated
**                    strOpts (string) - double delimited list of text and values to be used in populating <option> collection
**                    createDefaultVal (boolean) [optional] - true by default, should an empty default value be created within the <select>
**                    delimChar (string) [optional] - a comma by default, the character used to split the strOpts string
**                    keyValDelimChar (string) [optional] - a caret by default, the character used to split each option record into value|text array
*/
function loadSelectKeyVal(strObjSel, strOptsKeyVal, createDefaultVal, delimChar, keyValDelimChar){
    if(delimChar === undefined || delimChar == null) { delimChar = ','; }
    if(keyValDelimChar === undefined || keyValDelimChar == null) { keyValDelimChar = '^'; }

    if(delimChar == keyValDelimChar){
        alert('The record delimiter should be different than the key/value delimiter.');
        return;
    }

    if(createDefaultVal === undefined || createDefaultVal == null || createDefaultVal){ $(strObjSel).append($('<option />')); }

    $.each(strOptsKeyVal.split(delimChar), function(index, value){
        keyValArr = value.split(keyValDelimChar);
        $(strObjSel).append($('<option />').attr({'value':keyValArr[0]}).text(keyValArr[1]));
    });
}

/*
**    Description:    Populate select box with <option> generated from two delimited strings, one containing the value and the other containing the text
**    Arguments:        strObjSel (string) - jQuery selector string identifying the <select> object to be manipulated
**                    strOptsKey (string) - delimited list of values to be used to populate the 'value' attribute of the <option> collection
**                    strOptsVal (string) - delimited list of values to be used to populate the 'text' attribute of the <option> collection
**                    createDefaultVal (boolean) [optional] - true by default, should an empty default value be created within the <select>
**                    delimChar (string) [optional] - a comma by default, the character used to split the strOpts string
*/
function loadSelectKeyValTwoLists(strObjSel, strOptsKey, strOptsVal, createDefaultVal, delimChar){
    if(delimChar === undefined || delimChar == null) { delimChar = ','; }
    if(strOptsKey.split(delimChar).length != strOptsVal.split(delimChar).length){
        alert('The list of keys and the list of values should be the same length.\n\nPlease make sure the delimiter was not inadvertently included in one of the lists');
        return;
    }
    
    if(createDefaultVal === undefined || createDefaultVal == null || createDefaultVal) { $(strObjSel).append($('<option />')); }
    
    var texts = strOptsVal.split(delimChar);
    $.each(strOptsKey.split(delimChar), function(index, key){
        $(strObjSel).append($('<option />').attr({'value':key}).text(texts[index]));
    });
}

/*
**    Description:    Populate select box with <option> spanning a user-specified numeric range
**    Arguments:        strObjSel (string) - jQuery selector string identifying the <select> object to be manipulated
**                    startVal (numeric) - the numeric value of the first record
**                    endVal (numeric) - the numeric value of the last record
**                    isAscending (boolean) [optional] - true by default, indicates whether the numeric range is in ascending or descending order
**                    createDefaultVal (boolean) [optional] - true by default, should an empty value be created as the first option in the <select>
**                    stepIncrement (numeric) [optional] - 1 by default, the amount to increment/decrement the loop by during the iteration over the range
*/
function loadSelectRange(strObjSel, startVal, endVal, isAscending, createDefaultVal, stepIncrement){
    if(createDefaultVal === undefined || createDefaultVal == null || createDefaultVal) { $(strObjSel).append($('<option />')); }
    
    var step = stepIncrement === undefined || stepIncrement == null ? 1 : stepIncrement;
    //If the range is to be sorted in descending order, reverse the sign of the step (descending will be largest to smallest so the counter has to decrement)
    var sortAscending = isAscending === undefined || isAscending == null || isAscending ? step : step * -1;
    //Add one increment of amount [step] to the end value so the terminating condition in the for-loop is met at the correct time
    endVal += sortAscending;
    for(var ii = startVal; ii != endVal; ii += sortAscending){
        $(strObjSel).append($('<option />').attr({'value':ii}).text(ii));
    }
}

/*
**    Description:    Remove <option> tags from specified <select> element
**    Arguments:        strObjSel (string) - jQuery selector string identifying the <select> object to be cleared
**                    keepFirst (boolean) [optional] - false by default, indicates whether the first <option> in the <select> should be removed (should be true when first option is place holder, ie "Select One")
*/
function clearSelect(strObjSel, keepFirst){
    if(keepFirst === undefined || keepFirst == null) { keepFirst = false; }
    $(strObjSel + ' option').not(keepFirst ? ':first' : '').each(function() { $(this).remove(); });
}

function clearMultipleSelects(selectorList, keepFirst, selectorDelim){
    if(keepFirst === undefined || keepFirst == null) { keepFirst = false; }
    if(selectorDelim === undefined || selectorDelim == null) { selectorDelim = ','; }
    var optionList = '', firstList = '', selectors = selectorList.split(selectorDelim);
    $.each(selectors, function(index, selector){
        var isLast = index == selectors.length - 1;
        optionList += selector + ' option' + (isLast ? '' : ',');
        firstList += selector + ' :first' + (isLast ? '' : ',');
    });
    $(optionList).not(firstList).each(function() { $(this).remove(); });
}

/*
**    Description:    Takes initial string and pads the left side of the string with a specified character until it reaches the desired length
**    Arguments:        num (string) - initial string to be adjusted to desired length
**                    len (numeric) [optional] - the desired length of the string at which point the function ends, defaults to 2
**                    padChar (character) [optional] - the character to prepend to num (see above), defaults to '0'
*/
function padNumber(num, len, padChar){
    if(len === undefined || len == null || len < 1) { len = 2; }
    if(padChar === undefined || padChar == null || padChar == '') { padChar = '0'; }
    while(num.toString().length < len){
        num = padChar + num;
    }
    return num;
}

/*
**    Description:    Crude manual approach to formatting a dateTime object.
**    Arguments:        date (dateTime) - the date value to be formatted
**                    mask (string) - the desired output format of the date
**                    delim (character) [optional] - the delimiter that is used between the various date parts, defaults to '-'
**                    pad (boolean) [optional] - flag indicating whether single digit date parts should be forced to two characters, defaults to 'true'
*/
function dateFormat(date, mask, delim, pad){
    if(delim === undefined || delim == null) { delim = '-'; };
    if(pad === undefined || pad == null) { pad = true; };
    var dateStr = '';
    switch(mask){
        case 'yyyymmdd':
            dateStr = date.getFullYear() + delim + padNumber(date.getMonth() + 1) + delim + padNumber(date.getDate());
            break;
        case 'mmdd':
            dateStr = padNumber(date.getMonth() + 1) + delim + padNumber(date.getDate());
            break;
        case 'mmddyyyy':
            dateStr = padNumber(date.getMonth() + 1) + delim + padNumber(date.getDate()) + delim + date.getFullYear();
            break;
        case 'mmmmdd':
            dateStr = getMonthName(date) + delim + date.getDate();
            break;
        case 'mmmmyyyy':
            dateStr = getMonthName(date) + delim + date.getFullYear();
            break;
        default:
            alert('Unrecognized Mask: ' + mask);
            break;
    }
    return dateStr;
}

/*
**    Description:    Changes the passed in date by adding or subtracting a specified number of date part units from the initial value
**    Arguments:        date (dateTime) - the original date to be modified
**                    part (string) - the part of the date to add or subtract from. Currently supports 'd' (day), 'm' (month), 'y' (year)
**                    increment (numeric) - the amount by which to increase (positive number) or decrease (negative number) the date
*/
function dateAdd(date, part, increment){
    var day = date.getDate(), month = date.getMonth(), year = date.getFullYear();
    switch(part){
        case 'd':
            day += increment;
            break;
        case 'm':
            month += increment;
            break;
        case 'y':
            year += increment;
            break;
    }
    return new Date(year, month, day);
}

//Returns the full name of the month given the provided date
function getMonthName(date){
    var monthNames = ['January','February','March','April','May','June','July','August','September','October','November','December'];
    return monthNames[date.getMonth()];
}

//Returns the readable representation of the day of the week based on the provided date
function getDayOfWeek(date){
    var dayNames = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
    return dayNames[date.getDay()];
}

/*
**    Description:    Calculates the difference between two dates' specified date part
**    Arguments:        part (string) - the part of the date to be used for comparison. Currently supports 'd' (days), 'w' (weeks), 'm' (months), 'y' (years)
**                    date1 (dateTime) - the earlier of the two dates
**                    date2 (dateTime) - the later of the two dates
*/
function dateDiff(part, date1, date2){
    var returnVal;
    switch(part){
        case 'd':
            returnVal = parseInt((date2.getTime()-date1.getTime())/(24*3600*1000));
            break;
        case 'w':
            returnVal = parseInt((date2.getTime()-date1.getTime())/(24*3600*1000*7));
            break;
        case 'm':
            returnVal = (date2.getMonth() + 12 * date2.getFullYear()) - (date1.getMonth() + 12 * date1.getFullYear());
            break;
        case 'y':
            returnVal = date2.getFullYear() - date1.getFullYear();
            break;
        default:
            alert('Unknown date part');
            break;
    }
    return returnVal;
}

function setSelectByText(strSelectObj, text){
    $(strSelectObj + ' option').filter(function(index){
        return $(this).text() === text;
    }).prop("selected", "selected").change();
}
