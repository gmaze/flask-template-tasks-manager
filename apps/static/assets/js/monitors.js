var monitor1;
var monitor2;
var monitor3;

var RefreshTasksList = window.setInterval(function(){
    fill_in_cpu_card(API_CPU, monitor1);
    fill_in_vmem_card(API_VMEM, monitor2);
}, 1000);

var RefreshTasksList = window.setInterval(function(){
    fill_in_du_card(API_DISK, monitor3);
}, 5000);


$( document ).ready(function() {
    monitor1 = init_monitor("cpu-card", "%", ['#ff5370', '#ff869a'], [0,100]);
    monitor2 = init_monitor("vmem-card", "%", ['#53ff70', '#86ff9a'], [0, 100]);
    monitor3 = init_monitor("du-card", "%", ['#4099ff', '#4099ff'], [0, 100]);
    fill_in_cpu_card(API_CPU, monitor1);
    fill_in_vmem_card(API_VMEM, monitor2);
    fill_in_du_card(API_DISK, monitor3);
})

init_monitor = function(div_id,
                        labels,
                        colors,
                        ylim=[0,100],
                        ){
    var options1 = {
        chart: {
            type: 'area',
            height: 145,
            sparkline: {
                enabled: true
            }
        },
        dataLabels: {
            enabled: false
        },
        colors: [colors[0]],
        fill: {
            type: 'gradient',
            gradient: {
                shade: 'dark',
                gradientToColors: [colors[1]],
                shadeIntensity: 1,
                type: 'horizontal',
                opacityFrom: 1,
                opacityTo: 0.8,
                stops: [0, 100, 100, 100]
            },
        },
        stroke: {
            curve: 'smooth',
            width: 2,
        },
        series: [],
        yaxis: {
           min: ylim[0],
           max: ylim[1],
        },
        tooltip: {
            fixed: {
                enabled: false
            },
            x: {
                show: false
            },
            y: {
                title: {
                    formatter: function(seriesName) {
                        return labels
                    }
                }
            },
            marker: {
                show: false
            }
        },
        noData: {
            text: 'Waiting for data...',
        },
    }
    var chart = new ApexCharts(document.querySelector("#"+div_id), options1);
    chart.render();
    return chart
}

function humanFileSize(bytes, si=false, dp=1) {
    const thresh = si ? 1000 : 1024;

    if (Math.abs(bytes) < thresh) {
        return bytes + ' B';
    }

    const units = si
    ? ['kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
    : ['KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB'];
    let u = -1;
    const r = 10**dp;

    do {
        bytes /= thresh;
        ++u;
    } while (Math.round(Math.abs(bytes) * r) / r >= thresh && u < units.length - 1);

    return bytes.toFixed(dp) + ' ' + units[u];
}

fill_in_cpu_card = function(api, this_graphe) {
    $.ajax({
        url: api + "?page=1",
        type: "GET",
        headers: {'X-API-KEY': APIKEY},
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            //console.log(data['data'])
            $("#cpu-label").html(data['label']);
            $("#cpu-current").html(data['data'].slice(0)[0]['value']+data['unit']);
            let L = data['data'];
            let D = {};
            Object.keys(L[0]).forEach(k => {
                D[k] = L.map(o => o[k]);
            });
            //console.log(D);
            this_graphe.updateSeries([{data: D['value'].reverse()}]);
        }
    })
};

fill_in_vmem_card = function(api, this_graphe) {
    $.ajax({
        url: api + "?page=1",
        type: "GET",
        headers: {'X-API-KEY': APIKEY},
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            let percent = data['data'].slice(-1)[0]['value'];
            let total = data['data'].slice(-1)[0]['total'];
            let used = total*percent/100*1e6;

            $("#vmem-label").html(data['label'] + " (" +humanFileSize(total*1e6)+ ")");
            $("#vmem-current").html(humanFileSize(used) + " - " + percent + "%");

            let L = data['data'];
            let D = {};
            Object.keys(L[0]).forEach(k => {
                D[k] = L.map(o => o[k]);
            });
            this_graphe.updateSeries([{data: D['value'].reverse()}]);
        }
    })
};

fill_in_du_card = function(api, this_graphe) {
    $.ajax({
        url: api + "?page=1",
        type: "GET",
        headers: {'X-API-KEY': APIKEY},
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            // percent = data['data'].slice(-1)[0]['value'];
            let percent = Number((data['data'].slice(-1)[0]['value']).toFixed(1));
            let total = data['data'].slice(-1)[0]['total'];
            let used = total*percent/100*1e6;

            $("#du-label").html(data['label'] + " (" +humanFileSize(total*1e6)+ ")");
            //$("#du-current").html(humanFileSize(used));
            $("#du-current").html(humanFileSize(used) + " - " + percent + "%");

            let L = data['data'];
            let D = {};
            Object.keys(L[0]).forEach(k => {
                D[k] = L.map(o => o[k]);
            });
            this_graphe.updateSeries([{data: D['value'].reverse()}]);
        }
    })
};