// namespace hc = historical comparison
var hc = hc = hc || {};

hc.method_name = "";
hc.param_name = "";
var hc.active_datasets;
var hc.active_libraries;

hc.onTypeSelect = function()
{
  selectHolder.append("label")
      .attr("for", "method_select")
      .attr("class", "method-select-label")
      .text("Select method:");
  selectHolder.append("select")
      .attr("id", "method_select")
      .attr("onchange", "hc.methodSelect()");
  selectHolder.append("label")
      .attr("for", "param_select")
      .attr("class", "param-select-label")
      .text("Select parameters:");
  selectHolder.append("select")
      .attr("id", "param_select")
      .attr("onchange", "hc.paramSelect()");
  selectHolder.append("br");
  selectHolder.append("label")
      .attr("for", "main_dataset_select")
      .attr("class", "main-dataset-select-label")
      .text("Select dataset:");
  selectHolder.append("select")
      .attr("id", "main_dataset_select")
      .attr("onchange", "hc.datasetSelect()");

  listMethods();
}

// List the available methods.
hc.listMethods = function()
{
  var methods = db.exec("SELECT DISTINCT methods.name FROM methods, results WHERE methods.id=results.method_id ORDER BY name;");

  var method_select_box = document.getElementById("method_select");

  // Put new things in the list box.
  clearSelectBox(method_select_box);
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
hc.methodSelect = function()
{
  // Extract the name of the method we selected.
  var method_select_box = document.getElementById("method_select");
  method_name = method_select_box.options[method_select_box.selectedIndex].text; // At higher scope.

  var sqlstr = "SELECT methods.parameters, results.libary_id FROM methods, results WHERE methods.name == '" + method_name + "' AND methods.id == results.method_id GROUP BY methods.parameters;";

  var params = db.exec(sqlstr);
  
  // Loop through results and fill the second list box.
  var param_select_box = document.getElementById("param_select");
  
  // Put in the new options.
  clearSelectBox(param_select_box);
  for (i = 0; i < params[0].values.length; i++)
  {
    var new_option = document.createElement("option");
    if (params[0].values[i][0])
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

// The user has selected parameters.
hc.paramSelect = function()
{
  var method_select_box = document.getElementById("method_select");
  var method_name = method_select_box.options[method_select_box.selectedIndex].text;
  var param_select_box = document.getElementById("param_select");
  var param_name_full = param_select_box.options[param_select_box.selectedIndex].text;
  // Parse out actual parameters.
  param_name = param_name_full.split("(")[0].replace(/^\s+|\s+$/g, ''); // At higher scope.
  if (param_name == "[no parameters]") { param_name = ""; }

  // Given a method name and parameters, query the SQLite database for all of
  // the runs.
  var sqlstr = "SELECT DISTINCT results.time, results.var, libraries.id, libraries.name, datasets.name, datasets.id " +  "FROM results, datasets, methods, libraries WHERE results.dataset_id == datasets.id AND results.method_id == methods.id " +     "AND methods.name == '" + method_name + "' AND methods.parameters == '" + param_name + "' AND libraries.id == results.libary_id " + "GROUP BY datasets.id, libraries.id;";
  results = db.exec(sqlstr);

  // Obtain unique list of datasets.
  datasets = results[0].values.map(function(d) { return d[4]; }).reduce(function(p, c) { if(p.indexOf(c) < 0) p.push(c); return p; }, []);
  // Obtain unique list of libraries.
  libraries = results[0].values.map(function(d) { return d[3]; }).reduce(function(p, c) { if(p.indexOf(c) < 0) p.push(c); return p; }, []);

  var dataset_select_box = document.getElementById("main_dataset_select");

  // Remove old things.
  clearSelectBox(dataset_select_box);
  for (i = 0; i < datasets.length; i++)
  {
    var new_option = document.createElement("option");
    new_option.text = datasets[i];
    dataset_select_box.add(new_option);
  }
  dataset_select_box.selectedIndex = -1;
}

// Remove everything on the page that belongs to us.
hc.clear = function()
{
  // Only things that belong to us are in the chart.
  clearChart();
}

// Remove everything we have in the chart.
hc.clearChart = function()
{
  d3.select("svg").remove();
  d3.selectAll(".d3-tip").remove();
  d3.selectAll(".library-select-title").remove();
  d3.selectAll(".library-select-div").remove();
  d3.selectAll(".dataset-select-title").remove();
  d3.selectAll(".dataset-select-div").remove();
}

// Build the chart and display it on the screen.
hc.buildChart = function()
{
    // Set up x axis scale.
  var minDate = results[0].values.map(function(d) { return new Date(d[3]); }).reduce(function(p, c) { if(c < p) { return c; } else { return p; } }, new Date("2099-01-01"));
  var maxDate = results[0].values.map(function(d) { return new Date(d[3]); }).reduce(function(p, c) { if(c > p) { return c; } else { return p; } }, new Date("1900-01-01"));
  console.log(minDate);
  console.log(maxDate);
  var build_scale = d3.time.scale().domain([minDate, maxDate]).range([0, width]);

  // Set up y axis scale.
  var max_runtime = d3.max(results[0].values, function(d) { if(active_libraries[d[4]] == false) { return 0; } else { return mapRuntime(d[0], 0); } });
  var runtime_scale = d3.scale.linear().domain([0, max_runtime]).range([height, 0]);


  // Set up axes.
  var dateFormat = d3.time.format("%b %Y");
  var xAxis = d3.svg.axis().scale(build_scale).orient("bottom")
      .tickFormat(function(d) { return dateFormat(d); });
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

  // Create tooltips.
  var tip = d3.tip()
      .attr("class", "d3-tip")
      .offset([-10, 0])
      .html(function(d) {
          var runtime = d[0];
          if (d[0] != ">9000" && d[0] != "failure") { runtime = d[0].toFixed(1); }
          var date = new Date(d[3]);
          var dFormat = d3.time.format("%b %d, %Y");
          return "<strong>" + d[4] + "; " + dFormat(date) + ":</strong> <span style='color:yellow'>" + runtime + "s</span>"; }
      );
  svg.call(tip);

  // Add all of the data points.
  var lineFunc = d3.svg.line()
      .x(function(d) { return build_scale(new Date(d[3])); })
      .y(function(d) { return runtime_scale(mapRuntime(d[0], max_runtime)); })
      .interpolate("step-after");

  var lineResults = [];
  for (var l in libraries)
  {
    if (active_libraries[libraries[l]] == true)
    {
      lineResults.push(results[0].values.map(function(d) { return d; }).reduce(function(p, c) { if(c[4] == libraries[l]) { p.push(c); } return p; }, []));
    }
    else { lineResults.push([]); }
  }

  for(i = 0; i < lineResults.length; i++)
  {
    svg.append('svg:path')
        .attr('d', lineFunc(lineResults[i]))
        .attr('stroke', color(libraries[i]))
        .attr('stroke-width', 2)
        .attr('fill', 'none');
  }
  for(i = 0; i < lineResults.length; i++)
  {
    // Colored circle enclosed in white circle enclosed in background color
    // circle; looks kind of nice.
    svg.selectAll("dot").data(lineResults[i]).enter().append("circle")
        .attr("r", 6)
        .attr("cx", function(d) { return build_scale(new Date(d[3])); })
        .attr("cy", function(d) { return runtime_scale(mapRuntime(d[0],
max_runtime)); })
        .attr('fill', '#222222')
        .on('mouseover', tip.show)
        .on('mouseout', tip.hide);
    svg.selectAll("dot").data(lineResults[i]).enter().append("circle")
        .attr("r", 4)
        .attr("cx", function(d) { return build_scale(new Date(d[3])); })
        .attr("cy", function(d) { return runtime_scale(mapRuntime(d[0],
max_runtime)); })
        .attr('fill', '#ffffff')
        .on('mouseover', tip.show)
        .on('mouseout', tip.hide);
    svg.selectAll("dot").data(lineResults[i]).enter().append("circle")
        .attr("r", 3)
        .attr("cx", function(d) { return build_scale(new Date(d[3])); })
        .attr("cy", function(d) { return runtime_scale(mapRuntime(d[0],
max_runtime)); })
        .attr('fill', function(d) { return color(d[4]) })
        .on('mouseover', tip.show)
        .on('mouseout', tip.hide);
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

// Toggle a library to on or off.
hc.toggleLibrary = function(library)
{
  active_libraries[library] = !active_libraries[library];

  clearChart();
  buildChart();
}

// Toggle a dataset to on or off.
hc.toggleDataset = function(dataset)
{
  active_datasets[dataset] = !active_datasets[dataset];

  clearChart();
  buildChart();
}

// Set all libraries on.
hc.enableAllLibraries = function()
{
  for (v in active_libraries) { active_libraries[v] = true; }

  clearChart();
  buildChart();
}

// Set all libraries off.
hc.disableAllLibraries = function()
{
  for (v in active_libraries) { active_libraries[v] = false; }

  clearChart();
  buildChart();
}

// Set all datasets on.
hc.enableAllDatasets = function()
{
  for (v in active_datasets) { active_datasets[v] = true; }

  clearChart();
  buildChart();
}

// Set all datasets off.
hc.disableAllDatasets = function()
{
  for (v in active_datasets) { active_datasets[v] = false; }

  clearChart();
  buildChart();
}
