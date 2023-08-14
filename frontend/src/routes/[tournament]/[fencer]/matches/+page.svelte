<script lang="ts">
	import type { PageData } from './$types';
    import { pageTitle } from '$lib/stores';

    import NextMatch from '$lib/components/NextMatch.svelte';

	export let data: PageData;

    pageTitle.set('Matches');
</script>

<NextMatch showToggleButton>
    
</NextMatch>