// Define namespace: mc = metric-comparison.
var mc = mc = mc || {};

// Remove everything on the page that belongs to us.
mc.clear = function()
{
  // Only things that belong to us are in the chart.
  clearChart();
}

// Remove everything we have in the chart.
mc.clearChart = function()
{
  d3.select("svg").remove();
  d3.selectAll(".d3-tip").remove();
  d3.selectAll(".library-select-title").remove();
  d3.selectAll(".library-select-div").remove();
  d3.selectAll(".dataset-select-title").remove();
  d3.selectAll(".dataset-select-div").remove();
}

// Build the chart and display it on screen.
mc.buildChart = function()
{
  // Set up scales.
  var group_scale = d3.scale.ordinal()
    .domain(metric_names.map(function(d) { return d; }).reduce(function(p, c) { if(active_metrics[c] == true) { p.push(c); } return p; }, []))
    .rangeRoundBands([0, width], .1);
  var library_scale = d3.scale.ordinal()
    .domain(libraries.map(function(d) { return d; }).reduce(function(p, c) { if(active_libraries[c] == true) { p.push(c); } return p; }, []))
    .rangeRoundBands([0, group_scale.rangeBand()]);
  var max_score = 3

  var score_scale = d3.scale.linear()
    .domain([0, max_score])
    .range([height, 0]);

  // Set up axes.
  var xAxis = d3.svg.axis().scale(group_scale).orient("bottom");
  var yAxis = d3.svg.axis().scale(score_scale).orient("left").tickFormat(d3.format(".2s"));

  // Create svg object.
  var svg = d3.select(".svgholder").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  // Add x axis.
  svg.append("g").attr("id", "xaxis")
    .attr("class", "x axis")
    .attr("transform", "translate(0, " + height + ")")
    .call(xAxis)
    .selectAll("text")
    .style("text-anchor", "end")
    .attr("dx", "-.8em")
    .attr("dy", ".15em")
    .attr("transform", "rotate(-65)");

  // Add y axis.
  svg.append("g")
    .attr("class", "y axis")
    .call(yAxis)
    .append("text")
    .attr("transform", "rotate(-90)")
    .attr("y", 6)
    .attr("dy", ".71em")
    .style("text-anchor", "end")
    .text("Metric Score");

  // Create groups.
  var group = svg.selectAll(".group")
    .data(metric_names.map(function(d) { return d; }).reduce(function(p, c) { if(active_metrics[c] == true) { p.push(c); } return p; }, []))
    .enter().append("g")
    .attr("class", "g")
    .attr("transform", function(d) { return "translate(" + group_scale(d) + ", 0)"; });

  // Create tooltips.
  var tip = d3.tip()
    .attr("class", "d3-tip")
    .offset([-10, 0])
    .html(function(d) {
        var score = d[0];
        if (d[0] != "") { score = d[0].toFixed(3); }
        return "<strong>Score for " + d[1] + ":</strong> <span style='color:yellow'>" + score + "s</span>"; });

  svg.call(tip);
  // Add all of the data points.
  group.selectAll("rect")
    .data(function(d) // For a given dataset d, collect all of the data points for that dataset.
        {
        var ret = [];
        for(i = 0; i < results[0].values.length; i++)
        {
          var json = jQuery.parseJSON(results[0].values[i][0]);
          $.each(json, function (k, data) {
            if((k == d) && active_libraries[results[0].values[i][3]] == true) { ret.push([data, results[0].values[i][3], k]); }
          })
        }
        return ret;
        })
  .enter().append("rect")
    .attr("width", library_scale.rangeBand())
    .attr("x", function(d) { return library_scale(d[1]); })
    .attr("y", function(d) { return score_scale(d[0], max_score); })
    .attr("height", function(d) { return height - score_scale(d[0]); })
    .style("fill", function(d) { return color(d[1]); })
    .on('mouseover', tip.show)
    .on('mouseout', tip.hide);

  // Add a horizontal legend at the bottom.
  var librarySelectTitle = d3.select(".legendholder").append("div")
    .attr("class", "library-select-title");
  librarySelectTitle.append("div")
    .attr("class", "library-select-title-text")
    .text("Libraries:");
  librarySelectTitle.append("div")
    .attr("class", "library-select-title-open-paren")
    .text("(");
  librarySelectTitle.append("div")
    .attr("class", "library-select-title-enable-all")
    .text("enable all")
    .on('click', function() { mc.enableAllLibraries(); });
  librarySelectTitle.append("div")
    .attr("class", "library-select-title-bar")
    .text("|");
  librarySelectTitle.append("div")
    .attr("class", "library-select-title-disable-all")
    .text("disable all")
    .on('click', function() { mc.disableAllLibraries(); });
  librarySelectTitle.append("div")
    .attr("class", "library-select-title-close-paren")
    .text(")");

  var libraryDivs = d3.select(".legendholder").selectAll("input")
    .data(libraries)
    .enter()
    .append("div")
    .attr("class", "library-select-div")
    .attr("id", function(d) { return d + '-library-checkbox-div'; });

  libraryDivs.append("label")
    .attr('for', function(d) { return d + '-library-checkbox'; })
    .style('background', color)
    .attr('class', 'library-select-color');
  libraryDivs.append("input")
    .property("checked", function(d) { return active_libraries[d]; })
    .attr("type", "checkbox")
    .attr("id", function(d) { return d + '-library-checkbox'; })
    .attr('class', 'library-select-box')
    .attr("onClick", function(d, i) { return "mc.toggleLibrary(\"" + d + "\");"; });

  libraryDivs.append("label")
    .attr('for', function(d) { return d + '-library-checkbox'; })
    .attr('class', 'library-select-label')
    .text(function(d) { return d; });

  // Add a clear box.
  d3.select(".legendholder").append("div").attr("class", "clear");

  var metricSelectTitle = d3.select(".legendholder").append("div")
    .attr("class", "dataset-select-title");
  metricSelectTitle.append("div")
    .attr("class", "dataset-select-title-text")
    .text("Datasets:");
  metricSelectTitle.append("div")
    .attr("class", "dataset-select-title-open-paren")
    .text("(");
  metricSelectTitle.append("div")
    .attr("class", "dataset-select-title-enable-all")
    .text("enable all")
    .on('click', function() { mc.enableAllMetrics(); });
  metricSelectTitle.append("div")
    .attr("class", "dataset-select-title-bar")
    .text("|");
  metricSelectTitle.append("div")
    .attr("class", "dataset-select-title-disable-all")
    .text("disable all")
    .on('click', function() { mc.disableAllMetrics(); });
  metricSelectTitle.append("div")
    .attr("class", "dataset-select-title-close-paren")
    .text(")");

  // Add another legend for the datasets.
  var metricDivs = d3.select(".legendholder").selectAll(".dataset-select-div")
    .data(metric_names)
    .enter()
    .append("div")
    .attr("class", "dataset-select-div")
    .attr("id", function(d) { return d + "-dataset-checkbox-div"; });

  // Imitate color boxes so things line up.
  metricDivs.append("label")
    .attr('for', function(d) { return d + "-dataset-checkbox"; })
    .attr('class', 'dataset-select-color');

  metricDivs.append("input")
    .property("checked", function(d) { return active_metrics[d]; })
    .attr("type", "checkbox")
    .attr("id", function(d) { return d + "-dataset-checkbox"; })
    .attr("class", "dataset-select-box")
    .attr("onClick", function(d) { return "mc.toggleMetric(\"" + d + "\");"; });

  metricDivs.append("label")
    .attr('for', function(d) { return d + '-dataset-checkbox'; })
    .attr('class', 'dataset-select-label')
    .text(function(d) { return d; });
}

// Toggle a library to on or off.
mc.toggleLibrary = function(library)
{
  active_libraries[library] = !active_libraries[library];

  clearChart();
  buildChart();
}

// Toggle a metric to on or off.
mc.toggleMetric = function(metric)
{
  active_metrics[metric] = !active_metrics[metric];

  clearChart();
  buildChart();
}

// Set all libraries on.
mc.enableAllLibraries = function()
{
  for (v in active_libraries) { active_libraries[v] = true; }

  clearChart();
  buildChart();
}

// Set all libraries off.
mc.disableAllLibraries = function()
{
  for (v in active_libraries) { active_libraries[v] = false; }

  clearChart();
  buildChart();
}

// Set all metrics on.
mc.enableAllMetrics = function()
{
  for (v in active_metrics) { active_metrics[v] = true; }

  clearChart();
  buildChart();
}

// Set all metrics off.
mc.disableAllMetrics = function()
{
  for (v in active_metrics) { active_metrics[v] = false; }

  clearChart();
  buildChart();
}