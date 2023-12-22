'use strict';
document.addEventListener("DOMContentLoaded", function () {
    setTimeout(function() {
        floatchart()
    }, 100);
});

function floatchart() {

    // [ seo-card1 ] start
    (function () {
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
            colors: ["#ff5370"],
            fill: {
                type: 'gradient',
                gradient: {
                    shade: 'dark',
                    gradientToColors: ['#ff869a'],
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
            series: [{
                data: [5, 35, 60, 80, 95, 20, 12, 5]
            }],
            yaxis: {
               min: 0,
               max: 100,
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
                            return 'CPU Usage '
                        }
                    }
                },
                marker: {
                    show: false
                }
            }
        }
        new ApexCharts(document.querySelector("#seo-card1"), options1).render();
    })();
    // [ seo-card1 ] end

    // [ seo-card2 ] start
    (function () {
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
            colors: ["#53ff70"],
            fill: {
                type: 'gradient',
                gradient: {
                    shade: 'dark',
                    gradientToColors: ['#86ff9a'],
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
            series: [{
                data: [5, 5, 30, 55, 40, 20]
            }],
            yaxis: {
               min: 0,
               max: 100,
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
                            return ' (Mb) '
                        }
                    }
                },
                marker: {
                    show: false
                }
            }
        }
        new ApexCharts(document.querySelector("#seo-card2"), options1).render();
    })();
    // [ seo-card2 ] end

    // [ seo-card3 ] start
    (function () {
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
            colors: ["#53ff70"],
            fill: {
                type: 'gradient',
                gradient: {
                    shade: 'dark',
                    gradientToColors: ['#86ff9a'],
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
            series: [{
                data: [5, 5, 10, 12, 14, 18]
            }],
            yaxis: {
               min: 0,
               max: 100,
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
                            return 'Disk (Mb) '
                        }
                    }
                },
                marker: {
                    show: false
                }
            }
        }
        new ApexCharts(document.querySelector("#seo-card3"), options1).render();
    })();
    // [ seo-card3 ] end

}
