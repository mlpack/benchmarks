// Define namespace: mc = metric-comparison.
var mc = mc = mc || {};

mc.method_name = "";
mc.param_name = "";
mc.dataset_name = "";
mc.control_list_length = 0;
mc.libraries = [];
mc.datasets = []
mc.active_metrics = [];
mc.active_libraries = [];
mc.metric_names = [];
mc.results = 
mc.active_library_list = [];

// The chart type has been selected.
mc.onTypeSelect = function()
{
  var selectHolder = d3.select(".selectholder");
  selectHolder.append("label")
      .attr("for", "main_dataset_select")
      .attr("class", "main-dataset-select-label")
      .text("Select dataset:");
  selectHolder.append("select")
      .attr("id", "main_dataset_select")
      .attr("onchange", "mc.datasetSelect()");

  mc.listDatasets();
}

// List the datasets.
mc.listDatasets = function()
{ 
  var sqlstr = "SELECT DISTINCT datasets.name FROM datasets, metrics WHERE datasets.id=metrics.dataset_id ORDER BY datasets.name;";
  var results = db.exec(sqlstr);

  var dataset_select_box = document.getElementById("main_dataset_select");
  clearSelectBox(dataset_select_box);
  for (i = 0; i < results[0].values.length; i++)
  {
    var new_option = document.createElement("option");
    new_option.text = results[0].values[i][0];
    dataset_select_box.add(new_option);
  }
  dataset_select_box.selectedIndex = -1;
}

mc.listMethods = function()
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
mc.methodSelect = function()
{
  // Extract the name of the method we selected.
  var method_select_box = document.getElementById("method_select");
  mc.method_name = method_select_box.options[method_select_box.selectedIndex].text; // At higher scope.

  var sqlstr = "SELECT DISTINCT methods.parameters, metrics.libary_id, COUNT(DISTINCT metrics.libary_id) FROM methods, metrics WHERE methods.name == '" + mc.method_name + "' AND methods.id == metrics.method_id GROUP BY methods.parameters;";

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
mc.paramSelect = function()
{
  // The user has selected a library and parameters.  Now we need to
  // generate
  // a chart for all applicable datasets.
  var method_select_box = document.getElementById("method_select");
  mc.method_name = method_select_box.options[method_select_box.selectedIndex].text;
  var param_select_box = document.getElementById("param_select");
  var param_name_full = param_select_box.options[param_select_box.selectedIndex].text;
  // Parse out actual parameters.
  mc.param_name = param_name_full.split("(")[0].replace(/^\s+|\s+$/g, ''); // At higher scope.
  if (mc.param_name == "[no parameters]") { mc.param_name = ""; }

  // Given a method name and parameters, query the SQLite database for all of
  // the runs.
  var sqlstr = "SELECT DISTINCT metrics.metric, libraries.id, libraries.name, datasets.name, datasets.id " +
    "FROM metrics, datasets, methods, libraries WHERE metrics.dataset_id == datasets.id AND metrics.method_id == methods.id " +
    "AND methods.name == '" + mc.method_name + "' AND methods.parameters == '" + mc.param_name + "' AND libraries.id == metrics.libary_id " +
    "AND metrics.metric<>'{}' GROUP BY datasets.id, libraries.id;";
  mc.results = db.exec(sqlstr);

  // Obtain unique list of datasets.
  mc.datasets = mc.results[0].values.map(function(d) { return d[3]; }).reduce(function(p, c) { if(p.indexOf(c) < 0) p.push(c); return p; }, []);
  // Obtain unique list of libraries.
  mc.libraries = mc.results[0].values.map(function(d) { return d[2]; }).reduce(function(p, c) { if(p.indexOf(c) < 0) p.push(c); return p; }, []);

  var dataset_select_box = document.getElementById("main_dataset_select");

  // Remove old things.
  for (i = dataset_select_box.options.length - 1; i >= 0; i--)
  {
    dataset_select_box.options[i] = null;
  }

  for (i = 0; i < mc.datasets.length; i++)
  {
    var new_option = document.createElement("option");
    new_option.text = mc.datasets[i];
    dataset_select_box.add(new_option);
  }
}

mc.datasetSelect = function()
{
  var dataset_select_box = document.getElementById("main_dataset_select");
  mc.dataset_name = dataset_select_box.options[dataset_select_box.selectedIndex].text;

  // Create an empty chart.
  mc.clear();

  // Now create the legend at the bottom that will allow us to add/remove
  // methods.
  d3.selectAll(".legendholder").append("div").attr("class", "methodcontrol");

  d3.selectAll(".legendholder").append("input")
      .attr("type", "button")
      .attr("class", "add_method_button")
      .attr("onclick", "mc.clickAddButton()")
      .attr("value", "Add another method");
  d3.selectAll(".legendholder").append("input")
      .attr("type", "button")
      .attr("class", "clear_methods_button")
      .attr("onclick", "mc.clickClearMethods()")
      .attr("value", "Remove all methods");
  d3.selectAll(".legendholder").append("input")
      .attr("type", "button")
      .attr("class", "redraw_methods_button")
      .attr("onclick", "mc.clickRedrawMethods()")
      .attr("value", "Redraw graph");

  mc.control_list_length = 0;

  // Collect the results for lists of methods.
  var sqlstr = "SELECT DISTINCT methods.name, methods.parameters, libraries.name FROM methods, metrics, datasets, libraries WHERE metrics.dataset_id == datasets.id AND metrics.method_id == methods.id AND datasets.name == '" + mc.dataset_name + "' AND libraries.id == metrics.libary_id ORDER BY methods.name;";
  mc.methods = db.exec(sqlstr);
}

// The user has requested to add a new thing.
mc.clickAddButton = function()
{
  var newmethodcontrol = d3.selectAll(".methodcontrol").append("div").attr("class", "methodcontroldiv");

  newmethodcontrol.append("label")
      .attr("class", "dc-index-label")
      .text(String(mc.control_list_length));
  newmethodcontrol.append("label")
      .attr("for", "method_select_" + String(mc.control_list_length))
      .attr("class", "dc-method-select-label")
      .text("Method:");
  newmethodcontrol.append("select")
      .attr("id", "method_select_" + String(mc.control_list_length))
      .attr("onchange", "mc.methodControlListSelect('" + String(mc.control_list_length) + "')");
  newmethodcontrol.append("label")
      .attr("for", "param_select_" + String(mc.control_list_length))
      .attr("class", "dc-param-select-label")
      .text("Parameters:");
  newmethodcontrol.append("select")
      .attr("id", "param_select_" + String(mc.control_list_length))
      .attr("onchange", "mc.paramControlListSelect('" + String(mc.control_list_length) + "')");
  newmethodcontrol.append("label")
      .attr("for", "library_select_" + String(mc.control_list_length))
      .attr("class", "mc-library-select-label")
      .text("Library:");
  newmethodcontrol.append("select")
      .attr("id", "library_select_" + String(mc.control_list_length));

  mc.control_list_length++;

  // Add list of methods.
  var newbox = document.getElementById("method_select_" + String(mc.control_list_length - 1));
  distinct_methods = mc.methods[0].values.map(function(d) { return d[0]; }).reduce(function(p, c) { if(p.indexOf(c) < 0) p.push(c); return p; }, []);
  for (i = 0; i < distinct_methods.length; i++)
  {
    var new_option = document.createElement("option");
    new_option.text = distinct_methods[i];
    newbox.add(new_option);
  }
  newbox.selectedIndex = -1;
}

mc.methodControlListSelect = function(id)
{
  var selectbox = document.getElementById("method_select_" + id);
  var method_name = selectbox.options[selectbox.selectedIndex].text;

  // Now we need to add parameters.
  distinct_parameters = mc.methods[0].values.map(function(d) { return d; }).reduce(function(p, c) { if(c[0] != method_name) { return p; } else if(p.indexOf(c[1]) < 0) { p.push(c[1]); } return p; }, []);
  var parambox = document.getElementById("param_select_" + id);
  clearSelectBox(parambox);
  for (i = 0; i < distinct_parameters.length; i++)
  {
    var new_option = document.createElement("option");
    new_option.text = distinct_parameters[i];
    if (new_option.text == "") { new_option.text == "[no parameters]"; }
    parambox.add(new_option);
  }
  parambox.selectedIndex = -1;
}

mc.paramControlListSelect = function(id)
{
  var method_select_box = document.getElementById("method_select_" + id);
  var method_name = method_select_box.options[method_select_box.selectedIndex].text;
  var param_select_box = document.getElementById("param_select_" + id);
  var param_name = param_select_box.options[param_select_box.selectedIndex].text;
  if (param_name == "[no parameters]") { param_name = ""; }

  distinct_libraries = mc.methods[0].values.map(function(d) { return d; }).reduce(function(p, c) { if(c[0] != method_name || c[1] != param_name) { return p; } else if(p.indexOf(c[2]) < 0) { p.push(c[2]); } return p; }, []);

  var library_select_box = document.getElementById("library_select_" + id);
  clearSelectBox(library_select_box);
  for(i = 0; i < distinct_libraries.length; i++)
  {
    var new_option = document.createElement("option");
    new_option.text = distinct_libraries[i];
    library_select_box.add(new_option);
  }
  library_select_box.selectedIndex = -1;
}

mc.clickClearMethods = function()
{
  d3.selectAll(".methodcontroldiv").remove();
  mc.control_list_length = 0;
  mc.active_library_list = [];
  clearChart(); // Remove the chart too.
}

// The user wants a plot of everything we have.
mc.clickRedrawMethods = function()
{
  mc.active_library_list = [];

  // We need to generate a big SQL query.
  var sqlstr = "";
  for (i = 0; i < mc.control_list_length; i++)
  {
    var methodbox = document.getElementById("method_select_" + String(i));
    var method_name = methodbox.options[methodbox.selectedIndex].text;
    var parambox = document.getElementById("param_select_" + String(i));
    var param_name = parambox.options[parambox.selectedIndex].text;
    if (param_name == "[no parameters]") { param_name = ""; }
    var librarybox = document.getElementById("library_select_" + String(i));
    var library_name = librarybox.options[librarybox.selectedIndex].text;

    // mc.libraries.push(library_name);

    mc.active_library_list.push(library_name + method_name + param_name)

    // Given a method name and parameters, query the SQLite database for all of
    // the runs.
    sqlstr = sqlstr + "SELECT DISTINCT metrics.metric, libraries.id, libraries.name, datasets.name, datasets.id, methods.name, methods.parameters " +
            "FROM metrics, datasets, methods, libraries WHERE metrics.dataset_id == datasets.id AND metrics.method_id == methods.id AND datasets.name == '" + mc.dataset_name + "' AND " +
            "methods.name == '" + method_name + "' AND methods.parameters == '" + param_name + "' AND libraries.name == '" + library_name + "' AND metrics.metric<>'{}' GROUP BY datasets.id, libraries.id";

    if (i < mc.control_list_length - 1)
    {
      sqlstr = sqlstr + " UNION ";
    }
  }

  sqlstr = sqlstr + ";";
  mc.results = db.exec(sqlstr);

  // Obtain unique list of metric names.
  mc.metric_names = []
  for(i = 0; i < mc.results[0].values.length; i++)
  {
    var json = jQuery.parseJSON(mc.results[0].values[i][0]);
    $.each(json, function (k, d) {
      if(mc.metric_names.indexOf(k) < 0) mc.metric_names.push(k);
    })
  }

  mc.clearChart();
  mc.buildChart();
}

// Remove everything on the page that belongs to us.
mc.clear = function()
{
  d3.selectAll(".methodcontrol").remove();
  d3.selectAll(".add_method_button").remove();
  d3.selectAll(".clear_methods_button").remove();
  d3.selectAll(".redraw_methods_button").remove();

  // Only things that belong to us are in the chart.
  mc.clearChart();
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
  d3.selectAll(".runtime-table").remove();
}

// Build the chart and display it on screen.
mc.buildChart = function()
{
  // Set up scales.
  var max_score = 0
  for(i = 0; i < mc.results[0].values.length; i++)
  {
    var json = jQuery.parseJSON(mc.results[0].values[i][0]);
    $.each(json, function (k, data) {
      if (data > max_score) max_score = data;
    })
  }

  var group_scale = d3.scale.ordinal()
    .domain(mc.metric_names)
    .rangeRoundBands([0, width], .1);

  var library_scale = d3.scale.ordinal()
    .domain(mc.active_library_list)
    .rangeRoundBands([0, group_scale.rangeBand()]);
  
  var score_scale = d3.scale.linear()
    .domain([0, max_score])
    .range([height, 0]);

  var y_scale = d3.scale.linear()
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
    .data(mc.metric_names.map(function(d) { return d; }).reduce(function(p, c) { p.push(c); return p; }, []))
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
        return "<strong>Score for " + d[3] + " (" + d[5] + "):</strong> <span style='color:yellow'>" + score + "</span>"; });

  svg.call(tip);

  // Add all of the data points.
  group.selectAll("rect")
    .data(function(d)
        {
        var ret = [];
        for(i = 0; i < mc.results[0].values.length; i++)
        {
          var json = jQuery.parseJSON(mc.results[0].values[i][0]);
          $.each(json, function (k, data) {
            if(k == d) { ret.push([data, mc.results[0].values[i][3], k, mc.results[0].values[i][2], mc.results[0].values[i][5], mc.results[0].values[i][6]]); }
          })
        }
        return ret;
        })
  .enter().append("rect")
    .attr("width", library_scale.rangeBand())
    .attr("x", function(d) { 
      return library_scale(d[3] + d[4] + d[5]);
    })
    .attr("y", function(d) { return score_scale(d[0], max_score); })
    .attr("height", function(d) { return height - score_scale(d[0]); })
    .style("fill", function(d) { return color(mc.active_library_list.indexOf(d[3] + d[4] + d[5])); })
    .on('mouseover', tip.show)
    .on('mouseout', tip.hide);

  // Now add a table of runtimes at the bottom.
  var table = d3.select(".svgholder").append("table")
      .attr("class", "runtime-table");
  var thead = table.append("thead");
  var tbody = table.append("tbody");

  var table_names = ["metric"];
  for(i = 0; i < mc.results[0].values.length; i++) table_names.push(i);

  mc.active_library_list.unshift("metric");
  var hrow = thead.append("tr").selectAll("th")
      .data(table_names)
      .enter()
      .append("th")
      .text(function(d) { return d; });

  var rows = tbody.selectAll("tr")
      .data(mc.metric_names)
      .enter()
      .append("tr");

  var resultFormat = d3.format("x>7.2f");
  rows.selectAll("td")
      .data(function(d) {
          var ret = [d];

          for(i = 1; i < mc.active_library_list.length; i++) // Skip "metric".
          {
            ret.push(['---']);
          }

          for(i = 0; i < mc.results[0].values.length; i++)
          {
            var library = mc.results[0].values[i][2] + mc.results[0].values[i][5] + mc.results[0].values[i][6];
            var json = jQuery.parseJSON(mc.results[0].values[i][0]);
            $.each(json, function (k, data) {
              if(k == d) {
                ret[mc.active_library_list.indexOf(library)] = ([data, mc.results[0].values[i][3], k]);
              }
            })
          }
          return ret;
      }).enter()
      .append("td")
      .html(function(d) { if (d[0] != "failure" && d[0] != "---") { if (typeof d == "string") { return d; } else { if (d[0] == ">9000") { return ">9000s"; } else { return "&nbsp;" + String(resultFormat(d[0])).replace(/x/g, '&nbsp;') + "&nbsp;"; } } } else { return d[0]; } })
      .attr("class", function(d) { if (typeof d == "string") { return "dataset-name"; } else if (d[0] == "---") { return "timing-not-run-cell"; } else if (d[0] == ">9000" || d[0] == "failure") { return "timing-text-cell"; } else { return "timing-cell"; } });
}
