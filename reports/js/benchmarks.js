// Load benchmark.db.  Later, we will do something cool with it, once I figure
// out how.  If this is file:///, suggest that the user start a server since
// XMLHttpRequests may not work.
if(window.location.protocol == "file:")
{
  var holder = document.getElementById("selectholder");
  holder.innerHTML = "The protocol you are using is file:///.  This means that Javascript XMLHttpRequests may not work.  You should use http://.  If you are working from a local machine, consider starting a Python SimpleHTTPServer in the reports/ directory, with <pre>python -m SimpleHTTPServer</pre> and then access the site via http://.";
}
else
{
  var xhr = new XMLHttpRequest();
  xhr.open('GET', 'benchmark.db', true);
  xhr.responseType = 'arraybuffer';
  var db = new SQL.Database();

  xhr.onload = function(e) {
    var uInt8Array = new Uint8Array(this.response);
    db = new SQL.Database(uInt8Array);

    createColorMapping();
  };

  xhr.send(); // Load the dataset.
}

// "Global" variables.
var libraries; // Full list of libraries for this method and parameters.
var active_libraries; // List of active libraries for this method and parameters.
var datasets; // Full list of datasets for this method and parameters.
var active_datasets; // Full list of active datasets for this method and parameters.
var method_name; // Name of currently active method;
var param_name; // Name of currently active parameters.
var dataset_name; // Name of currently active dataset (for historical runtime view).
var results; // Results for current method and parameters.
var metric_names; // Full list of metrics for this method and parameters.
var active_metrics; // Full list of active metrics for this method and parameters.
var chartType;
var control_list_length = 0;

// Basic chart parameters.
var width = 800; // This should be parameterizable...
var height = 600; // This should be parameterizable...
var margin = { top: 20, right: 20, bottom: 120, left: 40 };

// Static bindings of library names to colors.
var color = d3.scale.ordinal().range(["#98abc5", "#8a89a6", "#7b6888", "#6b486b", "#a05d56", "#d0743c", "#ff8c00"]);

/**
 * Utility function to map runtime results, which are in seconds or ">9000" or
 * "failure", to seconds.  ">9000" maps to max, and "failure" maps to 0.
 */
function mapRuntime(runtime, max)
{
  if (runtime == ">9000") { return max; }
  else if (runtime == "failure") { return 0; }
  else { return runtime; }
}

function listMethods(chartType)
{
  // Given a chartType get all of the possible method names.
  if (chartType == "timing")
  {
    var methods = db.exec("SELECT DISTINCT methods.name FROM methods, results WHERE methods.id=results.method_id ORDER BY name;");
  }
  else if (chartType == "metric")
  {
    var methods = db.exec("SELECT DISTINCT methods.name FROM methods, metrics WHERE methods.id=metrics.method_id AND metrics.metric<>'{}' ORDER BY name;");
  }

  var method_select_box = document.getElementById("method_select");

  // Remove old things from the list box.
  for(i = method_select_box.options.length - 1; i >= 0; i--)
  {
    method_select_box.options[i] = null;
  }

  // Put new things in the list box.
  for(i = 0; i < methods[0].values.length; i++)
  {
    var new_option = document.createElement("option");
    new_option.text = methods[0].values[i];
    method_select_box.add(new_option);
  }
  method_select_box.selectedIndex = -1;

  // Clear parameters box.
  var param_select_box = document.getElementById("param_select");
  for (i = param_select_box.options.length - 1; i >= 0; i--)
  {
    param_select_box.options[i] = null;
  }
}

function methodSelect(chartType)
{
  // Extract the name of the method we selected.
  var method_select_box = document.getElementById("method_select");
  method_name = method_select_box.options[method_select_box.selectedIndex].text; // At higher scope.

  // Now get all of the possible parameters for that function and chartType.
  if (chartType == "timing")
  {
    var sqlstr = "SELECT methods.parameters, results.libary_id FROM methods, results WHERE methods.name == '" + method_name + "' AND methods.id == results.method_id GROUP BY methods.parameters;";
  }
  else if (chartType == "metric")
  {
    var sqlstr = "SELECT methods.parameters, metrics.libary_id FROM methods, metrics WHERE methods.name == '" + method_name + "' AND methods.id == metrics.method_id GROUP BY methods.parameters;";
  }
  var params = db.exec(sqlstr);

  // Loop through results and fill the second list box.
  var param_select_box = document.getElementById("param_select");

  // Remove old things.
  for(i = param_select_box.options.length - 1; i >= 0; i--)
  {
    param_select_box.options[i] = null;
  }

  // Put in the new options.
  for(i = 0; i < params[0].values.length; i++)
  {
    var new_option = document.createElement("option");
    if(params[0].values[i][0])
    {
      new_option.text = params[0].values[i][0] + " (" + params[0].values[i][1] + " libraries)";
    }
    else
    {
      new_option.text = "[no parameters] (" + params[0].values[i][1] + " libraries)";
    }
    param_select_box.add(new_option);
  }
  param_select_box.selectedIndex = -1;
}

function paramSelect()
{
  // The user has selected a library and parameters.  Now we need to generate
  // a chart for all applicable datasets.
  var method_select_box = document.getElementById("method_select");
  var method_name = method_select_box.options[method_select_box.selectedIndex].text;
  var param_select_box = document.getElementById("param_select");
  var param_name_full = param_select_box.options[param_select_box.selectedIndex].text;
  // Parse out actual parameters.
  param_name = param_name_full.split("(")[0].replace(/^\s+|\s+$/g, ''); // At higher scope.
  if (param_name == "[no parameters]")
  {
    param_name = "";
  }

  // Given a method name and parameters, query the SQLite database for all of
  // the runs.
  var sqlstr = "SELECT DISTINCT results.time, results.var, libraries.id, libraries.name, datasets.name, datasets.id " +
    "FROM results, datasets, methods, libraries WHERE results.dataset_id == datasets.id AND results.method_id == methods.id " +
    "AND methods.name == '" + method_name + "' AND methods.parameters == '" + param_name + "' AND libraries.id == results.libary_id " +
    "GROUP BY datasets.id, libraries.id;";
  results = db.exec(sqlstr);

  // Obtain unique list of datasets.
  datasets = results[0].values.map(function(d) { return d[4]; }).reduce(function(p, c) { if(p.indexOf(c) < 0) p.push(c); return p; }, []);
  // Obtain unique list of libraries.
  libraries = results[0].values.map(function(d) { return d[3]; }).reduce(function(p, c) { if(p.indexOf(c) < 0) p.push(c); return p; }, []);

  // By default, everything is active.
  active_datasets = {};
  for(i = 0; i < datasets.length; i++)
  {
    active_datasets[datasets[i]] = true;
  }

  active_libraries = {};
  for(i = 0; i < libraries.length; i++)
  {
    active_libraries[libraries[i]] = true;
  }

  clearChart();
  buildChart();
}

function clearChart()
{
  d3.select("svg").remove();
  d3.selectAll(".d3-tip").remove();
  d3.selectAll(".library-select-title").remove();
  d3.selectAll(".library-select-div").remove();
  d3.selectAll(".dataset-select-title").remove();
  d3.selectAll(".dataset-select-div").remove();
}

function clearMethodControl()
{
  d3.selectAll(".methodcontrol").remove();
  d3.selectAll(".add_method_button").remove();
  d3.selectAll(".clear_methods_button").remove();
  d3.selectAll(".redraw_methods_button").remove();
}

function buildChart()
{
  if (chartType == "algorithm-parameter-comparison") { rc.buildChart(); }
  else if (chartType == "historical-comparison") { hc.buildChart(); }
  else if (chartType == "dataset-comparison") { /*buildDatasetComparisonChart();*/ }
  else if (chartType == "metric-comparison") { buildMetricChart(); }
}

function toggleLibrary(library)
{
  active_libraries[library] = !active_libraries[library];

  clearChart();
  buildChart();
}

function toggleDataset(dataset)
{
  active_datasets[dataset] = !active_datasets[dataset];

  clearChart();
  buildChart();
}

function enableAllLibraries()
{
  for (v in active_libraries) { active_libraries[v] = true; }

  clearChart();
  buildChart();
}

function disableAllLibraries()
{
  for (v in active_libraries) { active_libraries[v] = false; }

  clearChart();
  buildChart();
}

function enableAllDatasets()
{
  for (v in active_datasets) { active_datasets[v] = true; }

  clearChart();
  buildChart();
}

function disableAllDatasets()
{
  for (v in active_datasets) { active_datasets[v] = false; }

  clearChart();
  buildChart();
}

// Query for the list of libraries, and create a mapping from library names to
// colors for use by the graphs.
function createColorMapping()
{
  var librarylist = db.exec("SELECT libraries.name FROM libraries;");

  libraries = librarylist[0].values.map(function(d) { return d[0]; }).reduce(function(p, c) { if(p.indexOf(c) < 0) p.push(c); return p; }, []);
  color.domain(libraries);
}
function chartTypeSelect()
{
  var radios = document.getElementsByName('chart-type');
  for (i = 0; i < radios.length; i++)
  {
    if (radios[i].checked)
    {
      chartType = radios[i].value;
      break;
    }
  }

  // Ditch whatever's there.
  clearChart();
  clearMethodControl();
  var selectHolder = d3.select(".selectholder");
  selectHolder.selectAll('label').remove();
  selectHolder.selectAll('select').remove();
  selectHolder.selectAll('br').remove();

  if (chartType == "algorithm-parameter-comparison")
  {
    selectHolder.append("label")
      .attr("for", "method_select")
      .attr("class", "method-select-label")
      .text("Select method:");
    selectHolder.append("select")
      .attr("id", "method_select")
      .attr("onchange", "methodSelect('timing')");
    selectHolder.append("label")
      .attr("for", "param_select")
      .attr("class", "param-select-label")
      .text("Select parameters:");
    selectHolder.append("select")
      .attr("id", "param_select")
      .attr("onchange", "paramSelect()");

    listMethods("timing");
  }
  else if (chartType == "historical-comparison")
  {
    selectHolder.append("label")
      .attr("for", "method_select")
      .attr("class", "method-select-label")
      .text("Select method:");
    selectHolder.append("select")
      .attr("id", "method_select")
      .attr("onchange", "methodSelect('timing')");
    selectHolder.append("label")
      .attr("for", "param_select")
      .attr("class", "param-select-label")
      .text("Select parameters:");
    selectHolder.append("select")
      .attr("id", "param_select")
      .attr("onchange", "paramSelectHistorical()");
    selectHolder.append("br");
    selectHolder.append("label")
      .attr("for", "main_dataset_select")
      .attr("class", "main-dataset-select-label")
      .text("Select dataset:");
    selectHolder.append("select")
      .attr("id", "main_dataset_select")
      .attr("onchange", "datasetSelectTiming()");

    listMethods("timing");
  }
  else if (chartType == "metric-comparison")
  {
    selectHolder.append("label")
      .attr("for", "method_select")
      .attr("class", "method-select-label")
      .text("Select method:");
    selectHolder.append("select")
      .attr("id", "method_select")
      .attr("onchange", "methodSelect('metric')");
    selectHolder.append("label")
      .attr("for", "param_select")
      .attr("class", "param-select-label")
      .text("Select parameters:");
    selectHolder.append("select")
      .attr("id", "param_select")
      .attr("onchange", "paramSelectMetric()");
    selectHolder.append("br");
    selectHolder.append("label")
      .attr("for", "main_dataset_select")
      .attr("class", "main-dataset-select-label")
      .text("Select dataset:");
    selectHolder.append("select")
      .attr("id", "main_dataset_select")
      .attr("onchange", "datasetSelectMetric()");

    listMethods("metric");
  }
  else if (chartType == "dataset-comparison")
  {
    selectHolder.append("label")
        .attr("for", "main_dataset_select")
        .attr("class", "main-dataset-select-label")
        .text("Select dataset:");
    selectHolder.append("select")
        .attr("id", "main_dataset_select")
        .attr("onchange", "mainDatasetSelect()");

    listMainDatasets();
  }
}

function paramSelectMetric()
{
  // The user has selected a library and parameters.  Now we need to
  // generate
  // a chart for all applicable datasets.
  var method_select_box = document.getElementById("method_select");
  var method_name = method_select_box.options[method_select_box.selectedIndex].text;
  var param_select_box = document.getElementById("param_select");
  var param_name_full = param_select_box.options[param_select_box.selectedIndex].text;
  // Parse out actual parameters.
  param_name = param_name_full.split("(")[0].replace(/^\s+|\s+$/g, ''); // At higher scope.
  if (param_name == "[no parameters]") { param_name = ""; }

  // Given a method name and parameters, query the SQLite database for all of
  // the runs.
  var sqlstr = "SELECT DISTINCT metrics.metric, libraries.id, libraries.name, datasets.name, datasets.id " +
    "FROM metrics, datasets, methods, libraries WHERE metrics.dataset_id == datasets.id AND metrics.method_id == methods.id " +
    "AND methods.name == '" + method_name + "' AND methods.parameters == '" + param_name + "' AND libraries.id == metrics.libary_id " +
    "AND metrics.metric<>'{}' GROUP BY datasets.id, libraries.id;";
  results = db.exec(sqlstr);

  // Obtain unique list of datasets.
  datasets = results[0].values.map(function(d) { return d[3]; }).reduce(function(p, c) { if(p.indexOf(c) < 0) p.push(c); return p; }, []);
  // Obtain unique list of libraries.
  libraries = results[0].values.map(function(d) { return d[2]; }).reduce(function(p, c) { if(p.indexOf(c) < 0) p.push(c); return p; }, []);

  var dataset_select_box = document.getElementById("main_dataset_select");

  // Remove old things.
  for(i = dataset_select_box.options.length - 1; i >= 0; i--)
  {
    dataset_select_box.options[i] = null;
  }

  for(i = 0; i < datasets.length; i++)
  {
    var new_option = document.createElement("option");
    new_option.text = datasets[i];
    dataset_select_box.add(new_option);
  }
}

function listMainDatasets()
{
  // We want the list of methods and dataset combinations.  Then we will figure
  // out how many methods go with each dataset.  For now though I'll just get a
  // list of datasets...
//  var sqlstr = "SELECT DISTINCT datasets.name, methods.id, methods.name, methods.parameters from methods, datasets, results where results.dataset_id == datasets.id and results.method_id == methods.id group by results.build_id;";
  var sqlstr = "SELECT datasets.name FROM datasets;";
  results = db.exec(sqlstr);

  var dataset_select_box = document.getElementById("main_dataset_select");
  for (i = dataset_select_box.options.length - 1; i >= 0; i--)
  {
    dataset_select_box.options[i] = null;
  }
  for (i = 0; i < results[0].values.length; i++)
  {
    var new_option = document.createElement("option");
    new_option.text = results[0].values[i][0];
    dataset_select_box.add(new_option);
  }
  dataset_select_box.selectedIndex = -1;
}

function mainDatasetSelect()
{
  var dataset_select_box = document.getElementById("main_dataset_select");
  dataset_name = dataset_select_box.options[dataset_select_box.selectedIndex].text;

  // Create an empty chart.
  clearChart();
  clearMethodControl();
  buildChart();

  // Now create the legend at the bottom that will allow us to add/remove
  // methods.
  d3.selectAll(".legendholder").append("div").attr("class", "methodcontrol");

  d3.selectAll(".legendholder").append("input")
      .attr("type", "button")
      .attr("class", "add_method_button")
      .attr("onclick", "clickAddButton()")
      .attr("value", "Add another method");
  d3.selectAll(".legendholder").append("input")
      .attr("type", "button")
      .attr("class", "clear_methods_button")
      .attr("onclick", "clickClearMethods()")
      .attr("value", "Remove all methods");
  d3.selectAll(".legendholder").append("input")
      .attr("type", "button")
      .attr("class", "redraw_methods_button")
      .attr("onclick", "clickRedrawMethods()")
      .attr("value", "Redraw graph");

  control_list_length = 0;

  // Collect the results for lists of methods.
}

function clickAddButton()
{
  var newmethodcontrol = d3.selectAll(".methodcontrol").append("div").attr("class", "methodcontroldiv");

  newmethodcontrol.append("label")
      .attr("for", "method_select_" + String(control_list_length))
      .attr("class", "method-select-label")
      .text("Method:");
  newmethodcontrol.append("select")
      .attr("id", "method_select_" + String(control_list_length))
      .attr("onchange", "methodControlListSelect()");
  newmethodcontrol.append("label")
      .attr("for", "param_select_" + String(control_list_length))
      .attr("class", "param-select-label")
      .text("Parameters:");
  newmethodcontrol.append("select")
      .attr("id", "param_select_" + String(control_list_length));

  control_list_length++;
}

function paramSelectHistorical()
{
  // The user has selected a library and parameters.  Now we need to
  // generate
  // a chart for all applicable datasets.
  var method_select_box = document.getElementById("method_select");
  var method_name = method_select_box.options[method_select_box.selectedIndex].text;
  var param_select_box = document.getElementById("param_select");
  var param_name_full = param_select_box.options[param_select_box.selectedIndex].text;
  // Parse out actual parameters.
  param_name = param_name_full.split("(")[0].replace(/^\s+|\s+$/g, ''); // At higher scope.
  if (param_name == "[no parameters]") { param_name = ""; }

  // Given a method name and parameters, query the SQLite database for all of
  // the runs.
  var sqlstr = "SELECT DISTINCT results.time, results.var, libraries.id, libraries.name, datasets.name, datasets.id " +
    "FROM results, datasets, methods, libraries WHERE results.dataset_id == datasets.id AND results.method_id == methods.id " +
    "AND methods.name == '" + method_name + "' AND methods.parameters == '" + param_name + "' AND libraries.id == results.libary_id " +
    "GROUP BY datasets.id, libraries.id;";
  results = db.exec(sqlstr);

  // Obtain unique list of datasets.
  datasets = results[0].values.map(function(d) { return d[4]; }).reduce(function(p, c) { if(p.indexOf(c) < 0) p.push(c); return p; }, []);
  // Obtain unique list of libraries.
  libraries = results[0].values.map(function(d) { return d[3]; }).reduce(function(p, c) { if(p.indexOf(c) < 0) p.push(c); return p; }, []);

  var dataset_select_box = document.getElementById("main_dataset_select");

  // Remove old things.
  for(i = dataset_select_box.options.length - 1; i >= 0; i--)
  {
    dataset_select_box.options[i] = null;
  }

  for(i = 0; i < datasets.length; i++)
  {
    var new_option = document.createElement("option");
    new_option.text = datasets[i];
    dataset_select_box.add(new_option);
  }
  dataset_select_box.selectedIndex = -1;
}

function datasetSelectTiming()
{
  // The user has selected a method, parameters, and a dataset.  Now we need to generate a chart.  We have method_name and param_name.
  var dataset_select_box = document.getElementById("main_dataset_select");
  dataset_name = dataset_select_box.options[dataset_select_box.selectedIndex].text;

  // Okay, now get the results of the query for that method, parameters, and dataset.
  var sqlstr = "SELECT results.time, results.var, results.build_id, builds.build, libraries.name from results, methods, libraries, builds, datasets WHERE methods.id == results.method_id AND methods.name == '" + method_name + "' AND methods.parameters == '" + param_name + "' AND results.libary_id == libraries.id AND builds.id == results.build_id AND datasets.id == results.dataset_id AND datasets.name == '" + dataset_name + "' GROUP BY results.build_id;";
  results = db.exec(sqlstr);

  active_libraries = {};
  for(i = 0; i < libraries.length; i++)
  {
    active_libraries[libraries[i]] = true;
  }

  clearChart();
  buildChart();
}

function datasetSelectMetric()
{
  // The user has selected a method, parameters, and a dataset.  Now we need to generate a chart.  We have method_name and param_name.
  var dataset_select_box = document.getElementById("main_dataset_select");
  dataset_name = dataset_select_box.options[dataset_select_box.selectedIndex].text;

  // Okay, now get the results of the query for that method, parameters, and dataset.
  var sqlstr = "SELECT metrics.metric, metrics.build_id, builds.build, libraries.name from metrics, methods, libraries, builds, datasets WHERE methods.id == metrics.method_id AND methods.name == '" + method_name + "' AND methods.parameters == '" + param_name + "' AND metrics.libary_id == libraries.id AND builds.id == metrics.build_id AND datasets.id == metrics.dataset_id AND datasets.name == '" + dataset_name + "' GROUP BY metrics.build_id;";
  results = db.exec(sqlstr);

  // Obtain unique list of metric names.
  metric_names = []
  for(i = 0; i < results[0].values.length; i++)
  {
    var json = jQuery.parseJSON(results[0].values[i][0]);
    $.each(json, function (k, d) {
      if(metric_names.indexOf(k) < 0) metric_names.push(k);
    })
  }

  // By default, everything is active.
  active_metrics = {};
  for(i = 0; i < metric_names.length; i++)
  {
    active_metrics[metric_names[i]] = true;
  }

  active_libraries = {};
  for(i = 0; i < libraries.length; i++)
  {
    active_libraries[libraries[i]] = true;
  }

  clearChart();
  buildChart();
}

function buildMetricChart()
{
  // Set up scales.
  var group_scale = d3.scale.ordinal()
    .domain(metric_names.map(function(d) { return d; }).reduce(function(p, c) { if(active_metrics[c] == true) { p.push(c); } return p; }, []))
    .rangeRoundBands([0, width], .1);
  var library_scale = d3.scale.ordinal()
    .domain(libraries.map(function(d) { return d; }).reduce(function(p, c) { if(active_libraries[c] == true) { p.push(c); } return p; }, []))
    .rangeRoundBands([0, group_scale.rangeBand()]);
  var max_runtime = 3

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
    .data(metric_names.map(function(d) { return d; }).reduce(function(p, c) { if(active_metrics[c] == true) { p.push(c); } return p; }, []))
    .enter().append("g")
    .attr("class", "g")
    .attr("transform", function(d) { return "translate(" + group_scale(d) + ", 0)"; });

  // Create tooltips.
  // var tip = d3.tip()
  //   .attr("class", "d3-tip")
  //   .offset([-10, 0])
  //   .html(function(d) {
  //       var runtime = d[0];
  //       if (d[0] != ">9000" && d[0] != "failure") { runtime = d[0].toFixed(1); }
  //       return "<strong>Runtime for " + d[3] + ":</strong> <span style='color:yellow'>" + runtime + "s</span>"; });

  // svg.call(tip);
  // Add all of the data points.
  group.selectAll("rect")
    .data(function(d) // For a given dataset d, collect all of the data points for that dataset.
        {
        var ret = [];
        for(i = 0; i < results[0].values.length; i++)
        {
          var json = jQuery.parseJSON(results[0].values[i][0]);
          console.log(results[0].values[i])
          $.each(json, function (k, data) {
            if((k == d) && active_libraries[results[0].values[i][3]] == true) { ret.push([data, results[0].values[i][3], k]); }
          })
        }
        //console.log(ret)
        return ret;
        })
  .enter().append("rect")
    .attr("width", library_scale.rangeBand())
    .attr("x", function(d) { return library_scale(d[1]); })
    .attr("y", function(d) { return runtime_scale(d[0], max_runtime); })
    .attr("height", function(d) { return height - runtime_scale(d[0]); })
    .style("fill", function(d) { return color(d[1]); });

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
    .on('click', function() { enableAllLibraries(); });
  librarySelectTitle.append("div")
    .attr("class", "library-select-title-bar")
    .text("|");
  librarySelectTitle.append("div")
    .attr("class", "library-select-title-disable-all")
    .text("disable all")
    .on('click', function() { disableAllLibraries(); });
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
    .attr("onClick", function(d, i) { return "toggleLibrary(\"" + d + "\");"; });

  libraryDivs.append("label")
    .attr('for', function(d) { return d + '-library-checkbox'; })
    .attr('class', 'library-select-label')
    .text(function(d) { return d; });

  // // Add a clear box.
  // d3.select(".legendholder").append("div").attr("class", "clear");

  // var datasetSelectTitle = d3.select(".legendholder").append("div")
  //   .attr("class", "dataset-select-title");
  // datasetSelectTitle.append("div")
  //   .attr("class", "dataset-select-title-text")
  //   .text("Datasets:");
  // datasetSelectTitle.append("div")
  //   .attr("class", "dataset-select-title-open-paren")
  //   .text("(");
  // datasetSelectTitle.append("div")
  //   .attr("class", "dataset-select-title-enable-all")
  //   .text("enable all")
  //   .on('click', function() { enableAllDatasets(); });
  // datasetSelectTitle.append("div")
  //   .attr("class", "dataset-select-title-bar")
  //   .text("|");
  // datasetSelectTitle.append("div")
  //   .attr("class", "dataset-select-title-disable-all")
  //   .text("disable all")
  //   .on('click', function() { disableAllDatasets(); });
  // datasetSelectTitle.append("div")
  //   .attr("class", "dataset-select-title-close-paren")
  //   .text(")");

  // // Add another legend for the datasets.
  // var datasetDivs = d3.select(".legendholder").selectAll(".dataset-select-div")
  //   .data(datasets)
  //   .enter()
  //   .append("div")
  //   .attr("class", "dataset-select-div")
  //   .attr("id", function(d) { return d + "-dataset-checkbox-div"; });

  // // Imitate color boxes so things line up.
  // datasetDivs.append("label")
  //   .attr('for', function(d) { return d + "-dataset-checkbox"; })
  //   .attr('class', 'dataset-select-color');

  // datasetDivs.append("input")
  //   .property("checked", function(d) { return active_datasets[d]; })
  //   .attr("type", "checkbox")
  //   .attr("id", function(d) { return d + "-dataset-checkbox"; })
  //   .attr("class", "dataset-select-box")
  //   .attr("onClick", function(d) { return "toggleDataset(\"" + d + "\");"; });

  // datasetDivs.append("label")
  //   .attr('for', function(d) { return d + '-dataset-checkbox'; })
  //   .attr('class', 'dataset-select-label')
  //   .text(function(d) { return d; });
}
