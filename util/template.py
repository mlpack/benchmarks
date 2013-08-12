'''
  @file template.py
  @author Marcus Edel

  This file contains the page templates.
'''

pageTemplate = """
<!doctype html>
<html>
    <head>
        <meta charset="utf-8">
        <meta name="description" content="">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title></title>
        <link rel="stylesheet" href="framework/bs3/css/bootstrap.min.css">
        <link rel="stylesheet" href="framework/font/style.css">
        <link rel="stylesheet" href="css/style.css">
    </head>
    <body>
  <div class="container">
    <div class="row">
      <div class="col-lg-12">
        <div class="text-center">
          <h4>Benchmarks</h4>
        </div>  

        <!-- Container Start -->
        <div class="container--graph collapse-group well">
          <div class="container__topContent">
            <div>
              <img class="center--image" src="%(topLineChart)s" alt="">
            </div>          
          </div>
        </div>

        %(methods)s

        </div>
      </div>
    </div>
    <div class="pagination--holder">
      <ul class="pagination">
        %(pagination)s
      </ul>
    </div>
  </div>
    <script src="framework/jquery/jquery.min.js"></script>
    <script src="framework/bs3/js/bootstrap.min.js"></script>
    <script src="js/slider.js"></script>
    <!--[if lte IE 7]>
      <script src="framework/font/lte-ie7.js"></script>
    <![endif]-->      
    </body>
</html>
"""

paginationTemplate = """
</ul>
    </div>
  </div>
    <script src="framework/jquery/jquery.min.js"></script>
    <script src="framework/bs3/js/bootstrap.min.js"></script>
    <script src="js/slider.js"></script>
    <!--[if lte IE 7]>
      <script src="framework/font/lte-ie7.js"></script>
    <![endif]-->      
    </body>
</html>
"""

methodTemplate = """
        <!-- Container Start -->
        <div class="container--graph collapse-group well">
          <div class="container__topContent">
            <p class="graph--name">%(methodName)s</p>
            <div class="holder--progressBar">
              <span class="progressBar__percentage">%(progressPositive)s</span>
              <span class="progressBar__firstPart" style="width:%(progressPositive)s;"></span>
              <span class="progressBar__secondPart" style="width:%(progressNegative)s;"></span>
            </div>
            <div class="btn-group">
              <a href="#collapseOne" class="btn graphs btn-grey icon-bars js-button"></a>
              <a href="#collapseTwo" class="btn info btn-grey icon-info js-button"></a>
              <a href="#collapseThree" class="btn memory btn-grey icon-paragraph-right-2 js-button"></a>
            </div>
          </div>
          <div id="collapseOne" class="container__bottomContent graph collapse">
            <div>
              <img class="center--image" src="%(lineChart)s" alt="">
            </div>
            <div>
              <img class="center--image" src="%(barChart)s" alt="">
            </div>
            <div>
              <table class="table table-striped">
                <thead>
                  <tr>
                    <th></th>
                    %(timingHeader)s
                  </tr>
                </thead>
                <tbody>
                  %(timingTable)s
                </tbody>
              </table>
            </div>
          </div>
          <div id="collapseTwo" class="container__bottomContent infos collapse">
            <div>
              <table class="table table-striped">
                <thead>
                  <tr>
                    <th></th>
                    <th>Size</th>   
                    <th>Number of Instances</th>
                    <th>Number of Attributes</th>
                    <th>Attribute Types</th>                                     
                  </tr>
                </thead>
                <tbody>
                  %(datasetTable)s
                </tbody>
              </table>
            </div>
          </div>

          <div id="collapseTwo" class="container__bottomContent memories collapse">
            <div>
              <div class="panel">
                <div class="panel-heading">Massif Log</div>
                  <div class="row">
                    
                  </div>
              </div>

            </div>
          </div>

          <div class="container__bottomContent">&#160;</div>
           <div class="row">
            <div class="col-lg-2">Libraries: %(numLibararies)s</div>
            <div class="col-lg-2">Datasets: %(numDatasets)s</div>
            <div class="col-lg-3">Total time: %(totalTime)s seconds</div>
            <div class="col-lg-2">Script failure: %(failure)s</div>
            <div class="col-lg-2">Timeouts failure: %(timeouts)s</div>          
          </div>
          <div class="row">
            <div class="col-lg-10">Parameters: %(parameters)s</div>
          </div>
        </div>

"""