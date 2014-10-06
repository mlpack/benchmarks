// Define namespace: rc = runtime-comparison.
var rc = rc = rc || {};

// Remove everything on the page that belongs to us.
rc.clear = function()
{
  // Only things that belong to us are in the chart.
  clearChart();
}

// Remove everything we have in the chart.
rc.clearChart = function()
{
  d3.select("svg").remove();
  d3.selectAll(".d3-tip").remove();
  d3.selectAll(".library-select-title").remove();
  d3.selectAll(".library-select-div").remove();
  d3.selectAll(".dataset-select-title").remove();
  d3.selectAll(".dataset-select-div").remove();
}

// Build the chart and display it on screen.
rc.buildChart = function()
{
   // Set up scales.
  var group_scale = d3.scale.ordinal()
      .domain(datasets.map(function(d) { return d; }).reduce(function(p, c) { if(active_datasets[c] == true) { p.push(c); } return p; }, []))
      .rangeRoundBands([0, width], .1);

  var library_scale = d3.scale.ordinal()
      .domain(libraries.map(function(d) { return d; }).reduce(function(p, c) { if(active_libraries[c] == true) { p.push(c); } return p; }, []))
      .rangeRoundBands([0, group_scale.rangeBand()]);

  var max_runtime = d3.max(results[0].values, function(d) { if(active_datasets[d[4]] == false || active_libraries[d[3]] == false) { return 0; } else { return mapRuntime(d[0], 0); } });

  var runtime_scale = d3.scale.linear()
      .domain([0, max_runtime])
      .range([height, 0]);

  // Set up axes.
  var xAxis = d3.svg.axis().scale(group_scale).orient("bottom");
  var yAxis = d3.svg.axis().scale(runtime_scale).orient("left").tickFormat(d3.format(".2s"));

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
      .text("Runtime (s)");

  // Create groups.
  var group = svg.selectAll(".group")
      .data(datasets.map(function(d) { return d; }).reduce(function(p, c) { if(active_datasets[c] == true) { p.push(c); } return p; }, []))
      .enter().append("g")
      .attr("class", "g")
      .attr("transform", function(d) { return "translate(" + group_scale(d) + ", 0)"; });

  // Create tooltips.
  var tip = d3.tip()
      .attr("class", "d3-tip")
      .offset([-10, 0])
      .html(function(d) {
          var runtime = d[0];
          if (d[0] != ">9000" && d[0] != "failure") { runtime = d[0].toFixed(1); }
          return "<strong>Runtime for " + d[3] + ":</strong> <span style='color:yellow'>" + runtime + "s</span>"; }
      );

  svg.call(tip);

  // Add all of the data points.
  group.selectAll("rect")
    .data(function(d) // For a given dataset d, collect all of the data points for that dataset.
        {
          var ret = [];
          for(i = 0; i < results[0].values.length; i++)
          {
            if(results[0].values[i][4] == d && active_libraries[results[0].values[i][3]] == true)
            {
              ret.push(results[0].values[i]);
            }
          }
          return ret;
        })
    .enter().append("rect")
        .attr("width", library_scale.rangeBand())
        .attr("x", function(d) { return library_scale(d[3]); })
        .attr("y", function(d) { return runtime_scale(mapRuntime(d[0], max_runtime)); })
        .attr("height", function(d) { return height - runtime_scale(mapRuntime(d[0], max_runtime)); })
        .style("fill", function(d) { return color(d[3]); })
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
      .on('click', function() { rc.enableAllLibraries(); });
  librarySelectTitle.append("div")
      .attr("class", "library-select-title-bar")
      .text("|");
  librarySelectTitle.append("div")
      .attr("class", "library-select-title-disable-all")
      .text("disable all")
      .on('click', function() { rc.disableAllLibraries(); });
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
      .attr("onClick", function(d, i) { return "rc.toggleLibrary(\"" + d + "\");"; });

  libraryDivs.append("label")
      .attr('for', function(d) { return d + '-library-checkbox'; })
      .attr('class', 'library-select-label')
      .text(function(d) { return d; });

  // Add a clear box.
  d3.select(".legendholder").append("div").attr("class", "clear");

  var datasetSelectTitle = d3.select(".legendholder").append("div")
      .attr("class", "dataset-select-title");
  datasetSelectTitle.append("div")
      .attr("class", "dataset-select-title-text")
      .text("Datasets:");
  datasetSelectTitle.append("div")
      .attr("class", "dataset-select-title-open-paren")
      .text("(");
  datasetSelectTitle.append("div")
      .attr("class", "dataset-select-title-enable-all")
      .text("enable all")
      .on('click', function() { rc.enableAllDatasets(); });
  datasetSelectTitle.append("div")
      .attr("class", "dataset-select-title-bar")
      .text("|");
  datasetSelectTitle.append("div")
      .attr("class", "dataset-select-title-disable-all")
      .text("disable all")
      .on('click', function() { rc.disableAllDatasets(); });
  datasetSelectTitle.append("div")
      .attr("class", "dataset-select-title-close-paren")
      .text(")");

  // Add another legend for the datasets.
  var datasetDivs = d3.select(".legendholder").selectAll(".dataset-select-div")
      .data(datasets)
      .enter()
      .append("div")
      .attr("class", "dataset-select-div")
      .attr("id", function(d) { return d + "-dataset-checkbox-div"; });

  // Imitate color boxes so things line up.
  datasetDivs.append("label")
      .attr('for', function(d) { return d + "-dataset-checkbox"; })
      .attr('class', 'dataset-select-color');

  datasetDivs.append("input")
      .property("checked", function(d) { return active_datasets[d]; })
      .attr("type", "checkbox")
      .attr("id", function(d) { return d + "-dataset-checkbox"; })
      .attr("class", "dataset-select-box")
      .attr("onClick", function(d) { return "rc.toggleDataset(\"" + d + "\");"; });

  datasetDivs.append("label")
      .attr('for', function(d) { return d + '-dataset-checkbox'; })
      .attr('class', 'dataset-select-label')
      .text(function(d) { return d; });
}

// Toggle a library to on or off.
rc.toggleLibrary = function(library)
{
  active_libraries[library] = !active_libraries[library];

  clearChart();
  buildChart();
}

// Toggle a dataset to on or off.
rc.toggleDataset = function(dataset)
{
  active_datasets[dataset] = !active_datasets[dataset];

  clearChart();
  buildChart();
}

// Set all libraries on.
rc.enableAllLibraries = function()
{
  for (v in active_libraries) { active_libraries[v] = true; }

  clearChart();
  buildChart();
}

// Set all libraries off.
rc.disableAllLibraries = function()
{
  for (v in active_libraries) { active_libraries[v] = false; }

  clearChart();
  buildChart();
}

// Set all datasets on.
rc.enableAllDatasets = function()
{
  for (v in active_datasets) { active_datasets[v] = true; }

  clearChart();
  buildChart();
}

// Set all datasets off.
rc.disableAllDatasets = function()
{
  for (v in active_datasets) { active_datasets[v] = false; }

  clearChart();
  buildChart();
}
