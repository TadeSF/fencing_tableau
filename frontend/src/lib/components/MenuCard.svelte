<script lang="ts">
	import type { PageData } from '../../routes/[tournament]/[fencer]/$types';
	import { page } from '$app/stores';
	import { fly } from 'svelte/transition';

	export let headline: string;
	export let text: string;
	export let image: string | undefined = undefined;
	export let buttonLabel: string = 'See Details';
	export let buttonLink: string = '#';
	export let alt: string = headline;
	export let transitionDelay: number = 0;
</script>

<a
	href={buttonLink}
	class="flex-1 card bg-base-100 shadow-xl"
	in:fly={{ y: 50, duration: 500, delay: transitionDelay }}
>
	{#if image}
		<figure class="overflow-hidden"><img src={image} {alt} /></figure>
	{/if}
	<div class="card-body">
		<h2 class="card-title">{headline}</h2>
		<p>{text}</p>
		<div class="card-actions justify-end">
			<button class="btn btn-primary">{buttonLabel}</button>
		</div>
	</div>
</a>
