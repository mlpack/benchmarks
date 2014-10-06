// Define namespace: dc = dataset comparison.
var dc = dc = dc || {};

dc.dataset_name = "";
dc.control_list_length = 0;
dc.methods = [];

// The chart type has been selected.
dc.onTypeSelect = function()
{
  var selectHolder = d3.select(".selectholder");
  selectHolder.append("label")
      .attr("for", "main_dataset_select")
      .attr("class", "main-dataset-select-label")
      .text("Select dataset:");
  selectHolder.append("select")
      .attr("id", "main_dataset_select")
      .attr("onchange", "dc.datasetSelect()");

  dc.listDatasets();
}

// List the datasets.
dc.listDatasets = function()
{
  var sqlstr = "SELECT datasets.name FROM datasets;";
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

// The user has selected a dataset.
dc.datasetSelect = function()
{
  var dataset_select_box = document.getElementById("main_dataset_select");
  dc.dataset_name = dataset_select_box.options[dataset_select_box.selectedIndex].text;

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
      .attr("onclick", "dc.clickAddButton()")
      .attr("value", "Add another method");
  d3.selectAll(".legendholder").append("input")
      .attr("type", "button")
      .attr("class", "clear_methods_button")
      .attr("onclick", "dc.clickClearMethods()")
      .attr("value", "Remove all methods");
  d3.selectAll(".legendholder").append("input")
      .attr("type", "button")
      .attr("class", "redraw_methods_button")
      .attr("onclick", "dc.clickRedrawMethods()")
      .attr("value", "Redraw graph");

  dc.control_list_length = 0;

  // Collect the results for lists of methods.
  var sqlstr = "SELECT DISTINCT methods.name, methods.parameters FROM methods, results, datasets WHERE results.dataset_id == datasets.id AND results.method_id == methods.id AND datasets.name == '" + dc.dataset_name + "' ORDER BY methods.name;";
  dc.methods = db.exec(sqlstr);
}

// The user has requested to add a new thing.
dc.clickAddButton = function()
{
  var newmethodcontrol = d3.selectAll(".methodcontrol").append("div").attr("class", "methodcontroldiv");

  newmethodcontrol.append("label")
      .attr("for", "method_select_" + String(dc.control_list_length))
      .attr("class", "method-select-label")
      .text("Method:");
  newmethodcontrol.append("select")
      .attr("id", "method_select_" + String(dc.control_list_length))
      .attr("onchange", "dc.methodControlListSelect('method_select_" + String(dc.control_list_length) + "')");
  newmethodcontrol.append("label")
      .attr("for", "param_select_" + String(dc.control_list_length))
      .attr("class", "param-select-label")
      .text("Parameters:");
  newmethodcontrol.append("select")
      .attr("id", "param_select_" + String(dc.control_list_length));

  dc.control_list_length++;

  // Add list of methods.
  var newbox = document.getElementById("method_select_" + String(dc.control_list_length - 1));
  console.log(JSON.stringify(dc.methods));
  distinct_methods = dc.methods[0].values.map(function(d) { return d[0]; }).reduce(function(p, c) { if(p.indexOf(c) < 0) p.push(c); return p; }, []);
  for (i = 0; i < distinct_methods.length; i++)
  {
    var new_option = document.createElement("option");
    new_option.text = distinct_methods[i];
    newbox.add(new_option);
  }
  newbox.selectedIndex = -1;
}

dc.methodControlListSelect = function(selectbox_id)
{
  var selectbox = document.getElementById(selectbox_id);
  var method_name = selectbox.options[selectbox.selectedIndex].text;

  // Now we need to add parameters.
  distinct_parameters = dc.methods[0].values.map(function(d) { return d;
}).reduce(function(p, c) { if
}

dc.clickClearMethods = function()
{
  d3.selectAll(".methodcontroldiv").remove();
  dc.control_list_length = 0;
}

// Remove everything on the page that belongs to us.
dc.clearChart = function()
{

}

// Build the chart and display it on screen.
dc.buildChart = function()
{

}
