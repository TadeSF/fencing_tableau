<script lang="ts">
	import type { PageData } from './$types';
	import { page } from '$app/stores';
	import { userData, standingsData, pageTitle } from '$lib/stores';
	import { flip } from 'svelte/animate';
	import { crossfade } from 'svelte/transition';
	import Fa from 'svelte-fa';
	import {
		faArrowDown19,
		faFlag,
		faHand,
		faHourglassHalf,
		faHouseFlag,
		faMinus,
		faPercent,
		faPlus,
		faPlusMinus,
		faSignature,
		faSquareCheck,
		faVenusMars
	} from '@fortawesome/free-solid-svg-icons';
	import AvatarFlag from '$lib/components/AvatarFlag.svelte';

	export let data: PageData;

	pageTitle.set('Standings');
</script>

<div class="w-full flex justify-center align-center">
	<div class="overflow-x-auto">
		<table class="table">
			<thead>
				<tr>
					<th>
						<div class="tooltip tooltip-bottom" data-tip="Rank">
							<Fa icon={faArrowDown19} />
						</div>
					</th>
					<th>
						<div class="tooltip tooltip-bottom" data-tip="Nationality">
							<Fa icon={faFlag} />
						</div>
					</th>
					<th>
						<div class="tooltip tooltip-bottom" data-tip="Start Number and Name">
							<Fa icon={faSignature} />
						</div>
					</th>
					<th>
						<div class="tooltip tooltip-bottom" data-tip="Club">
							<Fa icon={faHouseFlag} />
						</div>
					</th>
					<th>
						<div class="tooltip tooltip-bottom" data-tip="Win Percentage">
							<Fa icon={faPercent} />
						</div>
					</th>
					<th>
						<div class="tooltip tooltip-bottom" data-tip="Wins - Lost">
							<Fa icon={faSquareCheck} />
						</div>
					</th>
					<th>
						<div class="tooltip tooltip-bottom" data-tip="Point Difference">
							<Fa icon={faPlusMinus} />
						</div>
					</th>
					<th>
						<div class="tooltip tooltip-bottom" data-tip="Points for">
							<Fa icon={faPlus} />
						</div>
					</th>
					<th>
						<div class="tooltip tooltip-bottom" data-tip="Points against">
							<Fa icon={faMinus} />
						</div>
					</th>
					<th>
						<div class="tooltip tooltip-bottom" data-tip="Gender">
							<Fa icon={faVenusMars} />
						</div>
					</th>
					<th>
						<div class="tooltip tooltip-bottom" data-tip="Handedness">
							<Fa icon={faHand} />
						</div>
					</th>
					<th>
						<div class="tooltip tooltip-bottom" data-tip="Age">
							<Fa icon={faHourglassHalf} />
						</div>
					</th>
				</tr>
			</thead>
			<tbody>
				{#each $standingsData.standings as standings (standings.id)}
					<tr
						class={standings.id === $userData.id ? 'bg-primary-100' : 'bg-base-100'}
						animate:flip
					>
						<td>{standings.rank}</td>
						<td>
							<AvatarFlag flag={standings.nationality} size="w-10" />
						</td>
						<td>
							<button class="btn btn-ghost">{standings.name}</button>
						</td>
						<td>{standings.club}</td>
						<td>{standings.win_percentage}</td>
						<td>{standings.win_lose}</td>
						<td>{standings.points_difference}</td>
						<td>{standings.points_for}</td>
						<td>{standings.points_against}</td>
						<td>{standings.gender}</td>
						<td>{standings.handedness}</td>
						<td>{standings.age}</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
</div>
