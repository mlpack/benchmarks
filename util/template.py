'''
  @file template.py
  @author Marcus Edel

  This file contains the page templates.
'''

chartTemplate = r"""
$(document).ready(function() {
  var options = {
    chart: {
        renderTo: '%(container)s',
        type: '%(type)s'
    },
    title: {
        text: '%(title)s'
    },
    subtitle: {
        text: '%(subtitle)s'
    },
    xAxis: {
        labels:
        {
          enabled: %(xAxisLabels)s,
          rotation: %(xAxisRotation)s
        },
        categories: []
    },
    yAxis: {
        title: {
            text: '%(yAxis)s'
        }
    },
    tooltip: {
        headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
        pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
            '<td style="padding:0"><b>{point.y:.4f} %(tooltipText)s</b></td></tr>',
        footerFormat: '</table>',
        shared: true,
        useHTML: true
    },
    plotOptions: {
        column: {
            pointPadding: 0.2,
            borderWidth: 0
        },
        series: {
            cursor: 'pointer'
        }
    },

    series: []
  };

  $.get('%(data)s', function(data) {
    var lines = data.split('\n');
    $.each(lines, function(lineNo, line) {
        var items = line.split(',');
        if (lineNo == 0) {
          $.each(items, function(itemNo, item) {
            if (itemNo > 0) options.xAxis.categories.push(item);
          });
        }
        else {
          var series = {
            data: []
          };
          $.each(items, function(itemNo, item) {
            if (itemNo == 0) {
              series.name = item;
            } else {
              series.data.push(parseFloat(item));
            }
          });
          options.series.push(series);
        }
    });
    var chart = new Highcharts.Chart(options);
  });
});
"""

pageTemplate = """
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="description" content="">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Benchmark Results</title>
<link rel="stylesheet" href="framework/bs3/css/bootstrap.min.css">
<link rel="stylesheet" href="framework/font/style.css">
<link rel="stylesheet" href="css/style.css">

<script type="text/javascript" src="js/jquery.min.js"></script>
<script type="text/javascript" src="js/highcharts.js"></script>
<script src="js/sand-signika.js"></script>
<script src="js/exporting.js"></script>

<script type="text/javascript">
function loadScript( url, callback ) {
  var script = document.createElement( "script" )
  script.type = "text/javascript";
  if(script.readyState) {  //IE
    script.onreadystatechange = function() {
      if ( script.readyState === "loaded" || script.readyState === "complete" ) {
        script.onreadystatechange = null;
        callback();
      }
    };
  } else {  //Others
    script.onload = function() {
      callback();
    };
  }

  script.src = url;
  document.getElementsByTagName( "head" )[0].appendChild( script );
}
</script>

%(scripts)s


</head>
<body>
<div class="container">
<div class="row">
<div class="col-lg-12">
<div class="text-center"><h4>Benchmarks</h4></div>
<div class="container--graph collapse-group well overall-timing-chart">
<div class="container__topContent">
<div class="overall-timing-chart">
<div id="%(container)s" style="width: 100%%; height: 100%%; margin: 0 auto"></div>
</div>

</div></div>

<div class="panel panel-default">
<div class="panel-heading"><b>System Information</b></div>
<div class="row">
<div class="col-lg-3">CPU Model: %(CPUModel)s</div>
<div class="col-lg-3">Distribution: %(Distribution)s</div>
<div class="col-lg-2">Platform: %(Platform)s</div>
<div class="col-lg-2">Memory: %(Memory)s</div>
<div class="col-lg-2">CPU Cores: %(CPUCores)s</div>
</div></div>

<div class="panel panel-default">
<div class="panel-heading"><b>Library Information</b></div>

<div class="row">
%(LibraryInformation)s
</div>
</div>

%(methods)s</div></div></div>
<div class="pagination--holder">
<ul class="pagination">%(pagination)s</ul></div>
<script src="framework/jquery/jquery.min.js"></script>
<script src="framework/bs3/js/bootstrap.min.js"></script>
<script src="js/slider.js"></script>
<!--[if lte IE 7]>
<script src="framework/font/lte-ie7.js"></script>
<![endif]-->
</body>
</html>
"""

LibraryInformation = """
<div class="col-lg-2">%(name)s: %(version)s</div>
"""

paginationTemplate = """
</div>
</div>
<script src="framework/jquery/jquery.min.js"></script>
<script src="framework/bs3/js/bootstrap.min.js"></script>
<script src="js/slider.js"></script>
<!--[if lte IE 7]>
<script src="framework/font/lte-ie7.js"></script>
<![endif]-->
</body>
</html>
"""

methodTemplate = """
<div class="container--graph collapse-group well">
<div class="container__topContent">
<p class="graph--name">%(methodName)s</p>
<div class="holder--progressBar">
<span class="progressBar__percentage">%(progressPositive)s</span>
<span class="progressBar__firstPart" style="width:%(progressPositiveStyle)s"></span>
<span class="progressBar__secondPart" style="width:%(progressNegativeStyle)s"></span>
</div><div class="btn-group">
<a href="#collapse%(groupOne)s" class="btn graphs btn-grey icon-bars js-button"></a>
<a href="#collapse%(groupTwo)s" class="btn info btn-grey icon-info js-button"></a>
<a href="#collapse%(groupThree)s" class="btn memory btn-grey icon-paragraph-right-2 js-button"></a>
</div></div>
<div id="collapse%(groupOne)s" class="container__bottomContent graph collapse">
<div><div class="panel panel-default">
<div class="panel-heading">Timing Results</div>
<div class="panel-body">%(resultsPanel)s</div></div></div>
%(MetricResultsPanel)s
%(resultsPanelBootstrap)s
</div>
<div id="collapse%(groupTwo)s" class="container__bottomContent infos collapse">
<div>
<div class="panel panel-default">
<div class="panel-heading">Dataset Infos</div>
<div class="panel-body">
<table class="table table-striped">
  <thead>
    <tr><th></th><th>Size</th><th>Number of Instances</th><th>Number of Attributes</th><th>Instances</th><th>Attribute Types</th></tr>
  </thead>
  <tbody>%(datasetTable)s</tbody>
</table>%(methodInfo)s</div></div></div></div>
<div id="collapse%(groupThree)s" class="container__bottomContent memories collapse"><div>
<div><div class="panel panel-default">
<div class="panel-heading">Memory Results</div>
<div class="panel-body">%(memoryContent)s</div></div></div></div></div>
<div class="container__bottomContent">&#160;</div>
<div class="row">
<div class="col-lg-2">Libraries: %(numLibararies)s</div>
<div class="col-lg-2">Datasets: %(numDatasets)s</div>
<div class="col-lg-3">Total time: %(totalTime)s seconds</div>
<div class="col-lg-2">Script failure: %(failure)s</div>
<div class="col-lg-2">Timeouts failure: %(timeouts)s</div>
<div class="col-lg-2">Parameters: %(methods)s</div></div></div>
"""

memoryPanelTemplate = """
<div id="%(container)s" style="width: 100%%; height: 100%%;"></div>
<div class="panel panel-default">
  <div class="panel-body">
    <center><a href="%(massifFilePath)s">%(massifFile)s - Profiler Output</a></center>
  </div>
</div>
"""

panelTemplate = """
<div class="accordion-group">
<div class="accordion-heading"><a class="accordion-toggle" data-toggle="collapse" data-parent="#accordion2" href="#%(nameID)s">%(name)s</a></div>
<div id="%(nameID)s" class="accordion-body collapse">
<div class="accordion-inner"><pre>%(content)s</pre></div></div></div>
"""

resultsTemplate = """
<div class="accordion-group">
<div class="accordion-heading">
<a id="%(containerID)s" class="accordion-toggle chart" data-toggle="collapse" data-parent="#accordion2" href="#%(nameID)s">%(name)s</a></div>
<div id="%(nameID)s" class="accordion-body collapse"><div class="accordion-inner">%(content)s</div></div></div>
"""

resultsPanel = """
<div class="panel-body">
<div id="%(container)s" style="width: 100%%; height: 100%%;"></div>
<div><div class="panel">
<table class="table table-striped">
<thead><tr><th></th>%(timingHeader)s</tr></thead>
<tbody>%(timingTable)s</tbody>
</table></div></div></div>
"""

progressBarStyle = "%;-webkit-border-radius:4px 4px 4px 4px;-moz-border-radius:4px 4px 4px 4px;border-radius:4px 4px 4px 4px;"
