$("#generateHash").click(function generateHash(eventObj)
{
    var original = $("#hashOriginal").val();
    var hash = CryptoJS.MD5(original);
    
    while (hash.length < 32)
        hash = "0" + hash;
        
    $("#hashString").val(hash);
    
    $("a.user_item").removeClass("user_item_selected");
    
    $("a[title=" + hash + "]").addClass("user_item_selected");
});

$("#hashString").prop("readonly", "true");
