// namespace mmpc = metric-multiple-parameter comparison
var mmpc = mmpc = mmpc || {};

mmpc.option = "";
mmpc.method_name = "";
mmpc.dataset_name = "";
mmpc.metric_name = "";
mmpc.control_list_length = 0;
mmpc.results = []

mmpc.onTypeSelect = function()
{
  var selectHolder = d3.select(".selectholder");
  selectHolder.append("label")
      .attr("for", "method_select")
      .attr("class", "method-select-label")
      .text("Select method:");
  selectHolder.append("select")
      .attr("id", "method_select")
      .attr("onchange", "mmpc.methodSelect()");
  selectHolder.append("label")
      .attr("for", "main_dataset_select")
      .attr("class", "main-dataset-select-label")
      .text("Select dataset:");
  selectHolder.append("select")
      .attr("id", "main_dataset_select")
      .attr("onchange", "mmpc.datasetSelect()");
  selectHolder.append("br");
  selectHolder.append("label")
      .attr("for", "option_select")
      .attr("class", "method-select-label")
      .text("Select option:");
  selectHolder.append("select")
      .attr("id", "option_select")
      .attr("onchange", "mmpc.optionSelect()");
  selectHolder.append("label")
      .attr("for", "metric_select")
      .attr("class", "method-select-label")
      .text("Select metric:");
  selectHolder.append("select")
      .attr("id", "metric_select")
      .attr("onchange", "mmpc.metricSelect()");
  mmpc.listMethods();
}

// List the methods.
mmpc.listMethods = function()
{
  var methods = db.exec("SELECT DISTINCT methods.name FROM methods, metrics " +
                        "WHERE methods.id=metrics.method_id ORDER BY name;");

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
  // Clear datasets box.
  clearSelectBox(document.getElementById("main_dataset_select"));
}

// List the datasets.
mmpc.listDatasets = function()
{
  var sqlstr = "SELECT DISTINCT datasets.name FROM datasets, metrics, methods " +
               "WHERE datasets.id == metrics.dataset_id " +
                 "AND methods.id == metrics.method_id " +
                 "AND methods.name == '" + mmpc.method_name + "' " +
                 "ORDER BY datasets.name;";
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
  // Clear metrics box.
  clearSelectBox(document.getElementById("option_select"));
}

// List different parameters.
mmpc.listOptions = function()
{
  var sqlstr = "SELECT DISTINCT methods.parameters FROM datasets, methods, metrics " +
               "WHERE datasets.id == metrics.dataset_id " +
                 "AND methods.id == metrics.method_id " +
                 "AND methods.name == '" + mmpc.method_name + "' " +
                 "AND datasets.name == '" + mmpc.dataset_name + "';";
  var results = db.exec(sqlstr);

  var addOption = function(p, c) {
    var options = mmpc.getOptionList(c.toString());
    for (i = 0; i < options.length; i++)
      if(p.indexOf(options[i]) < 0) p.push(options[i]);
    return p;
  };
  var options = results[0].values.reduce(addOption, []);

  var option_select_box = document.getElementById("option_select");
  clearSelectBox(option_select_box);
  for (i = 0; i < options.length; i++)
  {
    var new_option = document.createElement("option");
    new_option.text = options[i];
    option_select_box.add(new_option);
  }
  option_select_box.selectedIndex = -1;
  // Clear metrics box.
  clearSelectBox(document.getElementById("metric_select"));
}

// List the metrics.
mmpc.listMetrics = function()
{
  var sqlstr = "SELECT metrics.metric FROM datasets, metrics, methods " +
               "WHERE datasets.id == metrics.dataset_id " +
                 "AND methods.id == metrics.method_id " +
                 "AND methods.name == '" + mmpc.method_name + "' " +
                 "AND datasets.name == '" + mmpc.dataset_name + "';";
  var results = db.exec(sqlstr);

  addMetric = function(p, c) {
    var json = jQuery.parseJSON(c);
    for(var k in json)
      if(p.indexOf(k) < 0)
        p.push(k);
    return p;
  };
  metrics = results[0].values.reduce(addMetric, []);

  var metric_select_box = document.getElementById("metric_select");
  clearSelectBox(metric_select_box);
  for (i = 0; i < metrics.length; i++)
  {
    var new_option = document.createElement("option");
    new_option.text = metrics[i];
    metric_select_box.add(new_option);
  }
  metric_select_box.selectedIndex = -1;
}

// The user has selected a method.
mmpc.methodSelect = function()
{
  // Extract the name of the method we selected.
  var method_select_box = document.getElementById("method_select");
  mmpc.method_name = method_select_box.options[method_select_box.selectedIndex].text;

  mmpc.listDatasets();
}

// The user has selected a dataset.
mmpc.datasetSelect = function()
{
  // Extract the name of the dataset we selected.
  var dataset_select_box = document.getElementById("main_dataset_select");
  mmpc.dataset_name = dataset_select_box.options[dataset_select_box.selectedIndex].text;

  mmpc.listOptions();
}

// The user has selected an option.
mmpc.optionSelect = function()
{
  // Extract the name of the option we selected.
  var option_select_box = document.getElementById("option_select");
  mmpc.option = option_select_box.options[option_select_box.selectedIndex].text;

  mmpc.listMetrics();
}

// The user has selected a metric.
mmpc.metricSelect = function()
{
  // Extract the name of the metric we selected.
  var metric_select_box = document.getElementById("metric_select");
  mmpc.metric_name = metric_select_box.options[metric_select_box.selectedIndex].text;

  var sqlstr = "SELECT metrics.metric, methods.parameters, libraries.name, metrics.build_id " +
               "FROM datasets, metrics, methods, libraries, builds " +
               "WHERE datasets.id == metrics.dataset_id " +
                 "AND methods.id == metrics.method_id " +
                 "AND metrics.libary_id == libraries.id " +
                 "AND builds.id == metrics.build_id " +
                 "AND methods.name == '" + mmpc.method_name + "' " +
                 "AND datasets.name == '" + mmpc.dataset_name + "';";
  mmpc.results = db.exec(sqlstr);

  var filterAndSet = function(p, d) {
    var metrics = jQuery.parseJSON(d[0]);
    var value = mmpc.getOptionValue(d[1].toString(), mmpc.option);
    if(value != "" && mmpc.metric_name in metrics)
    {
      d[0] = metrics[mmpc.metric_name];
      d[1] = mmpc.removeOption(d[1].toString(), mmpc.option);
      d[4] = value;
      p.push(d);
    }
    return p;
  };
  mmpc.results[0].values = mmpc.results[0].values.reduce(filterAndSet,[]);

  // Create an empty chart.
  mmpc.clear();

  // Now create the legend at the bottom that will allow us to add/remove
  // methods.
  d3.selectAll(".legendholder").append("div").attr("class", "methodcontrol");

  d3.selectAll(".legendholder").append("input")
      .attr("type", "button")
      .attr("class", "add_method_button")
      .attr("onclick", "mmpc.clickAddButton()")
      .attr("value", "Add");
  d3.selectAll(".legendholder").append("input")
      .attr("type", "button")
      .attr("class", "clear_methods_button")
      .attr("onclick", "mmpc.clickClearMethods()")
      .attr("value", "Remove all");
  d3.selectAll(".legendholder").append("input")
      .attr("type", "button")
      .attr("class", "redraw_methods_button")
      .attr("onclick", "mmpc.clickRedrawMethods()")
      .attr("value", "Redraw graph");

  mmpc.control_list_length = 0;
}

// The user has requested to add a new thing.
mmpc.clickAddButton = function()
{
  var newmethodcontrol = d3.selectAll(".methodcontrol").append("div").attr("class", "methodcontroldiv");

  newmethodcontrol.append("label")
      .attr("class", "mmpc-index-label")
      .text(String(mmpc.control_list_length));
  newmethodcontrol.append("label")
      .style('background', color(mmpc.control_list_length))
      .attr('class', 'library-select-color');
  newmethodcontrol.append("label")
      .attr("for", "library_select_" + String(mmpc.control_list_length))
      .attr("class", "mmpc-library-select-label")
      .text("Library:");
  newmethodcontrol.append("select")
      .attr("id", "library_select_" + String(mmpc.control_list_length))
      .attr("onchange", "mmpc.libraryControlListSelect('" + String(mmpc.control_list_length) + "')");
  newmethodcontrol.append("label")
      .attr("for", "param_select_" + String(mmpc.control_list_length))
      .attr("class", "mmpc-param-select-label")
      .text("Parameter:");
  newmethodcontrol.append("select")
      .attr("id", "param_select_" + String(mmpc.control_list_length));

  mmpc.control_list_length++;

  var addLibrary = function(p, d) {
    if (p.indexOf(d[2]) < 0)
        p.push(d[2]);
    return p;
  };
  distinct_libraries = mmpc.results[0].values.reduce(addLibrary, []);

  var library_select_box = document.getElementById("library_select_" + String(mmpc.control_list_length - 1));
  clearSelectBox(library_select_box);
  for(i = 0; i < distinct_libraries.length; i++)
  {
    var new_option = document.createElement("option");
    new_option.text = distinct_libraries[i];
    library_select_box.add(new_option);
  }
  library_select_box.selectedIndex = -1;
}

mmpc.libraryControlListSelect = function(id)
{
  var library_select_box = document.getElementById("library_select_" + id);
  var library_name = library_select_box.options[library_select_box.selectedIndex].text;

  // Add list of parameters.
  var addParams = function(p, d) {
    if (library_name === d[2].toString() && p.indexOf(d[1]) < 0)
      p.push(d[1]);
    return p;
  };
  var params = mmpc.results[0].values.reduce(addParams, []);
  var parambox = document.getElementById("param_select_" + id);
  clearSelectBox(parambox);
  for (i = 0; i < params.length; i++)
  {
    var new_option = document.createElement("option");
    new_option.text = params[i];
    parambox.add(new_option);
  }
  parambox.selectedIndex = -1;
}

mmpc.clickClearMethods = function()
{
  d3.selectAll(".methodcontroldiv").remove();
  mmpc.control_list_length = 0;
  clearChart(); // Remove the chart too.
}

// The user wants a plot of everything we have.
mmpc.clickRedrawMethods = function()
{
  mmpc.clearChart();
  mmpc.buildChart();
}

// Remove everything on the page that belongs to us.
mmpc.clear = function()
{
  d3.selectAll(".methodcontrol").remove();
  d3.selectAll(".add_method_button").remove();
  d3.selectAll(".clear_methods_button").remove();
  d3.selectAll(".redraw_methods_button").remove();

  mmpc.clearChart();
}

// Remove everything we have in the chart.
mmpc.clearChart = function()
{
  d3.select("svg").remove();
  d3.selectAll(".d3-tip").remove();
}

// Return a param's value from a list of parameters.
mmpc.getOptionValue = function(str, opt)
{
  var list = str.split("-" + opt)
  if (list.length < 2)
    return "";
  list = list[1].split(/[\s=]+/);
  if (list.length < 2)
    return "";
  return list[1];
}

// Remove a parameter from the list of parameters.
mmpc.removeOption = function(str, opt)
{
  return str.replace(new RegExp("-+" + opt + "[^-]*"),'').replace(/^\s+|\s+$/g, '');
}

// Returns a list of parameters.
mmpc.getOptionList = function(str)
{
  optList = str.split(/-+/)
      .map(function (d) {return d.replace(/^\s+|\s+$/g, '').split(/[\s=]+/); })
      .filter(function (d) {return (d.length > 1);})
      .map(function (d) {return d[0];});
  optList.shift();
  return optList;
}

// Build the chart and display it on the screen.
mmpc.buildChart = function()
{
  var numeric_param = ! mmpc.results[0].values
      .map(function (d) {return isNaN(d[4]);})
      .reduce(function (p, c) {return (p || c);},false);


  if (numeric_param) //Parse numbers.
    mmpc.results[0].values = mmpc.results[0].values
        .map(function (d) {d[4] = parseFloat(d[4]); return d;});

  var lineResults = [];
  for (i = 0; i < mmpc.control_list_length; i++)
  {
    var parambox = document.getElementById("param_select_" + String(i));
    var param_name = parambox.options[parambox.selectedIndex].text;
    var librarybox = document.getElementById("library_select_" + String(i));
    var library_name = librarybox.options[librarybox.selectedIndex].text;
    //Filter results that match library and parameters.
    var hasLibraryAndParams = function(d) {
      return (param_name == d[1] && library_name == d[2]);
    };
    var results = mmpc.results[0].values.filter(hasLibraryAndParams)
    //Order by asc parameter value, desc build id.
    results = results.sort(function (a, b) {
        if (a[4] == b[4])
          return b[3] - a[3];
        if (a[4] < b[4])
          return -1;
        return 1
    });
    //Remove duplicated cases for a given value (The first is chosen, the one with higher build id).
    distinct_res = [];
    for (j = 0; j < results.length; j++)
      if(j == 0 || results[j-1][4] != results[j][4])
        distinct_res.push(results[j]);
    //Add list of results.
    lineResults.push(distinct_res);
  }

  // Set up scales.
  var instances = lineResults.reduce(function (p, d) {return p.concat(d);},[]);
  var score_list = instances.map(function(d) {return d[0];});
  var maxScore = Math.max.apply(null, score_list);
  var score_scale = d3.scale.linear()
      .domain([0, maxScore])
      .range([height, 0]);

  var params_scale;
  var param_list = instances.map(function(d) {return d[4];})
      .reduce(function (p, d) {if(p.indexOf(d) < 0) p.push(d); return p;},[]);
  if (numeric_param)
  {
    var minParam = Math.min.apply(null, param_list);
    var maxParam = Math.max.apply(null, param_list);
    params_scale = d3.scale.linear()
        .domain([minParam, maxParam])
        .range([0, width]);
  }
  else
    params_scale = d3.scale.ordinal()
        .domain(param_list)
        .rangePoints([0, width], .1);

  // Set up axes.
  var xAxis = d3.svg.axis().scale(params_scale).orient("bottom");
  var yAxis = d3.svg.axis().scale(score_scale).orient("left")
      .tickFormat(d3.format(".2s"));

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
      .text(mmpc.metric_name);

  // Create tooltips.
  var tip = d3.tip()
      .attr("class", "d3-tip")
      .offset([-10, 0])
      .html(function(d) {
          return "<strong> Score for '" + d[4].toString() + "' (" + d[2] +
              ", '" + d[1] + "'):</strong> <span style='color:yellow'>" + d[0] + "</span>"; }
      );
  svg.call(tip);

  // Add all of the data points.
  var lineFunc = d3.svg.line()
      .x(function(d) { return params_scale(d[4]); })
      .y(function(d) { return score_scale(d[0]); });

  for(i = 0; i < lineResults.length; i++)
  {
    if (lineFunc(lineResults[i]) != null)
    {
      svg.append('svg:path')
          .attr('d', lineFunc(lineResults[i]))
          .attr('stroke', color(i))
          .attr('stroke-width', 2)
          .attr('fill', 'none');
    }
  }

  for(i = 0; i < lineResults.length; i++)
  {
    if (lineFunc(lineResults[i]) == null)
      continue;

    // Colored circle enclosed in white circle enclosed in background color
    // circle; looks kind of nice.
    svg.selectAll("dot").data(lineResults[i]).enter().append("circle")
        .attr("r", 6)
        .attr("cx", function(d) { return params_scale(d[4]); })
        .attr("cy", function(d) { return score_scale(d[0]); })
        .attr('fill', '#222222')
        .on('mouseover', tip.show)
        .on('mouseout', tip.hide);
    svg.selectAll("dot").data(lineResults[i]).enter().append("circle")
        .attr("r", 4)
        .attr("cx", function(d) { return params_scale(d[4]); })
        .attr("cy", function(d) { return score_scale(d[0]); })
        .attr('fill', '#ffffff')
        .on('mouseover', tip.show)
        .on('mouseout', tip.hide);
    svg.selectAll("dot").data(lineResults[i]).enter().append("circle")
        .attr("r", 3)
        .attr("cx", function(d) { return params_scale(d[4]); })
        .attr("cy", function(d) { return score_scale(d[0]); })
        .attr('fill', function(d) { return color(i); })
        .on('mouseover', tip.show)
        .on('mouseout', tip.hide);
  }
}

