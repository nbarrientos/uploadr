$(function() {
    $("#download_link").hide();

    $("#request_token").click(function() {
        $.getJSON("/token", function(data) {
                if(data.s == 0) {
                    var href = $("#download_link").attr("href");
                    href = href + data.t;
                    $("#download_link").attr("href", href);
                    $("#request_token").hide();
                    $("#download_link").show();
                }
                else {
                    $("#token").html("<div><p>"+data.r+"</p></div>");
                }
            });
    });
});
