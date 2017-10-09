// Define namespace: apmc = all parameters metric comparison.
var apmc = apmc = apmc || {};

apmc.methodName = "";
apmc.dataset = "";
apmc.libraries = [];
apmc.activeLibraries = [];
apmc.results = [];
apmc.sweepId = -1;

// This chart type has been selected.
apmc.onTypeSelect = function()
{
  // The user needs to be able to select a method, then parameters, then a
  // dataset.
  var selectHolder = d3.select(".selectholder");
  selectHolder.append("label")
      .attr("for", "method_select")
      .attr("class", "method-select-label")
      .text("Select method:");
  selectHolder.append("select")
      .attr("id", "method_select")
      .attr("onchange", "apmc.methodSelect()");
  selectHolder.append("label")
      .attr("for", "dataset_select")
      .attr("class", "dataset-select-label")
      .text("Select dataset:");
  selectHolder.append("select")
      .attr("id", "dataset_select")
      .attr("onchange", "apmc.datasetSelect()");
  selectHolder.append("label")
      .attr("for", "metric_select")
      .attr("class", "metric-select-label")
      .text("Select metric:");
  selectHolder.append("select")
      .attr("id", "metric_select")
      .attr("onchange", "apmc.metricSelect()");

  apmc.listMethods();
}

apmc.clear = function()
{
  apmc.clearChart();
}

apmc.process_library_name = function(l, p)
{
  // We want to turn the library name and parameters dict into, e.g.,
  // mlpack: max_iterations=sweep(10, 10, 100), algorithm=lbfgs
  var output = l;
  var i = 0;
  var d = jQuery.parseJSON(p);
  if (Object.keys(d).length > 0)
  {
    output += ": ";
    for (pp in d)
    {
      output += pp + "=" + d[pp];
      i++;
      if (i != Object.keys(d).length)
        output += ";";
    }
  }

  return output;
}

// List the available methods where there is a sweep.
apmc.listMethods = function()
{
  var methods = dbExec("SELECT DISTINCT methods.name FROM methods, results "
      + "WHERE methods.id = results.method_id ORDER BY name;");
  var methodSelectBox = document.getElementById("method_select");

  // Remove old things.
  clearSelectBox(methodSelectBox);

  // Add new things.
  var length = dbType === "sqlite" ? methods[0].values.length : methods.length;
  for (i = 0; i < length; i++)
  {
    var newOption = document.createElement("option");
    newOption.text = dbType === "sqlite" ? methods[0].values[i] :
        methods[i].name;
    methodSelectBox.add(newOption);
  }
  methodSelectBox.selectedIndex = -1;

  // Clear dataset box.
  clearSelectBox(document.getElementById("dataset_select"));
}

// Called when the user selects a method.
apmc.methodSelect = function()
{
  // Extract the name of the method we selected.
  var methodSelectBox = document.getElementById("method_select");
  apmc.methodName = methodSelectBox.options[methodSelectBox.selectedIndex].text; // At higher scope.

  // Now we need to get the datasets.
  var sqlstr = "SELECT DISTINCT datasets.name FROM datasets, results, methods "
      + "WHERE datasets.id = results.dataset_id AND methods.name = '"
      + apmc.methodName + "' AND results.method_id = methods.id;";
  var datasets = dbExec(sqlstr);

  // Loop through results and fill the second list box.
  var datasetSelectBox = document.getElementById("dataset_select");
  clearSelectBox(datasetSelectBox);

  var newOption = document.createElement("option");
  datasetSelectBox.add(newOption);

  datasetSelectBox.selectedIndex = 0;
  if ((dbType === "sqlite" && datasets[0]) || (dbType === "mysql" && datasets))
  {
    // Put in the datasets.
    var length = dbType === "sqlite" ? datasets[0].values.length : datasets.length;
    for (i = 0; i < length; i++)
    {
      newOption = document.createElement("option");

      var datasetName = dbType === "sqlite" ? datasets[0].values[i][0] : datasets[i].name;
      newOption.text = datasetName;
      datasetSelectBox.add(newOption);
    }
  }

  datasetSelectBox.selectedIndex = 0;
}

apmc.datasetSelect = function()
{
  // The user selected a dataset, so now we can ask them to select the metric
  // they want.
  var methodSelectBox = document.getElementById("method_select");
  apmc.methodName = methodSelectBox.options[methodSelectBox.selectedIndex].text;
  var datasetSelectBox = document.getElementById("dataset_select");
  var datasetName =
      datasetSelectBox.options[datasetSelectBox.selectedIndex].text;

  // What metrics do we have available?  We can do our actual query for results
  // here, then we need to parse it.  We want all of the most recent results.
  var sqlstr = "SELECT metrics.metric, metrics.build_id, metrics.sweep_id, "
      + "metrics.sweep_elem_id, libraries.name, methods.parameters "
      + "FROM datasets, methods, metrics, libraries "
      + "WHERE metrics.libary_id = libraries.id"
      + "  AND datasets.id = metrics.dataset_id"
      + "  AND datasets.name = '" + datasetName + "'"
      + "  AND methods.name = '" + apmc.methodName + "'"
      + "  AND metrics.method_id = methods.id;";
  apmc.results = dbExec(sqlstr);
  apmc.results = dbType === "sqlite" ? apmc.results[0].values : apmc.results;

  // Also determine the maximum build number for a given library.
  apmc.libraryVersions = {}
  addLibrary = function(p, c)
  {
    var lib = (dbType === "sqlite") ? c[4] : c.name;
    var params = (dbType === "sqlite") ? c[5] : c.parameters;
    var bid = (dbType === "sqlite") ? c[1] : c.build_id;

    if (lib in apmc.libraryVersions)
    {
      if (params in apmc.libraryVersions[lib])
      {
        if (apmc.libraryVersions[lib][params] < bid)
          apmc.libraryVersions[lib][params] = bid;
      }
      else
      {
        apmc.libraryVersions[lib][params] = bid;
      }
    }
    else
    {
      apmc.libraryVersions[lib] = {}
      apmc.libraryVersions[lib][params] = bid;
    }

    return;
  }
  apmc.results.reduce(addLibrary, []);

  // Filter out rows that weren't the newest.
  apmc.results = apmc.results.filter(function(c)
      {
        return (((dbType === "sqlite") ? c[1] : c.build_id) ==
            apmc.libraryVersions[((dbType === "sqlite") ? c[4] : c.name)][((dbType === "sqlite") ? c[5] : c.params)]);
      });

  // Lastly, we need to gather all of the sweeps we might have.
  apmc.sweeps = {}
  addSweep = function(p, c)
  {
    var params = jQuery.parseJSON((dbType === "sqlite") ? c[5] : c.parameters);
    for (e in params)
    {
      if (String(params[e]).indexOf("sweep(") != -1)
      {
        // Do we already know about this sweep?
        if (String(params[e]) in apmc.sweeps)
          continue;

        // Great, we have a sweep---now we need to get the information.
        sqlstr = "SELECT type, begin, step, end FROM sweeps WHERE id = " +
            ((dbType === "sqlite") ? c[2] : c.sweep_id) + ";";
        var sweepResults = dbExec(sqlstr);
        // There should only be one result...
        sweepResults = (dbType === "sqlite" ? sweepResults[0].values[0] : sweepResults[0]);

        // Insert these results into the dict.
        apmc.sweeps[String(params[e])] =
            { "type": (dbType === "sqlite" ? sweepResults[0] : sweepResults.type),
              "begin": (dbType === "sqlite" ? sweepResults[1] : sweepResults.begin),
              "step": (dbType === "sqlite" ? sweepResults[2] : sweepResults.step),
              "end": (dbType === "sqlite" ? sweepResults[3] : sweepResults.end) };
      }
    }
  }
  apmc.results.reduce(addSweep, []);

  // Now we have to parse through the metrics and see what we find.
  addMetric = function(p, c)
  {
    var json = jQuery.parseJSON(dbType === "sqlite" ? c[0] : c.metric);
    for(var k in json)
      if(p.indexOf(k) < 0)
        p.push(k);
    return p;
  };
  metrics = apmc.results.reduce(addMetric, []);

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

apmc.metricSelect = function()
{
  // We've already got the results, and now the user has specified the metric
  // they want plotted.
  var metricSelectBox = document.getElementById("metric_select");
  apmc.metricName = metricSelectBox.options[metricSelectBox.selectedIndex].text;

  // Obtain unique list of libraries.
  apmc.libraries = apmc.results.map(
      function(d) {
          return dbType === "sqlite" ? apmc.process_library_name(d[4], d[5]) : apmc.process_library_name(d.lib, d.parameters);
      }).reduce(
      function(p, c) {
          if (p.indexOf(c) < 0) p.push(c); return p;
      }, []);
  console.log(apmc.libraries);

  // By default, all libraries are active.
  apmc.activeLibraries = {};
  for (i = 0; i < apmc.libraries.length; ++i)
  {
    apmc.activeLibraries[apmc.libraries[i]] = true;
  }

  clearChart();
  buildChart();
}

apmc.clearChart = function()
{
  d3.select("svg").remove();
  d3.selectAll(".d3-tip").remove();
  d3.selectAll(".library-select-title").remove();
  d3.selectAll(".library_select_div").remove();
  d3.selectAll(".legendholder").selectAll("*").remove();
}

apmc.extractRuntime = function(d)
{
  var json = jQuery.parseJSON(d);
  for (var m in json)
  {
    if (m == "Runtime")
    {
      if (json[m] == -2)
        return "failure";
      else if (json[m] == -1)
        return "timeout";
      else if (String(json[m]).indexOf(">") != -1)
        return "timeout";
      else
        return json[m];
    }
  }

  return "failure";
}

apmc.extractMetric = function(d, metricName, notFoundValue)
{
  var json = jQuery.parseJSON(d);
  for (var m in json)
    if (m == metricName)
      return json[m];

  return notFoundValue;
}

apmc.buildChart = function()
{
  // Get lists of active library/param combinations.
  var activeLibraryList = apmc.libraries.map(function(d) { return d; }).reduce(
      function(p, c)
      {
        if (apmc.activeLibraries[c] == true)
          p.push(c);
        return p;
      }, []);

  var maxRuntime = d3.max(apmc.results,
      function(d)
      {
        if (apmc.activeLibraries[dbType === "sqlite" ? apmc.process_library_name(d[4], d[5]) : apmc.process_library_name(d.name, d.parameters)] == false)
        {
          return 0;
        }
        else
        {
          x = apmc.extractRuntime(dbType === "sqlite" ? d[0] : d.metric);
          if (x === "failure" || x === "timeout")
            return 0;
          else
            return x;
        }
      });

  var maxMetric = d3.max(apmc.results,
      function(d)
      {
        if (apmc.activeLibraries[dbType === "sqlite" ? apmc.process_library_name(d[4], d[5]) : apmc.process_library_name(d.name, d.parameters)] == false)
          return 0;
        else
          return apmc.extractMetric(dbType === "sqlite" ? d[0] : d.metric,
              apmc.metricName, 0);
      });

  // Increase so we have 16 spare pixels at the top.
  maxMetric *= ((height + 16) / height);

  console.log(maxRuntime);
  var runtimeScale = d3.scale.linear()
      .domain([0, maxRuntime])
      .range([0, width]);

  // We need to find out how big the sweep is.
//  var sweepSql = "SELECT type, begin, step, end FROM sweeps where id = " + apmc.sweepId;
//  var sweepResults = dbExec(sweepSql);
//  sweepResults = dbType === "sqlite" ? sweepResults[0].values : sweepResults.results;

//  var func = (dbType === "sqlite" ? sweepResults[0][0] : sweepResults[0].type) === "int" ? parseInt : parseFloat;
//  var start = func(dbType === "sqlite" ? sweepResults[0][1] : sweepResults[0].start);
//  var step = func(dbType === "sqlite" ? sweepResults[0][2] : sweepResults[0].step);
//  var end = func(dbType === "sqlite" ? sweepResults[0][3] : sweepResults[0].end);

  var metricScale = d3.scale.linear()
      .domain([0, maxMetric])
      .range([height, 0]);

  var xAxis = d3.svg.axis().scale(runtimeScale).orient("bottom");
  var yAxis = d3.svg.axis().scale(metricScale).orient("left");

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
      .append("text")
      .style("text-anchor", "end")
      .attr("dx", 500)
      .attr("dy", "3em")
      .text("Runtime (s)");

  // Add y axis.
  svg.append("g").attr("id", "yaxis")
      .attr("class", "y axis")
      .call(yAxis)
      .append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 6)
      .attr("dy", ".71em")
      .style("text-anchor", "end")
      .text(apmc.metricName);

  // Create tooltips.
  var tip = d3.tip()
      .attr("class", "d3-tip")
      .offset([-10, 0])
      .html(function(d) {
          var runtime = apmc.extractRuntime(dbType === "sqlite" ? d[0] : d.metric);
          if (runtime != "timeout" && runtime != "failure") {
            runtime = runtime.toFixed(3);
          }
          var metricValue = apmc.extractMetric(dbType === "sqlite" ? d[0] : d.metric, apmc.metricName, "");
          if (metricValue != "timeout" && metricValue != "failure" &&
String(metricValue).indexOf(">") == -1 && metricValue != "")
          {
            metricValue = metricValue.toFixed(3);
          }
          else if (metricValue == "")
          {
            metricValue = "failure";
          }

          var libName = (dbType === "sqlite" ? d[4] : d.name);
          var paramName = (dbType === "sqlite" ? d[5] : d.parameters);
          var start = 0;
          var step = 0;
          // Goal: output, e.g.,
          // mlpack:
          // non_sweep_param_1=x, non_sweep_param_2=x, sweep_param=x
          // metric: <value>
          // runtime: <value>
          // All centered with a border in the desired color.
          output = "<b>" + libName + "</b><br/>";
          // Loop over parameters.
          params = jQuery.parseJSON(paramName);
          for (p in params)
          {
            output += p + ": ";
            // Is it a sweep option?
            if (String(params[p]).indexOf("sweep(") != -1)
            {
              // Get sweep element.
              var sweepElemId = (dbType === "sqlite" ? d[3] : d.sweep_elem_id);

              var func = (apmc.sweeps[params[p]]['type'] === "int" ? parseInt : parseFloat);
              var start = func(apmc.sweeps[params[p]]['begin']);
              var step = func(apmc.sweeps[params[p]]['step']);

              output += (start + step * sweepElemId);
            }
            else
            {
              output += String(params[p]);
            }
            output += "; ";
          }
          output += "<br/>";
          output += apmc.metricName + ": " + metricValue + "<br/>";
          output += "Runtime: " + runtime;
          if (runtime != "failure" && runtime != "timeout")
          {
            output += "s<br/>";
          }

          return output;
      });
  svg.call(tip);

  // Add all of the data points.
  var lineFunc = d3.svg.line()
      .x(function(d) { return runtimeScale(mapRuntime(apmc.extractRuntime(
          dbType === "sqlite" ? d[0] : d.metric), maxRuntime)); })
      .y(function(d) { return metricScale(apmc.extractMetric(
          dbType === "sqlite" ? d[0] : d.metric, apmc.metricName, 0)); })
      .interpolate("linear");

  // Add all of the data points.
  for (var l in apmc.libraryVersions)
  {
    for (var p in apmc.libraryVersions[l])
    {
      if (!apmc.activeLibraries[apmc.process_library_name(l, p)])
        continue;

      // Now we have a library/parameters combination.
      // Collect all the data and let's see if we have a sweep or just a single
      // point.
      var res = apmc.results.filter(function(c)
          {
            var ln = (dbType === "sqlite") ? c[4] : c.name;
            var pn = (dbType === "sqlite") ? c[5] : c.parameters;
            return ((ln === l) && (pn === p));
          });

      if (res.length > 0)
      {
        svg.append('svg:path')
            .attr('d', lineFunc(res))
            .attr('stroke', color(l + ': ' + p))
            .attr('stroke-width', 2)
            .attr('fill', 'none');

        // Colored circle enclosed in white circle enclosed in background color
        // circle; looks kind of nice.
        svg.selectAll("dot").data(res).enter().append("circle")
            .attr("r", 6)
            .attr("cx", function(d) { return runtimeScale(mapRuntime(apmc.extractRuntime(dbType === "sqlite" ? d[0] : d.metric), maxRuntime)); })
            .attr("cy", function(d) { return metricScale(apmc.extractMetric(dbType === "sqlite" ? d[0] : d.metric, apmc.metricName, 0)); })
            .attr('fill', '#222222')
            .on('mouseover', function(d, i)
                {
                  d3.select('.d3-tip').style("border-color", color((dbType === "sqlite") ? apmc.process_library_name(d[4], d[5]) : apmc.process_library_name(d.name, d.parameters)));
                  tip.show(d, i);
                })
            .on('mouseout', tip.hide);
        svg.selectAll("dot").data(res).enter().append("circle")
            .attr("r", 4)
            .attr("cx", function(d) { return runtimeScale(mapRuntime(apmc.extractRuntime(dbType === "sqlite" ? d[0] : d.metric), maxRuntime)); })
            .attr("cy", function(d) { return metricScale(apmc.extractMetric(dbType === "sqlite" ? d[0] : d.metric, apmc.metricName, 0)); })
            .attr('fill', '#ffffff')
            .on('mouseover', function(d, i)
                {
                  d3.select('.d3-tip').style("border-color", color((dbType === "sqlite") ? apmc.process_library_name(d[4], d[5]) : apmc.process_library_name(d.name, d.parameters)));
                  tip.show(d, i);
                })
            .on('mouseout', tip.hide);
        svg.selectAll("dot").data(res).enter().append("circle")
            .attr("r", 3)
            .attr("cx", function(d) { return runtimeScale(mapRuntime(apmc.extractRuntime(dbType === "sqlite" ? d[0] : d.metric), maxRuntime)); })
            .attr("cy", function(d) { return metricScale(apmc.extractMetric(dbType === "sqlite" ? d[0] : d.metric, apmc.metricName, 0)); })
            .attr('fill', function(d) { return color((dbType === "sqlite") ? apmc.process_library_name(d[4], d[5]) : apmc.process_library_name(d.name, d.parameters)) })
            .on('mouseover', function(d, i)
                {
                  d3.select('.d3-tip').style("border-color", color((dbType === "sqlite") ? apmc.process_library_name(d[4], d[5]) : apmc.process_library_name(d.name, d.parameters)));
                  tip.show(d, i);
                })
            .on('mouseout', tip.hide);
      }
    }
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
    .on('click', function() { apmc.enableAllLibraries(); });
  librarySelectTitle.append("div")
    .attr("class", "library-select-title-bar")
    .text("|");
  librarySelectTitle.append("div")
    .attr("class", "library-select-title-disable-all")
    .text("disable all")
    .on('click', function() { apmc.disableAllLibraries(); });
  librarySelectTitle.append("div")
    .attr("class", "library-select-title-close-paren")
    .text(")");

  var libraryDivs = d3.select(".legendholder").selectAll("input")
    .data(apmc.libraries)
    .enter()
    .append("div")
    .attr("class", "library-select-div")
    .attr("id", function(d) { return d + '-library-checkbox-div'; });

  libraryDivs.append("label")
    .attr('for', function(d) { return d + '-library-checkbox'; })
    .style('background', color)
    .attr('class', 'library-select-color');

  libraryDivs.append("input")
    .property("checked", function(d) { return apmc.activeLibraries[d]; })
    .attr("type", "checkbox")
    .attr("id", function(d) { return d + '-library-checkbox'; })
    .attr('class', 'library-select-box')
    .attr("onClick", function(d, i) { return "apmc.toggleLibrary('" + d + "');"; });

  libraryDivs.append("label")
    .attr('for', function(d) { return d + '-library-checkbox'; })
    .attr('class', 'library-select-label')
    .text(function(d) { return d; });
}

// Toggle a library to on or off.
apmc.toggleLibrary = function(library)
{
  apmc.activeLibraries[library] = !apmc.activeLibraries[library];

  clearChart();
  buildChart();
}

// Set all libraries on.
apmc.enableAllLibraries = function()
{
  for (v in apmc.activeLibraries) { apmc.activeLibraries[v] = true; }

  clearChart();
  buildChart();
}

// Set all libraries off.
apmc.disableAllLibraries = function()
{
  for (v in apmc.activeLibraries) { apmc.activeLibraries[v] = false; }

  clearChart();
  buildChart();
}
