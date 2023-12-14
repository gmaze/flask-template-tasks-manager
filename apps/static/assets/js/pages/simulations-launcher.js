$('input[name=nb_floats]').change(function() { $('#nfloats_value').text($('input[name=nb_floats]').val()) });

$('button[name=reset]').on('click', function(){
  // Clean-up the form:
  $('input[name=label]').val("");
  $('input[name=nb_floats]').val();
  $('#nfloats_value').text($('input[name=nb_floats]').val());
  console.log("Form reset");
} );

get_a_cancel_btn = function(runid, disabled){
    var html = "<button type='button' class='btn btn-outline-danger btn-sm' ";
    html += " data-vf-action='cancel'";
    html += " data-vf-runid='"+runid+"'";
    html += disabled;
    html += ">Cancel</button>";
    return html
}

html_progress = function(value, vmin=0, vmax=100, color='secondary', txt){
    let width = Number(value) * 100 / (vmax-vmin);
    width = width.toFixed(0);
    let html = "";
    //html += "<div class='progress mt-1' style='height:6px;'>"
    html += "<div class='progress mt-1'>";
    html += "<div class='progress-bar bg-" + color + " rounded' role='progressbar' style='width: "+width+"%;'";
    html += " aria-valuenow='"+value+"'";
    html += " aria-valuemin='"+vmin+"' ";
    html += "aria-valuemax='"+vmax+"'>";
    html += width + "%</div></div>";
    return html
}

list_tasks = function(api, api_cancel = null) {
    if (api_cancel === null){
        api_cancel = api;
    }
    $.ajax({
      url:api,
      type:"GET",
      headers: { 'X-API-KEY': APIKEY },
      contentType:"application/json; charset=utf-8",
      dataType:"json",
      success: function(data){
        var html = '';
        for(var i = 0; i < data.length; i++){
            //console.log(data[i]);
            var html_status = data[i].run.status + " ";
            var progress = Number(data[i].run.progress);
            var color;
            var cancel_disabled = "";

            if (data[i].run.status === 'queue') {
                //html_status += "<i class='feather icon-clock'></i>";
                color = 'info';
                cancel_disabled = "disabled";

            } else if (data[i].run.status === 'error'){
                //html_status += "<i class='feather icon-phone-missed'></i>";
                color = 'danger';
                cancel_disabled = "disabled";

            } else if (data[i].run.status === 'cancelled'){
                //html_status += "<i class='feather icon-phone-missed'></i>";
                color = 'warning';
                cancel_disabled = "disabled";

            } else if (data[i].run.status === 'running'){
                //html_status += "<i class='feather icon-phone-call'></i>";
                color = 'primary';

            } else if (data[i].run.status === 'done'){
                //html_status += "<i class='feather icon-phone-off'></i>";
                cancel_disabled = "disabled";
                if (data[i].run.final_state === 'success') {
                    color = 'success';
                    html_status += "(success)";
                } else if (data[i].run.final_state === 'failed') {
                    color = 'danger';
                    html_status += "(failed)";
                }
                progress = 100;

            } else {
                //html_status += "<i class='feather icon-alert-circle'></i>";
                color = 'danger';
            }

            //var html_status = data[i].status + " ";
            html_status += html_progress(progress, 0, 100, color, data[i].run.status);

            var html_cancel = get_a_cancel_btn(data[i].id, cancel_disabled);

            var html_actions = html_cancel;

            html += '<tr>'+
                        '<td>' + data[i].id + '</td>' +
                        '<td>' + data[i].user.username + '</td>' +
                        '<td>' + html_status + '</td>' +
                        '<td>' + data[i].params.nfloats + '</td>' +
                        '<td>' + data[i].params.label + '</td>' +
                        '<td>' + html_actions + '</td>' +
                    '</tr>';
            }
        $('#tasks_table tbody').html(html);

        $('button[data-vf-action=cancel]').on('click', function(){
            // Cancel a task:
            let runid = $(this).data('vf-runid');
            console.log("Cancelling " + runid);
            $.ajax({
                url: api_cancel + "/" + runid,
                type: "DELETE",
                headers: {'X-API-KEY': APIKEY},
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                success: function (data) {
                },
                error: function (data) {
                    alert(data);
                }
            })

        })
      },

    })
};

init_donut = function(div_id, labels, colors, offsetY=0){
    var options1 = {
        chart: {
            height: 150,
            type: 'donut',
            offsetY: offsetY,
        },
        dataLabels: {
            enabled: false
        },
        plotOptions: {
            pie: {
                donut: {
                    size: '50%'
                }
            }
        },
        labels: labels,
        series: [],
        legend: {
            show: false
        },
        tooltip: {
            theme: 'dark'
        },
        grid: {
            padding: {
                top: 20,
                right: 0,
                bottom: 0,
                left: 0
            },
        },
        colors: colors,
        fill: {
            opacity: [1, 1]
        },
        stroke: {
            width: 0,
        },
        noData: {
            text: 'Waiting for data...',
        },
    }
    var chart = new ApexCharts(document.querySelector("#"+div_id), options1);
    chart.render();
    return chart
}

init_gauge = function(div_id){
    let fill = {
            type: 'gradient',
            gradient: {
                shade: 'dark',
                shadeIntensity: 0.15,
                inverseColors: false,
                opacityFrom: 1,
                opacityTo: 1,
                stops: [0, 50, 65, 91]
            },
        };
    fill = {
            type: 'gradient',
            gradient: {
                shade: 'light',
                shadeIntensity: 0.4,
                inverseColors: false,
                opacityFrom: 1,
                opacityTo: 1,
                stops: [0, 50, 53, 91]
            },
        };
    fill = {
            type: 'gradient',
            gradient: {
                shade: 'dark',
                type: 'horizontal',
                shadeIntensity: 0.5,
                gradientToColors: ['#F00'],
                inverseColors: false,
                opacityFrom: 1,
                opacityTo: 1,
                stops: [0, 100]
            }
        };

    let radialBar = {
            startAngle: -90,
            endAngle: 90,
            dataLabels: {
                name: {
                    show: false,
                    fontSize: '16px',
                    color: undefined,
                    offsetY: 0
                },
                value: {
                    offsetY: -20,
                    fontSize: '25px',
                    color: 'white',
                    formatter: function (val) {
                            return val + "%";
                        }
                }
            },
            track: {
                background: "#fff",
                strokeWidth: '97%',
                margin: 5, // margin is in pixels
                dropShadow: {
                    enabled: true,
                    top: 2,
                    left: 0,
                    color: '#999',
                    opacity: 1,
                    blur: 2
                }
            },
        };

    var options = {
        series: [],
        chart: {
            height: 300,
            type: 'radialBar',
            offsetY: 0,
            sparkline: {enabled: true},
        },
        plotOptions: {
            radialBar: radialBar,
        },
        fill: fill,
        labels: [''],
        noData: {
           text: 'Waiting for data...',
        },
    };
    var chart = new ApexCharts(document.querySelector("#"+div_id), options);
    chart.render();
    return chart
}

fill_in_tasks_card = function(api, this_donut) {
    $.ajax({
        url: api,
        type: "GET",
        headers: {'X-API-KEY': APIKEY},
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            let census = data.tasks.results;
            let total = census['cancelled'] + census['success'] + census['failed'];

            $("#tasks_count_total").html(total);
            $("#tasks_count_success").html("<i class='fas fa-circle f-10 m-r-5 text-success'></i>" + census['success']);
            $("#tasks_count_failed").html("<i class='fas fa-circle f-10 m-r-5 text-danger'></i>" + census['failed']);
            $("#tasks_count_cancelled").html("<i class='fas fa-circle f-10 m-r-5 text-warning'></i>" + census['cancelled']);
            this_donut.updateSeries([census['failed'], census['success'], census['cancelled']])

            // $("#tasks_count_total_head").html("<i class='feather icon-shopping-cart ms-1'></i> " + data.subscription_plan.quota_tasks);

        }
    })
};

fill_in_quota_card = function(api, this_donut) {
    $.ajax({
        url: api,
        type: "GET",
        headers: {'X-API-KEY': APIKEY},
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            let quota_count = data.tasks.quota_count;
            let quota_left = data.tasks.quota_left;
            let quota = data.subscription_plan.quota_tasks;

            $("#quota_count_total_head").html("<i class='feather icon-shopping-cart ms-1'></i> " + quota);
            $("#quota_count_left_head").html(quota_left);
            $("#quota_count_done").html("<i class='fas fa-circle f-10 m-r-5 text-black'></i>" + quota_count);
            $("#quota_count_left").html("<i class='fas fa-circle f-10 m-r-5 text-white'></i>" + quota_left);
            this_donut.updateSeries([quota_count, quota_left]);
        }
    })
};

fill_in_user_cards = function(api, this_donutA, this_donutB) {
    $.ajax({
        url: api,
        type: "GET",
        headers: {'X-API-KEY': APIKEY},
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            // TASKS CARD:
            let census = data.tasks.results;
            let total = census['cancelled'] + census['success'] + census['failed'];

            $("#tasks_count_total").html(total);
            $("#tasks_count_success").html("<i class='fas fa-circle f-10 m-r-5 text-success'></i>" + census['success']);
            $("#tasks_count_failed").html("<i class='fas fa-circle f-10 m-r-5 text-danger'></i>" + census['failed']);
            $("#tasks_count_cancelled").html("<i class='fas fa-circle f-10 m-r-5 text-warning'></i>" + census['cancelled']);
            this_donutA.updateSeries([census['failed'], census['success'], census['cancelled']])

            // $("#tasks_count_total_head").html("<i class='feather icon-shopping-cart ms-1'></i> " + data.subscription_plan.quota_tasks);

            // QUOTA CARD:
            let quota_count = data.tasks.quota_count;
            let quota_left = data.tasks.quota_left;
            let quota = data.subscription_plan.quota_tasks;

            $("#quota_count_total_head").html("<i class='feather icon-shopping-cart ms-1'></i> " + quota);
            $("#quota_count_left_head").html(quota_left);
            $("#quota_count_done").html("<i class='fas fa-circle f-10 m-r-5 text-black'></i>" + quota_count);
            $("#quota_count_left").html("<i class='fas fa-circle f-10 m-r-5 text-white'></i>" + quota_left);
            this_donutB.updateSeries([quota_count, quota_left]);

        }
    })
};