// Define namespace: mc = metric-comparison.
var mpc = mpc = mpc || {};

mpc.method_name = "";
mpc.param_name = "";
mpc.dataset_name = "";
mpc.libraries = [];
mpc.datasets = []
mpc.active_metrics = [];
mpc.active_libraries = [];
mpc.metric_names = [];
mpc.results = [];

// This chart type has been selected.  What do we do now?
mpc.onTypeSelect = function()
{
  var selectHolder = d3.select(".selectholder");
  selectHolder.append("label")
      .attr("for", "method_select")
      .attr("class", "method-select-label")
      .text("Select method:");
  selectHolder.append("select")
      .attr("id", "method_select")
      .attr("onchange", "mpc.methodSelect()");
  selectHolder.append("label")
      .attr("for", "param_select")
      .attr("class", "param-select-label")
      .text("Select parameters:");
  selectHolder.append("select")
      .attr("id", "param_select")
      .attr("onchange", "mpc.paramSelect()");
  selectHolder.append("br");
  selectHolder.append("label")
      .attr("for", "main_dataset_select")
      .attr("class", "main-dataset-select-label")
      .text("Select dataset:");
  selectHolder.append("select")
      .attr("id", "main_dataset_select")
      .attr("onchange", "mpc.datasetSelect()");

  mpc.listMethods();
}

mpc.listMethods = function()
{
  var methods = db.exec("SELECT DISTINCT methods.name FROM methods, metrics WHERE methods.id=metrics.method_id AND metrics.metric<>'{}' ORDER BY name;");

  var method_select_box = document.getElementById("method_select");
  clearSelectBox(method_select_box);
  // Put new things in the list box.
  for(i = 0; i < methods[0].values.length; i++)
  {
    var new_option = document.createElement("option");
    new_option.text = methods[0].values[i];
    method_select_box.add(new_option);
  }
  method_select_box.selectedIndex = -1;

  // Clear parameters box.
  clearSelectBox(document.getElementById("param_select"));
}

// The user has selected a method.
mpc.methodSelect = function()
{
  // Extract the name of the method we selected.
  var method_select_box = document.getElementById("method_select");
  mpc.method_name = method_select_box.options[method_select_box.selectedIndex].text; // At higher scope.

  var sqlstr = "SELECT DISTINCT methods.parameters, metrics.libary_id, COUNT(DISTINCT metrics.libary_id) FROM methods, metrics WHERE methods.name == '" + mpc.method_name + "' AND methods.id == metrics.method_id GROUP BY methods.parameters;";

  var params = db.exec(sqlstr);

  // Loop through results and fill the second list box.
  var param_select_box = document.getElementById("param_select");
  clearSelectBox(param_select_box);

  // Put in the new options.
  for (i = 0; i < params[0].values.length; i++)
  {
    var new_option = document.createElement("option");
    if (params[0].values[i][0])
    {
      new_option.text = params[0].values[i][0] + " (" + params[0].values[i][2] + " libraries)";
    }
    else
    {
      new_option.text = "[no parameters] (" + params[0].values[i][2] + " libraries)";
    }
    param_select_box.add(new_option);
  }
  param_select_box.selectedIndex = -1;
}

// The user has selected parameters.
mpc.paramSelect = function()
{
  // The user has selected a library and parameters.  Now we need to
  // generate
  // a chart for all applicable datasets.
  var method_select_box = document.getElementById("method_select");
  mpc.method_name = method_select_box.options[method_select_box.selectedIndex].text;
  var param_select_box = document.getElementById("param_select");
  var param_name_full = param_select_box.options[param_select_box.selectedIndex].text;
  // Parse out actual parameters.
  mpc.param_name = param_name_full.split("(")[0].replace(/^\s+|\s+$/g, ''); // At higher scope.
  if (mpc.param_name == "[no parameters]") { mpc.param_name = ""; }

  // Given a method name and parameters, query the SQLite database for all of
  // the runs.
  var sqlstr = "SELECT DISTINCT metrics.metric, libraries.id, libraries.name, datasets.name, datasets.id " +
    "FROM metrics, datasets, methods, libraries WHERE metrics.dataset_id == datasets.id AND metrics.method_id == methods.id " +
    "AND methods.name == '" + mpc.method_name + "' AND methods.parameters == '" + mpc.param_name + "' AND libraries.id == metrics.libary_id " +
    "AND metrics.metric<>'{}' GROUP BY datasets.id, libraries.id;";
  mpc.results = db.exec(sqlstr);

  // Obtain unique list of datasets.
  mpc.datasets = mpc.results[0].values.map(function(d) { return d[3]; }).reduce(function(p, c) { if(p.indexOf(c) < 0) p.push(c); return p; }, []);
  // Obtain unique list of libraries.
  mpc.libraries = mpc.results[0].values.map(function(d) { return d[2]; }).reduce(function(p, c) { if(p.indexOf(c) < 0) p.push(c); return p; }, []);

  var dataset_select_box = document.getElementById("main_dataset_select");

  // Remove old things.
  for (i = dataset_select_box.options.length - 1; i >= 0; i--)
  {
    dataset_select_box.options[i] = null;
  }

  for (i = 0; i < mpc.datasets.length; i++)
  {
    var new_option = document.createElement("option");
    new_option.text = mpc.datasets[i];
    dataset_select_box.add(new_option);
  }
}

mpc.datasetSelect = function()
{
  // The user has selected a method, parameters, and a dataset.  Now we need to generate a chart.  We have method_name and param_name.
  var dataset_select_box = document.getElementById("main_dataset_select");
  mpc.dataset_name = dataset_select_box.options[dataset_select_box.selectedIndex].text;

  // Okay, now get the results of the query for that method, parameters, and dataset.
  var sqlstr = "SELECT metrics.metric, metrics.build_id, builds.build, libraries.name from metrics, methods, libraries, builds, datasets WHERE methods.id == metrics.method_id AND methods.name == '" + mpc.method_name + "' AND methods.parameters == '" + mpc.param_name + "' AND metrics.libary_id == libraries.id AND builds.id == metrics.build_id AND datasets.id == metrics.dataset_id AND datasets.name == '" + mpc.dataset_name + "' GROUP BY metrics.build_id;";
  mpc.results = db.exec(sqlstr);

  // Obtain unique list of metric names.
  mpc.metric_names = []
  for(i = 0; i < mpc.results[0].values.length; i++)
  {
    var json = jQuery.parseJSON(mpc.results[0].values[i][0]);
    $.each(json, function (k, d) {
      if(mpc.metric_names.indexOf(k) < 0) mpc.metric_names.push(k);
    })
  }

  // By default, everything is active.
  mpc.active_metrics = {};
  for(i = 0; i < mpc.metric_names.length; i++)
  {
    mpc.active_metrics[mpc.metric_names[i]] = true;
  }

  mpc.active_libraries = {};
  for(i = 0; i < mpc.libraries.length; i++)
  {
    mpc.active_libraries[mpc.libraries[i]] = true;
  }

  clearChart();
  buildChart();
}

// Remove everything on the page that belongs to us.
mpc.clear = function()
{
  // Only things that belong to us are in the chart.
  mpc.clearChart();
}

// Remove everything we have in the chart.
mpc.clearChart = function()
{
  d3.select("svg").remove();
  d3.selectAll(".d3-tip").remove();
  d3.selectAll(".library-select-title").remove();
  d3.selectAll(".library-select-div").remove();
  d3.selectAll(".dataset-select-title").remove();
  d3.selectAll(".dataset-select-div").remove();
  d3.selectAll(".runtime-table").remove();
}

// Build the chart and display it on screen.
mpc.buildChart = function()
{
  // Get lists of active libraries and active datasets.
  var active_library_list = mpc.libraries.map(function(d) { return d; }).reduce(function(p, c) { if(mpc.active_libraries[c] == true) { p.push(c); } return p; }, []);
  var active_dataset_list = mpc.metric_names.map(function(d) { return d; }).reduce(function(p, c) { if(mpc.active_metrics[c] == true) { p.push(c); } return p; }, []);

  // Set up scales.
  var max_score = 0
  for(i = 0; i < mpc.results[0].values.length; i++)
  {
    var json = jQuery.parseJSON(mpc.results[0].values[i][0]);
    $.each(json, function (k, data) {
      if (data > max_score) max_score = data;
    })
  }
  var group_scale = d3.scale.ordinal()
    .domain(active_dataset_list)
    .rangeRoundBands([0, width], .1);
  var library_scale = d3.scale.ordinal()
    .domain(active_library_list)
    .rangeRoundBands([0, group_scale.rangeBand()]);

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
    .data(mpc.metric_names.map(function(d) { return d; }).reduce(function(p, c) { if(mpc.active_metrics[c] == true) { p.push(c); } return p; }, []))
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
        return "<strong>Score for " + d[1] + ":</strong> <span style='color:yellow'>" + score + "</span>"; });

  svg.call(tip);

  // Add all of the data points.
  group.selectAll("rect")
    .data(function(d) // For a given dataset d, collect all of the data points for that dataset.
        {
        var ret = [];
        for(i = 0; i < mpc.results[0].values.length; i++)
        {
          var json = jQuery.parseJSON(mpc.results[0].values[i][0]);
          $.each(json, function (k, data) {
            if((k == d) && mpc.active_libraries[mpc.results[0].values[i][3]] == true) { ret.push([data, mpc.results[0].values[i][3], k]); }
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
    .on('click', function() { mpc.enableAllLibraries(); });
  librarySelectTitle.append("div")
    .attr("class", "library-select-title-bar")
    .text("|");
  librarySelectTitle.append("div")
    .attr("class", "library-select-title-disable-all")
    .text("disable all")
    .on('click', function() { mpc.disableAllLibraries(); });
  librarySelectTitle.append("div")
    .attr("class", "library-select-title-close-paren")
    .text(")");

  var libraryDivs = d3.select(".legendholder").selectAll("input")
    .data(mpc.libraries)
    .enter()
    .append("div")
    .attr("class", "library-select-div")
    .attr("id", function(d) { return d + '-library-checkbox-div'; });

  libraryDivs.append("label")
    .attr('for', function(d) { return d + '-library-checkbox'; })
    .style('background', color)
    .attr('class', 'library-select-color');
  libraryDivs.append("input")
    .property("checked", function(d) { return mpc.active_libraries[d]; })
    .attr("type", "checkbox")
    .attr("id", function(d) { return d + '-library-checkbox'; })
    .attr('class', 'library-select-box')
    .attr("onClick", function(d, i) { return "mpc.toggleLibrary(\"" + d + "\");"; });

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
    .on('click', function() { mpc.enableAllMetrics(); });
  metricSelectTitle.append("div")
    .attr("class", "dataset-select-title-bar")
    .text("|");
  metricSelectTitle.append("div")
    .attr("class", "dataset-select-title-disable-all")
    .text("disable all")
    .on('click', function() { mpc.disableAllMetrics(); });
  metricSelectTitle.append("div")
    .attr("class", "dataset-select-title-close-paren")
    .text(")");

  // Add another legend for the datasets.
  var metricDivs = d3.select(".legendholder").selectAll(".dataset-select-div")
    .data(mpc.metric_names)
    .enter()
    .append("div")
    .attr("class", "dataset-select-div")
    .attr("id", function(d) { return d + "-dataset-checkbox-div"; });

  // Imitate color boxes so things line up.
  metricDivs.append("label")
    .attr('for', function(d) { return d + "-dataset-checkbox"; })
    .attr('class', 'dataset-select-color');

  metricDivs.append("input")
    .property("checked", function(d) { return mpc.active_metrics[d]; })
    .attr("type", "checkbox")
    .attr("id", function(d) { return d + "-dataset-checkbox"; })
    .attr("class", "dataset-select-box")
    .attr("onClick", function(d) { return "mpc.toggleMetric(\"" + d + "\");"; });

  metricDivs.append("label")
    .attr('for', function(d) { return d + '-dataset-checkbox'; })
    .attr('class', 'dataset-select-label')
    .text(function(d) { return d; });

  // Now add a table of runtimes at the bottom.
  var table = d3.select(".svgholder").append("table")
      .attr("class", "runtime-table");
  var thead = table.append("thead");
  var tbody = table.append("tbody");

  active_library_list.unshift("metric");
  var hrow = thead.append("tr").selectAll("th")
      .data(active_library_list)
      .enter()
      .append("th")
      .text(function(d) { return d; });

  var rows = tbody.selectAll("tr")
      .data(active_dataset_list)
      .enter()
      .append("tr");

  var resultFormat = d3.format("x>7.2f");
  rows.selectAll("td")
      .data(function(d) {
          var ret = [d];

          for(i = 1; i < active_library_list.length; i++) // Skip "metric".
          {
            ret.push(['---']);
          }

          for(i = 0; i < mpc.results[0].values.length; i++)
          {
            var library = mpc.results[0].values[i][3];
            var json = jQuery.parseJSON(mpc.results[0].values[i][0]);
            $.each(json, function (k, data) {
              if((k == d) && mpc.active_libraries[library] == true) {
                ret[active_library_list.indexOf(library)] = ([data, mpc.results[0].values[i][3], k]);
              }
            })
          }
          return ret;
      }).enter()
      .append("td")
      .html(function(d) { if (d[0] != "failure" && d[0] != "---") { if (typeof d == "string") { return d; } else { if (d[0] == ">9000") { return ">9000s"; } else { return "&nbsp;" + String(resultFormat(d[0])).replace(/x/g, '&nbsp;') + "&nbsp;"; } } } else { return d[0]; } })
      .attr("class", function(d) { if (typeof d == "string") { return "dataset-name"; } else if (d[0] == "---") { return "timing-not-run-cell"; } else if (d[0] == ">9000" || d[0] == "failure") { return "timing-text-cell"; } else { return "timing-cell"; } });
}

// Toggle a library to on or off.
mpc.toggleLibrary = function(library)
{
  mpc.active_libraries[library] = !mpc.active_libraries[library];

  clearChart();
  buildChart();
}

// Toggle a metric to on or off.
mpc.toggleMetric = function(metric)
{
  mpc.active_metrics[metric] = !mpc.active_metrics[metric];

  clearChart();
  buildChart();
}

// Set all libraries on.
mpc.enableAllLibraries = function()
{
  for (v in mpc.active_libraries) { mpc.active_libraries[v] = true; }

  clearChart();
  buildChart();
}

// Set all libraries off.
mpc.disableAllLibraries = function()
{
  for (v in mpc.active_libraries) { mpc.active_libraries[v] = false; }

  clearChart();
  buildChart();
}

// Set all metrics on.
mpc.enableAllMetrics = function()
{
  for (v in mpc.active_metrics) { mpc.active_metrics[v] = true; }

  clearChart();
  buildChart();
}

// Set all metrics off.
mpc.disableAllMetrics = function()
{
  for (v in mpc.active_metrics) { mpc.active_metrics[v] = false; }

  clearChart();
  buildChart();
}
