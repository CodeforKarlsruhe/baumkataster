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
		    let m = document.getElementById("mapid")
		    m.style.width = Math.floor(w * .95) + "px"
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
			console.log(total + " trees added")
		}
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
			dsTrees.forEach(function(d){
				totalTrees += d.length
				console.log(d[0][5],": ",d.length)
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
				let marker = L.circle([t[0],t[1]], {
				  color: "green",
				  fillColor: (infoLink > "") ? "#0f0" : "#888",
				  fillOpacity: 0.5,
				  radius: 3.0
				})
				let info = '<div class="info">'
				info += t[2] + "<br>" + t[3] + "<br>" + t[1] + "<br>" + t[0]
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
			treeMap.panTo(new L.LatLng(dsList[id].center[1],dsList[id].center[0]))   //dsTrees[id][0][0],dsTrees[id][0][1]))
            document.getElementById("chart").style.display = "block"
            chart = mkChart(null)

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
				    dsList.push({"id":d.id,"name":d.name,"area":d.area,"bounds":d.bounds,"center":d.center})
					totalPop += parseInt(d.population)
					totalArea += parseInt(d.area)
				})
			})
			.then(function() {
				//console.log(dsList)
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
				i.innerHTML = "<h2>" + city + " " + totalPop + " Einwohner " + 
				(totalArea/1000000.0).toFixed(2) + "km² Fläche " + totalTrees + " Bäume</h2>"
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


// create a chart for the district
function mkChart(data){
    let chart = c3.generate({
        bindto: '#chart',
        size: {
            height: 150
        },
        bar: {
            width: 40
        },
        padding: {
            left: 60
        },
        color: {
            pattern: ['#FABF62', '#ACB6DD']
        },
        data: {
            x: 'x',
            columns:
                [
              ['x', 'Category1', 'Category2'],
              ['value', 300, 400]
              ],

            type: 'bar',
           
            color: function(inColor, data) {
                var colors = ['#FABF62', '#ACB6DD'];
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
            }
        },
        tooltip: {
            grouped: false
        },
        legend: {
            show: false
        }
    });
    return chart
}	
		

