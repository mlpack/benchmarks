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

var activeChartType = null;

// Basic chart parameters.
var width = 800; // This should be parameterizable...
var height = 450; // This should be parameterizable...
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
    activeChartType.clearChart();
  }
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
  if (activeChartType != null)
  {
    activeChartType.clear();
  }

  var selectHolder = d3.select(".selectholder");
  selectHolder.selectAll('label').remove();
  selectHolder.selectAll('select').remove();
  selectHolder.selectAll('br').remove();

  if (chartType == "algorithm-parameter-comparison") { activeChartType = rc; }
  else if (chartType == "historical-comparison") { activeChartType = hc; }
  else if (chartType == "metric-multiple-parameter-comparison") { activeChartType = mmpc; }
  else if (chartType == "metric-parameter-comparison") { activeChartType = mpc; }
  else if (chartType == "dataset-comparison") { activeChartType = dc; }
  else if (chartType == "metric-comparison") { activeChartType = mc; }
  else if (chartType == "highest-metric-comparison") { activeChartType = hmc; }

  activeChartType.onTypeSelect();
}
