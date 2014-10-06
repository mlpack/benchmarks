// Load benchmark.db.  Later, we will do something cool with it, once I figure
// out how.  If this is file:///, suggest that the user start a server since
// XMLHttpRequests may not work.
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
var chartType;
var control_list_length = 0;

var activeChartType = null;

// Basic chart parameters.
var width = 800; // This should be parameterizable...
var height = 600; // This should be parameterizable...
var margin = { top: 20, right: 20, bottom: 120, left: 40 };

// Static bindings of library names to colors.
var color = d3.scale.ordinal().range(["#98abc5", "#8a89a6", "#7b6888", "#6b486b", "#a05d56", "#d0743c", "#ff8c00"]);

/**
 * Utility function to map runtime results, which are in seconds or ">9000" or
 * "failure", to seconds.  ">9000" maps to max, and "failure" maps to 0.
 */
function mapRuntime(runtime, max)
{
  if (runtime == ">9000") { return max; }
  else if (runtime == "failure") { return 0; }
  else { return runtime; }
}

function clearSelectBox(box)
{
  for (i = box.options.length - 1; i >= 0; i--) { box.options[i] = null; }
}

function clearChart()
{
  if (activeChartType != null)
  {
    activeChartType.clear();
  }
}

function clearMethodControl()
{
  d3.selectAll(".methodcontrol").remove();
  d3.selectAll(".add_method_button").remove();
  d3.selectAll(".clear_methods_button").remove();
  d3.selectAll(".redraw_methods_button").remove();
}

function buildChart()
{
  if (activeChartType != null)
  {
    activeChartType.buildChart();
  }
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
  clearMethodControl();
  var selectHolder = d3.select(".selectholder");
  selectHolder.selectAll('label').remove();
  selectHolder.selectAll('select').remove();
  selectHolder.selectAll('br').remove();

  if (chartType == "algorithm-parameter-comparison") { activeChartType = rc; }
  else if (chartType == "historical-comparison") { activeChartType = hc; }
  else if (chartType == "metric-comparison") { activeChartType = mc; }
  //else if (chartType == "dataset-comparison")

  activeChartType.onTypeSelect();
}

function listMainDatasets()
{
  // We want the list of methods and dataset combinations.  Then we will figure
  // out how many methods go with each dataset.  For now though I'll just get a
  // list of datasets...
//  var sqlstr = "SELECT DISTINCT datasets.name, methods.id, methods.name, methods.parameters from methods, datasets, results where results.dataset_id == datasets.id and results.method_id == methods.id group by results.build_id;";
  var sqlstr = "SELECT datasets.name FROM datasets;";
  results = db.exec(sqlstr);

  var dataset_select_box = document.getElementById("main_dataset_select");
  for (i = dataset_select_box.options.length - 1; i >= 0; i--)
  {
    dataset_select_box.options[i] = null;
  }
  for (i = 0; i < results[0].values.length; i++)
  {
    var new_option = document.createElement("option");
    new_option.text = results[0].values[i][0];
    dataset_select_box.add(new_option);
  }
  dataset_select_box.selectedIndex = -1;
}

function mainDatasetSelect()
{
  var dataset_select_box = document.getElementById("main_dataset_select");
  dataset_name = dataset_select_box.options[dataset_select_box.selectedIndex].text;

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
      .attr("onclick", "clickAddButton()")
      .attr("value", "Add another method");
  d3.selectAll(".legendholder").append("input")
      .attr("type", "button")
      .attr("class", "clear_methods_button")
      .attr("onclick", "clickClearMethods()")
      .attr("value", "Remove all methods");
  d3.selectAll(".legendholder").append("input")
      .attr("type", "button")
      .attr("class", "redraw_methods_button")
      .attr("onclick", "clickRedrawMethods()")
      .attr("value", "Redraw graph");

  control_list_length = 0;

  // Collect the results for lists of methods.
}

function clickAddButton()
{
  var newmethodcontrol = d3.selectAll(".methodcontrol").append("div").attr("class", "methodcontroldiv");

  newmethodcontrol.append("label")
      .attr("for", "method_select_" + String(control_list_length))
      .attr("class", "method-select-label")
      .text("Method:");
  newmethodcontrol.append("select")
      .attr("id", "method_select_" + String(control_list_length))
      .attr("onchange", "methodControlListSelect()");
  newmethodcontrol.append("label")
      .attr("for", "param_select_" + String(control_list_length))
      .attr("class", "param-select-label")
      .text("Parameters:");
  newmethodcontrol.append("select")
      .attr("id", "param_select_" + String(control_list_length));

  control_list_length++;
}
