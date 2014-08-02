'''
  @file template.py
  @author Marcus Edel

  This file contains the page templates.
'''

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
</head>
<body>
<div class="container">
<div class="row">
<div class="col-lg-12">
<div class="text-center"><h4>Benchmarks</h4></div>
<div class="container--graph collapse-group well overall-timing-chart">
<div class="container__topContent">
<div class="overall-timing-chart"><img class="center--image" src="%(topLineChart)s" alt="" style="max-width: 100%%;"></div>
</div></div>%(methods)s</div></div></div>
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
<div class="panel-heading">Benchmark Results</div>
<div class="panel-body">%(resultsPanel)s</div></div></div></div>
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
<div class="panel">
<div><img class="center--image" src="%(memoryChart)s" alt="" style="max-width: 100%%;"></div>
<div class="accordion-group">
<div class="accordion-heading"><a class="accordion-toggle" data-toggle="collapse" data-parent="#accordion2" href="#%(nameID)s">%(name)s</a></div>
<div id="%(nameID)s" class="accordion-body collapse">
<div class="accordion-inner"><pre>%(content)s</pre></div></div></div></div>
"""

panelTemplate = """
<div class="accordion-group">
<div class="accordion-heading"><a class="accordion-toggle" data-toggle="collapse" data-parent="#accordion2" href="#%(nameID)s">%(name)s</a></div>
<div id="%(nameID)s" class="accordion-body collapse">
<div class="accordion-inner"><pre>%(content)s</pre></div></div></div>
"""

resultsTemplate = """
<div class="accordion-group">
<div class="accordion-heading"><a class="accordion-toggle" data-toggle="collapse" data-parent="#accordion2" href="#%(nameID)s">%(name)s</a></div>
<div id="%(nameID)s" class="accordion-body collapse"><div class="accordion-inner">%(content)s</div></div></div>
"""

resultsPanel = """
<div class="panel-body">
<div class="overall-timing-chart"><img class="panel" src="%(lineChart)s" alt="" style="max-width: 100%%;"></div>
<div><img class="panel" src="%(barChart)s" alt="" style="max-width: 100%%;"></div>
<div><div class="panel">
<table class="table table-striped">
<thead><tr><th></th>%(timingHeader)s</tr></thead>
<tbody>%(timingTable)s</tbody>
</table></div></div></div>
"""

groupedBarTemplate = """
<!DOCTYPE html>
<meta charset="utf-8">
<style>
body {
      font: 10px sans-serif;
}
.axis path,
.axis line {
    fill: none;
      stroke: #000;
        shape-rendering: crispEdges;
}
.bar {
    fill: steelblue;
}
.x.axis path {
    display: none;
}
</style>
<body>
<h1>Metrics Representation and Analysis for method : %(methodName)s</h1>
<script src="http://d3js.org/d3.v3.min.js"></script>
<script>
var margin = {top: 20, right: 20, bottom: 30, left: 40},
    width = 960 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;
var x0 = d3.scale.ordinal()
     .rangeRoundBands([0, width], .1);
var x1 = d3.scale.ordinal();
var y = d3.scale.linear()
    .range([height, 0]);
var color = d3.scale.ordinal()
     .range(["#98abc5", "#8a89a6", "#7b6888", "#6b486b", "#a05d56", "#d0743c", "#ff8c00", "#d0859b", "#c0743f",]);
var xAxis = d3.svg.axis()
     .scale(x0)
     .orient("bottom");
var yAxis = d3.svg.axis()
     .scale(y)
     .orient("left")
     .tickFormat(d3.format(".2s"));
var svg = d3.select("body").append("svg")
     .attr("width", width + margin.left + margin.right)
     .attr("height", height + margin.top + margin.bottom)
     .append("g")
     .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
d3.csv(%(metricsFile)s, function(error, data) {
  var ageNames = d3.keys(data[0]).filter(function(key) { return key !== "LibName"; });
  data.forEach(function(d) {
    d.ages = ageNames.map(function(name) { return {name: name, value: +d[name]}; });
  });
  x0.domain(data.map(function(d) { return d.LibName; }));
  x1.domain(ageNames).rangeRoundBands([0, x0.rangeBand()]);
  y.domain([0, d3.max(data, function(d) { return d3.max(d.ages, function(d) { return d.value; }); })]);
  svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis);
  svg.append("g")
      .attr("class", "y axis")
      .call(yAxis)
      .append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 6)
      .attr("dy", ".71em")
      .style("text-anchor", "end")
      .text("Metric Value");
  var state = svg.selectAll(".state")
      .data(data)
      .enter().append("g")
      .attr("class", "g")
      .attr("transform", function(d) { return "translate(" + x0(d.LibName) + ",0)"; });
  state.selectAll("rect")
      .data(function(d) { return d.ages; })
      .enter().append("rect")
      .attr("width", x1.rangeBand())
      .attr("x", function(d) { return x1(d.name); })
      .attr("y", function(d) { return y(d.value); })
      .attr("height", function(d) { return height - y(d.value); })
      .style("fill", function(d) { return color(d.name); });
  var legend = svg.selectAll(".legend")
      .data(ageNames.slice().reverse())
      .enter().append("g")
      .attr("class", "legend")
      .attr("transform", function(d, i) { return "translate(0," + i * 20 + ")"; });
  legend.append("rect")
      .attr("x", width - 18)
      .attr("width", 18)
      .attr("height", 18)
      .style("fill", color);
  legend.append("text")
      .attr("x", width - 24)
      .attr("y", 9)
      .attr("dy", ".35em")
      .style("text-anchor", "end")
      .text(function(d) { return d; });
});
</script>
"""

progressBarStyle = "%;-webkit-border-radius:4px 4px 4px 4px;-moz-border-radius:4px 4px 4px 4px;border-radius:4px 4px 4px 4px;"
