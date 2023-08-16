<script lang="ts">
	import { onMount } from 'svelte';
	import { pageTitle } from '$lib/stores';
	import { userData } from '$lib/stores';

	import Chart from 'chart.js/auto';

	pageTitle.set('Statistics');

	let pointDifferenceOverTimeChart: Chart | null = null;
    let pointDifferenceOverTime: Chart | null = null;
	const lineTension = 0.3;

	onMount(() => {
		const pointDifferenceOverTimeCtx = pointDifferenceOverTimeChart.getContext('2d');

		pointDifferenceOverTime = new Chart(pointDifferenceOverTimeCtx, {
			data: {
				labels: $userData.graph_data.points_difference.labels,
				datasets: [
					{
						type: 'line',
						label: 'Points Difference Development',
						data: [0].concat($userData.graph_data.points_difference.data),
						borderColor: '#000000',
						borderWidth: 2,
						tension: lineTension,
						xAxisID: 'x1',
						yAxisID: 'y1',
						pointBackgroundColor: '#000000',
					}
				]
			},
			options: {
				// responsive: false,
				// maintainAspectRatio: false,
				plugins: {
					legend: {
						display: false
					},
				},
				scales: {
					x1: {
						grid: {
							display: false
						}
					},
					y1: {
						grid: {
							display: true
						}
					}
				},
				animation: {
					duration: 1000
				}
			}
		});
	});

    $: if (pointDifferenceOverTime instanceof Chart) {
		updateChart(pointDifferenceOverTime, $userData.graph_data.points_difference.labels, [0].concat($userData.graph_data.points_difference.data));
	}

	// Update function for the chart
	function updateChart(chart: Chart, labels: string[], data: number[]) {
		if (chart.data.datasets[0].data !== data) {
            chart.data.labels = labels;
            chart.data.datasets[0].data = data;
			chart.update();
		}
	}

</script>

<canvas bind:this={pointDifferenceOverTimeChart} id="chart" width="400" height="300" />
