// Define namespace: rc = runtime-comparison.
var rc = rc = rc || {};

rc.method_name = ""; // Name of currently selected method.
rc.param_name = ""; // Name of currently selected parameters.
rc.datasets = [];
rc.libraries = [];
rc.active_datasets = [];
rc.active_libraries = [];
rc.results = [];
rc.groupBy = "datasets.instances"

// This chart type has been selected.  What do we do now?
rc.onTypeSelect = function()
{
  // The user needs to be able to select a method, then parameters.
  var selectHolder = d3.select(".selectholder");
  selectHolder.append("label")
      .attr("for", "method_select")
      .attr("class", "method-select-label")
      .text("Select method:");
    selectHolder.append("select")
      .attr("id", "method_select")
      .attr("onchange", "rc.methodSelect()");
    selectHolder.append("label")
      .attr("for", "param_select")
      .attr("class", "param-select-label")
      .text("Select parameters:");
    selectHolder.append("select")
      .attr("id", "param_select")
      .attr("onchange", "rc.paramSelect()");
    selectHolder.append("br");
    selectHolder.append("label")
        .attr("for", "main_dataset_select")
        .attr("class", "main-dataset-select-label")
        .text("Sort results by:");
    selectHolder.append("select")
        .attr("id", "main_dataset_select")
        .attr("onchange", "rc.orderSelect()");

  rc.listMethods();
  rc.listOrder();
}

// List order.
rc.listOrder = function()
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
rc.listMethods = function()
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
rc.methodSelect = function()
{
  // Extract the name of the method we selected.
  var method_select_box = document.getElementById("method_select");
  rc.method_name = method_select_box.options[method_select_box.selectedIndex].text; // At higher scope.

  var sqlstr = "SELECT DISTINCT methods.parameters, results.libary_id, count(DISTINCT results.libary_id) FROM methods, results WHERE methods.name == '" + rc.method_name + "' AND methods.id == results.method_id GROUP BY methods.parameters;";
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
rc.paramSelect = function()
{
  // The user has selected a library and parameters.  Now we need to generate
  // a chart for all applicable datasets.
  var method_select_box = document.getElementById("method_select");
  rc.method_name = method_select_box.options[method_select_box.selectedIndex].text;
  var param_select_box = document.getElementById("param_select");
  var param_name_full = param_select_box.options[param_select_box.selectedIndex].text;

  // Parse out actual parameters.
  rc.param_name = param_name_full.split("(")[0].replace(/^\s+|\s+$/g, ''); // At higher scope.
  if (rc.param_name == "[no parameters]")
  {
    rc.param_name = "";
  }

  // Given a method name and parameters, query the SQLite database for all of
  // the runs.
  var sqlstr = "SELECT DISTINCT results.time, results.var, libraries.id, libraries.name, datasets.name, datasets.id " +
    "FROM results, datasets, methods, libraries WHERE results.dataset_id == datasets.id AND results.method_id == methods.id " +
    "AND methods.name == '" + rc.method_name + "' AND methods.parameters == '" + rc.param_name + "' AND libraries.id == results.libary_id " +
    "GROUP BY datasets.id, libraries.id, " + rc.groupBy + ";";
  rc.results = db.exec(sqlstr);

  // Obtain unique list of datasets.
  rc.datasets = rc.results[0].values.map(function(d) { return d[4]; }).reduce(function(p, c) { if(p.indexOf(c) < 0) p.push(c); return p; }, []);
  // Obtain unique list of libraries.
  rc.libraries = rc.results[0].values.map(function(d) { return d[3]; }).reduce(function(p, c) { if(p.indexOf(c) < 0) p.push(c); return p; }, []);

  // By default, everything is active.
  rc.active_datasets = {};
  for (i = 0; i < rc.datasets.length; i++)
  {
    rc.active_datasets[rc.datasets[i]] = true;
  }

  rc.active_libraries = {};
  for (i = 0; i < rc.libraries.length; i++)
  {
    rc.active_libraries[rc.libraries[i]] = true;
  }

  clearChart();
  buildChart();
}

rc.orderSelect = function()
{
  // Extract the name of the method we selected.
  var order_select_box = document.getElementById("main_dataset_select");
  rc.groupBy = "datasets." + order_select_box.options[order_select_box.selectedIndex].text; // At higher scope.

  var sqlstr = "SELECT DISTINCT results.time, results.var, libraries.id, libraries.name, datasets.name, datasets.id " +
    "FROM results, datasets, methods, libraries WHERE results.dataset_id == datasets.id AND results.method_id == methods.id " +
    "AND methods.name == '" + rc.method_name + "' AND methods.parameters == '" + rc.param_name + "' AND libraries.id == results.libary_id " +
    "GROUP BY libraries.id, " + rc.groupBy + ";";
  rc.results = db.exec(sqlstr);

   // Obtain unique list of datasets.
  rc.datasets = rc.results[0].values.map(function(d) { return d[4]; }).reduce(function(p, c) { if(p.indexOf(c) < 0) p.push(c); return p; }, []);
  // Obtain unique list of libraries.
  rc.libraries = rc.results[0].values.map(function(d) { return d[3]; }).reduce(function(p, c) { if(p.indexOf(c) < 0) p.push(c); return p; }, []);

  // By default, everything is active.
  rc.active_datasets = {};
  for (i = 0; i < rc.datasets.length; i++)
  {
    rc.active_datasets[rc.datasets[i]] = true;
  }

  rc.active_libraries = {};
  for (i = 0; i < rc.libraries.length; i++)
  {
    rc.active_libraries[rc.libraries[i]] = true;
  }

  rc.clearChart();
  rc.buildChart();
}

// Remove everything on the page that belongs to us.
rc.clear = function()
{
  // Only things that belong to us are in the chart.
  rc.clearChart();
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
  d3.selectAll(".runtime-table").remove();
}

// Build the chart and display it on screen.
rc.buildChart = function()
{
  // Get lists of active libraries and active datasets.
  var active_library_list = rc.libraries.map(function(d) { return d; }).reduce(function(p, c) { if(rc.active_libraries[c] == true) { p.push(c); } return p; }, []);
  var active_dataset_list = rc.datasets.map(function(d) { return d; }).reduce(function(p, c) { if(rc.active_datasets[c] == true) { p.push(c); } return p; }, []);

  // Set up scales.
  var group_scale = d3.scale.ordinal()
      .domain(active_dataset_list)
      .rangeRoundBands([0, width], .1);

  var library_scale = d3.scale.ordinal()
      .domain(active_library_list)
      .rangeRoundBands([0, group_scale.rangeBand()]);

  var max_runtime = d3.max(rc.results[0].values, function(d) { if(rc.active_datasets[d[4]] == false || rc.active_libraries[d[3]] == false) { return 0; } else { return mapRuntime(d[0], 0); } });
  // Increase max_runtime so we have 16 spare pixels at the top.
  max_runtime = max_runtime * ((height + 16) / height);

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
      .data(rc.datasets.map(function(d) { return d; }).reduce(function(p, c) { if(rc.active_datasets[c] == true) { p.push(c); } return p; }, []))
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
  var gs = group.selectAll("rect");

  // Bounding rectangles for tooltips' sake.
  gs.data(function(d) // For a given dataset d, collect all of the data points for that dataset.
        {
          var ret = [];
          for(i = 0; i < rc.results[0].values.length; i++)
          {
            if(rc.results[0].values[i][4] == d && rc.active_libraries[rc.results[0].values[i][3]] == true)
            {
              ret.push(rc.results[0].values[i]);
            }
          }
          return ret;
        })
    .enter().append("rect") // This rectangle is so tooltips work everywhere.
        .attr("width", library_scale.rangeBand())
        .attr("x", function(d) { return library_scale(d[3]); })
        .attr("y", function(d) { return runtime_scale(max_runtime); })
        .attr("height", function(d) { return height - runtime_scale(max_runtime); })
        .attr("fill", "rgba(0, 0, 0, 0.0)") // Complete transparency.
        .on('mouseover', tip.show)
        .on('mouseout', tip.hide);

  gs.data(function(d) // For a given dataset d, collect all of the data points for that dataset.
        {
          var ret = [];
          for(i = 0; i < rc.results[0].values.length; i++)
          {
            if(rc.results[0].values[i][4] == d && rc.active_libraries[rc.results[0].values[i][3]] == true && rc.results[0].values[i][0] != "failure" && rc.results[0].values[i][0] != ">9000")
            {
              ret.push(rc.results[0].values[i]);
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

  var failureData = gs.data(function(d)
      {
        var ret = [];
        for(i = 0; i < rc.results[0].values.length; i++)
        {
          if(rc.results[0].values[i][4] == d && rc.active_libraries[rc.results[0].values[i][3]] == true && rc.results[0].values[i][0] == "failure")
          {
            ret.push(rc.results[0].values[i]);
          }
        }
        return ret;
      })
    .enter();

//  failureData.append("rect")
//        .attr("width", library_scale.rangeBand())
//        .attr("x", function(d) { return library_scale(d[3]); })
//        .attr("y", runtime_scale(max_runtime))
//        .attr("height", height - runtime_scale(max_runtime))
//        .style("fill", function(d) { return color(d[3]); })
//        .attr("stroke-width", "1")
//        .attr("stroke", function(d) { return "#ff0000"; })
//        .on('mouseover', tip.show)
//        .on('mouseout', tip.hide);

  failureData.append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", function(d) { return library_scale(d[3]) + library_scale.rangeBand() / 2 })
        .attr("dy", "0.25em")
        .attr("x", -height + 2)
        .text("failure")
        .on('mouseover', tip.show)
        .on('mouseout', tip.hide);

  var timeoutData = gs.data(function(d)
      {
        var ret = [];
        for(i = 0; i < rc.results[0].values.length; i++)
        {
          if(rc.results[0].values[i][4] == d && rc.active_libraries[rc.results[0].values[i][3]] == true && rc.results[0].values[i][0] == ">9000")
          {
            ret.push(rc.results[0].values[i]);
          }
        }
        return ret;
      })
    .enter();

  // Make a rectangle that's almost full-height.
  timeoutData.append("rect")
      .attr("width", library_scale.rangeBand())
      .attr("x", function(d) { return library_scale(d[3]); })
      .attr("y", runtime_scale(max_runtime) + 16)
      .attr("height", height - (runtime_scale(max_runtime) + 16))
      .style("fill", function(d) { return color(d[3]); })
      .on('mouseover', tip.show)
      .on('mouseout', tip.hide);
  // Now make a little rectangle that's the bottom of the arrow.
  timeoutData.append("rect")
      .attr("width", library_scale.rangeBand() / 2)
      .attr("x", function(d) { return library_scale(d[3]) + library_scale.rangeBand() / 4; })
      .attr("y", 8)
      .attr("height", 8)
      .style("fill", function(d) { return color(d[3]); })
      .on('mouseover', tip.show)
      .on('mouseout', tip.hide);
  // Now create the triangle that points upwards.
  timeoutData.append("polygon")
      .attr("points", function(d)
        {
          var x = library_scale(d[3]);
          var width = library_scale.rangeBand();
          return String(x) + ",8 " + String(x + width) + ",8 " + String(x + (width / 2)) + ",0";
        })
      .attr("fill", function(d) { return color(d[3]); });

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
      .data(rc.libraries)
      .enter()
      .append("div")
      .attr("class", "library-select-div")
      .attr("id", function(d) { return d + '-library-checkbox-div'; });

  libraryDivs.append("label")
      .attr('for', function(d) { return d + '-library-checkbox'; })
      .style('background', color)
      .attr('class', 'library-select-color');
  libraryDivs.append("input")
      .property("checked", function(d) { return rc.active_libraries[d]; })
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
      .data(rc.datasets)
      .enter()
      .append("div")
      .attr("class", "dataset-select-div")
      .attr("id", function(d) { return d + "-dataset-checkbox-div"; });

  // Imitate color boxes so things line up.
  datasetDivs.append("label")
      .attr('for', function(d) { return d + "-dataset-checkbox"; })
      .attr('class', 'dataset-select-color');

  datasetDivs.append("input")
      .property("checked", function(d) { return rc.active_datasets[d]; })
      .attr("type", "checkbox")
      .attr("id", function(d) { return d + "-dataset-checkbox"; })
      .attr("class", "dataset-select-box")
      .attr("onClick", function(d) { return "rc.toggleDataset(\"" + d + "\");"; });

  datasetDivs.append("label")
      .attr('for', function(d) { return d + '-dataset-checkbox'; })
      .attr('class', 'dataset-select-label')
      .text(function(d) { return d; });

  // Now add a table of runtimes at the bottom.
  var table = d3.select(".svgholder").append("table")
      .attr("class", "runtime-table");
  var thead = table.append("thead");
  var tbody = table.append("tbody");

  active_library_list.unshift("dataset");
  var hrow = thead.append("tr").selectAll("th")
//  hrow.append("th").attr("class", "table-dataset-th").text("dataset")
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
          for(i = 1; i < active_library_list.length; i++) // Skip "dataset".
          {
            ret.push(['---']);
          }

          for(i = 0; i < rc.results[0].values.length; i++)
          {
            var library = rc.results[0].values[i][3];
            if(rc.results[0].values[i][4] == d && rc.active_libraries[library] == true)
            {
              ret[active_library_list.indexOf(library)] = rc.results[0].values[i];
            }
          }
          return ret;
      }).enter()
      .append("td")
      .html(function(d) { if (d[0] != "failure" && d[0] != "---") { if (typeof d == "string") { return d; } else { if (d[0] == ">9000") { return ">9000s"; } else { return "&nbsp;" + String(resultFormat(d[0])).replace(/x/g, '&nbsp;') + "s&nbsp;"; } } } else { return d[0]; } })
      .attr("class", function(d) { if (typeof d == "string") { return "dataset-name"; } else if (d[0] == "---") { return "timing-not-run-cell"; } else if (d[0] == ">9000" || d[0] == "failure") { return "timing-text-cell"; } else { return "timing-cell"; } });
}

// Toggle a library to on or off.
rc.toggleLibrary = function(library)
{
  rc.active_libraries[library] = !rc.active_libraries[library];

  clearChart();
  buildChart();
}

// Toggle a dataset to on or off.
rc.toggleDataset = function(dataset)
{
  rc.active_datasets[dataset] = !rc.active_datasets[dataset];

  clearChart();
  buildChart();
}

// Set all libraries on.
rc.enableAllLibraries = function()
{
  for (v in rc.active_libraries) { rc.active_libraries[v] = true; }

  clearChart();
  buildChart();
}

// Set all libraries off.
rc.disableAllLibraries = function()
{
  for (v in rc.active_libraries) { rc.active_libraries[v] = false; }

  clearChart();
  buildChart();
}

// Set all datasets on.
rc.enableAllDatasets = function()
{
  for (v in rc.active_datasets) { rc.active_datasets[v] = true; }

  clearChart();
  buildChart();
}

// Set all datasets off.
rc.disableAllDatasets = function()
{
  for (v in rc.active_datasets) { rc.active_datasets[v] = false; }

  clearChart();
  buildChart();
}
