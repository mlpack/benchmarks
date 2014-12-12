// Define namespace: mc = highest-metric-comparison.
var hmc = hmc = hmc || {};

hmc.method_name = "";
hmc.param_name = "";
hmc.dataset_name = "";
hmc.control_list_length = 0;
hmc.libraries = [];
hmc.datasets = []
hmc.active_metrics = [];
hmc.active_libraries = [];
hmc.metric_names = [];
hmc.results = 
hmc.active_library_list = [];

// The chart type has been selected.
hmc.onTypeSelect = function()
{
  var selectHolder = d3.select(".selectholder");
  selectHolder.append("label")
      .attr("for", "main_dataset_select")
      .attr("class", "main-dataset-select-label")
      .text("Select dataset:");
  selectHolder.append("select")
      .attr("id", "main_dataset_select")
      .attr("onchange", "hmc.datasetSelect()");
 selectHolder.append("label")
      .attr("for", "param_select")
      .attr("class", "param-select-label")
      .text("Sort results by:");
  selectHolder.append("select")
      .attr("id", "param_select")
      .attr("onchange", "hmc.orderSelect()");

  hmc.listDatasets();
}

hmc.orderSelect = function()
{
  var metric_select_box = document.getElementById("param_select");
  var metric = metric_select_box.options[metric_select_box.selectedIndex].text;

  hmc.results.sort(function(a, b)
  {

    var metric_a = 0;
    var metric_b = 0;

    for (i = 0; i < a[3].length; i++) {
      if (a[3][i][0] == metric) metric_a = a[3][i][1];
    };

    for (i = 0; i < b[3].length; i++) {
      if (b[3][i][0] == metric) metric_b = b[3][i][1];
    };

    return metric_a - metric_b;
  });
  hmc.results.reverse();

  hmc.clearChart();
  hmc.buildChart();
}

// List the datasets.
hmc.listDatasets = function()
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

hmc.datasetSelect = function()
{
  var dataset_select_box = document.getElementById("main_dataset_select");
  hmc.dataset_name = dataset_select_box.options[dataset_select_box.selectedIndex].text;

  // Create an empty chart.
  hmc.clear();



  var sqlstr = "SELECT DISTINCT libary_id from builds"
  var params = db.exec(sqlstr);
  sqlstr = "SELECT DISTINCT methods.name, methods.parameters, libraries.name, metrics.metric FROM methods, metrics, datasets, libraries, builds WHERE metrics.dataset_id == datasets.id AND metrics.method_id == methods.id AND datasets.name == '" + hmc.dataset_name + "' AND libraries.id == metrics.libary_id AND ("
  for(i = 0; i < params[0].values.length; i++)
  {
    var libsqlstr = "SELECT id FROM builds WHERE libary_id = " + params[0].values[i] + " ORDER BY id DESC LIMIT 1;"
    var libid = db.exec(libsqlstr)

    sqlstr += " metrics.build_id = "  + libid[0].values[0] + " OR "
  }
  sqlstr += " metrics.build_id = 0) ORDER BY methods.name;";

  hmc.results = db.exec(sqlstr)[0].values;

  // Obtain unique list of metric names.
  hmc.metric_names = ["Library", "Method"]
  var metric_select_box = document.getElementById("param_select");
  clearSelectBox(metric_select_box);
  for(i = 0; i < hmc.results.length; i++)
  {
    var json = jQuery.parseJSON(hmc.results[i][3]);
    var metrics = [];
    $.each(json, function (k, d) {
      metrics.push([k, d]);
      if(hmc.metric_names.indexOf(k) < 0) {
        hmc.metric_names.push(k);
        var new_option = document.createElement("option");
        new_option.text = k;
        metric_select_box.add(new_option);
      }
    })
    hmc.results[i][3] = metrics;
  }

  metric_select_box.selectedIndex = 0;
  hmc.orderSelect();

  hmc.clearChart();
  hmc.buildChart();
}

// Remove everything on the page that belongs to us.
hmc.clear = function()
{
  d3.selectAll(".methodcontrol").remove();
  d3.selectAll(".add_method_button").remove();
  d3.selectAll(".clear_methods_button").remove();
  d3.selectAll(".redraw_methods_button").remove();

  // Only things that belong to us are in the chart.
  hmc.clearChart();
}

// Remove everything we have in the chart.
hmc.clearChart = function()
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
hmc.buildChart = function()
{
  // Now add a table of metric results at the bottom.
  var table = d3.select(".svgholder").append("table")
      .attr("class", "runtime-table");
  var thead = table.append("thead");
  var tbody = table.append("tbody");
  
  var hrow = thead.append("tr").selectAll("th")
      .data(hmc.metric_names)
      .enter()
      .append("th")
      .text(function(d) { return d; });

  var rows = tbody.selectAll("tr")
      .data(hmc.results.map(function(d){
        return d[2];
      }))
      .enter()
      .append("tr")
      .text(function(d) { return d; });

  var resultFormat = d3.format("x>7.2f");
  rows.selectAll("td")
      .data(function(d, i) {        
        var method_name = hmc.results[i][0];
        if (hmc.results[i][1] == "") {
          method_name += " (default)";
        } else {
          method_name += " (" + hmc.results[i][1] + ")";
        }

        var ret = [method_name];
        for(j = 2; j < hmc.metric_names.length; j++) // Skip "library and method".
        {
          ret.push('---');
        }

        for(j = 0; j < hmc.results[i][3].length; j++)
        {
          ret[hmc.metric_names.indexOf(hmc.results[i][3][j][0]) - 1] = String(resultFormat(hmc.results[i][3][j][1])).replace(/x/g, '&nbsp;');
        }

        return ret;
      }).enter()
      .append("td")
      .html(function(d) { if (d[0] != "failure" && d[0] != "---") { if (typeof d == "string") { return d; } else { if (d[0] == ">9000") { return ">9000s"; } else { return "&nbsp;" + String(resultFormat(d[0])).replace(/x/g, '&nbsp;') + "&nbsp;"; } } } else { return d[0]; } })
      .attr("class", function(d) { if (typeof d == "string") { return "dataset-name"; } else if (d[0] == "---") { return "timing-not-run-cell"; } else if (d[0] == ">9000" || d[0] == "failure") { return "timing-text-cell"; } else { return "timing-cell"; } });
}
