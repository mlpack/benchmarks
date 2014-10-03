// Load benchmark.db.  Later, we will do something cool with it, once I figure
// out how.  If this is file:///, suggest that the user start a server since
// XMLHttpRequests may not work.
console.log(window.location.protocol);
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
var chartType;

// Basic chart parameters.
var width = 800; // This should be parameterizable...
var height = 600; // This should be parameterizable...
var margin = { top: 20, right: 20, bottom: 120, left: 40 };

// Static bindings of library names to colors.
var color = d3.scale.ordinal().range(["#98abc5", "#8a89a6", "#7b6888", "#6b486b", "#a05d56", "#d0743c", "#ff8c00"]);

function listMethods()
{
  var methods = db.exec("SELECT DISTINCT name FROM methods ORDER BY name;");
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

function methodSelect()
{
  // Extract the name of the method we selected.
  var method_select_box = document.getElementById("method_select");
  method_name = method_select_box.options[method_select_box.selectedIndex].text; // At higher scope.

  // Now get all of the possible parameters for that function.
  var sqlstr = "SELECT methods.parameters, results.libary_id FROM methods, results WHERE methods.name == '" + method_name + "' AND methods.id == results.method_id GROUP BY methods.parameters;";
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
  buildRuntimeComparisonChart();
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

function buildRuntimeComparisonChart()
{
  // Set up scales.
  var group_scale = d3.scale.ordinal()
    .domain(datasets.map(function(d) { return d; }).reduce(function(p, c) { if(active_datasets[c] == true) { p.push(c); } return p; }, []))
    .rangeRoundBands([0, width], .1);
  var library_scale = d3.scale.ordinal()
    .domain(libraries.map(function(d) { return d; }).reduce(function(p, c) { if(active_libraries[c] == true) { p.push(c); } return p; }, []))
    .rangeRoundBands([0, group_scale.rangeBand()]);
  var max_runtime = d3.max(results[0].values, function(d) { if(active_datasets[d[4]] == false || active_libraries[d[3]] == false) { return 0; } else if(d[0] == ">9000") { return 0; } else if(d[0] == "failure") { return 0; } else { return d[0]; } });

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
        return "<strong>Runtime for " + d[3] + ":</strong> <span style='color:yellow'>" + runtime + "s</span>"; });

  svg.call(tip);
  // Add all of the data points.
  group.selectAll("rect")
    .data(function(d) // For a given dataset d, collect all of the data points for that dataset.
        {
        var ret = [];
        for(i = 0; i < results[0].values.length; i++)
        {
        if(results[0].values[i][4] == d && active_libraries[results[0].values[i][3]] == true) { ret.push(results[0].values[i]); }
        }
        console.log(JSON.stringify(ret));
        return ret;
        })
  .enter().append("rect")
    .attr("width", library_scale.rangeBand())
    .attr("x", function(d) { return library_scale(d[3]); })
    .attr("y", function(d) { if(d[0] == ">9000") { return runtime_scale(max_runtime); } else if(d[0] == "failure") { return runtime_scale(0); } else { return runtime_scale(d[0]); } })
    .attr("height", function(d) { var subh; if(d[0] == ">9000") { subh = runtime_scale(max_runtime); } else if(d[0] == "failure") { subh = runtime_scale(0); } else { subh = runtime_scale(d[0]); } return height - subh; })
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
    .on('click', function() { enableAllDatasets(); });
  datasetSelectTitle.append("div")
    .attr("class", "dataset-select-title-bar")
    .text("|");
  datasetSelectTitle.append("div")
    .attr("class", "dataset-select-title-disable-all")
    .text("disable all")
    .on('click', function() { disableAllDatasets(); });
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
    .attr("onClick", function(d) { return "toggleDataset(\"" + d + "\");"; });

  datasetDivs.append("label")
    .attr('for', function(d) { return d + '-dataset-checkbox'; })
    .attr('class', 'dataset-select-label')
    .text(function(d) { return d; });

}
function toggleLibrary(library)
{
  active_libraries[library] = !active_libraries[library];

  clearChart();
  if (chartType == "algorithm-parameter-comparison")
  {
    buildRuntimeComparisonChart();
  }
  else if (chartType == "historical-comparison")
  {
    buildHistoricalRuntimeChart();
  }
}

function toggleDataset(dataset)
{
  active_datasets[dataset] = !active_datasets[dataset];

  clearChart();
  buildRuntimeComparisonChart();
}

function enableAllLibraries()
{
  for (v in active_libraries) { active_libraries[v] = true; }

  clearChart();
  buildRuntimeComparisonChart();
}

function disableAllLibraries()
{
  for (v in active_libraries) { active_libraries[v] = false; }

  clearChart();
  buildRuntimeComparisonChart();
}

function enableAllDatasets()
{
  for (v in active_datasets) { active_datasets[v] = true; }

  clearChart();
  buildRuntimeComparisonChart();
}

function disableAllDatasets()
{
  for (v in active_datasets) { active_datasets[v] = false; }

  clearChart();
  buildRuntimeComparisonChart();
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
      .attr("onchange", "methodSelect()");
    selectHolder.append("label")
      .attr("for", "param_select")
      .attr("class", "param-select-label")
      .text("Select parameters:");
    selectHolder.append("select")
      .attr("id", "param_select")
      .attr("onchange", "paramSelect()");

    listMethods();
  }
  else if (chartType == "historical-comparison")
  {
    selectHolder.append("label")
      .attr("for", "method_select")
      .attr("class", "method-select-label")
      .text("Select method:");
    selectHolder.append("select")
      .attr("id", "method_select")
      .attr("onchange", "methodSelect()");
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
      .attr("onchange", "datasetSelect()");

    listMethods();
  }
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
  var sqlstr = "SELECT DISTINCT results.time, results.var, libraries.id, libraries.name, datasets.name, datasets.id " +~
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
function datasetSelect()
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
  buildHistoricalRuntimeChart();
}

function buildHistoricalRuntimeChart()
{
  // Set up x axis scale.
  var min_build = d3.min(results[0].values, function(d) { return d[2]; });
  var max_build = d3.max(results[0].values, function(d) { return d[2]; });
  var build_scale = d3.scale.linear().domain([min_build, max_build]).range([0, width]);

  // Set up y axis scale.
  var max_runtime = d3.max(results[0].values, function(d) { if(active_libraries[d[4]] == false) { return 0; } if(d[0] == ">9000") { return 0; } else if(d[0] == "failure") { return 0; } else { return d[0]; } });
  var runtime_scale = d3.scale.linear().domain([0, max_runtime]).range([height, 0]);

  // Set up axes.
  var xAxis = d3.svg.axis().scale(build_scale).orient("bottom");
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

  // Add all of the data points.
  var lineFunc = d3.svg.line()
    .x(function(d) { return build_scale(d[2]); })
    .y(function(d) { if(d[0] == ">9000") { return runtime_scale(max_runtime); } else if(d[0] == "failure") { return runtime_scale(0); } else { return runtime_scale(d[0]); } })
    .interpolate("step-before");

  console.log(JSON.stringify(results[0].values));

  var lineResults = [];
  for (var l in libraries)
  {
    console.log(l);
    if (active_libraries[libraries[l]] == true)
    {
      lineResults.push(results[0].values.map(function(d) { return d; }).reduce(function(p, c) { if(c[4] == libraries[l]) { p.push(c); } return p; }, []));
    }
  }
  console.log(JSON.stringify(lineResults));
  for(i = 0; i < lineResults.length; i++)
  {
    svg.append('svg:path')
      .attr('d', lineFunc(lineResults[i]))
      .attr('stroke', color(libraries[i]))
      .attr('stroke-width', 2)
      .attr('fill', 'none');
  }
  // Create the library selector.
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

  console.log(JSON.stringify(active_libraries));
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
}
