$(document).ready(function () {
    $(window).resize(function () {
        if ($(window).width() < 1200) {
            $(".logoDiv1").css("display", "none");
            $(".logoDiv").css("display", "none");
        } else {
            $(".logoDiv1").css("display", "block");
            $(".logoDiv").css("display", "block");
        }
    });
});