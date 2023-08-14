<script lang="ts">
	import { page } from '$app/stores';

	import Fa from 'svelte-fa';
	import { faArrowLeft, faHome } from '@fortawesome/free-solid-svg-icons';
	import { fade } from 'svelte/transition';

	export let openBool = false;
    export let closeFunction: () => void;

	let isSubpage = false;

	$: if ($page.url.pathname.split('/').length > 3) {
		isSubpage = true;
	} else {
		isSubpage = false;
	}
</script>

<dialog id="SettingsModal" class="modal" class:modal-open={openBool}>
				<div class="modal-box">
					<h3 class="font-bold text-lg">Personal Settings</h3>
					<p class="py-4">Here Will be some options to change personal information as well as user preference things like language.</p>
					<div class="modal-action justify-between">
						<a href="/login" class="btn btn-error">Logout</a>
						<button class="btn" on:click={closeFunction}>Close</button>
					</div>
				</div>
			</dialog>

