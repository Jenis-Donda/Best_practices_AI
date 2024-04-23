// To prevent XSS attack
function escapeCode(rawStr) {
    if (rawStr == null || rawStr == "null") { rawStr = "" }
    return rawStr.toString().replace(/[\u00A0-\u017e\u0180-\u9999<>\&]/gim, function (i) { return '&#' + i.charCodeAt(0) + ';'; });
}

function processSeverityScore(severity, score) {
    return '(' + score + ') ' + severity
}

function investigate(ioc_value, ioc_type, applicationId) {
    if (ioc_value) {
        ioc_value = '"' + ioc_value + '"'
        applicationId = '"' + applicationId + '"'
        ioc_type = '"' + ioc_type + '"'

        return '<button type="button" class="btn btn-primary" onclick=openInvestigatePopUp(' + ioc_value + ',' + ioc_type + ',' + applicationId + ')>Investigate</button>'
    }
}


function openInvestigatePopUp(ioc_value, ioc_type, appId) {
    let QRadar = window.qappfw.QRadar;
    var base_url = QRadar.getApplicationBaseUrl(appId);
    var url = base_url + "/investigate?ioc=" + ioc_value + "&ioc_type=" + ioc_type;
    window.open(url, "ModalPopUp",
        "toolbar=no," +
        "scrollbars=no," +
        "location=no," +
        "statusbar=no," +
        "menubar=no," +
        "resizable=0," +
        "width=700," +
        "height=500," +
        "left = 300," +
        "top = 90," +
        "bottom=90," + "noopener,noreferrer");
}


function make_url(url_value) {
    if (url_value) {
        return '<a class="btn btn-primary" href="' + encodeURI(url_value) + '" target="_blank" rel="noopener noreferrer" role="button">View</a>'
    }
    return url_value
}
