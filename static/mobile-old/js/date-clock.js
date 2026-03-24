(function ($) {
    'use strict';

    var monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    var dayNames = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

    function updateDate() {
        var newDate = new Date();
        var day = dayNames[newDate.getDay()];
        var date = newDate.getDate();
        var month = monthNames[newDate.getMonth()];
        var year = newDate.getFullYear();

        $('#dashboardDate').html(`${day}, ${date} ${month} ${year}`);
        $('#dashboardDate2').html(`${day}, ${date} ${month}`);
    }

    function updateTime() {
        var newDate = new Date();
        var options = {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: true
        };

        var timeString = new Intl.DateTimeFormat(navigator.language, options).format(newDate);

        var timeParts = timeString.split(':');
        var hours = timeParts[0];
        var minutes = timeParts[1];
        var seconds = timeParts[2];

        $("#hours").html(hours);
        $("#min").html(minutes);
        $("#sec").html(seconds);
    }

    $(window).on("load", function() {
        updateDate();
        updateTime();
        setInterval(updateTime, 1000);
    });

})(jQuery);