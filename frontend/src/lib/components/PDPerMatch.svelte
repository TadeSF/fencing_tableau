<script lang="ts">
	import { onMount } from 'svelte';
	import { pageTitle } from '$lib/stores';
	import { userData } from '$lib/stores';

	import Chart from 'chart.js/auto';

	pageTitle.set('Statistics');

	let pointDifferencePerMatchChart: Chart | null = null;
    let pointDifferencePerMatch: Chart | null = null;
	const lineTension = 0.3;

    
	onMount(() => {
        let colors_for_difference_chart = [];
        for (let i = 0; i < $userData.graph_data.points_difference_per_match.data.length; i++) {
            if ($userData.graph_data.points_difference_per_match.data[i] < 0) {
                colors_for_difference_chart[i] = 'rgba(255, 0, 0, 1)';
            } else {
                colors_for_difference_chart[i] = 'rgba(0, 150, 0, 1)';
            }
        }
		const pointDifferencePerMatchCtx = pointDifferencePerMatchChart.getContext('2d');

		pointDifferencePerMatch = new Chart(pointDifferencePerMatchCtx, {
			data: {
				labels: $userData.graph_data.points_difference.labels.splice(1),
				datasets: [
					{
						type: 'bar',
						label: 'Points Difference per Match',
						data: $userData.graph_data.points_difference_per_match.data,
						backgroundColor: colors_for_difference_chart,
						yAxisID: 'y1',
						xAxisID: 'x1',
						borderRadius: 5,

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
						// min: -15,
						// max: 15,
						grid: {
							color: function (context) {
								if (context.tick.value == 0) {
									return '#000000';
								} else {
									return '#dddddd';
								}
							},
							lineWidth: function (context) {
								if (context.tick.value == 0) {
									return 2;
								} else {
									return 1;
								}
							}
						}
					},
					x1: {
						grid: {
							display: false
						}
					}
				},
				tooltips: {
					callbacks: {
						label: function (tooltipItem) {
							return tooltipItem.yLabel;
						}
					}
				},
				animation: {
					duration: 1000
				}
			}
		});
	});

    $: if (pointDifferencePerMatch) {
		updateChart(pointDifferencePerMatch, $userData.graph_data.points_difference.labels.splice(1), $userData.graph_data.points_difference_per_match.data);
	}

	// Update function for the chart
	function updateChart(chart: Chart, labels: string[], data: number[]) {
		if (chart.data.datasets[0].data.length !== data.length) {
			chart.data.labels = labels;
			chart.data.datasets[0].data = data;
			chart.update();
		}
	}
</script>

<canvas bind:this={pointDifferencePerMatchChart} id="chart" width="400" height="300" />
