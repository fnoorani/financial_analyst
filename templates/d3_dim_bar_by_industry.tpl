<body><!DOCTYPE html>
<meta charset="utf-8">
<head>
	<title>{{dimension}}</title>
    <script src="https://d3js.org/d3.v4.js"></script>
</head>
<style>
.tooltip {
    position: absolute;
}
</style>

</body>

<div id="my_dataviz" style="border: 1px solid black;"></div>

<script>
// ----------------
// Create a tooltip
// ----------------
var tooltip = d3.select("#my_dataviz")
.append("div")
.style("opacity", 0)
.attr("class", "tooltip")
.style("background-color", "yellow")
.style("border", "solid")
.style("border-width", "1px")
.style("border-radius", "5px")
.style("padding", "10px")

// Three function that change the tooltip when user hover / move / leave a cell
var mouseover = function(d) {
    var dim_val = d.n.toLocaleString('en-US', {
      style: 'currency',
      currency: 'USD',
    });
    var dim_label = d.label.toString();
    tooltip
        .html('<span style="font-style: italic;">' + dim_label + ', {{dimension}}</span>: <span style="font-weight: bold;">' + dim_val + "</span>")
        .style("opacity", 0.8)
}
var mousemove = function(d) {
    tooltip
      .style("left", (event.pageX + 10) + "px")
      .style("top", (event.pageY - 10) + "px")
}
var mouseleave = function(d) {
    tooltip
      .style("opacity", 0)
}


var margin = {top: 20, right: 40, bottom: 80, left: 220},
    width = 500 - margin.left - margin.right,
    height = 700 - margin.top - margin.bottom;

var svg = d3.select("#my_dataviz")
  .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform",
          "translate(" + margin.left + "," + margin.top + ")");

  // Parse the Data
  d3.json("/d3/top/nasdaq/{{dimension}}/industry/{{industry}}", function(json) {

  var data = json.items;
  let values = data.map(a => a.n);
  top_of_the_range = Math.max(...values);
  // Add X axis
  var x = d3.scaleLinear()
    .domain([0, top_of_the_range])
    .range([ 0, width]);
  svg.append("g")
    .attr("transform", "translate(0," + height + ")")
    .call(d3.axisBottom(x))
    .selectAll("text")
      .attr("transform", "translate(-10,0)rotate(-45)")
      .style("text-anchor", "end");

  // Y axis
  var y = d3.scaleBand()
    .range([ 0, height ])
    .domain(data.map(function(d) { return d.label; }))
    .padding(.1);
  svg.append("g")
    .call(d3.axisLeft(y))
  //Bars
  svg.selectAll("myRect")
    .data(data)
    .enter()
    .append("rect")
    .attr("x", x(0) )
    .attr("y", function(d) { return y(d.label); })
    .attr("width", function(d) { return x(d.n); })
    .attr("height", y.bandwidth() )
    .attr("fill", "steelblue")
  .on("mouseover", mouseover)
  .on("mousemove", mousemove)
  .on("mouseleave", mouseleave)


})

</script>
</html>