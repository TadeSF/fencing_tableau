<script lang="ts">
	import SettingsModal from './SettingsModal.svelte';

	import { page } from '$app/stores';
	import { userData, pageTitle } from '$lib/stores';

	import Fa from 'svelte-fa';
	import { faArrowLeft, faHome } from '@fortawesome/free-solid-svg-icons';
	import AvatarFlag from './AvatarFlag.svelte';

	let isSubpage = false;
	let isModalOpen = false;

	const closeModal = () => {
		isModalOpen = false;
	};

	$: if ($page.url.pathname.split('/').length > 3) {
		isSubpage = true;
	} else {
		isSubpage = false;
	}
</script>

<div class="navbar bg-white rounded-xl shadow-lg">
	<div class="flex-none">
		<button
			class="btn btn-ghost btn-square"
			disabled={!isSubpage}
			on:click={() => {
				if (isSubpage) {
					history.back();
				}
			}}
		>
			{#if !isSubpage}
				<i class="fas fa-home text-lg"></i>
				{:else}
				<i class="fas fa-arrow-left text-lg"></i>
			{/if}
		</button>
	</div>
	<div class="flex-1">
		<a class="ml-1 btn btn-ghost normal-case text-xl">{$pageTitle}</a>
	</div>
	<div class="flex-none">
		<button class={`btn btn-square btn-ghost`} on:click={() => (isModalOpen = true)}>
			<AvatarFlag flag={$userData.nationality} size="w-8" />
		</button>
		<SettingsModal openBool={isModalOpen} closeFunction={closeModal} />
	</div>
</div>
<div class="p-2">
	<slot />
</div>

<style lang="scss">
	.navbar {
		margin: 0.8rem;
		width: calc(100% - 1.6rem);
		position: sticky;
		top: 0.8rem;
		z-index: 100;
	}
</style>
