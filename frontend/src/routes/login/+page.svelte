<script lang="ts">
	import { page } from '$app/stores';

	const setTournamentId = () => {
		if ($page.url.searchParams.get('tournament_id'))
			return $page.url.searchParams.get('tournament_id');
		return '';
	};

	const disableIdField = () => {
		if ($page.url.searchParams.get('tournament_id')) return true;
		return false;
	};
</script>

<svelte:head>
	<title>Login</title>
</svelte:head>

<div class="w-full h-screen flex justify-center items-center bg-slate-200">
	<div class="card w-96 bg-base-100 shadow-xl m-4">
		<div class="card-body">
			<div class="card-title">Fencer Login</div>
			<form class="flex flex-col gap-2 my-5">
				<input
					type="text"
					placeholder="Tournament ID"
					class="input input-bordered w-full max-w-xs"
					value={setTournamentId()}
					disabled={disableIdField()}
				/>
				<input
					type="text"
					placeholder="Name or Number"
					class="input input-bordered w-full max-w-xs"
				/>
			</form>
			<a href="/QWCO0Z/1DMHDUNLHI" class="btn btn-secondary">Login</a>
		</div>
	</div>
</div>
