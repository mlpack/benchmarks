// namespace mmpc = metric-multiple-parameter comparison
var mmpc = mmpc = mmpc || {};

mmpc.option = "";
mmpc.param = "";
mmpc.method_name = "";
mmpc.dataset_name = "";
mmpc.metric_name = "";
mmpc.libraries = []
mmpc.active_libraries = [];
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
  selectHolder.append("label")
      .attr("for", "option_select")
      .attr("class", "method-select-label")
      .text("Select option:");
  selectHolder.append("select")
      .attr("id", "option_select")
      .attr("onchange", "mmpc.optionSelect()");
  selectHolder.append("br");
  selectHolder.append("label")
      .attr("for", "param_select")
      .attr("class", "param-select-label")
      .text("Select params:");
  selectHolder.append("select")
      .attr("id", "param_select")
      .attr("onchange", "mmpc.paramSelect()");
  selectHolder.append("label")
      .attr("for", "metric_select")
      .attr("class", "method-select-label")
      .text("Select metric:");
  selectHolder.append("select")
      .attr("id", "metric_select")
      .attr("onchange", "mmpc.metricSelect()");
  mmpc.listMethods();
}

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

// List the datasets.
mmpc.listOptions = function()
{
  var sqlstr = "SELECT DISTINCT methods.parameters FROM datasets, methods, metrics " +
               "WHERE datasets.id == metrics.dataset_id " +
                 "AND methods.id == metrics.method_id " +
                 "AND methods.name == '" + mmpc.method_name + "' " +
                 "AND datasets.name == '" + mmpc.dataset_name + "';";
  var results = db.exec(sqlstr);

  addOption = function(p, c) {
    var options = mmpc.parseParams(c.toString());
    for (var opt in options)
    {
      if(p.indexOf(opt) < 0) p.push(opt);
    }
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
  clearSelectBox(document.getElementById("param_select"));
}

// List the datasets.
mmpc.listParams = function()
{
  var sqlstr = "SELECT DISTINCT methods.parameters FROM datasets, methods, metrics " +
               "WHERE datasets.id == metrics.dataset_id " +
                 "AND methods.id == metrics.method_id " +
                 "AND methods.name == '" + mmpc.method_name + "' " +
                 "AND datasets.name == '" + mmpc.dataset_name + "';";
  var results = db.exec(sqlstr);

  addParams = function(p, c) {
    var options = mmpc.parseParams(c.toString());
    if (mmpc.option in options)
    {
      delete options[mmpc.option];
      str = JSON.stringify(options);
      if(p.indexOf(str) < 0) p.push(str);
    }
    return p;
  };
  var params = results[0].values.reduce(addParams, []);

  var param_select_box = document.getElementById("param_select");
  clearSelectBox(param_select_box);
  for (i = 0; i < params.length; i++)
  {
    var new_param = document.createElement("option");
    new_param.text = params[i];
    param_select_box.add(new_param);
  }
  param_select_box.selectedIndex = -1;
  // Clear metrics box.
  clearSelectBox(document.getElementById("metric_select"));
}

// List the datasets.
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

  mmpc.listParams();
}

// The user has selected parameters.
mmpc.paramSelect = function()
{
  // Extract the name of the parameters we selected.
  var param_select_box = document.getElementById("param_select");
  mmpc.param = param_select_box.options[param_select_box.selectedIndex].text;

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

  // Obtain unique list of libraries.
  mmpc.libraries = mmpc.results[0].values.map(function(d) { return d[2]; })
      .reduce(function(p, c) { if(p.indexOf(c) < 0) p.push(c); return p; }, []);

  mmpc.active_libraries = {};
  for(i = 0; i < mmpc.libraries.length; i++)
    mmpc.active_libraries[mmpc.libraries[i]] = true;

  hasOption = function(d) {
    var metrics = jQuery.parseJSON(d[0]);
    var params = mmpc.parseParams(d[1].toString());
    if ((mmpc.metric_name in metrics) && (mmpc.option in params))
    {
      delete params[mmpc.option];
      str = JSON.stringify(params);
      return (str === mmpc.param);
    }
    return false;
  };

  setOptionVal = function(d) {
    d[0] = jQuery.parseJSON(d[0])[mmpc.metric_name];
    d[1] = parseFloat(mmpc.parseParams(d[1].toString())[mmpc.option]);
    return d;
  };

  mmpc.results[0].values = mmpc.results[0].values.filter(hasOption).map(setOptionVal);

  clearChart();
  buildChart();
}

// Remove everything on the page that belongs to us.
mmpc.clear = function()
{
  // Only things that belong to us are in the chart.
  mmpc.clearChart();
}

// Remove everything we have in the chart.
mmpc.clearChart = function()
{
  d3.select("svg").remove();
  d3.selectAll(".d3-tip").remove();
  d3.selectAll(".library-select-title").remove();
  d3.selectAll(".library-select-div").remove();
  d3.selectAll(".dataset-select-title").remove();
  d3.selectAll(".dataset-select-div").remove();
}

// Parse a list of parameters into a key-value dict.
mmpc.parseParams = function(str)
{
  optList = str.split(/-+/)
      .map(function (d) {return d.replace(/^\s+|\s+$/g, '').split(/[\s=]+/); })
  optList.shift();
  return optList.reduce(function (p, c){
    if (c.length > 1)
      p[c[0]] = c[1];
    else
      p[c[0]] = undefined;
    return p;
  }, {});
}

// Build the chart and display it on the screen.
mmpc.buildChart = function()
{
  // Set up scales.
  var score_list = mmpc.results[0].values.map(function(d) { return d[0]; })
  var maxScore = Math.max.apply(null, score_list);

  var param_list = mmpc.results[0].values.map(function(d) { return d[1]; });
  var minParam = Math.min.apply(null, param_list);
  var maxParam = Math.max.apply(null, param_list);

  var params_scale = d3.scale.linear()//ordinal()
      .domain([minParam, maxParam])
      .range([0, width]);

  var score_scale = d3.scale.linear()
      .domain([0, maxScore])
      .range([height, 0]);

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
      .text("Metric Score");

  // Create tooltips.
  var tip = d3.tip()
      .attr("class", "d3-tip")
      .offset([-10, 0])
      .html(function(d) {
          var score = d[0];
          if (d[0] != "") { score = d[0].toFixed(3); }
          return "<strong> Score for '" + d[1] + "' " + d[2] +
              ":</strong> <span style='color:yellow'>" + score + "</span>"; }
      );
  svg.call(tip);

  // Add all of the data points.
  var lineFunc = d3.svg.line()
      .x(function(d) { return params_scale(d[1]); })
      .y(function(d) { return score_scale(d[0]); });

  var lineResults = [];
  for (var l in mmpc.libraries)
  {
    if (mmpc.active_libraries[mmpc.libraries[l]] == true)
    {
      lineResults.push(mmpc.results[0].values
          .reduce(function(p, c) { if(c[2] == mmpc.libraries[l]) { p.push(c); } return p; }, [])
          .sort(function (a, b) {return a[1] - b[1];}));
    }
    else
      lineResults.push([]);
  }

  for(i = 0; i < lineResults.length; i++)
  {
    if (lineFunc(lineResults[i]) != null)
    {
      svg.append('svg:path')
          .attr('d', lineFunc(lineResults[i]))
          .attr('stroke', color(mmpc.libraries[i]))
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
        .attr("cx", function(d) { return params_scale(d[1]); })
        .attr("cy", function(d) { return score_scale(d[0]); })
        .attr('fill', '#222222')
        .on('mouseover', tip.show)
        .on('mouseout', tip.hide);
    svg.selectAll("dot").data(lineResults[i]).enter().append("circle")
        .attr("r", 4)
        .attr("cx", function(d) { return params_scale(d[1]); })
        .attr("cy", function(d) { return score_scale(d[0]); })
        .attr('fill', '#ffffff')
        .on('mouseover', tip.show)
        .on('mouseout', tip.hide);
    svg.selectAll("dot").data(lineResults[i]).enter().append("circle")
        .attr("r", 3)
        .attr("cx", function(d) { return params_scale(d[1]); })
        .attr("cy", function(d) { return score_scale(d[0]); })
        .attr('fill', function(d) { return color(d[2]) })
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
      .on('click', function() { mmpc.enableAllLibraries(); });
  librarySelectTitle.append("div")
      .attr("class", "library-select-title-bar")
      .text("|");
  librarySelectTitle.append("div")
      .attr("class", "library-select-title-disable-all")
      .text("disable all")
      .on('click', function() { mmpc.disableAllLibraries(); });
  librarySelectTitle.append("div")
      .attr("class", "library-select-title-close-paren")
      .text(")");

  var libraryDivs = d3.select(".legendholder").selectAll("input")
      .data(mmpc.libraries)
      .enter()
      .append("div")
      .attr("class", "library-select-div")
      .attr("id", function(d) { return d + '-library-checkbox-div'; });

  libraryDivs.append("label")
      .attr('for', function(d) { return d + '-library-checkbox'; })
      .style('background', color)
      .attr('class', 'library-select-color');

  libraryDivs.append("input")
      .property("checked", function(d) { return mmpc.active_libraries[d]; })
      .attr("type", "checkbox")
      .attr("id", function(d) { return d + '-library-checkbox'; })
      .attr('class', 'library-select-box')
      .attr("onClick", function(d, i) { return "mmpc.toggleLibrary(\"" + d + "\");"; });

  libraryDivs.append("label")
      .attr('for', function(d) { return d + '-library-checkbox'; })
      .attr('class', 'library-select-label')
      .text(function(d) { return d; });
}

// Toggle a library to on or off.
mmpc.toggleLibrary = function(library)
{
  mmpc.active_libraries[library] = !mmpc.active_libraries[library];

  clearChart();
  buildChart();
}

// Set all libraries on.
mmpc.enableAllLibraries = function()
{
  for (v in mmpc.active_libraries) { mmpc.active_libraries[v] = true; }

  clearChart();
  buildChart();
}

// Set all libraries off.
mmpc.disableAllLibraries = function()
{
  for (v in mmpc.active_libraries) { mmpc.active_libraries[v] = false; }

  clearChart();
  buildChart();
}

