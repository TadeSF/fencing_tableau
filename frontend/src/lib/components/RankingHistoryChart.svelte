<script lang="ts">
	import { onMount } from 'svelte';
	import { pageTitle } from '$lib/stores';
	import { userData } from '$lib/stores';

	import Chart from 'chart.js/auto';

	pageTitle.set('Statistics');

	let rankingHistoryChart: Chart | null = null;
	let rankingHistory: Chart | null = null;
	const lineTension = 0.3;

	onMount(() => {
		const rankingHistoryCtx = rankingHistoryChart.getContext('2d');

		rankingHistory = new Chart(rankingHistoryCtx, {
			type: 'line',
			data: {
				labels: $userData.graph_data.standings.labels,
				datasets: [
					{
						label: 'Standings',
						data: $userData.graph_data.standings.data,
						backgroundColor: '#000000',
						borderColor: '#000000',
						borderWidth: 2,
						yAxisID: 'y1',
						xAxisID: 'x1',
						tension: lineTension
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
					y1: {
						reverse: true,
						min: 1,
						max: $userData.graph_data.standings.y_max
						// display: false
					},
					x1: {
						grid: {
							display: false
						}
					}
				},
				animation: {
					duration: 1000
				}
			}
		});
	});

	$: if (rankingHistory instanceof Chart) {
		updateChart(rankingHistory, $userData.graph_data.standings.labels, $userData.graph_data.standings.data);
	}

	// Update function for the chart
	function updateChart(chart: Chart, labels: string[], data: number[]) {
		if (chart.data.labels?.length !== labels.length) {
			chart.data.labels = labels;
			chart.data.datasets[0].data = data;
			chart.update();
		}
	}
</script>

<canvas bind:this={rankingHistoryChart} id="chart" width="400" height="300" />
