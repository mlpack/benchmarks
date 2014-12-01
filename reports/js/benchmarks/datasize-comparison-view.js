// Define namespace: dsc = datasize-comparison.
var dsc = dsc = dsc || {};

dsc.method_name = ""; // Name of currently selected method.
dsc.param_name = ""; // Name of currently selected parameters.
dsc.datasets = [];
dsc.libraries = [];
dsc.active_datasets = [];
dsc.active_libraries = [];
dsc.results = [];
dsc.groupBy = "datasets.instances"

// This chart type has been selected.  What do we do now?
dsc.onTypeSelect = function()
{
  // The user needs to be able to select a method, then parameters.
  var selectHolder = d3.select(".selectholder");
  selectHolder.append("label")
      .attr("for", "method_select")
      .attr("class", "method-select-label")
      .text("Select method:");
    selectHolder.append("select")
      .attr("id", "method_select")
      .attr("onchange", "dsc.methodSelect()");
    selectHolder.append("label")
      .attr("for", "param_select")
      .attr("class", "param-select-label")
      .text("Select parameters:");
    selectHolder.append("select")
      .attr("id", "param_select")
      .attr("onchange", "dsc.paramSelect()");
    selectHolder.append("br");
    selectHolder.append("label")
        .attr("for", "main_dataset_select")
        .attr("class", "main-dataset-select-label")
        .text("Sort results by:");
    selectHolder.append("select")
        .attr("id", "main_dataset_select")
        .attr("onchange", "dsc.orderSelect()");

  dsc.listMethods();
  dsc.listOrder();
}

// List order.
dsc.listOrder = function()
{
  var order_select_box = document.getElementById("main_dataset_select");

  // Remove old things.
  clearSelectBox(order_select_box);

  var options = ["instances", "attributes", "size", ]
  // // Add new things.
  for (i = 0; i < options.length; i++)
  {
    var new_option = document.createElement("option");
    new_option.text = options[i];
    order_select_box.add(new_option);
  }
  order_select_box.selectedIndex = 0;

  // Clear parameters box.
  clearSelectBox(document.getElementById("param_select"));
}

// List methods.
dsc.listMethods = function()
{
  var methods = db.exec("SELECT DISTINCT methods.name FROM methods, results WHERE methods.id == results.method_id ORDER BY name;");
  var method_select_box = document.getElementById("method_select");

  // Remove old things.
  clearSelectBox(method_select_box);

  // Add new things.
  for (i = 0; i < methods[0].values.length; i++)
  {
    var new_option = document.createElement("option");
    new_option.text = methods[0].values[i];
    method_select_box.add(new_option);
  }
  method_select_box.selectedIndex = -1;

  // Clear parameters box.
  clearSelectBox(document.getElementById("param_select"));
}

// Called when the user selects a method.
dsc.methodSelect = function()
{
  // Extract the name of the method we selected.
  var method_select_box = document.getElementById("method_select");
  dsc.method_name = method_select_box.options[method_select_box.selectedIndex].text; // At higher scope.

  var sqlstr = "SELECT DISTINCT methods.parameters, results.libary_id, COUNT(DISTINCT results.libary_id) FROM methods, results WHERE methods.name == '" + dsc.method_name + "' AND methods.id == results.method_id GROUP BY methods.parameters;";
  var params = db.exec(sqlstr);

  // Loop through results and fill the second list box.
  var param_select_box = document.getElementById("param_select");
  clearSelectBox(param_select_box);
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

// Called when a set of parameters is selected.  Now we are ready to draw the chart.
dsc.paramSelect = function()
{
  // The user has selected a library and parameters.  Now we need to generate
  // a chart for all applicable datasets.
  var method_select_box = document.getElementById("method_select");
  dsc.method_name = method_select_box.options[method_select_box.selectedIndex].text;
  var param_select_box = document.getElementById("param_select");
  var param_name_full = param_select_box.options[param_select_box.selectedIndex].text;

  // Parse out actual parameters.
  dsc.param_name = param_name_full.split("(")[0].replace(/^\s+|\s+$/g, ''); // At higher scope.
  if (dsc.param_name == "[no parameters]")
  {
    dsc.param_name = "";
  }

  // Given a method name and parameters, query the SQLite database for all of
  // the runs.
  var sqlstr = "SELECT DISTINCT results.time, results.var, libraries.id, libraries.name, datasets.name, datasets.id " +
    "FROM results, datasets, methods, libraries WHERE results.dataset_id == datasets.id AND results.method_id == methods.id " +
    "AND methods.name == '" + dsc.method_name + "' AND methods.parameters == '" + dsc.param_name + "' AND libraries.id == results.libary_id " +
    "GROUP BY datasets.id, libraries.id, " + dsc.groupBy + ";";
  dsc.results = db.exec(sqlstr);

  // Obtain unique list of datasets.
  dsc.datasets = dsc.results[0].values.map(function(d) { return d[4]; }).reduce(function(p, c) { if(p.indexOf(c) < 0) p.push(c); return p; }, []);
  // Obtain unique list of libraries.
  dsc.libraries = dsc.results[0].values.map(function(d) { return d[3]; }).reduce(function(p, c) { if(p.indexOf(c) < 0) p.push(c); return p; }, []);

  // By default, everything is active.
  dsc.active_datasets = {};
  for (i = 0; i < dsc.datasets.length; i++)
  {
    dsc.active_datasets[dsc.datasets[i]] = true;
  }

  dsc.active_libraries = {};
  for (i = 0; i < dsc.libraries.length; i++)
  {
    dsc.active_libraries[dsc.libraries[i]] = true;
  }

  clearChart();
  buildChart();
}

dsc.orderSelect = function()
{
  // Extract the name of the method we selected.
  var order_select_box = document.getElementById("main_dataset_select");
  dsc.groupBy = "datasets." + order_select_box.options[order_select_box.selectedIndex].text; // At higher scope.


  var sqlstr = "SELECT DISTINCT results.time, results.var, libraries.id, libraries.name, datasets.name, datasets.id " +
    "FROM results, datasets, methods, libraries WHERE results.dataset_id == datasets.id AND results.method_id == methods.id " +
    "AND methods.name == '" + dsc.method_name + "' AND methods.parameters == '" + dsc.param_name + "' AND libraries.id == results.libary_id " +
    "GROUP BY libraries.id, " + dsc.groupBy + ";";
  dsc.results = db.exec(sqlstr);

   // Obtain unique list of datasets.
  dsc.datasets = dsc.results[0].values.map(function(d) { return d[4]; }).reduce(function(p, c) { if(p.indexOf(c) < 0) p.push(c); return p; }, []);
  // Obtain unique list of libraries.
  dsc.libraries = dsc.results[0].values.map(function(d) { return d[3]; }).reduce(function(p, c) { if(p.indexOf(c) < 0) p.push(c); return p; }, []);

  // By default, everything is active.
  dsc.active_datasets = {};
  for (i = 0; i < dsc.datasets.length; i++)
  {
    dsc.active_datasets[dsc.datasets[i]] = true;
  }

  dsc.active_libraries = {};
  for (i = 0; i < dsc.libraries.length; i++)
  {
    dsc.active_libraries[dsc.libraries[i]] = true;
  }

  dsc.clearChart();
  dsc.buildChart();
}

// Remove everything on the page that belongs to us.
dsc.clear = function()
{
  // Only things that belong to us are in the chart.
  dsc.clearChart();
}

// Remove everything we have in the chart.
dsc.clearChart = function()
{
  d3.select("svg").remove();
  d3.selectAll(".d3-tip").remove();
  d3.selectAll(".library-select-title").remove();
  d3.selectAll(".library-select-div").remove();
  d3.selectAll(".dataset-select-title").remove();
  d3.selectAll(".dataset-select-div").remove();
}

// Build the chart and display it on screen.
dsc.buildChart = function()
{
   // Set up scales.
  var group_scale = d3.scale.ordinal()
      .domain(dsc.datasets.map(function(d) { return d; }).reduce(function(p, c) { if(dsc.active_datasets[c] == true) { p.push(c); } return p; }, []))
      .rangeRoundBands([0, width], .1);

  var library_scale = d3.scale.ordinal()
      .domain(dsc.libraries.map(function(d) { return d; }).reduce(function(p, c) { if(dsc.active_libraries[c] == true) { p.push(c); } return p; }, []))
      .rangeRoundBands([0, group_scale.rangeBand()]);

  var max_runtime = d3.max(dsc.results[0].values, function(d) { if(dsc.active_datasets[d[4]] == false || dsc.active_libraries[d[3]] == false) { return 0; } else { return mapRuntime(d[0], 0); } });

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
      .data(dsc.datasets.map(function(d) { return d; }).reduce(function(p, c) { if(dsc.active_datasets[c] == true) { p.push(c); } return p; }, []))
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
          for(i = 0; i < dsc.results[0].values.length; i++)
          {
            if(dsc.results[0].values[i][4] == d && dsc.active_libraries[dsc.results[0].values[i][3]] == true)
            {
              ret.push(dsc.results[0].values[i]);
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
      .on('click', function() { dsc.enableAllLibraries(); });
  librarySelectTitle.append("div")
      .attr("class", "library-select-title-bar")
      .text("|");
  librarySelectTitle.append("div")
      .attr("class", "library-select-title-disable-all")
      .text("disable all")
      .on('click', function() { dsc.disableAllLibraries(); });
  librarySelectTitle.append("div")
      .attr("class", "library-select-title-close-paren")
      .text(")");

  var libraryDivs = d3.select(".legendholder").selectAll("input")
      .data(dsc.libraries)
      .enter()
      .append("div")
      .attr("class", "library-select-div")
      .attr("id", function(d) { return d + '-library-checkbox-div'; });

  libraryDivs.append("label")
      .attr('for', function(d) { return d + '-library-checkbox'; })
      .style('background', color)
      .attr('class', 'library-select-color');
  libraryDivs.append("input")
      .property("checked", function(d) { return dsc.active_libraries[d]; })
      .attr("type", "checkbox")
      .attr("id", function(d) { return d + '-library-checkbox'; })
      .attr('class', 'library-select-box')
      .attr("onClick", function(d, i) { return "dsc.toggleLibrary(\"" + d + "\");"; });

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
      .on('click', function() { dsc.enableAllDatasets(); });
  datasetSelectTitle.append("div")
      .attr("class", "dataset-select-title-bar")
      .text("|");
  datasetSelectTitle.append("div")
      .attr("class", "dataset-select-title-disable-all")
      .text("disable all")
      .on('click', function() { dsc.disableAllDatasets(); });
  datasetSelectTitle.append("div")
      .attr("class", "dataset-select-title-close-paren")
      .text(")");

  // Add another legend for the datasets.
  var datasetDivs = d3.select(".legendholder").selectAll(".dataset-select-div")
      .data(dsc.datasets)
      .enter()
      .append("div")
      .attr("class", "dataset-select-div")
      .attr("id", function(d) { return d + "-dataset-checkbox-div"; });

  // Imitate color boxes so things line up.
  datasetDivs.append("label")
      .attr('for', function(d) { return d + "-dataset-checkbox"; })
      .attr('class', 'dataset-select-color');

  datasetDivs.append("input")
      .property("checked", function(d) { return dsc.active_datasets[d]; })
      .attr("type", "checkbox")
      .attr("id", function(d) { return d + "-dataset-checkbox"; })
      .attr("class", "dataset-select-box")
      .attr("onClick", function(d) { return "dsc.toggleDataset(\"" + d + "\");"; });

  datasetDivs.append("label")
      .attr('for', function(d) { return d + '-dataset-checkbox'; })
      .attr('class', 'dataset-select-label')
      .text(function(d) { return d; });
}

// Toggle a library to on or off.
dsc.toggleLibrary = function(library)
{
  dsc.active_libraries[library] = !dsc.active_libraries[library];

  clearChart();
  buildChart();
}

// Toggle a dataset to on or off.
dsc.toggleDataset = function(dataset)
{
  dsc.active_datasets[dataset] = !dsc.active_datasets[dataset];

  clearChart();
  buildChart();
}

// Set all libraries on.
dsc.enableAllLibraries = function()
{
  for (v in dsc.active_libraries) { dsc.active_libraries[v] = true; }

  clearChart();
  buildChart();
}

// Set all libraries off.
dsc.disableAllLibraries = function()
{
  for (v in dsc.active_libraries) { dsc.active_libraries[v] = false; }

  clearChart();
  buildChart();
}

// Set all datasets on.
dsc.enableAllDatasets = function()
{
  for (v in dsc.active_datasets) { dsc.active_datasets[v] = true; }

  clearChart();
  buildChart();
}

// Set all datasets off.
dsc.disableAllDatasets = function()
{
  for (v in dsc.active_datasets) { dsc.active_datasets[v] = false; }

  clearChart();
  buildChart();
}
