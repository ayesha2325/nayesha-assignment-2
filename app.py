from flask import Flask, render_template, jsonify, request
import numpy as np
from kmeans import KMeans
import plotly.graph_objs as go

app = Flask(__name__)

# Initialize global variables
np.random.seed(42)
data = np.vstack([np.random.randn(100, 2) + np.array([i * 5, i * 5]) for i in range(3)])
kmeans = None
steps = []
current_step = 0
converged = False


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/plot', methods=['GET'])
def plot():
    global data, kmeans, current_step, converged
    # Create the initial scatter plot of the data points
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data[:, 0].tolist(), y=data[:, 1].tolist(), mode='markers', marker=dict(color='blue', size=8), name='Data Points'))

    if kmeans and current_step > 0:
        centroids, clusters = steps[current_step - 1]
        centroids = centroids.tolist()
        for i, cluster in enumerate(clusters):
            cluster_points = data[cluster]
            fig.add_trace(go.Scatter(x=cluster_points[:, 0].tolist(), y=cluster_points[:, 1].tolist(), mode='markers', name=f'Cluster {i + 1}'))
        fig.add_trace(go.Scatter(x=[c[0] for c in centroids], y=[c[1] for c in centroids], mode='markers', marker=dict(color='red', size=12, symbol='x'), name='Centroids'))

    fig.update_layout(title=f'KMeans Clustering - Step {current_step}' if current_step > 0 else 'Initial Data Points', xaxis_title='X', yaxis_title='Y')
    return jsonify(fig.to_dict())


@app.route('/initialize', methods=['POST'])
def initialize_kmeans():
    global data, kmeans, steps, current_step, converged
    k = int(request.json.get('clusters', 3))
    method = request.json.get('method', 'random')
    centroids = np.array(request.json.get('centroids')) if method == 'manual' else None
    kmeans = KMeans(data, k, method=method, centroids=centroids)
    steps = kmeans.fit(max_steps=10)
    current_step = 0
    converged = False
    return jsonify({'message': f'KMeans initialized with {k} clusters using {method} method.'})


@app.route('/step', methods=['POST'])
def step_kmeans():
    global current_step, converged
    if not kmeans or converged:
        return jsonify({'message': 'KMeans has converged!'})
    current_step += 1 if current_step < len(steps) else 0
    converged = current_step == len(steps)
    if converged:
        return jsonify({'message': 'KMeans has converged!'})
    else:
        return jsonify({'converged': converged})


@app.route('/generate', methods=['POST'])
def generate_data():
    global data, kmeans, steps, current_step, converged
    data = np.vstack([np.random.randn(100, 2) + np.array([i * 5, i * 5]) for i in range(3)])
    kmeans = None
    steps = []
    current_step = 0
    converged = False
    return jsonify({'message': 'New dataset generated!'})


# New Route: Reset the KMeans algorithm with the same dataset
@app.route('/reset', methods=['POST'])
def reset_kmeans():
    global data, kmeans, steps, current_step, converged
    if kmeans:
        kmeans = KMeans(data, kmeans.k, method=kmeans.method)
        steps = kmeans.fit(max_steps=10)
        current_step = 0
        converged = False
        return jsonify({'message': 'KMeans has been reset with the same dataset.'})
    return jsonify({'message': 'KMeans is not initialized yet.'})


# New Route: Run to Convergence
@app.route('/run-to-convergence', methods=['POST'])
def run_to_convergence():
    global current_step, converged
    if not kmeans:
        return jsonify({'message': 'KMeans is not initialized yet.'})
    current_step = len(steps)
    converged = True
    return jsonify({'message': 'KMeans ran to convergence and final clusters are displayed.'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
