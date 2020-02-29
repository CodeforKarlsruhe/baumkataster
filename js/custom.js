    // ka baumkataster 
    
	const city = "Karlsruhe"
	
	var dsList = []
	var dsTrees = []
	var currentMarkers = null
	
	const center = [49.014, 8.404]
	
	var treeMap
	var dsPopups = [] // district popups
	
	var totalPop = 0
	var totalTrees = 0
	var totalArea = 0
	const maxZoom = 19

    var chart = null // need the variable to update data
	var means = null
	var distId

    var width, height // for checking later 
      
    //var init = function() {	
    function init() {	
		'use strict'
        // disable sorry and turn on works. Do an initial fetch before creating the map element
		fetch("/baumkataster/assets/fetch.json",{cache: "no-cache"})
		  .then(function(response) {
			return response.json();
		  })
		  .then(function(status) {
			console.log("Fetch returned:",status.fetch);
            document.getElementById("sorry").style.display="none"
            document.getElementById("works").style.display="block"
		    let w = window.innerWidth;
		    let h = window.innerHeight;
            width = w
            height = h
		    let m = document.getElementById("mapid")
            if (m.style.width >600) 
    		    m.style.width = Math.floor(w * .95) + "px"
            else
    		    m.style.width = Math.floor(w * .92) + "px"
		    m.style.height = Math.floor(h * .95) + "px"
	        treeMap = L.map('mapid').setView(center, 13);
            // use osm api. a bit slow .... but we don't have an api key yet
            let osmUrl='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
	        let osmAttrib='Map data © <a href="https://openstreetmap.org">OpenStreetMap</a> contributors';
	        //var osm = new L.TileLayer(osmUrl, {minZoom: 10, maxZoom: 30, attribution: osmAttrib});	
	        let osm = new L.TileLayer(osmUrl, {	maxZoom: maxZoom, attribution: osmAttrib});	
	        osm.addTo(treeMap);
	        let l = document.getElementById("loading")
	        l.style.display = "block"
	        getTrees()
		  })
		  .catch(function(err) {
			// Error: response error, request timeout or runtime error
			console.log('fetch error! ', err);
		  })
    }


	function updateProgressBar(processed, total, elapsed, layersArray) {
		'use strict'
		let l = document.getElementById("loading")
		l.innerHTML = "Processes " + processed + " of " + total
		if (processed === total) {
			l.style.display = "none"
			//console.log(total + " trees added")
		}
	}

    // updateMapSize will regularily check for changed dimensions of the scree
    // and will update the container and the map
    function updateMapSize(){
        // console.log("Check size")
	    let w = window.innerWidth;
	    let h = window.innerHeight;
        if ((w != width) || (h != height)) {
            // console.log("Update size:",w,h)
            width = w
            height = h
		    let m = document.getElementById("mapid")
            if (m.style.width >600) 
    		    m.style.width = Math.floor(w * .95) + "px"
            else
    		    m.style.width = Math.floor(w * .92) + "px"
		    m.style.height = Math.floor(h * .95) + "px"
	        treeMap.invalidateSize()
            treeMap.setView(center, 13);
        }
        setTimeout(function(){ updateMapSize()}, 500);
    }

	// Note: the reference examples uses 50k items provided in 2 files
	// of 25k items each. Each file uses a separate markerList.
	// this might be faster ....
	// tested, doesn't seem to be realy faster. 
	// loading slows down from 60k items
	// might need to load by city district, e.g.
	// from 
	// https://github.com/CodeforKarlsruhe/btw2017/blob/master/daten/karlsruhe/umrisse/ka_stadtteile.geojson
	
	
	function getTrees() {
		'use strict'
		console.log("Fetching trees")
		fetch("/baumkataster/assets/trees.json",{cache: "no-cache"})
		  .then(function(response) {
			return response.json();
		  })
		  .then(function(trees) {
			console.log("Fetch completed");
			console.log("Items: ",trees.length)
            //
			let i
			for (i in trees){
				let t = trees[i]
				let di = parseInt(t[4]) // district index
				if (undefined == dsTrees[di]) dsTrees[di] = [] // create array if not exists
				dsTrees[di].push(t)
			}

		  })
		  .then (function() {
            //console.log("processing dsTrees in getTrees:",dsTrees.length)
			dsTrees.forEach(function(d){
				totalTrees += d.length
				//console.log(d[0][5],": ",d.length)
			})
			// hide 
			let l = document.getElementById("loading")
			l.style.display = "none"
			// get the districts
			 getDistricts()
			// could add a default view
			//addTrees(treeMap,1)
		  })
		  .catch(function(err) {
			// Error: response error, request timeout or runtime error
			console.log('fetch error! ', err);
		  })
	}

	function addTrees(id) {
		'use strict'

		let l = document.getElementById("loading")
		l.style.display = "block"

		//var markers = L.markerClusterGroup({ chunkedLoading: true, chunkProgress: updateProgressBar });
		if (null == currentMarkers)
			currentMarkers = L.markerClusterGroup({ disableClusteringAtZoom : maxZoom -1, spiderfyOnMaxZoom: false, chunkedLoading: true, chunkProgress: updateProgressBar });
		 
		let markerList = [] // new Array(trees.length)
		// using a preallocated array doesn't help as most time goes into addint the marker
		// above 50k€ items we have to be patient ... 
		
		// using a markerList seems to be must faster than calling
		// addLay for every items ...
		let ii
		for (ii in dsTrees){
			if (ii == 0) continue // skip 0 

			if (id && (id != ii)) continue // skip others
			
			let trees = dsTrees[ii] // get the selected trees. id 0 is  special!
			
			let i
			for (i in trees){
				let t = trees[i]
			
				// check if we have an info link
				let infoLink=""
				if (t[6] > "") {
					infoLink = '<br><a href="' + t[6] + '" target="_blank">Info</a>'
				}			
				// we can use markers or circles ...
				//let marker = L.marker([t[0],t[1]],{"title":t[2]})
                // with KLAM data we need a more complex color scheme
                // 1 => mostly green, 2 => yellow, 3 => blue, 4 => red
                let cat1, cat2, col
                if (t[7] && t[7] > "" ) {
                    cat1 = parseInt(t[7].split(".")[0])
                    cat2 = parseInt(t[7].split(".")[1])
                }
                switch (cat1) {
                    case 1:
                        col = [0,200,0]
                        break;
                    case 2:
                        col = [200,200,0]
                        break;
                    case 3:
                        col = [0,0,200]
                        break;
                    case 4:
                        col = [200,0,0]
                        break;
                }
                let fc = "#"
                for (let c in col) 
                    fc += ("0" + Math.floor(col[c] / cat2).toString(16)).slice(-2)

                
				let marker = L.circle([t[0],t[1]], {
				  color: "green",
				  //fillColor: (infoLink > "") ? "#0f0" : "#888",
				  fillColor: fc,
				  fillOpacity: 0.5,
				  radius: 3.0
				})
				let info = '<div class="info">'
				info += t[2] + "<br>" + t[3] + "<br>" + t[1] + "<br>" + t[0] + "<br>KLAM: " + t[7] 
				info += infoLink + "</div>"
				marker.bindPopup(info);
				markerList.push(marker);
			}

		}
		currentMarkers.addLayers(markerList)		

		treeMap.addLayer(currentMarkers);
		// finally center map
		if (0 == id){
			treeMap.panTo(new L.LatLng(center[0],center[1]))
            document.getElementById("chart").style.display = "none"
		} else {
            console.log("Centering to id",id,dsList[id].center)
            console.log("DsList:",dsList)
            
			treeMap.panTo(new L.LatLng(dsList[id].center[1],dsList[id].center[0]))   //dsTrees[id][0][0],dsTrees[id][0][1]))
            document.getElementById("chart").style.display = "block"
            let chartData = {}
            chartData.p = (dsList[id-1].pop / means.pop).toFixed(2)
            chartData.t = (dsList[id-1].trees / means.trees).toFixed(2)
            chartData.a = (dsList[id-1].area / means.area).toFixed(2)
            chartData.h = dsList[id-1].name
            chartData.i = id
            //console.log(id,chartData)
            if (null == chart) 
                chart = mkChart(null) // create default
            updateChart(chartData)

		}
	}

	function getDistricts() {
		'use strict'
		console.log("Fetching districts")
		fetch("/baumkataster/assets/districtsLeaf.json",{cache: "no-cache"})
			.then(function(response) {
			return response.json();
			})
			.then(function(districts) {
				console.log("Fetch completed");
				console.log("Items: ",districts.length)

				districts.forEach(function(d) {
					var polygon = L.polygon(d.coordinates, {
						weight: 2,
						fillOpacity: 0.2,
						fillColor: "white",
						color: 'black',
						dashArray: '3'
					})
					polygon.bindPopup(d.name + "<br>" + (d.area/1000000.0).toFixed(2) + 
						"km²<br>" + d.population + " Bewohner<br>" +
						dsTrees[d.id].length + " Bäume<br>")
					polygon.addTo(treeMap);
					dsPopups.push(polygon) // store polygon so we can open the popup after selection
                    //console.log("Add ds ",d.id,", trees: ",dsTrees[d.id].length)
                    //console.log("Add ds ",d.id,", means: ",d.means)
				    dsList.push({"id":d.id,"name":d.name,"area":d.area/1000000,
                        "pop":d.population,
                        "bounds":d.bounds,"center":d.center,
                        "trees":dsTrees[d.id].length})
					totalPop += parseInt(d.population)
					totalArea += parseInt(d.area)
					if (null == means){
						means = d.means
						means.n = districts.length
					}
				})
			})
			.then(function() {
				let s = document.getElementById("select")
				let option = document.createElement("option");
				s.add(option); 
				for (let i in dsList){
					option = document.createElement("option");
					option.text = dsList[i].name
					s.add(option); 
				}
				option = document.createElement("option");
				option.text = "Alle"
				s.add(option); 
				// update info
				let i = document.getElementById("topInfo")
				i.innerHTML = "<h2>" + city + "</h2>"
                // call the size update function
                updateMapSize()
			})
		  .catch(function(err) {
			// Error: response error, request timeout or runtime error
			console.log('fetch error! ', err);
		  })
	}

	async function distSel() {
		'use strict'
		let s = document.getElementById("select")
		let i = s.selectedIndex
		// remove old
		if (null != currentMarkers) {
			currentMarkers.clearLayers()
		}
		if (0 == i) {
            document.getElementById("chart").style.display = "none"
            return
        }
		let l = document.getElementById("loading")
		l.style.display = "block"
		if (dsList.length + 1 != i) {
			let n = dsList[i-1].name
			let ii = dsList[i-1].id
			await Sleep(100)
			console.log("Selected: ",i,": ",n)
			addTrees(ii)
			dsPopups[i-1].openPopup()
		} else {
			l.innerHTML = "Loading all trees. Please be patient ..."
			await Sleep(100)
			console.log("all")
			addTrees(0)
		}
	}

	// helper function for delay
	function Sleep(milliseconds) {
		'use strict'
	  return new Promise(resolve => setTimeout(resolve, milliseconds));
	}


function updateChart(data)
{
    //console.log("Update:",data)
	distId = data.i // set global id for tooltip
    chart.load({
        columns:[
              ['x', 'Einwohner',"Bäume","Fläche"],
              ['Relative', data.p, data.t,data.a]
        ]
    });
    d3.select('#chart .c3-title').node().innerHTML = "Kennzahlen für " + data.h

}

// create a chart for the district
function mkChart(data){
    //console.log("init:",data)
    let chart = c3.generate({
        bindto: '#chart',
        size: {
            height: 150
        },
        margin: {
            right: 20
        },
        bar: {
            width: 20
        },
        padding: {
            right: 20,
            left: 60
        },
        /*
        color: {
            pattern: ['#0f0', '#f00',"#00f"]
        },
        */
        data: {
            x: 'x',
            columns:
                [
              ['x', 'Einwohner',"Bäume","Fläche"],
              ['Relative', 1,1,1]
              ],

            type: 'bar',
           
            color: function(inColor, data) {
                var colors = ['#00f', '#0f0',"#088"];
                if(data.index !== undefined) {
                    return colors[data.index];
                }

                return inColor;
            }
        },
        axis: {
            rotated: true,
            x: {
                type: 'category'
            },
            y: {
                label: {
                    text: "Daten relativ zum Mittelwert",
                    position:'outer-center'
                },
                tick: {
                    count: 5,
                    format: function (y) { return y.toFixed(2); }
                }
            }
        },
        tooltip: {
            grouped: false,
            /*
            format: {
                title: function (d) { return 'Data ' + d; },
                value: function (value, ratio, id) {
                    console.log("Tooltip fomtat:",data)
                    var format = id === 'data1' ? d3.format(',') : d3.format('$');
                    return format(value);
                }
                   //value: d3.format(',') // apply this format to both y and y2
            },
            */
            contents: function (d, defaultTitleFormat, defaultValueFormat, color) {
            //console.log("Tooltip content",d)
            /* input is array of data objects like so:
                id: "value",index: 0,name: "value",value: 1.81,x: 0
                index 0 is top on bar chart
            */
            // see https://stackoverflow.com/questions/24754239/how-to-change-tooltip-content-in-c3js
            let c = this // get chart
            //console.log(c.config)
			//console.log("tt: ",c.data)
            //console.log(defaultTitleFormat,defaultValueFormat)
            // we have only a single value 
            let title = defaultTitleFormat(d[0].x)
            let text = "<table class='" + c.CLASS.tooltip + "'><tr><th colspan='2'>" + title + "</th></tr>"
            name = d[0].name
            let value = defaultValueFormat(d[0].value, d[0].ratio, d[0].id, d[0].index);
			let absVal, totVal
			switch (parseInt(d[0].index)){
				case 0:
					absVal = dsList[distId - 1].pop //Math.round(value * means.pop)
					totVal = totalPop
					break
				case 1:
					absVal = dsList[distId - 1].trees
					totVal = totalTrees
					break
				case 2:
					absVal = dsList[distId - 1].area.toFixed(2) + "km²"
					totVal = (totalArea/1000000).toFixed(2) + "km²"
					break
			}
            let bgcolor = color(d[0].id)
            text += "<tr class='" + c.CLASS.tooltipName + "-" + d[0].id + "'>";
            text += "<td class='name'><span style='background-color:" + bgcolor + "'></span>Relativ</td>";
            text += "<td class='value'>" + value + "</td></tr>"
			text += "<tr><td class='name'><span style='background-color:" + bgcolor + "'></span>Absolut</td>";
            text += "<td class='value'>" + absVal + "</td></tr>"
			text += "<tr><td class='name'><span style='background-color:" + bgcolor + "'></span>Gesamt</td>";
            text += "<td class='value'>" + totVal + "</td></tr>"
            text + "</table>"
            return text
          }
        },
        legend: {
            show: false
        },
        title: {
            text: "Kennzahlen des Stadtteils"
        }
  
    });
    return chart
}	
		

