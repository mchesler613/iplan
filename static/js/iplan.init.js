// iplan.init.js
$(document).ready(function() {
    $('.datepicker').datepicker({
      minDate: 0,
    });
    $('.timepicker').timepicker({
      startTime: '9:00am',
      minTime: '9',
      maxTime: '5:30pm',
      dynamic: false
    });

    // initTabs();
    $( document ).tooltip();
    $("textarea").attr({"rows": "4",
                        "cols": "18"
    });
});
