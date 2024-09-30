
$(document).ready(function () {
    let config = {
        clusters: 3,
        method: 'random',
        centroids: []  // Store manually selected centroids here
    };
    let manualSelectionMode = false;

    // Load the initial Plotly plot when the page loads
    updatePlot();

    // Monitor changes to the initialization method dropdown
    $('#init-method').change(function () {
        const method = $('#init-method').val();
        if (method === 'manual') {
            manualSelectionMode = true;
            config.centroids = [];  // Reset manual centroids
            $('#instructions').show();  // Show instructions for manual selection
            alert('Click on the plot to manually select centroids.');
        } else {
            manualSelectionMode = false;
            $('#instructions').hide();
        }
    });

    // Handle Initialization
    $('#initialize').click(function () {
        config.clusters = parseInt($('#clusters').val());
        config.method = $('#init-method').val();

        // If manual mode, ensure we have enough centroids selected
        if (config.method === 'manual' && config.centroids.length < config.clusters) {
            alert(`Please select ${config.clusters} centroids on the plot.`);
            return;
        }

        // Send the selected centroids to the backend for KMeans initialization
        $.ajax({
            url: '/initialize',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(config),
            success: function (response) {
                if("message" in response)
                { alert(response.message);}
                updatePlot();  // Reload plot with updated centroids and clusters
            }
        });
    });

    // Handle Step-Through KMeans
    $('#step-through').click(function () {
        $.post('/step', {}, function (response) {
            if("message" in response)
            {alert(response.message);}
            updatePlot();  // Update the plot after each step
        });
    });

    // Handle Generate New Dataset
    $('#generate').click(function () {
        $.post('/generate', {}, function (response) {
            if("message" in response)
            {alert(response.message);}
            config.centroids = [];  // Reset manually selected centroids
            updatePlot();  // Load new dataset
        });
    });

    // Handle Reset Algorithm
    $('#reset').click(function () {
        $.post('/reset', {}, function (response) {
            if("message" in response)
            {alert(response.message);}
            updatePlot();  // Reload plot with the same dataset but reset KMeans
        });
    });

    // Handle Run to Convergence
    $('#run-to-convergence').click(function () {
        $.post('/run-to-convergence', {}, function (response) {
            if("message" in response)
            {alert(response.message);}
            updatePlot();  // Display the final outcome of KMeans
        });
    });

    // Load and display the Plotly plot
    function updatePlot() {
        $.get('/plot', function (response) {
            console.log("Plotly JSON data received:", response);  // Debug log
            Plotly.newPlot('plotly-div', response.data, response.layout).then(function () {
                if (manualSelectionMode) {
                    setupManualCentroidSelection();  // Setup manual centroid selection
                }
            });
        });
    }

    // Set up event handling for manual centroid selection using Plotly's click events
    function setupManualCentroidSelection() {
        var plot = document.getElementById('plotly-div');

        // Capture clicks on the Plotly plot
        plot.on('plotly_click', function (data) {
            if (manualSelectionMode) {
                const x = data.points[0].x;
                const y = data.points[0].y;

                // Check if the click event captured data points correctly
                console.log(`Click detected at: (${x}, ${y})`);
                if (x === undefined || y === undefined) {
                    console.error("Error: No valid data point detected in the click event.");
                    return;
                }

                // Add the selected centroid to the config object
                config.centroids.push([x, y]);
                console.log(`Centroid selected and added to config: (${x.toFixed(2)}, ${y.toFixed(2)})`);
                console.log("Updated config centroids array:", config.centroids);

                // Add a visual marker on the plot for feedback
                Plotly.addTraces('plotly-div', {
                    x: [x],
                    y: [y],
                    mode: 'markers',
                    marker: { color: 'red', size: 12, symbol: 'x' },
                    name: 'Selected Centroid'
                });
            }
        });
    }
});
